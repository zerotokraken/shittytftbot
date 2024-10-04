import discord
from discord.ext import commands
import random
import asyncio
import json
import os
from textblob import TextBlob  # Import TextBlob for sentiment analysis


class Personality(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'personality.json')
        with open(config_path, 'r') as config_file:
            self.config = json.load(config_file)

    def determine_sentiment(self, message_content):
        analysis = TextBlob(message_content)
        # Sentiment polarity ranges from -1 (negative) to 1 (positive)
        if analysis.sentiment.polarity > 0.1:
            return 'positive'
        elif analysis.sentiment.polarity < -0.1:
            return 'negative'
        return 'neutral'

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages sent by the bot itself
        if message.author == self.bot.user:
            return

        main_match = 'shitty tft bot'
        alternate_spellings = self.config['alternate_spellings']
        greeting_words = self.config['greeting_words']
        positive_responses = self.config['positive_responses']
        negative_responses = self.config['negative_responses']
        neutral_responses = self.config['neutral_responses']
        greeting_responses = self.config['greeting_responses']

        message_content = message.content.lower()

        if (self.bot.user.mention in message_content or main_match in message_content
                or any(alt in message_content for alt in alternate_spellings)):

            # Use sentiment analysis to determine the context
            context = self.determine_sentiment(message_content)

            # Handle greetings separately (if detected)
            if any(word in message_content for word in greeting_words):
                context = 'greeting'

            # Select a random response based on the detected context
            if context == 'positive':
                response = random.choice(positive_responses)
            elif context == 'negative':
                response = random.choice(negative_responses)
            elif context == 'greeting':
                response = random.choice(greeting_responses)
            else:
                response = random.choice(neutral_responses)

            # Format the response with the author's display name
            formatted_response = response.format(display_name=message.author.display_name)

            # Add a 1-second delay before responding
            await asyncio.sleep(1)

            # Send the formatted response
            await message.channel.send(formatted_response)


async def setup(bot):
    await bot.add_cog(Personality(bot))
