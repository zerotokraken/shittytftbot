import discord
from discord.ext import commands
import requests
import urllib.parse
import os

class LookupCommands(commands.Cog):
    def __init__(self, bot, apikey, latest_version):
        self.bot = bot
        self.APIKEY = apikey  # Assigning API key correctly
        self.latest_version = latest_version
        self.tt_url = os.getenv('tt_url')

    @commands.command(help="Lookup a player by name and tagline (format: name#tagline)")
    async def lookup(self, ctx, *, player: str):
        try:
            # Split the player argument into gameName and tagLine
            gameName, tagLine = player.split('#')

            shortened_gameName = gameName.strip()
            # Encode the gameName to handle spaces and special characters
            encoded_gameName = urllib.parse.quote(gameName)

            # Define the regions
            account_regions = ["americas", "asia", "europe"]
            summoner_regions = ["na1", "eun1", "euw1", "br1", "jp1", "kr", "la1", "la2", "me1", "oc1", "ph2", "ru", "sg2", "th2", "tr1", "tw2", "vn2"]

            # Try each account region to get puuid
            puuid = None
            for region in account_regions:
                api_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_gameName}/{tagLine}?api_key={self.APIKEY}"
                response = requests.get(api_url)
                if response.status_code == 200:
                    player_data = response.json()
                    puuid = player_data['puuid']
                    break
            if not puuid:
                print("Failed to lookup player in all account regions.")
                return

            # Try each summoner region to get summonerId
            summoner_id = None
            for region in summoner_regions:
                summoner_url = f"https://{region}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{puuid}?api_key={self.APIKEY}"
                summoner_response = requests.get(summoner_url)
                if summoner_response.status_code == 200:
                    summoner_data = summoner_response.json()
                    summoner_id = summoner_data['id']
                    break
            if not summoner_id:
                print("Failed to get summoner data in all summoner regions.")
                return

            # Try each summoner region to get league data
            league_data = None
            for region in summoner_regions:
                league_url = f"https://{region}.api.riotgames.com/tft/league/v1/entries/by-summoner/{summoner_id}?api_key={self.APIKEY}"
                league_response = requests.get(league_url)
                if league_response.status_code == 200:
                    league_data = league_response.json()
                    if league_data:
                        break
            if not league_data:
                print("Failed to get league data in all summoner regions.")
                return

            # Extract the required data
            tier = league_data[0]['tier']
            rank = league_data[0]['rank']
            league_points = league_data[0]['leaguePoints']
            wins = league_data[0]['wins']
            losses = league_data[0]['losses']
            total_games = wins + losses

            # Fetch match stats for calculating Win %, Top 4 %, and Avg Placement
            tactics_url = f"{self.tt_url}/{region}/{gameName}/{tagLine}/120/0"
            tactics_response = requests.get(tactics_url)

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

            # Add fields based on tier
            if tier in ["CHALLENGER", "GRANDMASTER", "MASTER"]:
                embed.add_field(name="Rank", value=f"{tier_key} ({league_points} LP)", inline=False)
            else:
                embed.add_field(name="Rank", value=f"{tier_key} {rank} ({league_points} LP)", inline=False)
            embed.add_field(name="Leaderboard", value=f"Top {display_rank} {region.capitalize()}", inline=False)
            embed.add_field(name="Total Games", value=str(total_games), inline=False)
            embed.add_field(name="Win %", value=f"{win_percentage:.2f}%", inline=False)
            embed.add_field(name="Top 4 %", value=f"{top4_percentage:.2f}%", inline=False)
            embed.add_field(name="Average Placement", value=f"{average_placement:.2f}", inline=False)

            if rank_image_url:
                embed.set_thumbnail(url=rank_image_url)

            await ctx.send(embed=embed)

        except ValueError:
            print("Invalid format. Please use the format: name#tagline.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


async def setup(bot, apikey, latest_version):
    await bot.add_cog(LookupCommands(bot, apikey, latest_version))
