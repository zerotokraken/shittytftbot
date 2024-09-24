import discord
from discord.ext import commands
import random
import time

class MaldingCommand(commands.Cog):
    def __init__(self, bot, cache, cache_duration):
        self.bot = bot
        self.cache = cache
        self.cache_duration = cache_duration

    @commands.command()
    async def malding(self, ctx, num_messages: int = 1):
        current_time = time.time()

        # Check if cache is expired
        if current_time - self.cache['timestamp'] > self.cache_duration:
            print('Cache is expired. Please wait for it to refresh.')
            return

        # Check if there are messages in the cache
        if not self.cache.get('messages', []):
            print('No messages found in the cache.')
            return

        # Ensure num_messages is within the limit
        num_messages = min(max(num_messages, 1), 3)  # Adjust 10 to your desired limit

        for _ in range(num_messages):
            # Send a random message from the cache
            random_message = random.choice(self.cache['messages'])
            await ctx.send(random_message)

async def setup(bot, cache, cache_duration):
    await bot.add_cog(MaldingCommand(bot, cache, cache_duration))
