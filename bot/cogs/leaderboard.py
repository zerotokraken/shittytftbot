import discord
from discord.ext import commands
import aiohttp
import asyncio
import urllib.parse

class Leaderboard(commands.Cog):
    def __init__(self, bot, apikey):
        self.bot = bot
        self.apikey = apikey

    def get_rank_value(self, tier, rank, league_points):
        """Helper function to convert rank to a numeric value for sorting"""
        tier_values = {
            'CHALLENGER': 9000,
            'GRANDMASTER': 8000,
            'MASTER': 7000,
            'DIAMOND': 6000,
            'EMERALD': 5000,
            'PLATINUM': 4000,
            'GOLD': 3000,
            'SILVER': 2000,
            'BRONZE': 1000,
            'IRON': 0
        }
        
        # For Challenger/Grandmaster/Master, only LP matters after tier
        if tier in ['CHALLENGER', 'GRANDMASTER', 'MASTER']:
            return tier_values[tier] + league_points
        
        # For other ranks, convert rank (I-IV) to points
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
        if ctx.channel.id != 1285382023887978526:
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

            async def fetch_player_data(session, discord_id, name, tag, region):
                try:
                    print(f"\nProcessing player: {name}#{tag} ({region})")
                    # For SEA region, use asia region for account lookup
                    account_region = 'asia' if region.lower() == 'sea' else region
                    print(f"Using account region: {account_region}")
                    
                    # Get PUUID
                    api_url = f"https://{account_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{urllib.parse.quote(name)}/{tag}?api_key={self.apikey}"
                    print(f"PUUID URL: {api_url}")
                    async with session.get(api_url) as response:
                        if response.status != 200:
                            print(f"Failed to get PUUID for {name}: {response.status}")
                            return None
                        player_data = await response.json()
                        puuid = player_data['puuid']

                    # Get player's sub-region for TFT
                    region_url = f"https://{account_region}.api.riotgames.com/riot/account/v1/region/by-game/tft/by-puuid/{puuid}?api_key={self.apikey}"
                    print(f"Region URL: {region_url}")
                    async with session.get(region_url) as region_response:
                        if region_response.status != 200:
                            print(f"Failed to get region for {name}: {region_response.status}")
                            return None
                        region_data = await region_response.json()
                        sub_region = region_data['region'].lower()
                        print(f"Using sub-region: {sub_region}")

                    # Get rank data using the correct sub-region
                    league_url = f"https://{sub_region}.api.riotgames.com/tft/league/v1/by-puuid/{puuid}?api_key={self.apikey}"
                    print(f"League URL: {league_url}")
                    async with session.get(league_url) as league_response:
                        if league_response.status != 200:
                            print(f"Failed to get league data for {name}: {league_response.status}")
                            return None
                        league_data = await league_response.json()
                        print(f"League data for {name}: {league_data}")
                        if not league_data:  # Empty list means no ranked data
                            print(f"No ranked data found for {name}")
                            return None
                        
                        rank_data = league_data[0]
                        return {
                            'discord_id': discord_id,
                            'name': name,
                            'tier': rank_data['tier'],
                            'rank': rank_data.get('rank', 'I'),  # Default to I for Master+
                            'lp': rank_data['leaguePoints'],
                            'wins': rank_data['wins'],
                            'losses': rank_data['losses']
                        }
                except Exception as e:
                    print(f"Error fetching data for {name}: {str(e)}")
                    return None

            # Fetch rank data for all players concurrently
            async with aiohttp.ClientSession() as session:
                tasks = [fetch_player_data(session, p[0], p[1], p[2], p[3]) for p in players]
                player_ranks = [p for p in await asyncio.gather(*tasks) if p is not None]

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
                total_games = player['wins'] + player['losses']
                rank_str = self.format_rank(player['tier'], player['rank'], player['lp'])
                
                # Get member name if possible, otherwise use TFT name
                member = ctx.guild.get_member(player['discord_id'])
                display_name = member.display_name if member else player['name']
                
                embed.add_field(
                    name=f"#{i} {display_name}",
                    value=f"{rank_str}\nGames: {total_games}",
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

async def setup(bot, apikey):
    await bot.add_cog(Leaderboard(bot, apikey))
