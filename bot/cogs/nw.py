import discord
from discord.ext import commands
import psycopg2
import os

class NoobWatchCommand(commands.Cog):
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

    def update_noobwatch_count(self, user_id):
        if self.conn is None:
            print("No database connection.")
            return None

        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO noobwatch (user_id, count) 
                VALUES (%s, 1) 
                ON CONFLICT (user_id) 
                DO UPDATE SET count = noobwatch.count + 1 
                RETURNING count
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            self.conn.commit()
            cursor.close()
            return result[0] if result else None
        except psycopg2.Error as e:
            print(f"Error updating noobwatch count: {e}")
            return None

    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)  # 1-hour cooldown per user
    async def noobwatch(self, ctx):
        if ctx.message.reference:  # Check if the message is a reply
            replied_to_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            user = replied_to_message.author  # Get the user the command issuer replied to
            count = self.update_noobwatch_count(user.id)
            if count is not None:
                await ctx.send(f"{user.name}'s NoobWatch count is now {count}.")
            else:
                print("There was an error updating the NoobWatch count.")
        else:
            print("You did the command wrong that's a NoobWatch")

async def setup(bot):
    await bot.add_cog(NoobWatchCommand(bot))

