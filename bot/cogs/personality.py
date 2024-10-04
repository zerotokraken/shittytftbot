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

        # Check for bot mention or specific phrases
        if (self.bot.user.mention in message.content or main_match in message.content.lower()
                or any(alt in message.content.lower() for alt in alternate_spellings)):

            # Lowercase the full message
            message_content = message.content.lower()

            # Use TextBlob for sentiment analysis
            analysis = TextBlob(message_content)
            sentiment = analysis.sentiment

            # Determine context based on sentiment polarity
            context = 'neutral'
            if sentiment.polarity < 0:  # Negative sentiment
                context = 'negative'
            elif sentiment.polarity > 0:  # Positive sentiment
                context = 'positive'
            elif any(word in message_content for word in greeting_words):  # Check for greeting
                context = 'greeting'

            # Select a random response based on the context
            if context == 'positive':
                response = random.choice(positive_responses)
            elif context == 'negative':
                response = random.choice(negative_responses)
            elif context == 'greeting':
                response = random.choice(greeting_responses)
            else:
                response = random.choice(neutral_responses)

            # Format the response to include the author's display name if needed
            formatted_response = response.format(display_name=message.author.display_name)

            # Add a 1-second delay before responding
            await asyncio.sleep(1)

            # Send the formatted response
            await message.channel.send(formatted_response)


async def setup(bot):
    await bot.add_cog(Personality(bot))
