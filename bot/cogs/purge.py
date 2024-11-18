import discord
from discord.ext import commands


class MessageManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1113518194712383578  # Replace with the ID of the specific log channel
        self.allowed_roles = ["Hairy Frog", "Admin", "Discord Moderator"]  # Specify allowed role names

    def has_allowed_role(self, member):
        """
        Checks if the member has at least one of the allowed roles.
        """
        return any(role.name in self.allowed_roles for role in member.roles)

    @commands.command()
    async def delete(self, ctx, user: discord.Member, amount: int):
        """
        Deletes a specified number of messages from a specific user and logs the result.

        Parameters:
        - user: Mentioned user whose messages are to be deleted.
        - amount: The number of messages to delete.
        """
        if not self.has_allowed_role(ctx.author):
            print(f"{ctx.author.mention}, you do not have the required role to use this command.")
            return

        if amount < 1:
            print("Please specify a number greater than 0.")
            return

        try:
            # Get the log channel
            log_channel = self.bot.get_channel(self.log_channel_id)
            if log_channel is None:
                print("Log channel not found. Please check the log channel ID.")
                return

            # Counter to keep track of deleted messages
            deleted_count = 0

            # Manually fetch and delete messages
            async for message in ctx.channel.history(limit=100):
                if message.author == user:
                    await message.delete()
                    deleted_count += 1
                    if deleted_count >= amount:
                        break

            # Send confirmation to the log channel
            embed = discord.Embed(
                title="Messages Deleted",
                color=discord.Color.orange(),
                description=f"{deleted_count} message(s) from {user.mention} were deleted in {ctx.channel.mention}."
            )
            embed.add_field(name="Actioned By", value=ctx.author.mention, inline=True)
            embed.add_field(name="User", value=user.mention, inline=True)
            embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
            await log_channel.send(embed=embed)

        except discord.Forbidden:
            print("I don't have permission to manage messages in this channel.")
        except discord.HTTPException as e:
            print(f"Failed to delete messages: {e}")

    @delete.error
    async def delete_error(self, ctx, error):
        """
        Handles errors for the delete command.
        """
        if isinstance(error, commands.MissingRequiredArgument):
            print("Please mention a user and the number of messages to delete.")
        elif isinstance(error, commands.BadArgument):
            print("Invalid arguments. Please check the user mention and amount.")
        else:
            print("An error occurred while processing the command.")


# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(MessageManagement(bot))
