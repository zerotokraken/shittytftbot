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
    async def malding(self, ctx):
        current_time = time.time()

        # Check if cache is expired
        if current_time - self.cache['timestamp'] > self.cache_duration:
            print('Cache is expired. Please wait for it to refresh.')
            return

        # Check if there are messages in the cache
        if not self.cache.get('messages', []):
            print('No messages found in the cache.')
            return

        # Send a random message from the cache
        random_message = random.choice(self.cache['messages'])
        await ctx.send(random_message)

def setup(bot, cache, cache_duration):
    bot.add_cog(MaldingCommand(bot, cache, cache_duration))
