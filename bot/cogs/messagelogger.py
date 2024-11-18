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

        # Format the timestamp
        timestamp = message.created_at.strftime("%-m/%-d/%Y %-I:%M %p")

        # Create an embed for the deleted message
        embed = discord.Embed(
            description=f"**Message deleted in {message.channel.mention}**",
            color=discord.Color.red(),
        )

        # Set the author with the user's display name and avatar
        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.avatar.url  # Set user's avatar as icon
        )

        # Add fields for content and message details
        if message.content:
            embed.add_field(name="", value=message.content, inline=False)
        else:
            embed.add_field(name="", value="(No text content)", inline=False)

        embed.add_field(name="", value=f"Message ID: {message.id}", inline=False)

        # Set the footer with user ID and formatted timestamp
        embed.set_footer(text=f"User ID: {message.author.id} • {timestamp}")

        # Attach files if there were any in the message
        if message.attachments:
            files = [await attachment.to_file() for attachment in message.attachments]
            await log_channel.send(embed=embed, files=files)
        else:
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel is None:
            print(f"Log channel with ID {self.log_channel_id} not found.")
            return

        embed = discord.Embed(
            title="Member Banned",
            description=f"{user.mention} ({user.name}#{user.discriminator}) was banned.",
            color=discord.Color.dark_red(),
        )
        embed.set_footer(text=f"User ID: {user.id}")
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Check if the user was kicked (by checking the audit log)
        guild = member.guild
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel is None:
            print(f"Log channel with ID {self.log_channel_id} not found.")
            return

        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                embed = discord.Embed(
                    title="Member Kicked",
                    description=f"{member.mention} ({member.name}#{member.discriminator}) was kicked by {entry.user.mention}.",
                    color=discord.Color.orange(),
                )
                embed.set_footer(text=f"User ID: {member.id}")
                await log_channel.send(embed=embed)
                return

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(MessageLogger(bot))
