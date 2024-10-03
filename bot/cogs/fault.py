import discord
from discord.ext import commands
import random
import time

class FaultCommand(commands.Cog):
    def __init__(self, bot, cache_fault, cache_duration):
        self.bot = bot
        self.cache_fault = cache_fault
        self.cache_duration = cache_duration

    @commands.command(help="Find a random message containing 'is it even my fault'.")
    async def myfault(self, ctx):
        current_time = time.time()

        # Check if the cache is expired
        if current_time - self.cache_fault['timestamp'] > self.cache_duration:
            print('Cache is expired. Please wait for it to refresh.')
            return

        # Check if there are messages in the cache
        if not self.cache_fault.get('messages', []):
            print('No messages found in the cache.')
            return

        # Send a random message from the cached messages
        random_message = random.choice([msg for _, msg in self.cache_fault['messages']])
        await ctx.send(random_message)

async def setup(bot, cache_fault, cache_duration):
    await bot.add_cog(FaultCommand(bot, cache_fault, cache_duration))
