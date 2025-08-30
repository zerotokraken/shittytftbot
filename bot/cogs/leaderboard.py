import discord
from discord.ext import commands
import aiohttp
import asyncio
import os
import urllib.parse

class Leaderboard(commands.Cog):
    def __init__(self, bot, apikey, set_number):
        self.bot = bot
        self.apikey = apikey
        self.set_number = set_number
        self.tt_url = os.getenv('tt_url')

    def get_rank_value(self, tier, rank, league_points):
        """Helper function to convert rank to a numeric value for sorting"""
        # For Challenger/Grandmaster/Master, sort by LP first but keep them above other ranks
        if tier in ['CHALLENGER', 'GRANDMASTER', 'MASTER']:
            # Use a high base value to keep them above other ranks
            base = 1000000
            # Add additional value based on tier to keep the general tier order
            tier_bonus = {'CHALLENGER': 2000, 'GRANDMASTER': 1000, 'MASTER': 0}
            # LP becomes the primary sort value within these tiers
            return base + league_points + tier_bonus[tier]
        
        # For other ranks, use the traditional tier + division + LP system
        tier_values = {
            'DIAMOND': 6000,
            'EMERALD': 5000,
            'PLATINUM': 4000,
            'GOLD': 3000,
            'SILVER': 2000,
            'BRONZE': 1000,
            'IRON': 0
        }
        rank_values = {'I': 400, 'II': 300, 'III': 200, 'IV': 100}
        return tier_values[tier] + rank_values[rank] + league_points

    def format_rank(self, tier, rank, league_points):
        """Format rank string based on tier"""
        if tier in ['CHALLENGER', 'GRANDMASTER', 'MASTER']:
            return f"{tier.capitalize()} ({league_points} LP)"
        return f"{tier.capitalize()} {rank} ({league_points} LP)"

    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx):
        """Show top 10 ranked players"""
        # Check if command is used in the correct channel
        if ctx.channel.id not in [1285382023887978526, 1308312472419307602]:
            await ctx.send(f"This command can only be used in <#1285382023887978526>", delete_after=5)
            try:
                await ctx.message.delete()
            except:
                pass
            return

        try:
            # Get all registered players from database
            conn = self.bot.get_cog('UserSettings').get_db_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('SELECT discord_id, tft_name, tft_tag, region FROM tft_settings')
                players = cursor.fetchall()
                print(f"Found {len(players)} registered players")
                if not players:
                    await ctx.send("No registered players found.")
                    return
            finally:
                cursor.close()
                conn.close()

            # Add loading message
            message = await ctx.send("Fetching leaderboard data...")

            async def make_request(session, url, name, operation):
                for attempt in range(3):  # Try up to 3 times
                    try:
                        async with session.get(url, timeout=10) as response:  # 10 second timeout
                            if response.status == 429:  # Rate limit hit
                                retry_after = int(response.headers.get('Retry-After', 1))
                                print(f"Rate limit hit for {name}, waiting {retry_after}s")
                                await asyncio.sleep(retry_after)
                                continue
                            elif response.status != 200:
                                print(f"Failed {operation} for {name}: {response.status}")
                                return None
                            return await response.json()
                    except asyncio.TimeoutError:
                        print(f"Timeout for {operation} {name}, attempt {attempt + 1}")
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"Error in {operation} for {name}: {str(e)}")
                        return None
                return None

            async def fetch_player_data(session, discord_id, name, tag, region):
                try:
                    print(f"\nProcessing player: {name}#{tag} ({region})")
                    account_region = 'asia' if region.lower() == 'sea' else region
                    
                    # Get PUUID
                    api_url = f"https://{account_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{urllib.parse.quote(name)}/{tag}?api_key={self.apikey}"
                    player_data = await make_request(session, api_url, name, "PUUID lookup")
                    if not player_data:
                        return None
                    puuid = player_data['puuid']

                    await asyncio.sleep(0.5)  # Increased delay between requests

                    # Get player's sub-region for TFT
                    region_url = f"https://{account_region}.api.riotgames.com/riot/account/v1/region/by-game/tft/by-puuid/{puuid}?api_key={self.apikey}"
                    region_data = await make_request(session, region_url, name, "region lookup")
                    if not region_data:
                        return None
                    sub_region = region_data['region'].lower()

                    await asyncio.sleep(0.5)  # Increased delay between requests

                    # Get rank data using the correct sub-region
                    league_url = f"https://{sub_region}.api.riotgames.com/tft/league/v1/by-puuid/{puuid}?api_key={self.apikey}"
                    league_data = await make_request(session, league_url, name, "league data")
                    if not league_data or not league_data[0]:  # Check for empty list or missing data
                        print(f"No ranked data found for {name}")
                        return None
                    
                    rank_data = league_data[0]

                    # Get tactics.tools data
                    tactics_url = f"{self.tt_url}/{sub_region}/{name}/{tag}/{self.set_number}0/0"
                    tactics_data = await make_request(session, tactics_url, name, "tactics.tools data")
                    if not tactics_data:
                        print(f"No tactics.tools data found for {name}")
                        return None

                    overview = tactics_data["queueSeasonStats"]["1100"]
                    plays = overview["games"]
                    wins = overview["win"]
                    tops = overview["top4"]
                    win_percentage = (wins / plays) * 100
                    top4_percentage = (tops / plays) * 100

                    return {
                        'discord_id': discord_id,
                        'name': name,
                        'tier': rank_data['tier'],
                        'rank': rank_data.get('rank', 'I'),  # Default to I for Master+
                        'lp': rank_data['leaguePoints'],
                        'games': plays,
                        'win_rate': win_percentage,
                        'top4_rate': top4_percentage
                    }
                except Exception as e:
                    print(f"Error fetching data for {name}: {str(e)}")
                    return None

            # Process players in chunks to avoid rate limits
            timeout = aiohttp.ClientTimeout(total=120)  # Increased timeout for slower processing
            chunk_size = 10  # Process 5 players at a time
            player_ranks = []

            async with aiohttp.ClientSession(timeout=timeout) as session:
                for i in range(0, len(players), chunk_size):
                    chunk = players[i:i + chunk_size]
                    tasks = [fetch_player_data(session, p[0], p[1], p[2], p[3]) for p in chunk]
                    chunk_results = [p for p in await asyncio.gather(*tasks) if p is not None]
                    player_ranks.extend(chunk_results)
                    
                    if i + chunk_size < len(players):  # If there are more chunks to process
                        print(f"Processed {i + chunk_size}/{len(players)} players, waiting before next chunk...")
                        await asyncio.sleep(2)  # Wait 2 seconds between chunks

            if not player_ranks:
                await ctx.send("No ranked data found for any players.")
                return

            # Sort players by rank
            player_ranks.sort(
                key=lambda x: self.get_rank_value(x['tier'], x['rank'], x['lp']),
                reverse=True
            )

            # Create embed
            embed = discord.Embed(
                title="Comp TFT Leaderboard",
                color=discord.Color.blue()
            )

            # Add top 10 players to embed
            for i, player in enumerate(player_ranks[:10], 1):
                rank_str = self.format_rank(player['tier'], player['rank'], player['lp'])
                
                # Get member name if possible, otherwise use TFT name
                member = ctx.guild.get_member(player['discord_id'])
                display_name = member.display_name if member else player['name']
                
                embed.add_field(
                    name=f"#{i} {display_name}",
                    value=f"{rank_str}\nWin: {player['win_rate']:.1f}%\nTop 4: {player['top4_rate']:.1f}%\nGames: {player['games']}",
                    inline=False
                )

            await message.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            import traceback
            print(f"Error in leaderboard command:")
            print(f"Error message: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            await ctx.send("An error occurred while fetching the leaderboard.")

async def setup(bot, apikey, set_number):
    await bot.add_cog(Leaderboard(bot, apikey, set_number))
