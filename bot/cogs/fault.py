import discord
from discord.ext import commands
from collections import deque
import asyncio

class FaultCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = deque(maxlen=1000)

    async def cache_messages(self, channel):
        # Fetch the last 1000 messages and store them in the cache
        async for message in channel.history(limit=1000):
            self.message_cache.append(message)

    @commands.command(help="Fetch a random message containing 'is it even my fault'")
    async def myfault(self, ctx):
        search_phrase = "is it even my fault"
        channel = ctx.channel

        # If the cache is empty, populate it
        if not self.message_cache:
            await self.cache_messages(channel)

        # Filter the cache for messages containing the search phrase
        matching_messages = [msg for msg in self.message_cache if search_phrase in msg.content.lower()]

        if matching_messages:
            random_message = random.choice(matching_messages)
            await ctx.send(f"{random_message.content}")
        else:
            print(f"No messages found with the phrase '{search_phrase}'.")

async def setup(bot):
    await bot.add_cog(FaultCommands(bot))
