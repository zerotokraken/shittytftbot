import discord
from discord.ext import commands
import psycopg2
import os
import random

class MaldingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = self.connect_to_db()

    def connect_to_db(self):
        DATABASE_URL = os.environ.get('DATABASE_URL')
        try:
            return psycopg2.connect(DATABASE_URL, sslmode='require')
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            return None

    def get_random_malding_message(self):
        if self.conn is None:
            print("No database connection.")
            return None

        try:
            cursor = self.conn.cursor()
            query = """
                SELECT content 
                FROM malding_messages 
                WHERE author_id != 1285268322551726140 
                ORDER BY RANDOM() 
                LIMIT 1
            """
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except psycopg2.Error as e:
            print(f"Error fetching random message: {e}")
            return None

    @commands.command()
    async def malding(self, ctx, num_messages: int = 1):
        # Ensure num_messages is within the limit
        num_messages = min(max(num_messages, 1), 3)  # Adjust 3 to your desired limit

        for _ in range(num_messages):
            # Get a random message from the database
            random_message = self.get_random_malding_message()
            if random_message:
                await ctx.send(random_message)
            else:
                print("No malding messages found in the database.")

async def setup(bot):
    await bot.add_cog(MaldingCommand(bot))
