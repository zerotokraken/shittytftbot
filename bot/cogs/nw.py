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
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            self.create_table_if_not_exists(conn)  # Ensure the table exists
            return conn
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            return None

    def create_table_if_not_exists(self, conn):
        # Create table if it doesn't exist
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS noobwatch (
                    user_id BIGINT PRIMARY KEY,
                    count INTEGER DEFAULT 1
                )
            """)
            conn.commit()
            cursor.close()
        except psycopg2.Error as e:
            print(f"Error creating table: {e}")

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

    def get_leaderboard(self):
        """Fetch the top 10 users with the highest noobwatch count."""
        if self.conn is None:
            print("No database connection.")
            return None

        try:
            cursor = self.conn.cursor()
            query = """
                SELECT user_id, count 
                FROM noobwatch 
                ORDER BY count DESC 
                LIMIT 10
            """
            cursor.execute(query)
            leaderboard = cursor.fetchall()
            cursor.close()
            return leaderboard
        except psycopg2.Error as e:
            print(f"Error fetching leaderboard: {e}")
            return None

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)  # 30 second cooldown per user
    async def noobwatch(self, ctx):

        if ctx.author.id == "372292699597832192":  # Replace with your Discord ID
            # Reset the command's cooldown for this user
            self.my_command.reset_cooldown(ctx)

        if ctx.message.reference:  # Check if the message is a reply
            replied_to_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            user = replied_to_message.author  # Get the user the command issuer replied to
            count = self.update_noobwatch_count(user.id)
            if count is not None:
                await ctx.send(f"{user.display_name}'s NoobWatch count is now {count}.")
            else:
                print("There was an error updating the NoobWatch count.")
        else:
            print("Please reply to a user's message to use this command.")

    @commands.command()
    async def topnoobs(self, ctx):
        """Display the top 10 users in the NoobWatch leaderboard as an embed."""
        leaderboard = self.get_leaderboard()
        if leaderboard:
            # Create the embed
            embed = discord.Embed(
                title="🏆 NoobWatch Leaderboard",
                color=discord.Color.gold()
            )

            # Add leaderboard entries to the embed
            for i, (user_id, count) in enumerate(leaderboard, start=1):
                user = await self.bot.fetch_user(user_id)
                username = user.display_name if user else "Unknown User"
                embed.add_field(
                    name=f"{i}. {username}",
                    value=f"Count: {count}",
                    inline=False
                )

            await ctx.send(embed=embed)
        else:
            print("No leaderboard data available.")

async def setup(bot):
    await bot.add_cog(NoobWatchCommand(bot))
