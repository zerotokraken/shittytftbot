import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import re
from datetime import datetime, timedelta

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_duration(self, duration_str):
        """Parse duration string and return the total duration in seconds."""
        duration_regex = re.compile(r'(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?')
        match = duration_regex.fullmatch(duration_str)
        if not match:
            return None

        weeks, days, hours, minutes = match.groups(default='0')
        total_seconds = (int(weeks) * 604800) + (int(days) * 86400) + (int(hours) * 3600) + (int(minutes) * 60)
        return total_seconds

    @commands.command()
    @has_permissions(administrator=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason: str = None):
        """Timeout a member for a custom duration (e.g., 3m, 6h, 2d, 1w)."""
        total_seconds = self.parse_duration(duration)
        if total_seconds is None:
            await ctx.send("Invalid duration format. Please use the format like 3m, 6h, 2d, 1w.")
            return

        timeout_until = datetime.utcnow() + timedelta(seconds=total_seconds)

        try:
            await member.edit(timeout_until=timeout_until, reason=reason)
            await ctx.send(f"{member.mention} has been timed out for {duration}.")
        except discord.Forbidden:
            print("I do not have permission to timeout this member.")
        except discord.HTTPException as e:
            print(f"Failed to timeout {member.mention}. Error: {e}")

    @timeout.error
    async def timeout_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            print("You do not have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            print("Please specify a member and duration.")
        elif isinstance(error, commands.BadArgument):
            print("Invalid argument. Please specify a valid member and duration.")
        else:
            print("An error occurred while processing the command.")

async def setup(bot):
    await bot.add_cog(Timeout(bot))
