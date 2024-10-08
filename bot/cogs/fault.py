import discord
from discord.ext import commands
import psycopg2
import os
import random

class FaultCommand(commands.Cog):
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

    def fetch_fault_messages(self):
        if self.conn is None:
            print("No database connection.")
            return []

        try:
            cursor = self.conn.cursor()
            query = """
                (SELECT content FROM general_messages WHERE content ILIKE '%is it even my fault%')
                UNION
                (SELECT content FROM advice_messages WHERE content ILIKE '%is it even my fault%')
                UNION
                (SELECT content FROM malding_messages WHERE content ILIKE '%is it even my fault%')
            """
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return [row[0] for row in result] if result else []
        except psycopg2.Error as e:
            print(f"Error fetching fault messages: {e}")
            return []

    @commands.command()
    async def myfault(self, ctx):
        # Fetch matching messages from the database
        fault_messages = self.fetch_fault_messages()

        if not fault_messages:
            print("No messages found containing 'is it even my fault'.")
            return

        # Send a random message from the matching messages
        random_message = random.choice(fault_messages)
        await ctx.send(random_message)

async def setup(bot):
    await bot.add_cog(FaultCommand(bot))
