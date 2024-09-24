import discord
from discord.ext import commands
import random
import asyncio

class MessageResponder(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = on_message

    @commands.Cog.listener()
    async def on_message(self, message):
        # Main match parameter
        main_match = 'shitty tft bot'

        alternate_spellings = self.config['alternate_spellings']
        positive_words = self.config['positive_words']
        negative_words = self.config['negative_words']
        greeting_words = self.config['greeting_words']
        positive_responses = self.config['positive_responses']
        negative_responses = self.config['negative_responses']
        neutral_responses = self.config['neutral_responses']
        greeting_responses = self.config['greeting_responses']

        # Ignore messages sent by the bot itself
        if message.author == self.bot.user:
            return

        if (self.bot.user.mention in message.content or main_match in message.content.lower()
                or any(alt in message.content.lower() for alt in alternate_spellings)):

            # Lowercase the full message
            message_content = message.content.lower()

            # Determine context (positive, negative, neutral, greeting)
            context = 'neutral'
            if any(word in message_content for word in negative_words):
                context = 'negative'
            elif any(word in message_content for word in positive_words):
                context = 'positive'
            elif any(word in message_content for word in greeting_words):
                context = 'greeting'

            # Select a random response based on the context
            if context == 'positive':
                response = random.choice(positive_responses)
            elif context == 'negative':
                response = random.choice(negative_responses)
            elif context == 'greeting':
                response = random.choice(greeting_responses)  # Greeting the user by name
            else:
                response = random.choice(neutral_responses)

            # Add a 1-second delay before responding
            await asyncio.sleep(1)

            # Send the appropriate response
            await message.channel.send(response)

        # Process commands if the message is a command
        await self.bot.process_commands(message)

def setup(bot):
    # Note: `config` should be passed in some other way, e.g., global or through a different method
    bot.add_cog(MessageResponder(bot, on_message))
