import re
import discord
from discord.ext import commands
from datetime import timedelta
from discord.utils import utcnow

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_roles = ["Hairy Frog", "Admin", "Discord Moderator"]  # Replace with your roles
        self.log_channel_id = 1113518194712383578  # Replace with the ID of the channel you want to send messages to

    def has_allowed_role(self, member):
        """Check if the user has at least one of the allowed roles."""
        user_roles = [role.name for role in member.roles]
        return any(role in self.allowed_roles for role in user_roles)

    def parse_duration(self, duration_str):
        """Parse duration string and return the total duration in seconds."""
        duration_regex = re.compile(r"(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?")
        match = duration_regex.fullmatch(duration_str)
        if not match:
            return None

        weeks, days, hours, minutes = match.groups(default="0")
        total_seconds = (int(weeks) * 604800) + (int(days) * 86400) + (int(hours) * 3600) + (int(minutes) * 60)
        return total_seconds

    async def send_log_embed(self, guild, embed):
        """Send an embed to the specified log channel."""
        channel = guild.get_channel(self.log_channel_id)
        if channel:
            await channel.send(embed=embed)
        else:
            print(f"Log channel with ID {self.log_channel_id} not found.")

    @commands.command()
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason: str = None):
        """Timeout a member for a custom duration (e.g., 3m, 6h, 2d, 1w)."""
        if not self.has_allowed_role(ctx.author):
            print(f"{ctx.author} does not have the required role to use this command.")
            return

        total_seconds = self.parse_duration(duration)
        if total_seconds is None:
            print("Invalid duration format. Please use the format like 3m, 6h, 2d, 1w.")
            return

        timeout_duration = utcnow() + timedelta(seconds=total_seconds)

        try:
            await member.timeout(timeout_duration, reason=reason)
            embed = discord.Embed(
                title="🔒 Timeout Issued",
                color=discord.Color.red(),
                timestamp=utcnow(),
            )
            embed.add_field(name="Member", value=f"{member.mention} ({member.id})", inline=False)
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
            embed.add_field(name="Issued By", value=f"{ctx.author.mention}", inline=True)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await self.send_log_embed(ctx.guild, embed)
        except discord.Forbidden:
            print("I do not have permission to timeout this member.")
        except discord.HTTPException as e:
            print(f"Failed to timeout {member.mention}. Error: {e}")

    @commands.command()
    async def timein(self, ctx, member: discord.Member):
        """Remove the timeout from a member."""
        if not self.has_allowed_role(ctx.author):
            print(f"{ctx.author} does not have the required role to use this command.")
            return

        try:
            await member.timeout(None)  # Remove timeout by setting it to None
            embed = discord.Embed(
                title="✅ Timeout Removed",
                color=discord.Color.green(),
                timestamp=utcnow(),
            )
            embed.add_field(name="Member", value=f"{member.mention} ({member.id})", inline=False)
            embed.add_field(name="Removed By", value=f"{ctx.author.mention}", inline=True)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await self.send_log_embed(ctx.guild, embed)
        except discord.Forbidden:
            print("I do not have permission to remove the timeout for this member.")
        except discord.HTTPException as e:
            print(f"Failed to remove timeout for {member.mention}. Error: {e}")

    @timeout.error
    async def timeout_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            print("Please specify a member, duration, and optionally a reason.")
        elif isinstance(error, commands.BadArgument):
            print("Invalid argument. Make sure to tag the user and provide a valid duration.")
        else:
            print("An error occurred while processing the command.")

    @timein.error
    async def timein_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            print("Please specify a member whose timeout you want to remove.")
        elif isinstance(error, commands.BadArgument):
            print("Invalid argument. Make sure to tag the user.")
        else:
            print("An error occurred while processing the command.")

async def setup(bot):
    await bot.add_cog(Timeout(bot))
