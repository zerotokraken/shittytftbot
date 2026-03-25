import discord
from discord.ext import commands
import random

class AskCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.responses = [
            "Yes, definitely.",
            "It is certain.",
            "Without a doubt.",
            "Yes – definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]

    @commands.command()
    async def ask(self, ctx, *, question: str):
        # Check if question is provided
        if not question.strip():
            print("Please ask a question!", mention_author=True)
            return

        # Choose a random response
        answer = random.choice(self.responses)

        # Send response to user
        await ctx.reply(f"{answer}", mention_author=True)

async def setup(bot):
    await bot.add_cog(AskCommand(bot))
