import discord
from discord.ext import commands
from discord.utils import utcnow

class ChannelBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banned_channel_id = 1382416748913098833  # Static channel ID where typing is banned
        self.log_channel_id = 1113518194712383578  # Log channel for ban notifications
        self.whitelisted_roles = ["Hairy Frog", "Admin", "Discord Moderator", "Junior Mod"]  # Roles that can type in the channel

    def has_whitelisted_role(self, member):
        """Check if the user has at least one of the whitelisted roles."""
        user_roles = [role.name for role in member.roles]
        return any(role in self.whitelisted_roles for role in user_roles)

    async def send_log_embed(self, guild, embed):
        """Send an embed to the specified log channel."""
        channel = guild.get_channel(self.log_channel_id)
        if channel:
            await channel.send(embed=embed)
        else:
            print(f"Log channel with ID {self.log_channel_id} not found.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages and messages in other channels
        if message.author.bot or message.channel.id != self.banned_channel_id:
            return

        # Allow whitelisted roles to type in the channel
        if self.has_whitelisted_role(message.author):
            return

        try:
            # Create ban embed
            embed = discord.Embed(
                title="🔨 Auto-Ban Executed",
                color=discord.Color.dark_red(),
                timestamp=utcnow()
            )
            embed.add_field(name="Member", value=f"{message.author.mention} ({message.author.id})", inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Message Content", value=message.content[:1024] or "[No content/attachment]", inline=False)
            embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)

            # Ban the user
            reason = f"Automatic ban for sending message in restricted channel {message.channel.name}"
            await message.guild.ban(message.author, reason=reason)

            # Send log message
            await self.send_log_embed(message.guild, embed)

        except discord.Forbidden:
            print(f"Failed to ban {message.author}. Missing permissions.")
        except discord.HTTPException as e:
            print(f"Failed to ban {message.author}. Error: {e}")

async def setup(bot):
    await bot.add_cog(ChannelBan(bot))
