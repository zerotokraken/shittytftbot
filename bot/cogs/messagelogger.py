import discord
from discord.ext import commands


class MessageLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Specify the ID of the channel where you want to log deleted messages
        self.log_channel_id = 1273523623780552765  # Replace with your log channel's ID

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return

        # Get the logging channel
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel is None:
            print(f"Log channel with ID {self.log_channel_id} not found.")
            return
        timestamp = message.created_at.strftime("%-m/%-d/%Y %-I:%M %p")

        # Create an embed for the deleted message
        embed = discord.Embed(
            title=f"🗑️ {message.author}",
            description=f"**Message deleted in {message.channel.mention}**",
            color=discord.Color.red(),

        )

        # Add fields for content and message details
        if message.content:
            embed.add_field(name="", value=message.content, inline=False)
        else:
            embed.add_field(name="", value="(No text content)", inline=False)
        embed.add_field(name="", value=f"Message ID: {message.id}", inline=False)
        embed.set_footer(text=f"User ID: {message.author.id} • {timestamp}")

        # Attach files if there were any in the message
        if message.attachments:
            files = [await attachment.to_file() for attachment in message.attachments]
            await log_channel.send(embed=embed, files=files)
        else:
            await log_channel.send(embed=embed)


# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(MessageLogger(bot))
