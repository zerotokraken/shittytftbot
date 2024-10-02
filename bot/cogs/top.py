import discord
from discord.ext import commands
import aiohttp
import difflib


class LeaderboardCommands(commands.Cog):
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

    # Command to fetch top 10 Challenger players
    @commands.command(help="Fetch top 10 Challenger players for the closest matching region.")
    async def top(self, ctx, region_input: str):
        closest_region = self.get_closest_region(region_input)
        if not closest_region:
            print(f"No valid region found for '{region_input}'. Please check the region name.")
            return

        # Step 1: Fetch the list of users and their ranks (Top Challenger players)
        url = f"https://{closest_region}.api.riotgames.com/tft/league/v1/challenger?queue=RANKED_TFT&api_key={self.apikey}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Failed to fetch Challenger data for {closest_region}.")
                    return

                data = await response.json()
                entries = data['entries']
                sorted_entries = sorted(entries, key=lambda x: x['leaguePoints'], reverse=True)[:5]
                summoner_ids = [entry['summonerId'] for entry in sorted_entries]

        # Step 2: Fetch summoner information (get `puuid`)
        summoner_to_puuid = {}
        async with aiohttp.ClientSession() as session:
            for summoner_id in summoner_ids:
                summ_url = f"https://{closest_region}.api.riotgames.com/tft/summoner/v1/summoners/{summoner_id}?api_key={self.apikey}"
                async with session.get(summ_url) as summ_response:
                    if summ_response.status == 200:
                        summ_data = await summ_response.json()
                        if 'puuid' in summ_data:
                            summoner_to_puuid[summoner_id] = summ_data['puuid']
                    else:
                        print(f"Failed to fetch summoner data for summonerId {summoner_id}.")

        # Step 3: Fetch the actual summoner name using the `puuid`
        puuid_to_name = {}
        async with aiohttp.ClientSession() as session:
            for summoner_id, puuid in summoner_to_puuid.items():
                puuid_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}?api_key={self.apikey}"
                async with session.get(puuid_url) as puuid_response:
                    if puuid_response.status == 200:
                        puuid_data = await puuid_response.json()
                        puuid_to_name[puuid] = puuid_data['gameName']
                    else:
                        print(f"Failed to fetch account name for puuid {puuid}.")

        # Step 4: Create the embed with top 10 Challenger players
        embed = discord.Embed(
            title=f"Top 10 Challenger Players - {closest_region.upper()}",
            color=discord.Color.yellow()
        )

        # Add each player to the embed
        for idx, entry in enumerate(sorted_entries, start=1):
            summoner_id = entry['summonerId']
            if summoner_id in summoner_to_puuid:
                puuid = summoner_to_puuid[summoner_id]
                name = puuid_to_name.get(puuid, 'Unknown Summoner')
                embed.add_field(
                    name=f"#{idx} {name}",
                    value=f"{entry['leaguePoints']} LP",
                    inline=False
                )

        # Set footer for data source
        embed.set_footer(text=f"Data sourced from Riot API")

        # Send the embed message
        await ctx.send(embed=embed)


# Setup function for the cog
async def setup(bot, apikey):
    await bot.add_cog(LeaderboardCommands(bot, apikey))
