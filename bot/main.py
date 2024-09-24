import discord
from discord.ext import commands, tasks
import aiohttp
import time
import json
import os

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
cache_duration = config['cache_duration']
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

    await load_cogs(bot, config=config, cache=cache, cache_duration=cache_duration, champions_data=champions_data,
                    latest_version=latest_version, shop_odds=shop_odds)

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

    print(f'Bot {bot.user} is ready.')

    await fetch_latest_version()
    await fetch_champions_data()


async def fetch_latest_version():
    global latest_version
    async with aiohttp.ClientSession() as session:
        async with session.get(versions_url) as response:
            if response.status == 200:
                versions = await response.json()
                if versions:
                    latest_version = versions[0]
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


# Function to load cogs
async def load_cogs(bot, config=None, cache=None, cache_duration=None, champions_data=None, latest_version=None,
                    shop_odds=None):
    cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')

    # Iterate over files in cogs directory
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            cog_name = f'cogs.{filename[:-3]}'

            try:
                if cog_name == 'cogs.malding_command':
                    await bot.load_extension(cog_name)
                    malding_cog = bot.get_cog('MaldingCommand')
                    malding_cog.cache = cache
                    malding_cog.cache_duration = cache_duration
                elif cog_name == 'cogs.roll_commands':
                    # Directly call setup with arguments instead of loading it through bot.load_extension
                    roll_cog = __import__('cogs.roll_commands', fromlist=['setup'])
                    await roll_cog.setup(bot, champions_data, latest_version, shop_odds)
                elif cog_name == 'cogs.message_responder':
                    await bot.load_extension(cog_name)
                    bot.get_cog('MessageResponder').config = config
                elif cog_name == 'cogs.stickers_emojis':
                    await bot.load_extension(cog_name)
                elif cog_name == 'cogs.streamer_commands':
                    await bot.load_extension(cog_name)
                else:
                    await bot.load_extension(cog_name)
            except Exception as e:
                print(f"Failed to load extension {cog_name}: {e}")

# Run the bot using your token
bot.run(botkey)
