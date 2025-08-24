import discord
from discord.ext import commands
import requests
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

            # Fetch rank data for all players
            player_ranks = []
            for discord_id, name, tag, region in players:
                try:
                    print(f"\nProcessing player: {name}#{tag} ({region})")
                    # For SEA region, use asia region for account lookup
                    account_region = 'asia' if region.lower() == 'sea' else region
                    print(f"Using account region: {account_region}")
                    
                    # Get PUUID
                    api_url = f"https://{account_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{urllib.parse.quote(name)}/{tag}?api_key={self.apikey}"
                    print(f"PUUID URL: {api_url}")
                    response = requests.get(api_url)
                    print(f"PUUID Response status: {response.status_code}")
                    if response.status_code == 200:
                        player_data = response.json()
                        puuid = player_data['puuid']

                        # Get rank data
                        league_url = f"https://{region}.api.riotgames.com/tft/league/v1/by-puuid/{puuid}?api_key={self.apikey}"
                        print(f"League URL: {league_url}")
                        league_response = requests.get(league_url)
                        print(f"League Response status: {league_response.status_code}")
                        if league_response.status_code == 200:
                            league_data = league_response.json()
                            print(f"League data: {league_data}")
                            if league_data:  # Player has ranked data
                                rank_data = league_data[0]
                                player_ranks.append({
                                    'discord_id': discord_id,
                                    'name': name,
                                    'tier': rank_data['tier'],
                                    'rank': rank_data.get('rank', 'I'),  # Default to I for Master+
                                    'lp': rank_data['leaguePoints'],
                                    'wins': rank_data['wins'],
                                    'losses': rank_data['losses']
                                })
                except Exception as e:
                    print(f"Error fetching data for {name}: {str(e)}")
                    continue

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
                title="TFT Leaderboard",
                color=discord.Color.blue()
            )

            # Add top 10 players to embed
            for i, player in enumerate(player_ranks[:10], 1):
                total_games = player['wins'] + player['losses']
                win_rate = (player['wins'] / total_games * 100) if total_games > 0 else 0
                rank_str = self.format_rank(player['tier'], player['rank'], player['lp'])
                
                # Get member name if possible, otherwise use TFT name
                member = ctx.guild.get_member(player['discord_id'])
                display_name = member.display_name if member else player['name']
                
                embed.add_field(
                    name=f"#{i} {display_name}",
                    value=f"{rank_str}\nWin Rate: {win_rate:.1f}% ({player['wins']}/{total_games})",
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
