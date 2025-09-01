import discord
from discord.ext import commands
import random
import json
import os

class StreamerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Load streamer data from JSON file
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'streamers.json')
        with open(config_path, 'r') as config_file:
            self.streamer_data = json.load(config_file)

    @commands.command()
    async def setsuko(self, ctx):
        lines_setsuko = self.streamer_data.get('lines_setsuko', [])
        if not lines_setsuko:
            print("No lines available for Setsuko.")
            return

        selected_line_setsuko = random.choice(lines_setsuko)

        # Check if the selected line is an emoji ID
        if selected_line_setsuko.isdigit():
            emoji_id = int(selected_line_setsuko)
            emoji = discord.utils.get(ctx.guild.emojis, id=emoji_id)
            if emoji:
                await ctx.send(f'{emoji}')
            else:
                print("Emoji not found.")
        else:
            await ctx.send(f'{selected_line_setsuko}')

    @commands.command()
    async def dishsoap(self, ctx):
        lines_dish = self.streamer_data.get('lines_dish', [])
        if not lines_dish:
            print("No lines available for Dish Soap.")
            return

        selected_line_dish = random.choice(lines_dish)
        await ctx.send(f'{selected_line_dish}')

    @commands.command()
    async def brotherman(self, ctx):
        lines_brother = self.streamer_data.get('lines_brother', [])
        if not lines_brother:
            print("No lines available for Brotherman.")
            return

        selected_line_brother = random.choice(lines_brother)
        await ctx.send(f'{selected_line_brother}')

    @commands.command()
    async def crashout(self, ctx):
        lines_crashout = self.streamer_data.get('lines_crashout', [])
        if not lines_crashout:
            print("No lines available for crashout.")
            return

        selected_line_crashout = random.choice(lines_crashout)
        await ctx.send(f'{selected_line_crashout}')

    @commands.command()
    async def soju(self, ctx):
        lines_soju = self.streamer_data.get('lines_soju', [])
        if not lines_soju:
            print("No lines available for Soju.")
            return

        selected_line_soju = random.choice(lines_soju)

        # Check if the selected line is an emoji ID
        if selected_line_soju.isdigit():
            emoji_id = int(selected_line_soju)
            emoji = discord.utils.get(ctx.guild.emojis, id=emoji_id)
            if emoji:
                await ctx.send(f'{emoji}')
            else:
                print("Emoji not found.")
        else:
            await ctx.send(f'{selected_line_soju}')

async def setup(bot):
    await bot.add_cog(StreamerCommands(bot))
