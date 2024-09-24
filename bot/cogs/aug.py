import discord
from discord.ext import commands
import aiohttp
import json
import re

class AugCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Lookup augment data from tactics.tools, Usage: !aug <augment_name>")
    async def aug(self, ctx, *, augment_name: str):
        # Remove any spaces from the augment name
        search_term = augment_name.replace(' ', '')

        # URL to fetch data from
        url = "https://tactics.tools/_next/data/hX4-m6EX8cV19isHOjRQ_/en/augments.json"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    # Check if the request was successful (status code 200)
                    if response.status == 200:
                        # Get the content of the page
                        html_content = await response.text()

                        # Use regex to extract JSON-like data
                        json_pattern = r'{"id":".+?"[^}]*}'
                        matches = re.findall(json_pattern, html_content)

                        found = False  # To check if any matches were found

                        # Process each match to parse it as JSON and find the specific augment
                        for match in matches:
                            try:
                                json_data = json.loads(match + "}")  # Add closing bracket if necessary

                                # Check if the search term matches the 'id' field
                                if search_term.lower() in json_data['id'].lower():
                                    found = True
                                    # Access the nested data in the 'base' section
                                    base_data = json_data.get('base', {})
                                    place = base_data.get('place', 'N/A')
                                    top4_rate = base_data.get('top4', 'N/A')
                                    win_rate = base_data.get('won', 'N/A')

                                    # Send the result to Discord
                                    await ctx.send(f"{augment_name} - AVP: {place}, Top 4: {top4_rate}%, Win: {win_rate}%")
                                    break

                            except json.JSONDecodeError:
                                print("There was an issue with the augment data format.")
                                return

                        if not found:
                            print(f"No augment found matching `{augment_name}`.")

                    else:
                        print(f"Failed to retrieve augment data. Status code: {response.status}")

            except aiohttp.ClientError as e:
                print(f"Error fetching augment data: {str(e)}")

async def setup(bot):
    await bot.add_cog(AugCommands(bot))
