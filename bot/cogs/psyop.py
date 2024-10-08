import discord
from discord.ext import commands
import psycopg2
import random

class PsyopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def fetch_random_psyop_message(self, connection, cursor):
        try:
            # Query to fetch a random message containing "psyop" with LIMIT 1
            query = """
            SELECT content FROM (
                SELECT content FROM general_messages WHERE content ILIKE '%psyop%'
                UNION ALL
                SELECT content FROM advice_messages WHERE content ILIKE '%psyop%'
                UNION ALL
                SELECT content FROM malding_messages WHERE content ILIKE '%psyop%'
            ) AS combined
            ORDER BY random()
            LIMIT 1;
            """
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                return result[0]  # Return the content of the message
            else:
                return None
        except Exception as e:
            print(f"Error fetching psyop message: {e}")
            return None

    @commands.command()
    async def psyop(self, ctx):
        # Connect to the database
        connection = connect_to_db()
        if not connection:
            print("Error connecting to the database.")
            return

        cursor = connection.cursor()

        # Fetch a random psyop message
        message_content = self.fetch_random_psyop_message(connection, cursor)
        if message_content:
            await ctx.send(message_content)
        else:
            print("No psyop messages found.")

        # Close the cursor and connection
        cursor.close()
        connection.close()

# Function to set up the cog
async def setup(bot):
    await bot.add_cog(PsyopCommand(bot))
