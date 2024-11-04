import discord
from discord.ext import commands
import requests
import urllib.parse
import os
import re
import random

class TrainerCommands(commands.Cog):
    def __init__(self, bot, apikey, latest_version):
        self.bot = bot
        self.apikey = apikey  # Assigning API key correctly
        self.latest_version = latest_version

    @commands.command()
    async def trainer(self, ctx):
        try:
            url = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/data/en_US/tft-trait.json"
            # Fetch the trait data
            response = requests.get(url)
            data = response.json()["data"]

            # Define the ignore list and filter criteria
            ignore_list = {"TFT12_BatQueen", "TFT12_Druid", "TFT12_Explorer", "TFT12_Ascendant", "TFT12_Ravenous",
                           "TFT12_Relic", "TFT12_Dragon"}  # Add traits to ignore as needed

            # Filter for traits containing 'TFT12' and not in the ignore list
            valid_traits = [trait for trait in data.values() if
                            "TFT12" in trait["id"] and trait["id"] not in ignore_list]

            # Randomly select three traits
            selected_traits = random.sample(valid_traits, 3) if len(valid_traits) >= 3 else valid_traits

            # Prepare embed to send images without text
            embeds = []
            for trait in selected_traits:
                image_url = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/img/tft-trait/{trait['image']['full']}"
                embed = discord.Embed()
                embed.set_image(url=image_url)
                embeds.append(embed)

            # Send the images as separate embeds
            for embed in embeds:
                await ctx.send(embed=embed)

        except Exception as e:
            print(f"An error occurred: {str(e)}")


async def setup(bot, apikey, latest_version):
    await bot.add_cog(TrainerCommands(bot, apikey, latest_version))



