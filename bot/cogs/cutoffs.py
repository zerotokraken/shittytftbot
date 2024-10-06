import discord
from discord.ext import commands
import aiohttp
import difflib


class CutoffCommands(commands.Cog):
    def __init__(self, bot, apikey):
        self.bot = bot
        self.apikey = apikey

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
            await ctx.send(f"No valid region found for '{region_input}'. Please check the region name.")
            return

        async with aiohttp.ClientSession() as session:
            # Fetch Challenger leaderboard
            challenger_url = f"https://{closest_region}.api.riotgames.com/tft/league/v1/challenger?queue=RANKED_TFT&api_key={self.apikey}"
            async with session.get(challenger_url) as challenger_response:
                if challenger_response.status != 200:
                    await ctx.send(f"Failed to fetch Challenger data for {closest_region}.")
                    return
                challenger_data = await challenger_response.json()
                challenger_entries = challenger_data['entries']

            # Fetch Grandmaster leaderboard
            grandmaster_url = f"https://{closest_region}.api.riotgames.com/tft/league/v1/grandmaster?queue=RANKED_TFT&api_key={self.apikey}"
            async with session.get(grandmaster_url) as grandmaster_response:
                if grandmaster_response.status != 200:
                    await ctx.send(f"Failed to fetch Grandmaster data for {closest_region}.")
                    return
                grandmaster_data = await grandmaster_response.json()
                grandmaster_entries = grandmaster_data['entries']

            # Find the lowest League Points in both categories
            challenger_lowest_lp = min(challenger_entries, key=lambda x: x['leaguePoints'])['leaguePoints']
            grandmaster_lowest_lp = min(grandmaster_entries, key=lambda x: x['leaguePoints'])['leaguePoints']

        # Create and send the embed message with the cutoffs
        embed = discord.Embed(
            title=f"Cutoffs for {closest_region.upper()} Region",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="Challenger",
            value=f"{challenger_lowest_lp} LP",
            inline=False
        )
        embed.add_field(
            name="Grandmaster",
            value=f"{grandmaster_lowest_lp} LP",
            inline=False
        )
        embed.set_footer(text="Data sourced from Riot API")

        await ctx.send(embed=embed)


# Setup function for the cog
async def setup(bot, apikey):
    await bot.add_cog(CutoffCommands(bot, apikey))
