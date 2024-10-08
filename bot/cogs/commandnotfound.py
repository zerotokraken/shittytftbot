import discord
from discord.ext import commands
import psycopg2
import os
from datetime import datetime

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = self.connect_to_db()

    def create_unavailable_commands_table(self):
        if self.conn is None:
            print("No database connection.")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unavailable_commands (
                    id SERIAL PRIMARY KEY,
                    command TEXT NOT NULL,
                    attempted_by BIGINT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.conn.commit()
            cursor.close()
            print("Unavailable commands table checked/created.")
        except psycopg2.Error as e:
            print(f"Error creating unavailable commands table: {e}")

    def connect_to_db(self):
        DATABASE_URL = os.environ.get('DATABASE_URL')
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            print("Successfully connected to the database.")
            self.conn = conn
            self.create_unavailable_commands_table()  # Ensure table exists after connection
            return conn
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            return None

    def log_unavailable_command(self, command_name, user_id):
        if self.conn is None:
            print("No database connection.")
            return

        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO unavailable_commands (command, attempted_by)
                VALUES (%s, %s)
            """
            cursor.execute(query, (command_name, user_id))
            self.conn.commit()
            cursor.close()
            print(f"Logged unavailable command: {command_name} by user {user_id}.")
        except psycopg2.Error as e:
            print(f"Error logging unavailable command: {e}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Check if the error is due to an unrecognized command
        if isinstance(error, commands.CommandNotFound):
            # Log the unavailable command
            self.log_unavailable_command(ctx.message.content, ctx.author.id)  # Use ctx.author.id

            # Optionally send a response to the user (or handle it silently)
            print("That command is not available.")  # Send message or comment this line out if not needed
        else:
            # Handle other command errors (if needed)
            raise error

async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))
