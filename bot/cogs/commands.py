import discord
from discord.ext import commands
import aiohttp

class ShittyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to list main commands with custom descriptions and clump remaining into one line
    @commands.command()
    async def shittycommands(self, ctx):
        # Define a static list of main commands with custom descriptions
        main_commands = {
            'lookup': 'Look up a player’s TFT stats on tactics.tools, Include the player tag as well [!lookup BOT#TAG]',
            'aug': 'Lookup the statistics for an augment on tactics.tools [!aug Sweet Tooth]',
            'top': 'Look up the top 5 players in a region [!top na]',
            'roll': 'Simulate a shop roll at a specific level [!roll #]',
            'malding': 'Send up to 3 random messages from the malding channel. Refreshes once an hour',
            'avp': 'Predict your average placement. Random integer between 1.0-8.0',
            'suggest': 'Suggest a command or feature [!suggest myidea]',
            'cutoffs': 'Challenger and Grandmaster Cutoffs for a specific region [!cutoffs NA]',
            'links': 'Large list of TFT resources to include webpages, discords, youtube and reddits'
        }

        # Define a list of miscellaneous commands
        emoji_commands = ['frog', 'chris', '420', 'xdd']

        # Prepare the response for main commands
        main_response = '\n'.join([f'`{name}` - {desc}' for name, desc in main_commands.items()])

        # Prepare misc commands into one line
        misc_response = ', '.join([f'`{command}`' for command in emoji_commands])

        # Get remaining commands that are not in the main or misc list
        remaining_commands = [
            f'`{command.name}`' for command in self.bot.commands
            if command.name not in main_commands and command.name not in emoji_commands
        ]

        # Create a one-line response for remaining commands
        remaining_response = ', '.join(remaining_commands) if remaining_commands else 'No remaining commands.'

        # Create an embed message
        embed = discord.Embed(
            title="Shitty Commands",
            color=discord.Color.blue()  # Customize the color as you prefer
        )

        # Add main commands with custom descriptions as a field
        embed.add_field(name="Main", value=main_response, inline=False)

        # Add misc commands as a field
        embed.add_field(name="Stickers/Emojis", value=misc_response, inline=False)

        # Add remaining commands as a field
        embed.add_field(name="Misc", value=remaining_response, inline=False)

        # Send the embed response
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ShittyCommands(bot))