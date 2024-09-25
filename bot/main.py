import discord
from discord.ext import commands, tasks
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
bot = commands.Bot(command_prefix="!", intents=intents)

botkey = os.getenv('botkey')
APIKEY = os.getenv('APIKEY')

# Load configuration from config.json
config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Load static data from config
guild_name = config['guild_name']
versions_url = config['versions_url']
base_champions_url = config['base_champions_url']
shop_odds = config['shop_odds']

guild_id = None
channel_id = None
latest_version = None

champions_data = {}

# In-memory cache
cache = {
    'messages': [],
    'timestamp': 0
}


@bot.event
async def on_ready():
    global guild_id, channel_id

    if APIKEY:
        print(f"Riot API key was found with a value of: {APIKEY}")

    # Fetch and print guild and channel information
    for guild in bot.guilds:
        if guild.name == guild_name:
            guild_id = guild.id
            for channel in guild.channels:
                if channel.name == "malding":
                    channel_id = channel.id
                    break
            if channel_id is None:
                print(f'No channel with name malding found in guild {guild_name}.')
            else:
                break
    if guild_id is None or channel_id is None:
        print('Guild or Channel ID not set. Check your configuration.')
    else:
        refresh_cache.start()

    await fetch_latest_version()
    await fetch_champions_data()

    await load_cogs(bot, config=config, cache=cache, cache_duration=3600, champions_data=champions_data,
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


@tasks.loop(seconds=3600)  # Refresh every hour
async def refresh_cache():
    if guild_id is None or channel_id is None:
        print('Guild or Channel ID not set. Cannot refresh cache.')
        return

    guild = bot.get_guild(guild_id)
    if guild:
        channel = guild.get_channel(channel_id)
        if channel:
            messages = []
            try:
                async for message in channel.history(limit=1000):
                    messages.append(message.content)
                cache['messages'] = messages
                cache['timestamp'] = time.time()
                print('Cache refreshed.')
            except discord.Forbidden:
                print('Bot does not have permission to read messages in this channel.')
            except discord.HTTPException as e:
                print(f'Failed to fetch messages: {e}')
        else:
            print(f'Channel with ID {channel} not found.')
    else:
        print(f'Guild with ID {guild_id} not found.')


async def load_cogs(bot, config=None, cache=None, cache_duration=None, champions_data=None, latest_version=None, shop_odds=None):
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
                    if cog_name == 'cogs.malding':
                        await cog_module.setup(bot, cache, cache_duration)
                    elif cog_name == 'cogs.roll':
                        await cog_module.setup(bot, champions_data, latest_version, shop_odds)
                    elif cog_name == 'cogs.aug':
                        await cog_module.setup(bot, latest_version)
                    elif cog_name == 'cogs.lookup':
                        await cog_module.setup(bot, APIKEY)
                    else:
                        await cog_module.setup(bot)
                else:
                    await bot.load_extension(cog_name)

                print(f"Successfully loaded {cog_name}")
            except Exception as e:
                print(f"Failed to load extension {cog_name}: {e}")



# Run the bot using your token
bot.run(botkey)
