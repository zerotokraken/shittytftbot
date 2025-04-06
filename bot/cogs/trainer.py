import discord
from discord.ext import commands
import requests
import random
from io import BytesIO
from PIL import Image

class TrainerCommands(commands.Cog):
    def __init__(self, bot, apikey, latest_version):
        self.bot = bot
        self.apikey = apikey
        self.latest_version = latest_version

    @commands.command()
    async def trainer(self, ctx):
        try:
            url = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/data/en_US/tft-trait.json"
            response = requests.get(url)
            data = response.json()["data"]

            # Define the ignore list and filter criteria
            ignore_list = {"TFT14_ViegoUniqueTrait", "TFT14_Overlord", "TFT14_Virus", "TFT14_BallisTek", "TFT14_Netgod"}
            valid_traits = [trait for trait in data.values() if "TFT14" in trait["id"] and trait["id"] not in ignore_list]

            # Randomly select three traits
            selected_traits = random.sample(valid_traits, 3) if len(valid_traits) >= 3 else valid_traits

            images = []
            for trait in selected_traits:
                image_url = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/img/tft-trait/{trait['image']['full']}"
                response = requests.get(image_url)
                image = Image.open(BytesIO(response.content))
                images.append(image)

            # Combine the images horizontally
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
                    combined_image_file = discord.File(output, filename='combined_traits.png')
                    await ctx.send(file=combined_image_file)
            else:
                print("No images available to display.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

async def setup(bot, apikey, latest_version):
    await bot.add_cog(TrainerCommands(bot, apikey, latest_version))
