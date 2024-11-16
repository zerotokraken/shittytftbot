import re
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from discord.utils import get


class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # List of allowed roles
        self.allowed_roles = ["Hairy Frog", "Admin", "Discord Moderator"]   # Replace with your roles

    def has_allowed_role(self, member):
        """Check if the user has at least one of the allowed roles."""
        allowed_roles = self.allowed_roles
        user_roles = [role.name for role in member.roles]
        return any(role in allowed_roles for role in user_roles)

    def parse_duration(self, duration_str):
        """Parse duration string and return the total duration in seconds."""
        duration_regex = re.compile(r"(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?")
        match = duration_regex.fullmatch(duration_str)
        if not match:
            return None

        weeks, days, hours, minutes = match.groups(default="0")
        total_seconds = (int(weeks) * 604800) + (int(days) * 86400) + (int(hours) * 3600) + (int(minutes) * 60)
        return total_seconds

    @commands.command()
    async def timeout(self, ctx, member_name: str, duration: str, *, reason: str = None):
        """Timeout a member for a custom duration (e.g., 3m, 6h, 2d, 1w)."""
        if not self.has_allowed_role(ctx.message.author):
            print(f"{ctx.message.author} does not have the required role to use this command.")
            return

        # First, try to find the member by exact name (case-sensitive)
        member = discord.utils.get(ctx.guild.members, nick=member_name)

        # If no member found, attempt case-insensitive search
        if not member:
            member = discord.utils.get(ctx.guild.members, nick=lambda m: m.nick.lower() == member_name.lower())
            if not member:
                print("Member not found. Please check the username and try again.")
                return

        total_seconds = self.parse_duration(duration)
        if total_seconds is None:
            print("Invalid duration format. Please use the format like 3m, 6h, 2d, 1w.")
            return

        timeout_until = datetime.utcnow() + timedelta(seconds=total_seconds)

        try:
            await member.timeout(timeout_duration, reason=reason)
            await ctx.send(f"{member.mention} has been timed out for {duration}.")
        except discord.Forbidden:
            print("I do not have permission to timeout this member.")
        except discord.HTTPException as e:
            print(f"Failed to timeout {member.mention}. Error: {e}")

    @timeout.error
    async def timeout_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            print("Please specify a member and duration.")
        elif isinstance(error, commands.BadArgument):
            print("Invalid argument. Please specify a valid member and duration.")
        else:
            print("An error occurred while processing the command.")


async def setup(bot):
    await bot.add_cog(Timeout(bot))
