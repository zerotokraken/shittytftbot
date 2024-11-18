import discord
from discord.ext import commands


class MessageManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1273523623780552765  # Replace with the ID of the specific channel

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx, user: discord.Member, amount: int):
        """
        Deletes a specified number of messages from a specific user and logs the result.

        Parameters:
        - user: Mentioned user whose messages are to be deleted.
        - amount: The number of messages to delete.
        """
        if amount < 1:
            print("Please specify a number greater than 0.")
            return

        # Confirm the command is being used in a text channel
        if not isinstance(ctx.channel, discord.TextChannel):
            print("This command can only be used in text channels.")
            return

        try:
            # Get the logging channel
            log_channel = self.bot.get_channel(self.log_channel_id)
            if log_channel is None:
                print("Log channel not found. Please check the log channel ID.")
                return

            # Purge messages from the user
            def check(message):
                return message.author == user

            deleted = await ctx.channel.purge(limit=amount + 10, check=check, bulk=False)

            # Send confirmation to the log channel
            embed = discord.Embed(
                title="Messages Deleted",
                color=discord.Color.orange(),
                description=f"{len(deleted)} message(s) from {user.mention} were deleted in {ctx.channel.mention}."
            )
            embed.add_field(name="Actioned By", value=ctx.author.mention, inline=True)
            embed.add_field(name="User", value=user.mention, inline=True)
            embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
            await log_channel.send(embed=embed)

        except discord.Forbidden:
            print("I don't have permission to manage messages in this channel.")
        except discord.HTTPException as e:
            print(f"Failed to delete messages: {e}")


# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(MessageManagement(bot))
