import discord
from discord.ext import commands
import psycopg2
import os

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
                WHERE author_id != 1285268322551726140  -- Replace this with self.bot.user.id for flexibility
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
    @commands.cooldown(1, 30, commands.BucketType.user)  # 30-second cooldown per user
    async def malding(self, ctx):
        # Always limit to one message
        random_message = self.get_random_malding_message()
        if random_message:
            await ctx.send(random_message)
        else:
            print("No malding messages found in the database.")

    @malding.error
    async def malding_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            print(f"Please wait {error.retry_after:.2f} seconds before using the command again.")

async def setup(bot):
    await bot.add_cog(MaldingCommand(bot))
