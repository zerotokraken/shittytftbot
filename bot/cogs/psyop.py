import discord
from discord.ext import commands
import random
import time

class PsyopCommand(commands.Cog):
    def __init__(self, bot, cache_psyop, cache_duration_custom):
        self.bot = bot
        self.cache_psyop = cache_psyop
        self.cache_duration_custom = cache_duration_custom

    @commands.command()
    async def psyop(self, ctx):
        current_time = time.time()

        # Check if the cache is expired
        if current_time - self.cache_psyop['timestamp'] > self.cache_duration_custom:
            print('Cache is expired. Please wait for it to refresh.')
            return

        # Check if there are messages in the cache
        if not self.cache_psyop.get('messages', []):
            print('No messages found in the cache.')
            return

        # Send a random message from the cached messages
        random_message = random.choice([msg for _, msg in self.cache_psyop['messages']])
        await ctx.send(random_message)

async def setup(bot, cache_psyop, cache_duration_custom):
    await bot.add_cog(PsyopCommand(bot, cache_psyop, cache_duration_custom))
