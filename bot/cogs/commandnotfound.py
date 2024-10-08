import discord
from discord.ext import commands
import psycopg2
import os
from datetime import datetime

class CommandErrorHandler(commands.Cog):
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

    def log_unavailable_command(self, command, author):
        if self.conn is None:
            print("No database connection.")
            return

        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO unavailable_commands (command, author_id, author_name)
                VALUES (%s, %s, %s);
            """
            cursor.execute(query, (command, author.id, str(author)))
            self.conn.commit()
            cursor.close()
            print(f"Logged unavailable command: {command} from {author}")
        except psycopg2.Error as e:
            print(f"Error logging unavailable command: {e}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Check if the error is due to an unrecognized command
        if isinstance(error, commands.CommandNotFound):
            # Log the unavailable command
            self.log_unavailable_command(ctx.message.content, ctx.author)

            # Optionally send a response to the user (or handle it silently)
            print("That command is not available.")
        else:
            # Handle other command errors (if needed)
            raise error

async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))
