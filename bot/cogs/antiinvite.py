import re
import discord
from discord.ext import commands

class AntiInvite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Regular expression to detect Discord invite links
        self.invite_regex = re.compile(r"(discord\.gg/|discordapp\.com/invite/|discord\.com/invite/)")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Check if the message contains a Discord invite link
        if self.invite_regex.search(message.content):
            # Check if the user has permission to send invites (e.g., Administrator or Manage Server permission)
            if not message.author.guild_permissions.administrator:
                # Delete the message and send a warning
                await message.delete()
                return

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(AntiInvite(bot))