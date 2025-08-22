import discord
from discord.ext import commands
import psycopg2
import os
import re
import asyncio

class UserSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.create_tables()

    def get_db_connection(self):
        """Get a connection to the PostgreSQL database"""
        DATABASE_URL = os.environ.get('DATABASE_URL')
        return psycopg2.connect(DATABASE_URL, sslmode='require')

    def create_tables(self):
        """Create necessary database tables if they don't exist"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    discord_id BIGINT PRIMARY KEY,
                    tft_name VARCHAR(255) NOT NULL,
                    tft_tag VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")
        finally:
            cursor.close()
            conn.close()

    @commands.command(name='set_name')
    async def set_name(self, ctx, *, riot_id: str):
        """Set your TFT name and tag (Format: Name#TAG)"""
        # Validate the format
        if not re.match(r'^[^#]+#[^#]+$', riot_id):
            await ctx.message.add_reaction('❌')
            await ctx.send("Invalid format. Please use: `.set_name Name#TAG`")
            return

        # Split into name and tag
        name, tag = riot_id.split('#')

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Use INSERT ... ON CONFLICT for upsert operation
            cursor.execute('''
                INSERT INTO user_settings (discord_id, tft_name, tft_tag)
                VALUES (%s, %s, %s)
                ON CONFLICT (discord_id)
                DO UPDATE SET
                    tft_name = EXCLUDED.tft_name,
                    tft_tag = EXCLUDED.tft_tag
            ''', (ctx.author.id, name, tag))
            
            conn.commit()
            # Add checkmark reaction and wait briefly
            await ctx.message.add_reaction('✅')
            await asyncio.sleep(1)  # Wait 1 second for visibility
            # Delete the command message and send success message
            await ctx.message.delete()
            await ctx.send(f"Successfully set your TFT name to: {name}#{tag}")
        except Exception as e:
            await ctx.message.add_reaction('❌')
            await ctx.send(f"An error occurred: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def get_user_tft_name(self, discord_id: int) -> tuple:
        """Get a user's TFT name and tag from their Discord ID"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT tft_name, tft_tag FROM user_settings WHERE discord_id = %s', (discord_id,))
            result = cursor.fetchone()
            return result if result else None
        finally:
            cursor.close()
            conn.close()

async def setup(bot):
    await bot.add_cog(UserSettings(bot))
