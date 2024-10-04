import discord
from discord.ext import commands
import psycopg2
import os

class SuggestionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = self.connect_to_db()
        self.create_suggestions_table()

    def connect_to_db(self):
        DATABASE_URL = os.environ.get('DATABASE_URL')
        try:
            return psycopg2.connect(DATABASE_URL, sslmode='require')
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            return None

    def create_suggestions_table(self):
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS suggestions (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        suggestion TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.conn.commit()

    @commands.command(name="suggest")
    async def suggest(self, ctx, *, suggestion: str):
        """Allows users to submit suggestions."""
        user_id = ctx.author.id
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO suggestions (user_id, suggestion)
                    VALUES (%s, %s)
                """, (user_id, suggestion))
                self.conn.commit()

            await ctx.send(f"Thank you for your suggestion, {ctx.author.display_name}!")
        else:
            print("Sorry, there was an error saving your suggestion. Please try again later.")


async def setup(bot):
    await bot.add_cog(SuggestionCog(bot))