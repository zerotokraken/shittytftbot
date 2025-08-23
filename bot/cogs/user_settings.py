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
                CREATE TABLE IF NOT EXISTS tft_settings (
                    discord_id BIGINT PRIMARY KEY,
                    tft_name VARCHAR(255) NOT NULL,
                    tft_tag VARCHAR(255) NOT NULL,
                    region VARCHAR(50) DEFAULT 'americas',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")
        finally:
            cursor.close()
            conn.close()

    VALID_REGIONS = ['americas', 'europe', 'asia', 'sea']

    @commands.command(name='setname')
    async def set_user_settings(self, ctx, *, args):
        """Set your TFT name and region (Format: .setname Name#TAG region)"""
        # Split by space from the right to get region
        parts = args.rsplit(' ', 1)
        if len(parts) != 2:
            await ctx.message.add_reaction('❌')
            await ctx.send("Invalid format. Please use: `.setname Name#TAG region`\nExample: `.setname ZTK#TFT americas`")
            return
        
        riot_id, region = parts
        
        # Validate the name format
        if not re.match(r'^[^#]+#[^#]+$', riot_id):
            await ctx.message.add_reaction('❌')
            await ctx.send("Invalid format. Please use: `.setname Name#TAG region`\nExample: `.setname ZTK#TFT americas`")
            return

        # Validate the region
        region = region.lower()
        if region not in self.VALID_REGIONS:
            await ctx.message.add_reaction('❌')
            await ctx.send(f"Invalid region. Please use one of: {', '.join(self.VALID_REGIONS)}")
            return

        # Split riot_id into name and tag
        name, tag = riot_id.split('#')

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Use INSERT ... ON CONFLICT for upsert operation
            cursor.execute('''
                INSERT INTO tft_settings (discord_id, tft_name, tft_tag, region)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (discord_id)
                DO UPDATE SET
                    tft_name = EXCLUDED.tft_name,
                    tft_tag = EXCLUDED.tft_tag,
                    region = EXCLUDED.region
            ''', (ctx.author.id, name, tag, region))
            
            conn.commit()
            # Add checkmark reaction and wait briefly
            await ctx.message.add_reaction('✅')
            await asyncio.sleep(1)  # Wait 1 second for visibility
            # Delete the command message and send success message
            await ctx.message.delete()
            success_msg = await ctx.send(f"Successfully set your TFT name and region.")
            await asyncio.sleep(3)  # Wait 3 seconds
            await success_msg.delete()
        except Exception as e:
            await ctx.message.add_reaction('❌')
            print(f"Error setting user settings: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_user_tft_name(self, discord_id: int) -> tuple:
        """Get a user's TFT name, tag, and region from their Discord ID"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT tft_name, tft_tag, region FROM tft_settings WHERE discord_id = %s', (discord_id,))
            result = cursor.fetchone()
            return result if result else None
        finally:
            cursor.close()
            conn.close()

async def setup(bot):
    await bot.add_cog(UserSettings(bot))
