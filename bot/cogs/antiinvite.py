import re
import discord
from discord.ext import commands

class AntiInvite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Regular expression to detect Discord invite links
        self.invite_regex = re.compile(r"(discord\.gg/|discordapp\.com/invite/|discord\.com/invite/)")
        # List of allowed roles (use role names or IDs)
        self.allowed_roles = ["Hairy Frog", "Admin", "Discord Moderator"]  # Replace with your server's role names

    def has_allowed_role(self, member):
        """Check if the user has at least one of the allowed roles."""
        allowed_roles = self.allowed_roles
        user_roles = [role.name for role in member.roles]
        return any(role in allowed_roles for role in user_roles)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Check if the message contains a Discord invite link
        if self.invite_regex.search(message.content):
            # Allow users with allowed roles to post invite links
            if self.has_allowed_role(message.author):
                return

            # Check if the user has Administrator permissions
            if not message.author.guild_permissions.administrator:
                try:
                    # Delete the message and send a warning
                    await message.delete()
                    await message.channel.send(
                        f"{message.author.mention}, sharing invite links is not allowed here.",
                        delete_after=10
                    )
                except discord.Forbidden:
                    print("Bot lacks permissions to delete the message.")
                except discord.HTTPException as e:
                    print(f"Failed to delete message. Error: {e}")

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(AntiInvite(bot))
