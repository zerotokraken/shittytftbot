import discord
from discord.ext import commands
import aiohttp
import difflib  # For matching regions

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

            # Combine Challenger and Grandmaster players
            combined_challenger_gm = challenger_data['entries'] + grandmaster_data['entries']
            combined_challenger_gm.sort(key=lambda x: x['leaguePoints'], reverse=True)

            # Challenger cutoff: 250th player
            if len(combined_challenger_gm) >= 250:
                challenger_cutoff = combined_challenger_gm[249]['leaguePoints']
            else:
                challenger_cutoff = combined_challenger_gm[-1]['leaguePoints']

            # Fetch Grandmaster + Master for Grandmaster cutoff
            master_url = f"https://{closest_region}.api.riotgames.com/tft/league/v1/master?queue=RANKED_TFT&api_key={self.apikey}"

            async with session.get(master_url) as master_response:
                if master_response.status != 200:
                    print(f"Failed to fetch Master data for {closest_region}.")
                    return
                master_data = await master_response.json()

            # Combine Grandmaster and Master players
            combined_gm_master = grandmaster_data['entries'] + master_data['entries']
            combined_gm_master.sort(key=lambda x: x['leaguePoints'], reverse=True)

            # Grandmaster cutoff: 250th player
            if len(combined_gm_master) >= 250:
                grandmaster_cutoff = combined_gm_master[249]['leaguePoints']
            else:
                grandmaster_cutoff = combined_gm_master[-1]['leaguePoints']

        # Strip the number from the region (e.g., "na1" -> "na", "euw1" -> "euw")
        stripped_region = ''.join([char for char in closest_region if not char.isdigit()])

        # Create and send the embed with cutoff values
        embed = discord.Embed(
            title=f"Cutoffs for {stripped_region.upper()} Region",
            color=discord.Color.gold()
        )
        embed.add_field(name="Challenger", value=f"{challenger_cutoff} LP", inline=False)
        embed.add_field(name="Grandmaster", value=f"{grandmaster_cutoff} LP", inline=False)
        embed.set_footer(text="Data sourced from Riot API")

        await ctx.send(embed=embed)

# Setup function for the cog
async def setup(bot, apikey):
    await bot.add_cog(CutoffCommands(bot, apikey))
