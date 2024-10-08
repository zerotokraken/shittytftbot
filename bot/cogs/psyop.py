import discord
from discord.ext import commands
import psycopg2
import os
import random

class PsyopCommand(commands.Cog):
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

    def fetch_psyop_messages(self):
        if self.conn is None:
            print("No database connection.")
            return []

        try:
            cursor = self.conn.cursor()
            query = """
                (SELECT content FROM general_messages)
                UNION
                (SELECT content FROM advice_messages)
                UNION
                (SELECT content FROM malding_messages)
            """
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return [row[0] for row in result] if result else []
        except psycopg2.Error as e:
            print(f"Error fetching psyop messages: {e}")
            return []

    @commands.command()
    async def psyop(self, ctx):
        # Fetch messages from all tables
        psyop_messages = self.fetch_psyop_messages()

        if not psyop_messages:
            print ctx.send("No psyop messages found.")
            return

        # Send a random message from the messages
        random_message = random.choice(psyop_messages)
        await ctx.send(random_message)

async def setup(bot):
    await bot.add_cog(PsyopCommand(bot))
