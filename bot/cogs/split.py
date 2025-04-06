import discord
from discord.ext import commands
import random

class SplitCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.yes_responses = [
            "Split! The potential jackpot could be huge! 🎰",
            "Choose split. Surely no one else is gonna click it. 💰",
            "Go for the split. High risk, high reward! 🌟",
            "Split it! Sometimes greed is good. 🤝",
            "Yes! The collective pot could be worth more than the safe option. ✨",
            "Split - fortune favors the bold! 🎲",
            "Choose split. Go big or GO HOME! 🚀",
            "Split - the reward potential outweighs the safe play! 💎"
        ]
        self.no_responses = [
            "Take the guaranteed gold! A bird in hand is worth two in the bush. 🦅",
            "Play it safe - take the guaranteed payout! 🔒",
            "Secure the bag! Don't gamble! 💼",
            "Take the guaranteed gold - no risk, pure profit! ✅",
            "Go for the sure thing! Let others gamble their gold away. 🎯",
            "Choose the guaranteed payout - consistency is key! 💫",
            "Take what's guaranteed - don't leave your gold to chance! 🎁",
            "Secure gold now! Let others split their losses. 📈"
        ]

    @commands.command()
    async def shouldisplit(self, ctx):
        """Randomly decides if you should take guaranteed gold or split the pot with other players"""
        if random.random() < 0.5:  # 50% chance for either response
            response = random.choice(self.yes_responses)
        else:
            response = random.choice(self.no_responses)
        
        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(SplitCommands(bot))
