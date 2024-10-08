import discord
from discord.ext import commands
import psycopg2
import os

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

    def fetch_random_fault_message(self):
        if self.conn is None:
            print("No database connection.")
            return None

        try:
            cursor = self.conn.cursor()
            query = """
                SELECT content FROM (
                    SELECT content FROM general_messages WHERE content ILIKE '%is it even my fault%' AND author_id != 1285268322551726140
                    UNION ALL
                    SELECT content FROM advice_messages WHERE content ILIKE '%is it even my fault%' AND author_id != 1285268322551726140
                    UNION ALL
                    SELECT content FROM malding_messages WHERE content ILIKE '%is it even my fault%' AND author_id != 1285268322551726140
                ) AS combined
                ORDER BY RANDOM()
                LIMIT 1;
            """
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except psycopg2.Error as e:
            print(f"Error fetching fault message: {e}")
            return None

    @commands.command()
    async def myfault(self, ctx):
        # Fetch a random message containing 'is it even my fault'
        random_message = self.fetch_random_fault_message()

        if random_message:
            await ctx.send(random_message)
        else:
            await ctx.send("No messages found containing 'is it even my fault'.")

async def setup(bot):
    await bot.add_cog(FaultCommand(bot))
