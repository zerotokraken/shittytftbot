import discord
from discord.ext import commands
import requests
import urllib.parse
import os
import re

class StatCommands(commands.Cog):
    def __init__(self, bot, apikey, latest_version, set_number):
        self.bot = bot
        self.apikey = apikey  # Assigning API key correctly
        self.latest_version = latest_version
        self.set_number= set_number
        self.tt_url = os.getenv('tt_url')



    @commands.command()
    async def stats(self, ctx):
        try:
            # Get user settings from database
            conn = self.bot.get_cog('UserSettings').get_db_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('SELECT tft_name, tft_tag, region FROM tft_settings WHERE discord_id = %s', (ctx.author.id,))
                result = cursor.fetchone()
                if not result:
                    await ctx.send("Please set your TFT name and region first using `.set Name#TAG region`\nExample: `.set ZTK#TFT americas`")
                    return
                
                gameName, tagLine, stored_region = result
            finally:
                cursor.close()
                conn.close()

            shortened_gameName = gameName.strip()
            # Encode the gameName to handle spaces and special characters
            encoded_gameName = urllib.parse.quote(gameName)

            # Get player region and puuid
            api_url = f"https://{stored_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_gameName}/{tagLine}?api_key={self.apikey}"
            response = requests.get(api_url)
            if response.status_code == 200:
                player_data = response.json()
                puuid = player_data['puuid']
                # Get player's region
                region_url = f"https://{stored_region}.api.riotgames.com/riot/account/v1/region/by-game/tft/by-puuid/{puuid}?api_key={self.apikey}"
                region_response = requests.get(region_url)
                if region_response.status_code == 200:
                    region_data = region_response.json()
                    current_region = region_data['region'].lower()
                else:
                    print(f"Failed to get player region. Status code: {region_response.status_code}")
                    print(f"Response: {region_response.text}")
                    await ctx.send("Failed to get player region. Please check your name and region.")
                    return
            else:
                print(f"Failed to get puuid. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                await ctx.send("Failed to lookup player. Please check your name and region.")
                return

            # Get league data using PUUID and region
            league_url = f"https://{current_region}.api.riotgames.com/tft/league/v1/entries/by-puuid/{puuid}?api_key={self.apikey}"
            league_response = requests.get(league_url)
            if league_response.status_code == 200:
                league_data = league_response.json()
                if not league_data:
                    print("No league data found.")
                    print(f"PUUID: {puuid}")
                    print(f"Region: {current_region}")
                    await ctx.send("No ranked data found for this player.")
                    return
            else:
                print(f"Failed to get league data. Status code: {league_response.status_code}")
                print(f"Response: {league_response.text}")
                await ctx.send("Failed to get league data. Please check your name and region.")
                return

            # Extract the required data
            tier = league_data[0]['tier']
            rank = league_data[0]['rank']
            league_points = league_data[0]['leaguePoints']
            wins = league_data[0]['wins']
            losses = league_data[0]['losses']
            total_games = wins + losses

            # Fetch match stats for calculating Win %, Top 4 %, and Avg Placement
            tactics_url = f"{self.tt_url}/{stored_region}/{gameName}/{tagLine}/{self.set_number}0/0"
            print(f"Tactics.tools URL: {tactics_url}")
            tactics_response = requests.get(tactics_url)
            if tactics_response.status_code != 200:
                print(f"Failed to get tactics.tools data. Status code: {tactics_response.status_code}")
                print(f"Response: {tactics_response.text}")

            if tactics_response.status_code == 200:
                data = tactics_response.json()
                overview = data["queueSeasonStats"]["1100"]
                # icon_id = data["playerInfo"]["profileIconId"]
                local_rank = data["playerInfo"]["localRank"]

                # Unpack the array into two variables
                rank_value, rank_probability = local_rank
                # Determine which value to use for rank display

                if rank_value <= 1000:
                    display_rank = f"#{rank_value}"
                else:
                    display_rank = f"{rank_probability * 100:.2f}%"

                # Calculate Win %, Top 4 %, and Average Placement
                plays = overview["games"]
                wins = overview["win"]
                tops = overview["top4"]
                win_percentage = (wins / plays) * 100
                top4_percentage = (tops / plays) * 100
                average_placement = overview["avgPlace"]

            # Define colors based on rank
            rank_colors = {
                'Challenger': discord.Color.from_rgb(255, 215, 0),
                'Grandmaster': discord.Color.from_rgb(255, 165, 0),
                'Diamond': discord.Color.from_rgb(0, 191, 255),
                'Platinum': discord.Color.from_rgb(0, 128, 128),
                'Emerald': discord.Color.from_rgb(0, 128, 0),
                'Gold': discord.Color.from_rgb(255, 215, 0),
                'Silver': discord.Color.from_rgb(192, 192, 192),
                'Bronze': discord.Color.from_rgb(139, 69, 19),
                'Master': discord.Color.from_rgb(128, 0, 128)
            }

            # Convert the tier to match the regalia data keys
            tier_key = tier.capitalize()

            # Get the regalia image based on the player's rank
            regalia_url = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/data/en_US/tft-regalia.json"
            regalia_response = requests.get(regalia_url)
            regalia_data = regalia_response.json()

            rank_image_url = None
            if tier_key in regalia_data["data"]["RANKED_TFT"]:
                rank_image = regalia_data["data"]["RANKED_TFT"][tier_key]["image"]["full"]
                rank_image_url = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/img/tft-regalia/{rank_image}"

            embed_color = rank_colors.get(tier_key, discord.Color.default())

            embed = discord.Embed(
                title=f"{gameName}",
                color=embed_color
            )

            region_cleaned = re.sub(r'\d+', '', current_region).upper()

            # Add fields based on tier
            if tier in ["CHALLENGER", "GRANDMASTER", "MASTER"]:
                embed.add_field(name="Rank", value=f"{tier_key} ({league_points} LP)", inline=False)
            else:
                embed.add_field(name="Rank", value=f"{tier_key} {rank} ({league_points} LP)", inline=False)
            embed.add_field(name="Leaderboard", value=f"Top {display_rank} {region_cleaned}", inline=False)
            embed.add_field(name="Total Games", value=str(total_games), inline=False)
            embed.add_field(name="Win %", value=f"{win_percentage:.2f}%", inline=False)
            embed.add_field(name="Top 4 %", value=f"{top4_percentage:.2f}%", inline=False)
            embed.add_field(name="Average Placement", value=f"{average_placement:.2f}", inline=False)
            embed.set_footer(text=f"Data sourced from tactics.tools")

            if rank_image_url:
                embed.set_thumbnail(url=rank_image_url)

            await ctx.send(embed=embed)

        except Exception as e:
            import traceback
            print(f"Error in stats command:")
            print(f"Error message: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            await ctx.send(f"An error occurred while looking up your stats. Please check your name and region.")


async def setup(bot, apikey, latest_version, set_number):
    await bot.add_cog(StatCommands(bot, apikey, latest_version, set_number))
