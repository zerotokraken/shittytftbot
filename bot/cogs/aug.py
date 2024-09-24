import discord
from discord.ext import commands
import aiohttp
import json
import os


class AugCommands(commands.Cog):
    def __init__(self, bot, latest_version):
        self.bot = bot
        self.version = "".join(latest_version.split('.')[:2])
        self.augment_url = os.getenv('augment_url')
        self.latest_version = latest_version
        self.patch_numbers = [2, 1, 0]  # List of patch numbers to attempt

    async def fetch_augment_data(self, url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        # Directly parse the JSON response
                        data = await response.json()
                        return data
                    elif response.status == 404:
                        return None
            except aiohttp.ClientError as e:
                print(f"Error fetching augment data: {str(e)}")
                return None

    @commands.command(help="Lookup augment data from tactics.tools, Usage: !aug <augment_name>")
    async def aug(self, ctx, *, augment_name: str):
        search_term = augment_name.replace(' ', '')
        found = False

        for patch_number in self.patch_numbers:
            url = f"{self.augment_url}{self.version}{patch_number}/1"
            print(f"Fetching URL: {url}")
            json_data = await self.fetch_augment_data(url)

            if json_data:
                # Iterate over the 'singles' list in the JSON data
                singles = json_data.get('singles', [])
                for augment in singles:
                    if search_term.lower() in augment['id'].lower():
                        found = True
                        base_data = augment.get('base', {})
                        place = base_data.get('place', 'N/A')
                        top4_rate = base_data.get('top4', 'N/A')
                        win_rate = base_data.get('won', 'N/A')

                        # Create an embed
                        embed = discord.Embed(
                            title=f"{augment_name}",
                            description=f"Patch {self.latest_version} {patch_number}",
                            color=discord.Color.blue()  # Customize color as needed
                        )
                        embed.add_field(name="AVP", value=f"{place}", inline=False)
                        embed.add_field(name="Top 4 Rate", value=f"{top4_rate}%", inline=False)
                        embed.add_field(name="Win Rate", value=f"{win_rate}%", inline=False)
                        embed.set_footer(text="Data sourced from tactics.tools")

                        await ctx.send(embed=embed)
                        break

            if found:
                break

        if not found:
            print(f"No augment found matching `{augment_name}`.")


async def setup(bot, latest_version):
    await bot.add_cog(AugCommands(bot, latest_version))
