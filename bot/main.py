import discord
from discord.ext import commands, tasks
import psycopg2
import asyncio
import aiohttp
import time
import json
import os
import importlib

# Set up the bot with a command prefix
intents = discord.Intents.default()
intents.members = True  # Enable the members intent to access guild members
intents.message_content = True  # To read message content
intents.guilds = True  # Enable the guilds intent to get guild information
bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

botkey = os.getenv('botkey')
apikey = os.getenv('apikey')

# Load configuration from config.json
config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Load static data from config
versions_url = config['versions_url']
base_champions_url = config['base_champions_url']
shop_odds = config['shop_odds']
set_number = config['set']
latest_version = None
champions_data = {}

def connect_to_db():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    try:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# Check if a message already exists in a table
def message_exists(cursor, table_name, message_id):
    query = f"SELECT 1 FROM {table_name} WHERE message_id = %s"
    cursor.execute(query, (message_id,))
    return cursor.fetchone() is not None

# Insert a message into the appropriate table
def insert_message_to_db(connection, cursor, table_name, message):
    try:
        query = f"""
        INSERT INTO {table_name} (message_id, author_id, author_name, content, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (message.id, message.author.id, str(message.author), message.content, message.created_at))
        connection.commit()
        print(f"Inserted message {message.id} by {message.author} into {table_name}.")
    except Exception as e:
        connection.rollback()  # Rollback on failure
        print(f"Error inserting message: {e}")

# Fetch new messages from a channel and store them in the appropriate table
async def fetch_new_messages(channel, table_name, connection, cursor):
    print(f"Fetching messages from channel {channel.name}...")

    async for message in channel.history(limit=None):
        if message_exists(cursor, table_name, message.id):
            print(f"Message {message.id} already in {table_name}, stopping.")
            break
        insert_message_to_db(connection, cursor, table_name, message)

# Task loop to fetch messages every hour
@tasks.loop(hours=1)
async def fetch_messages_every_hour(client):
    db_connection = connect_to_db()
    if db_connection:
        cursor = db_connection.cursor()

        general_channel = client.get_channel(1113421046029242381)  # Replace with actual channel ID
        advice_channel = client.get_channel(1113429363950616586)   # Replace with actual channel ID
        malding_channel = client.get_channel(1113495131841110126)  # Replace with actual channel ID

        if general_channel:
            await fetch_new_messages(general_channel, "general_messages", db_connection, cursor)
        if advice_channel:
            await fetch_new_messages(advice_channel, "advice_messages", db_connection, cursor)
        if malding_channel:
            await fetch_new_messages(malding_channel, "malding_messages", db_connection, cursor)

        cursor.close()
        db_connection.close()

@bot.event
async def on_ready():

    if apikey:
        print(f"Riot API key was found with a value of: {apikey}")

    fetch_messages_every_hour.start(bot)

    await fetch_latest_version()
    await fetch_champions_data()

    await load_cogs(bot, config=config, champions_data=champions_data,
                    latest_version=latest_version, shop_odds=shop_odds)

    print(f'Bot {bot.user} is ready.')


async def fetch_latest_version():
    global latest_version
    async with aiohttp.ClientSession() as session:
        async with session.get(versions_url) as response:
            if response.status == 200:
                versions = await response.json()
                if versions:
                    latest_version = versions[0]
                    print(f"Current TFT Patch: {latest_version}")
            else:
                print(f"Failed to fetch versions data: {response.status}")


async def fetch_champions_data():
    global champions_data
    url = base_champions_url.format(version=latest_version)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                champions_data = data.get('data', {})
            else:
                print(f"Failed to fetch champions data: {response.status}")


async def load_cogs(bot, config=None, champions_data=None, latest_version=None, shop_odds=None):
    cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')

    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            cog_name = f'cogs.{filename[:-3]}'

            if cog_name == 'cogs.init':
                continue

            print(f"Loading {cog_name}...")

            # Check if the cog is already loaded
            if cog_name in bot.cogs:
                print(f"{cog_name} is already loaded.")
                continue

            try:
                cog_module = importlib.import_module(cog_name)

                if hasattr(cog_module, 'setup'):
                    if cog_name == 'cogs.roll':
                        await cog_module.setup(bot, champions_data, latest_version, shop_odds, set_number)
                    elif cog_name == 'cogs.last':
                        await cog_module.setup(bot, apikey, latest_version, set_number)
                    elif cog_name == 'cogs.stats':
                        await cog_module.setup(bot, apikey, latest_version, set_number)
                    elif cog_name == 'cogs.trainer':
                        await cog_module.setup(bot, apikey, latest_version)
                    elif cog_name == 'cogs.top':
                        await cog_module.setup(bot, apikey)
                    elif cog_name == 'cogs.leaderboard':
                        await cog_module.setup(bot, apikey, set_number)                        
                    elif cog_name == 'cogs.cutoffs':
                        await cog_module.setup(bot, apikey, latest_version)
                    elif cog_name == 'cogs.lookup':
                        await cog_module.setup(bot, set_number)
                    else:
                        await cog_module.setup(bot)
                else:
                    await bot.load_extension(cog_name)

                print(f"Successfully loaded {cog_name}")
            except Exception as e:
                print(f"Failed to load extension {cog_name}: {e}")



# Run the bot using your token
bot.run(botkey)
