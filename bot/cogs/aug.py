import discord
from discord.ext import commands
import aiohttp
import os
import re
from PIL import Image
from io import BytesIO


class AugCommands(commands.Cog):
    def __init__(self, bot, latest_version):
        self.bot = bot
        self.version = "".join(latest_version.split('.')[:2])
        self.augment_url = os.getenv('augment_url')
        self.latest_version = latest_version
        self.patch_numbers = [2, 1, 0]  # List of patch numbers to attempt
        self.patch_mapping = {0: "", 1: "B", 2: "C"}

    async def fetch_augment_data(self, url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
            except aiohttp.ClientError as e:
                print(f"Error fetching augment data: {str(e)}")
                return None

    async def get_augment_by_name(self, augment_name):
        augment_data_url = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/data/en_US/tft-augments.json"
        augment_data = await self.fetch_augment_data(augment_data_url)

        if not augment_data:
            print("Failed to retrieve augment data.")
            return None, None, None

        augments = augment_data.get('data', {}).values()

        # Normalize the input augment name for case-insensitive comparison
        augment_name = augment_name.lower().strip()

        # Search through the augments for a matching name
        for augment in augments:
            if augment_name == augment['name'].lower():
                augment_id = augment['id']

                # Use regex to extract the number after "TFT" and the text after "Augment_"
                match = re.search(r"TFT(\d+)_Augment_(.+)", augment_id)
                if match:
                    number = match.group(1)  # Get the number (like "12")
                    augment_text = match.group(2)  # Get the augment suffix (like "NunuCarry")
                    dynamic_id = f"{number}{augment_text}"

                    # Get the image file from the augment data
                    image_file = augment['image']['full']
                    image_url = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/img/tft-augment/{image_file}"

                    return dynamic_id, image_url, augment['name']

        return None, None, None

    async def resize_image(self, url, size=(48, 48)):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    img_data = await response.read()
                    img = Image.open(BytesIO(img_data))
                    img = img.resize(size, Image.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
                    img_byte_array = BytesIO()
                    img.save(img_byte_array, format='PNG')
                    img_byte_array.seek(0)
                    return img_byte_array
                return None

    @commands.command()
    async def aug(self, ctx, *, augment_name: str):
        search_term = augment_name.replace(' ', '')
        found = False

        for patch_number in self.patch_numbers:
            patch_suffix = self.patch_mapping.get(patch_number, "")
            url = f"{self.augment_url}{self.version}{patch_number}/1"
            json_data = await self.fetch_augment_data(url)

            if json_data:
                # Extract augment details from the name
                dynamic_id, image_url, found_name = await self.get_augment_by_name(augment_name)

                if not dynamic_id or not image_url:
                    await ctx.send(f"No augment found for `{augment_name}`.")
                    return

                # Iterate over the 'singles' list in the JSON data to match with dynamic ID
                singles = json_data.get('singles', [])
                for augment in singles:
                    if dynamic_id.lower() in augment['id'].lower():
                        found = True
                        base_data = augment.get('base', {})
                        place = base_data.get('place', 'N/A')
                        top4_rate = base_data.get('top4', 'N/A')
                        win_rate = base_data.get('won', 'N/A')
                        sample_size = base_data.get('count', 'N/A')

                        # Create an embed with stats
                        embed = discord.Embed(
                            title=f"{found_name}",
                            description=f"Patch {self.latest_version} {patch_suffix}",
                            color=discord.Color.blue()  # Customize color as needed
                        )
                        embed.add_field(name="AVP (Average Placement)", value=f"{place}", inline=False)
                        embed.add_field(name="Top 4 Rate", value=f"{top4_rate}%", inline=False)
                        embed.add_field(name="Win Rate", value=f"{win_rate}%", inline=False)
                        embed.add_field(name="Sample Size", value=f"{sample_size}", inline=False)

                        embed.set_footer(text=f"Data sourced from tactics.tools (Diamond +)")

                        # Resize the image
                        resized_image_bytes = await self.resize_image(image_url, size=(48, 48))

                        # Add the thumbnail image to the embed
                        if resized_image_bytes:
                            # Use an in-memory image file for the thumbnail
                            file = discord.File(resized_image_bytes, filename="augment_thumbnail.png")
                            # Set the thumbnail directly
                            embed.set_thumbnail(url="attachment://augment_thumbnail.png")


                        # Send the embed with the image
                        await ctx.send(embed=embed, file=file)
                        break

            if found:
                break

        if not found:
            print(f"No augment stats found for `{augment_name}`.")


async def setup(bot, latest_version):
    await bot.add_cog(AugCommands(bot, latest_version))
