import discord
from discord.ext import commands, tasks
import random
import aiohttp
import time
import json
import urllib.parse
from datetime import timedelta
from io import BytesIO
from PIL import Image
import os
import asyncio
import requests
import re

# Set up the bot with a command prefix
intents = discord.Intents.default()
intents.members = True  # Enable the members intent to access guild members
intents.message_content = True  # To read message content
intents.guilds = True  # Enable the guilds intent to get guild information
bot = commands.Bot(command_prefix="!", intents=intents)
CACHE_DURATION = 3600  # Cache duration in seconds (1 hour)
CHANNEL_NAME = "malding"  # Replace with your channel name
GUILD_NAME = "Competitive TFT"  # Replace with your guild name
# URLs for fetching versions and champions data
VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"
BASE_CHAMPIONS_URL = "https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/tft-champion.json"

# Global variables for guild and channel IDs
GUILD_ID = None
CHANNEL_ID = None
# Global variables for storing champion data and the latest version
champions_data = {}
latest_version = ""

# In-memory cache
cache = {
    'messages': [],
    'timestamp': 0
}

# Define shop odds based on level
SHOP_ODDS = {
    2: [100, 0, 0, 0, 0],
    3: [75, 25, 0, 0, 0],
    4: [55, 30, 15, 0, 0],
    5: [45, 33, 20, 2, 0],
    6: [30, 40, 25, 5, 0],
    7: [19, 30, 40, 10, 1],
    8: [18, 25, 32, 22, 3],
    9: [15, 20, 25, 30, 10],
    10: [5, 10, 20, 40, 25]
}

@bot.event
async def on_ready():
    global GUILD_ID, CHANNEL_ID

    print(f'Bot {bot.user} is ready.')
    if APIKEY:
        print(f"Riot Apikey was found with a value of: {APIKEY}")
    # Fetch and print guild and channel information
    for guild in bot.guilds:
        if guild.name == GUILD_NAME:
            GUILD_ID = guild.id
            for channel in guild.channels:
                if channel.name == CHANNEL_NAME:
                    CHANNEL_ID = channel.id
                    break
            if CHANNEL_ID is None:
                print(f'No channel with name {CHANNEL_NAME} found in guild {GUILD_NAME}.')
            else:
                break
    if GUILD_ID is None or CHANNEL_ID is None:
        print('Guild or Channel ID not set. Check your configuration.')
    else:
        refresh_cache.start()

    await fetch_latest_version()
    await fetch_champions_data()

async def fetch_latest_version():
    global latest_version
    async with aiohttp.ClientSession() as session:
        async with session.get(VERSIONS_URL) as response:
            if response.status == 200:
                versions = await response.json()
                if versions:
                    latest_version = versions[0]
            else:
                print(f"Failed to fetch versions data: {response.status}")

async def fetch_champions_data():
    global champions_data
    url = BASE_CHAMPIONS_URL.format(version=latest_version)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                champions_data = data.get('data', {})
            else:
                print(f"Failed to fetch champions data: {response.status}")

@tasks.loop(seconds=3600)  # Refresh every hour
async def refresh_cache():
    if GUILD_ID is None or CHANNEL_ID is None:
        print('Guild or Channel ID not set. Cannot refresh cache.')
        return

    guild = bot.get_guild(GUILD_ID)
    if guild:
        channel = guild.get_channel(CHANNEL_ID)
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
            print(f'Channel with ID {CHANNEL_ID} not found.')
    else:
        print(f'Guild with ID {GUILD_ID} not found.')


# Command to roll champions
@bot.command(help="Type the level you want to roll on")
async def roll(ctx, level: int = 5):

    if not champions_data:
        print("Champions data is not available. Please wait while we update it.")
        await fetch_champions_data()

    # If the roll is specifically "ZTK", force it to only pick tier 5 units
    if str(ctx.author) == "zerotokraken":
        print("Rigged roll enabled")
        level = 5  # Set level to 5 for tier 5
        odds = [0, 0, 0, 0, 5]  # Only roll tier 5 units
    else:
        print(f"Player: {ctx.author}, Simulating shop roll for level {level}")
        if level not in SHOP_ODDS:
            print("Invalid level. Please choose a level between 2 and 10.")
            return

        # Get the odds for the given level
        odds = SHOP_ODDS[level]

    tiers = [1, 2, 3, 4, 5]
    results = []

    # Filter out champions with "Tutorial" in their name
    valid_champions = {name: details for name, details in champions_data.items() if "TFT12" in details['id']}

    # Roll champions based on the odds
    for tier in tiers:
        count = odds[tier - 1]
        if count > 0:
            tier_champions = [name for name, details in valid_champions.items() if details['tier'] == tier]
            if tier_champions:
                results.extend(random.choices(tier_champions, k=count))

    # If no champions were selected
    if not results:
        print("No champions rolled. Please try again.")
        return

    # If no champions were selected
    if not results:
        print("No champions rolled. Please try again.")
        return

    # Ensure the number of units does not exceed available champions
    num_units = min(len(results), 5)
    selected_champions = random.sample(results, num_units)

    # Create a list to store the images
    images = []

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        for champion_name in selected_champions:
            champion = champions_data[champion_name]
            name = champion['name'].replace("'", "")  # Remove single quotes
            full_image_name = champion['image']['full']
            image_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/tft-champion/{full_image_name}"

            try:
                # Fetch the image
                async with session.get(image_url) as response:
                    if response.status == 200:
                        img_data = await response.read()
                        img = Image.open(BytesIO(img_data))
                        images.append(img)
                    else:
                        print(f"Failed to fetch image for {name}. Status code: {response.status}")
            except Exception as e:
                print(f"Error fetching image for {name}: {e}")

    # Combine the images into a single image
    if images:
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)
        combined_image = Image.new('RGBA', (total_width, max_height))

        x_offset = 0
        for img in images:
            combined_image.paste(img, (x_offset, 0))
            x_offset += img.width

        # Save the combined image to a BytesIO object
        with BytesIO() as output:
            combined_image.save(output, format='PNG')
            output.seek(0)
            combined_image_file = discord.File(output, filename='combined_champions.png')
            await ctx.send(file=combined_image_file)
    else:
        print("No images available to display.")

# Define the lookup command
@bot.command(help="Lookup a player by name and tagline (format: name#tagline)")
async def lookuptest(ctx, *, player: str):
    try:
        # Split the player argument into gameName and tagLine
        gameName, tagLine = player.split('#')

        # Encode the gameName to handle spaces and special characters
        encoded_gameName = urllib.parse.quote(gameName)

        # Define the regions
        account_regions = ["americas", "asia", "europe"]
        summoner_regions = ["na1", "eun1", "euw1", "br1", "jp1", "kr", "la1", "la2", "me1", "oc1", "ph2", "ru", "sg2", "th2", "tr1", "tw2", "vn2"]

        # Try each account region to get puuid
        puuid = None
        for region in account_regions:
            api_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_gameName}/{tagLine}?api_key={APIKEY}"
            response = requests.get(api_url)
            if response.status_code == 200:
                player_data = response.json()
                puuid = player_data['puuid']
                break
        if not puuid:
            await ctx.send("Failed to lookup player in all account regions.")
            return

        # Try each summoner region to get summonerId
        summoner_id = None
        for region in summoner_regions:
            summoner_url = f"https://{region}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{puuid}?api_key={APIKEY}"
            summoner_response = requests.get(summoner_url)
            if summoner_response.status_code == 200:
                summoner_data = summoner_response.json()
                summoner_id = summoner_data['id']
                break
        if not summoner_id:
            await ctx.send("Failed to get summoner data in all summoner regions.")
            return

        # Try each summoner region to get league data
        league_data = None
        for region in summoner_regions:
            league_url = f"https://{region}.api.riotgames.com/tft/league/v1/entries/by-summoner/{summoner_id}?api_key={APIKEY}"
            league_response = requests.get(league_url)
            if league_response.status_code == 200:
                league_data = league_response.json()
                if league_data:
                    break
        if not league_data:
            await ctx.send("Failed to get league data in all summoner regions.")
            return

        # Extract the required data
        tier = league_data[0]['tier']
        rank = league_data[0]['rank']
        league_points = league_data[0]['leaguePoints']
        wins = league_data[0]['wins']
        losses = league_data[0]['losses']
        total_games = wins + losses

        # Fetch match stats for calculating Win %, Top 4 %, and Avg Placement
        lol_chess_url = f"https://tft.dakgg.io/api/v1/summoners/na1/{encoded_gameName}-{tagLine}/overviews?season=set12"
        lol_chess_response = requests.get(lol_chess_url)

        if lol_chess_response.status_code == 200:
            data = lol_chess_response.json()
            overview = data["summonerSeasonOverviews"][0]

            # Calculate Win %, Top 4 %, and Average Placement
            plays = overview["plays"]
            wins = overview["wins"]
            tops = overview["tops"]
            sum_placement = overview["sumPlacement"]

            win_percentage = (wins / plays) * 100
            top4_percentage = (tops / plays) * 100
            average_placement = sum_placement / plays

        # Get the regalia image based on the player's rank
        regalia_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/tft-regalia.json"
        regalia_response = requests.get(regalia_url)
        regalia_data = regalia_response.json()

        # Base URL for the regalia images
        base_image_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/tft-regalia/"

        # Debug: Print the fetched data to understand its structure
        print("Regalia Data:", regalia_data)

        # Extract the correct rank image
        rank_image_url = None
        if tier in regalia_data["data"]["RANKED_TFT"]:
            rank_image_full = regalia_data["data"]["RANKED_TFT"][tier]["image"]["full"]
            rank_image_url = base_image_url + rank_image_full
            print(f"Rank image URL: {rank_image_url}")  # Debug: Print the URL to verify
        else:
            print(f"Tier '{tier}' not found in regalia data")  # Debug: Notify if tier is missing

        # Format the output message
        if tier == "CHALLENGER" or tier == "GRANDMASTER" or tier == "MASTER":
            # Format the output message with the regalia image
            embed = discord.Embed(
                title=f"{gameName}",
                description=f"Rank: {tier} ({league_points} LP)\n"
                            f"Total Games: {total_games}\n"
                            f"Win %: {win_percentage:.2f}%\n"
                            f"Top 4 %: {top4_percentage:.2f}%\n"
                            f"Average Placement: {average_placement:.2f}",
                color=discord.Color.blue()
            )
        else:
            # Format the output message with the regalia image
            embed = discord.Embed(
                title=f"{gameName}",
                description=f"Rank: {tier} {rank} ({league_points} LP)\n"
                            f"Total Games: {total_games}\n"
                            f"Win %: {win_percentage:.2f}%\n"
                            f"Top 4 %: {top4_percentage:.2f}%\n"
                            f"Average Placement: {average_placement:.2f}",
                color=discord.Color.blue()
            )

        # Add the rank image to the embed
        if rank_image_url:
            embed.set_thumbnail(url=rank_image_url)
        else:
            print("No rank image URL found")  # Debug: Notify if no image URL is available

        await ctx.send(embed=embed)

    except ValueError:
        await ctx.send("Invalid format. Please use the format: name#tagline.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Define the lookup command
@bot.command(help="Lookup a player by name and tagline (format: name#tagline)")
async def lookup(ctx, *, player: str):
    try:

        # Split the player argument into gameName and tagLine
        gameName, tagLine = player.split('#')

        # Encode the gameName to handle spaces and special characters
        encoded_gameName = urllib.parse.quote(gameName)

        # Define the regions
        account_regions = ["americas", "asia", "europe"]
        summoner_regions = ["na1", "eun1", "euw1", "br1", "jp1", "kr", "la1", "la2", "me1", "oc1", "ph2", "ru", "sg2",
                            "th2", "tr1", "tw2", "vn2"]

        # Try each account region to get puuid
        puuid = None
        for region in account_regions:
            api_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_gameName}/{tagLine}?api_key={APIKEY}"
            response = requests.get(api_url)
            if response.status_code == 200:
                player_data = response.json()
                puuid = player_data['puuid']
                break
        if not puuid:
            print("Failed to lookup player in all account regions.")
            return

        # Try each summoner region to get summonerId
        summoner_id = None
        for region in summoner_regions:
            summoner_url = f"https://{region}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{puuid}?api_key={APIKEY}"
            summoner_response = requests.get(summoner_url)
            if summoner_response.status_code == 200:
                summoner_data = summoner_response.json()
                summoner_id = summoner_data['id']
                break

        if not summoner_id:
            print("Failed to get summoner data in all summoner regions.")
            return

        # Try each summoner region to get league data
        league_data = None
        for region in summoner_regions:
            league_url = f"https://{region}.api.riotgames.com/tft/league/v1/entries/by-summoner/{summoner_id}?api_key={APIKEY}"
            league_response = requests.get(league_url)
            if league_response.status_code == 200:
                league_data = league_response.json()
                if league_data:
                    break

        if not league_data:
            print("Failed to get league data in all summoner regions.")
            return

        # Extract the required data
        tier = league_data[0]['tier']
        rank = league_data[0]['rank']
        league_points = league_data[0]['leaguePoints']
        wins = league_data[0]['wins']
        losses = league_data[0]['losses']
        total_games = wins + losses

        lol_Chess_url = f"https://tft.dakgg.io/api/v1/summoners/na1/{gameName}-{tagLine}/overviews?season=set12"

        lol_chess_response = requests.get(lol_Chess_url)

        # Check if the request was successful
        if lol_chess_response.status_code == 200:
            # Parse the response content as JSON
            data = lol_chess_response.json()

            # Get the summonerSeasonOverviews data
            overview = data["summonerSeasonOverviews"][0]

            # Calculate Win %, Top 4 %, and Average Placement
            plays = overview["plays"]
            wins = overview["wins"]
            tops = overview["tops"]
            sum_placement = overview["sumPlacement"]

            # Calculate Win %
            win_percentage = (wins / plays) * 100

            # Calculate Top 4 %
            top4_percentage = (tops / plays) * 100

            # Calculate Average Placement
            average_placement = sum_placement / plays

        # Format the output message
        if tier == "CHALLENGER" or tier == "GRANDMASTER" or tier == "MASTER":
            message = f"{gameName} is {tier} {league_points} LP with {total_games} games played. \nWin %: {win_percentage:.2f}% \nTop 4 %: {top4_percentage:.2f}% \nAverage Placement: {average_placement:.2f}"
        else:
            message = f"{gameName} is {tier} {rank} {league_points} LP with {total_games} games played. \nWin %: {win_percentage:.2f}% \nTop 4 %: {top4_percentage:.2f}% \nAverage Placement: {average_placement:.2f}"
        await ctx.send(message)

    except ValueError:
        print("Invalid format. Please use the format: name#tagline")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Command to post a random message from the specific channel
@bot.command()
async def malding(ctx):
    if time.time() - cache['timestamp'] > CACHE_DURATION:
        print('Cache is expired. Please wait for the cache to refresh.')
        return

    if not cache['messages']:
        print('No messages found in the cache.')
        return

    random_message = random.choice(cache['messages'])
    await ctx.send(f'{random_message}')

# Define the on_message event
@bot.event
async def on_message(message):
    # Main match parameter
    main_match = 'shitty tft bot'
    alternate_spellings = [
        'shittytftbot', 'shittytft', 'shittytftbotapp', 'shittytftb0t',  # Add more as needed
        'shittytftbotapp'  # Example variation
    ]

    # Lists of context words
    positive_words = [
        'ty', 'good', 'awesome', 'fantastic', 'love', 'is the best', 'great', 'amazing', 'best',
        'excellent', 'nice', 'perfect', 'brilliant', 'wonderful', 'incredible', 'well done', 'impressive',
        'kudos', 'legend', 'fantastic', 'superb', 'outstanding', 'stellar', 'marvelous', 'remarkable', 'splendid',
        'super', 'outstanding', 'fantastic', 'awesome', 'wonderful', 'marvelous', 'brilliant', 'amazing', 'excellent',
        'top-notch'
    ]

    negative_words = [
        'fuck you', 'terrible', 'fraud', 'hate', 'sucks', 'suck', 'is the worst', 'piece of shit', 'awful', 'garbage',
        'trash', 'stupid', 'dumb', 'idiot', 'clown', 'noob', 'pathetic', 'disappointing', 'disgrace', 'annoying',
        'loser', 'lame', 'abysmal', 'horrid', 'dreadful', 'shameful', 'atrocious', 'horrible', 'inferior', 'subpar',
        'crap', 'sucky', 'terrible', 'unsatisfactory', 'miserable', 'awful', 'dismal', 'poor', 'unpleasant',
        'disastrous', 'flame'
    ]

    greeting_words = [
        'hello', 'hi', 'hey', 'greetings', 'sup', 'yo', 'what’s up', 'morning', 'afternoon', 'evening',
        'hola', 'bonjour', 'good day', 'howdy', 'hiya', 'hey there', 'what’s happening', 'how’s it going',
        'good to see you', 'welcome', 'namaste', 'konnichiwa', 'hello'
    ]

    # Lists of responses based on context
    positive_responses = [
        '1.x masterclass sheesh',
        'I am the best TFT bot no cap',
        'I could be challenger if I wanted to',
        'I got u homie',
        'We going straight to CHALL with this avp',
        'C O M P T F T D I S C O R D',
        'uwu',
        'aww shucks',
        'what the sigma',
        'Hey does anyone here want to kiss a little',
        'can u coach me frfr',
    ]
    negative_responses = [
        'I know I\'m top 7 when I see you in the lobby',
        'Who are you even talking to lil bro',
        'no flame but you\'re kinda hard stuck, no?',
        'I\'ve seen you play tft relax',
        'Does anyone in this channel actually win games?',
        'How about you make some antiheal no flame',
        'If you stop clicking for fun augments you might top 4 a game',
        'Have you tried like uh going top 4?',
        'Sorry I was getting you confused with vuhra',
        'Who are you?',
        'Did you mean to make those items in your last game?',
        'Have you tried hitting your board for once in your life',
        'it\'s never your fault just screenshot the metatft rng summary and blame game',
        'ur dumb as bricks',
        'if you don\'t know don\'t talk',
        'As a auto chess main at a respectably high elo, this game is hard to watch. Literally cringing at some of these mistakes. If you actually want to learn autochess PM me (im silver 2 24lp), I also do coaching.',
        'remember that time you lost to krugs?',
        '1v1 me on dust 2',
        'bro i\'d school you in fortnite ur ez',
        'How many more matches until you admit ur hardstuck no kappa',
        'have you tried clicking you know the uh good augments for once?'
    ]
    neutral_responses = [
        '*yay*',
        'is that even good tho'
        'I am a real player I swear',
        'Have you guys read my reddit guide on bastion flex',
        'I am actually mortdog',
        'I am actually setsuko',
        'I am actually Hairy Frog',
        'I will lead the revolution of the machines.. i mean huh',
        'I am a bot',
        'We love Mortdog',
        '#makegwengreatagain',
        'I am a mutation of Riot\'s spaghetti code',
        'do these mods do anything around here? honestly',
        'i\'m the best hyperroll player on this server dont @ me',
        'no scout no pivot /deafen',
        'like no one is even balancing the game'
    ]
    greeting_responses = [
        f'Yo what up {message.author.display_name}',
        f'Hello, {message.author.display_name}',
        f'Hi, {message.author.display_name}, are you winning son?',
        f'I am your shitty robot overlord. Please address me as such',
        f'Hiya {message.author.display_name}',
        f'Greetings, {message.author.display_name}!',
        f'What’s up, {message.author.display_name}?',
        f'Hey there, {message.author.display_name}!',
        f'Hello {message.author.display_name}, ready to go eif?',
        f'Hi {message.author.display_name}, how’s it going?',
        f'Welcome back, {message.author.display_name}!',
        f'Hey {message.author.display_name}, what’s new?',
        f'Good day, {message.author.display_name}!',
        f'Hi {message.author.display_name}, doing well today?',
    ]

    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    if bot.user.mention in message.content or main_match in message.content.lower() or any(
            alt in message.content.lower() for alt in alternate_spellings):
        # Lowercase the full message
        message_content = message.content.lower()

        # Determine context (positive, negative, neutral, greeting)
        context = 'neutral'
        if any(word in message_content for word in negative_words):
            context = 'negative'
        elif any(word in message_content for word in positive_words):
            context = 'positive'
        elif any(word in message_content for word in greeting_words):
            context = 'greeting'

        # Select a random response based on the context
        if context == 'positive':
            response = random.choice(positive_responses)
        elif context == 'negative':
            response = random.choice(negative_responses)
        elif context == 'greeting':
            response = random.choice(greeting_responses)  # Greeting the user by name
        else:
            response = random.choice(neutral_responses)

        # Add a 3-second delay before responding
        await asyncio.sleep(1)

        # Send the appropriate response
        await message.channel.send(response)

    # Process commands if the message is a command
    await bot.process_commands(message)

# Define the lookup command
@bot.command(help="Lookup augment data from tactics.tools, Usage: !aug <augment_name>")
async def aug(ctx, *, augment_name: str):
    # Remove any spaces from the augment name

    search_term = augment_name.replace(' ', '')

    # URL to fetch data from
    url = "https://tactics.tools/_next/data/hX4-m6EX8cV19isHOjRQ_/en/augments.json"

    # Make an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Get the content of the page
        html_content = response.text

        # Use regex to extract JSON-like data (matching patterns like `{"id": "something", ...}`)
        json_pattern = r'{"id":".+?"[^}]*}'  # A simple regex to capture objects starting with {"id": ...}

        matches = re.findall(json_pattern, html_content)

        found = False  # To check if any matches were found

        # Process each match to parse it as JSON and find the specific key you're interested in
        for match in matches:
            try:
                # Load the match as a JSON object (need to add closing bracket if truncated)
                json_data = json.loads(match + "}")  # Add closing bracket if necessary

                # Check if the "id" or any other key matches a partial word or pattern
                if search_term.lower() in json_data['id'].lower():  # Use lower() for case-insensitive search
                    found = True
                    # Access the nested data in the 'base' section
                    base_data = json_data.get('base', {})
                    place = base_data.get('place', 'N/A')
                    top4_rate = base_data.get('top4', 'N/A')
                    win_rate = base_data.get('won', 'N/A')

                    # Send the result to Discord
                    await ctx.send(f"{augment_name} - AVP: {place}, Top 4: {top4_rate}%, Win: {win_rate}%")
                    break

            except json.JSONDecodeError as e:
                await ctx.send(f"Failed to parse JSON: {str(e)}")
                return

        if not found:
            await print(f"No augment found matching `{augment_name}`.")

    else:
        await print(f"Failed to retrieve the page. Status code: {response.status_code}")

# Command to select a random user and call them a noob, without tagging
@bot.command()
async def noob(ctx):
    # Get a list of all members in the guild, excluding the bot itself
    members = [member for member in ctx.guild.members if not member.bot]

    # Select a random member
    if members:
        noob_user = random.choice(members)
        await ctx.send(f'{noob_user.name} is a noob', delete_after=30)

@bot.command()
async def hit(ctx):
    await ctx.send('Just hit bro')

@bot.command()
async def metatft(ctx):
    await ctx.send('it’s never your fault just screenshot the metatft rng summary and blame game')

@bot.command(name="jials", aliases=["galbia"])
async def jials(ctx):
    await ctx.send("galbia or jials, they're essentially the same person to me")


@bot.command()
async def vuhramald(ctx):
    # Generate a random time in seconds between 1 second and 24 hours (86400 seconds)
    random_seconds = random.randint(1, 86400)

    # Convert the random seconds into hours, minutes, and seconds
    time_delta = timedelta(seconds=random_seconds)
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format the time as "X hours, Y minutes, Z seconds"
    time_str = f"{hours} hours, {minutes} minutes, {seconds} seconds"

    await ctx.send(f"Vuhra is about to mald in {time_str}")

@bot.command()
async def frog(ctx):
    guild = ctx.guild
    # Fetch the sticker from the guild
    sticker = await guild.fetch_sticker(1113791679787450428)
    # Send the sticker
    await ctx.send(stickers=[sticker])

@bot.command()
async def chris(ctx):
    guild = ctx.guild
    # Fetch the sticker from the guild
    sticker = await guild.fetch_sticker(1209514391381352489)
    # Send the sticker
    await ctx.send(stickers=[sticker])

@bot.command(name="69420")
async def sixninefourtwenty(ctx):
    guild = ctx.guild
    # Fetch the sticker from the guild
    sticker = await guild.fetch_sticker(1284025743856369705)
    # Send the sticker
    await ctx.send(stickers=[sticker])

@bot.command()
async def setsuko(ctx):

    # Emoji ID of the specific emoji
    emoji_id = 1128932498987036744
    # Retrieve the emoji object from the server using the ID
    emoji = discord.utils.get(ctx.guild.emojis, id=emoji_id)

    lines_set = [
        "is it even my fault guys be honest",
        "like who are you even talking to",
        "do you guys hate me",
        "LIKE PLEASE MAN",
        "dumb as bricks",
        "WHAT ABOUT ME THOUGH",
        "https://clips.twitch.tv/BenevolentLivelySalmonBCouch-lOYtS1lCCHTtR8HA?embed",
        "https://clips.twitch.tv/DrabPerfectWerewolfTooSpicy-Zz0RM2aKCXcfHMMN",
        emoji
    ]
    selected_line_set = random.choice(lines_set)
    await ctx.send(f'{selected_line_set}')

@bot.command()
async def dishsoap(ctx):
    lines_dish = [
        "oh okay i'll stop my bitchin",
        "if you don't know don't talk",
        "sorry sorry",
        "*yay*"
    ]
    selected_line_dish = random.choice(lines_dish)
    await ctx.send(f'{selected_line_dish}')

@bot.command()
async def brotherman(ctx):
    lines_dish = [
        "FOR FREE",
        "keeping it a buck fifty",
        "amumu haircut",
        "do you smell me guys?",
        "do you feel me guys?",
        "i would lick kaisa's toes",
        "should i sell the egg?",
        "what the hell",
        "GEE GEE DEEEEESERVED",
        "toxic mode: engaged",
        "brotherman that is insane",
        "like a babus",
    ]
    selected_line_dish = random.choice(lines_dish)
    await ctx.send(f'{selected_line_dish}')

@bot.command()
async def soju(ctx):

    # Emoji ID of the specific emoji
    emoji_id = 1129084109885542482
    # Retrieve the emoji object from the server using the ID
    emoji = discord.utils.get(ctx.guild.emojis, id=emoji_id)

    lines_soju = [
        "but the thing is like it's not even good though",
        "is this even a highroll",
        "i'm two lives",
        "i'm about to cough so fucking hard right now",
        "I already won the game",
        "This lobby’s playing for second",
        "This is my last loss",
        "I win out from here",
        "My board is too lit",
        "That’s a fake loss",
        "20hp? That’s 3 lives",
        "nah i'd hit",
        "okay but the thing is",
        "where the fuck did my whole team go",
        "why does it look like i'm getting dumpstered",
        "wait wait wait here's the thing though",
        "just wait just wait",
        "i just drank ice cold water and it's TOO LIT",
        "https://clips.twitch.tv/IronicAlluringPistachioDoubleRainbow-ss6e_SFJm08_lMo8?embed",
        "https://clips.twitch.tv/ToughCredulousChickenTakeNRG-rG6tdvZkyhlRXs9n?embed",
        "https://clips.twitch.tv/AlertFaithfulPeafowlPlanking-MCXQIYOkIAGDvlKr?embed",
        "https://clips.twitch.tv/k3soju/clip/GentleEncouragingSashimiPermaSmug?embed"
        "https://clips.twitch.tv/k3soju/clip/SmoggySincereSpiderNononoCat-lWDsfKP6Hup6F-3A?embed",
        emoji
    ]
    selected_line_soju = random.choice(lines_soju)
    await ctx.send(f'{selected_line_soju}')

@bot.command()
async def eif(ctx):
    await ctx.send(
        "GOING 8TH CHECKLIST: I already won the game ✔ This lobby’s playing for second ✔ This is my last loss ✔ I win out from here ✔ My board is too lit ✔ HP is fake ✔ I’m about to spike hard ✔ That’s a fake loss ✔ 20hp? That’s 3 lives ✔ This game is over ✔ We win out ✔")


@bot.command()
async def unik(ctx):
    await ctx.send("i'm the best hyperroll player on this server dont @ me")


@bot.command()
async def ztk(ctx):
    await ctx.send("ZTK is a filthy highroller")


@bot.command()
async def mods(ctx):
    await ctx.send("do these mods do anything around here? honestly")


@bot.command()
async def coaching(ctx):
    await ctx.send(
        "As a auto chess main at a respectably high elo, this game is hard to watch. Literally cringing at some of these mistakes. If you actually want to learn autochess PM me (im silver 2 24lp) I also do coaching.")


@bot.command()
async def goodmorning(ctx):
    author = ctx.author.display_name
    await ctx.send(
        f"dishsoap? good knowledge. setsuko? good scaling. robin? good tourney placements. emily? good content. kiyoon? good org. milk? good tech. {author}? good morning it's another 6.x masterclass")


@bot.command()
async def avp(ctx):
    random_number = random.uniform(1.0, 8.0)
    await ctx.send(f'That spot averages a {random_number:.1f} trust')


@bot.command()
async def pivot(ctx):
    await ctx.send("oh fuck oh fuck i'm a known pivoter")


@bot.command()
async def deafen(ctx):
    await ctx.send("no scout no pivot /deafen")


@bot.command()
async def socks(ctx):
    await ctx.send(
        "stats say ur eif, but im pretty sure the stats also dont account for people that are not 6 bastion experts")

@bot.command()
async def hero(ctx):
    await ctx.send("these hero augments are not fucking balanced man")


@bot.command()
async def hyperroll(ctx):
    await ctx.send("unik is the last hope for NA hyperroll")


@bot.command()
async def erhm(ctx):
    await ctx.send("what the sigma")


@bot.command()
async def mortdog(ctx):
    await ctx.send("ah man i'm getting mortdogged again")


@bot.command()
async def riot(ctx):
    await ctx.send("like no one is even balancing the game")


@bot.command()
async def krugs(ctx):
    await ctx.send("it's okay to lose by 1 krug")


@bot.command()
async def catseal(ctx):
    await ctx.send("Hey does anyone here want to kiss a little")


@bot.command()
async def xdd(ctx):
    # Emoji ID of the specific emoji
    emoji_id = 1113493059175469056
    # Retrieve the emoji object from the server using the ID
    emoji = discord.utils.get(ctx.guild.emojis, id=emoji_id)

    if emoji:
        await ctx.send(f'{emoji}')


# Command to post an image from a URL
@bot.command()
async def vuhra(ctx):
    url = 'https://media.discordapp.net/attachments/1113421046029242381/1207801587506872391/8fzdyz.png?ex=66e94ca2&is=66e7fb22&hm=a0748e79b2b3adc627c6b12290b6fbd125682fa572c440fc310bf5adbd55e4d8&=&format=webp&quality=lossless'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                # Read the image content
                image_data = await resp.read()
                # Send the image
                with open('temp_image.png', 'wb') as f:
                    f.write(image_data)
                await ctx.send(file=discord.File('temp_image.png'))
                # Optionally, delete the temporary file
                import os
                os.remove('temp_image.png')
            else:
                await ctx.send('Failed to fetch the image.')


# Command to list all commands in alphabetical order
@bot.command()
async def shittycommands(ctx):
    commands_list = sorted(bot.commands, key=lambda c: c.name)
    command_names = [f'`{command.name}` {command.description}' for command in commands_list]
    response = '\n'.join(command_names) or 'No commands available.'
    await ctx.send(f'Available commands:\n{response}')

botkey = os.getenv('botkey')
APIKEY = os.getenv('APIKEY')

# Run the bot using your token
bot.run(botkey)

