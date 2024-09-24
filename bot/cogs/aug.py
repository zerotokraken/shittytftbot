import discord
from discord.ext import commands
import aiohttp
import json
import re
import os

class AugCommands(commands.Cog):
    def __init__(self, bot, latest_version):
        self.bot = bot
        self.version = latest_version
        self.augment_url = os.getenv('augment_url')
        self.patch_numbers = [0, 1, 2]  # List of patch numbers to attempt

    async def fetch_augment_data(self, url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        json_pattern = r'{"id":".+?"[^}]*}'
                        matches = re.findall(json_pattern, html_content)

                        for match in matches:
                            try:
                                json_data = json.loads(match + "}")  # Add closing bracket if necessary
                                return json_data
                            except json.JSONDecodeError:
                                print("There was an issue with the augment data format.")
                                continue

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
            json_data = await self.fetch_augment_data(url)
            if json_data:
                # Process the data if found
                if search_term.lower() in json_data['id'].lower():
                    found = True
                    base_data = json_data.get('base', {})
                    place = base_data.get('place', 'N/A')
                    top4_rate = base_data.get('top4', 'N/A')
                    win_rate = base_data.get('won', 'N/A')
                    await ctx.send(f"{augment_name} - AVP: {place}, Top 4: {top4_rate}%, Win: {win_rate}%")
                    break

        if not found:
            await ctx.send(f"No augment found matching `{augment_name}`.")

async def setup(bot, latest_version):
    await bot.add_cog(AugCommands(bot, latest_version))
