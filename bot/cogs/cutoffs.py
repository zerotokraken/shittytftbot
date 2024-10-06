import discord
from discord.ext import commands
import aiohttp
import difflib  # For matching regions
import json
import os

class CutoffCommands(commands.Cog):
    def __init__(self, bot, apikey, latest_version):
        self.bot = bot
        self.apikey = apikey
        self.latest_version = latest_version
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'cutoffs.json')
        with open(config_path, 'r') as config_file:
            self.config = json.load(config_file)

    # List of available summoner regions
    summoner_regions = ["na1", "eun1", "euw1", "br1", "jp1", "kr", "la1", "la2", "me1", "oc1", "ph2", "ru", "sg2",
                        "th2", "tr1", "tw2", "vn2"]

    # Function to get the closest region match
    def get_closest_region(self, region_input):
        closest_region = difflib.get_close_matches(region_input.lower(), self.summoner_regions, n=1, cutoff=0.1)
        return closest_region[0] if closest_region else None

    # Command to fetch Challenger and Grandmaster cutoffs
    @commands.command()
    async def cutoffs(self, ctx, region_input: str):
        closest_region = self.get_closest_region(region_input)
        if not closest_region:
            print(f"No valid region found for '{region_input}'. Please check the region name.")
            return

        async with aiohttp.ClientSession() as session:
            # Fetch Challenger + Grandmaster for Challenger cutoff
            challenger_url = f"https://{closest_region}.api.riotgames.com/tft/league/v1/challenger?queue=RANKED_TFT&api_key={self.apikey}"
            grandmaster_url = f"https://{closest_region}.api.riotgames.com/tft/league/v1/grandmaster?queue=RANKED_TFT&api_key={self.apikey}"

            async with session.get(challenger_url) as challenger_response:
                if challenger_response.status != 200:
                    print(f"Failed to fetch Challenger data for {closest_region}.")
                    return
                challenger_data = await challenger_response.json()

            async with session.get(grandmaster_url) as grandmaster_response:
                if grandmaster_response.status != 200:
                    print(f"Failed to fetch Grandmaster data for {closest_region}.")
                    return
                grandmaster_data = await grandmaster_response.json()

            # Fetch Grandmaster + Master for Grandmaster cutoff
            master_url = f"https://{closest_region}.api.riotgames.com/tft/league/v1/master?queue=RANKED_TFT&api_key={self.apikey}"

            async with session.get(master_url) as master_response:
                if master_response.status != 200:
                    print(f"Failed to fetch Master data for {closest_region}.")
                    return
                master_data = await master_response.json()
            # Combine Challenger and Grandmaster players for Challenger cutoff
            combined_data = challenger_data['entries'] + grandmaster_data['entries'] + master_data['entries']
            combined_data.sort(key=lambda x: x['leaguePoints'], reverse=True)

            # Store player counts in the config
            region_config = next((region for region in self.config['regions'] if region['region'] == closest_region), None)
            if region_config:
                challenger_players_count = region_config['num_challenger_players']
                grandmaster_players_count = region_config['num_challenger_players'] + region_config['num_grandmaster_players']

            # Challenger cutoff: 250th player
            if len(combined_data) >= challenger_players_count:
                challenger_cutoff = combined_data[challenger_players_count - 1]['leaguePoints']
            else:
                challenger_cutoff = combined_data[-1]['leaguePoints']

            # Grandmaster cutoff: 750th player
            if len(combined_data) >= grandmaster_players_count:
                grandmaster_cutoff = combined_data[grandmaster_players_count - 1]['leaguePoints']
            else:
                grandmaster_cutoff = combined_data[-1]['leaguePoints']

        # Strip the number from the region (e.g., "na1" -> "na", "euw1" -> "euw")
        stripped_region = ''.join([char for char in closest_region if not char.isdigit()])

        # Enforce baseline cutoffs (500 LP for Challenger, 250 LP for Grandmaster)
        if challenger_cutoff < 500:
            challenger_cutoff = 500

        if grandmaster_cutoff < 200:
            grandmaster_cutoff = 200

        chall_image_url = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/img/tft-regalia/TFT_Regalia_Challenger.png"
        gm_image_url = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/img/tft-regalia/TFT_Regalia_GrandMaster.png"

        # Create and send the embed with cutoff values
        embed_chall = discord.Embed(
            title=f"Challenger Cutoff for {stripped_region.upper()} Region",
            color=discord.Color.from_rgb(255, 215, 0)
        )
        embed_chall.add_field(name=None, value=f"{challenger_cutoff} LP", inline=False)
        embed_chall.set_footer(text="Data sourced from Riot API")

        # Create and send the embed with cutoff values
        embed_gm = discord.Embed(
            title=f"Grandmaster Cutoff for {stripped_region.upper()} Region",
            color=discord.Color.from_rgb(255, 165, 0)
        )
        embed_gm.add_field(name=None, value=f"{grandmaster_cutoff} LP", inline=False)
        embed_gm.set_footer(text="Data sourced from Riot API")

        embed_chall.set_thumbnail(url=chall_image_url)
        embed_gm.set_thumbnail(url=gm_image_url)
        await ctx.send(embed=embed_chall)
        await ctx.send(embed=embed_gm)

# Setup function for the cog
async def setup(bot, apikey, latest_version):
    await bot.add_cog(CutoffCommands(bot, apikey, latest_version))
