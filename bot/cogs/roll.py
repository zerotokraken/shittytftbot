import discord
from discord.ext import commands
import random
import aiohttp
from PIL import Image
from io import BytesIO

class RollCommands(commands.Cog):
    def __init__(self, bot, champions_data, latest_version, shop_odds, set_number):
        self.bot = bot
        self.champions_data = champions_data
        self.latest_version = latest_version
        self.shop_odds = shop_odds
        self.set_number = set_number

    @commands.command()
    async def roll(self, ctx, level: int = 5):
        if not self.champions_data:
            print("Champions data is not available. Please wait while we update it.")
            await self.fetch_champions_data()

        # Convert level to string when accessing shop_odds
        odds = self.shop_odds[str(level)]

        tiers = [1, 2, 3, 4, 5]
        results = []

        # Filter out champions with "Tutorial" in their name
        valid_champions = {name: details for name, details in self.champions_data.items() if f"TFT{self.set_number}" in details['id']}

        # Roll champions based on the odds
        for tier in tiers:
            count = odds[tier - 1]
            if count > 0:
                tier_champions = [name for name, details in valid_champions.items() if details['tier'] == tier]
                if tier_champions:
                    results.extend(random.choices(tier_champions, k=count))

        # If no champions were selected
        if not results:
            print("No champions rolled. Please try again.")
            return

        # Ensure the number of units does not exceed available champions
        num_units = min(len(results), 5)
        selected_champions = random.sample(results, num_units)

        # Create a list to store the images
        images = []

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            for champion_name in selected_champions:
                champion = self.champions_data[champion_name]
                name = champion['name'].replace("'", "")  # Remove single quotes
                full_image_name = champion['image']['full']
                image_url = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/img/tft-champion/{full_image_name}"

                try:
                    # Fetch the image
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            img_data = await response.read()
                            img = Image.open(BytesIO(img_data))
                            images.append(img)
                        else:
                            await ctx.send(f"Failed to fetch image for {name}. Status code: {response.status}")
                except Exception as e:
                    await ctx.send(f"Error fetching image for {name}: {e}")

        # Combine the images into a single image
        if images:
            total_width = sum(img.width for img in images)
            max_height = max(img.height for img in images)
            combined_image = Image.new('RGBA', (total_width, max_height))

            x_offset = 0
            for img in images:
                combined_image.paste(img, (x_offset, 0))
                x_offset += img.width

            # Save the combined image to a BytesIO object
            with BytesIO() as output:
                combined_image.save(output, format='PNG')
                output.seek(0)
                combined_image_file = discord.File(output, filename='combined_champions.png')
                await ctx.send(file=combined_image_file)
        else:
            await ctx.send("No images available to display.")

async def setup(bot, champions_data, latest_version, shop_odds, set_number):
    await bot.add_cog(RollCommands(bot, champions_data, latest_version, shop_odds, set_number))
