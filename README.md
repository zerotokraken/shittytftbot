# shittytftbot

ShittyTFTBot is a Discord bot designed for managing and interacting with players and data related to Teamfight Tactics (TFT). It supports various commands to look up player information and provide updates based on Riot Games' API.

# Hosting

The bot is deployed via pipeline from Github to Heroku. When commits are made the updates are then pushed to the hosted instance and a rolling update will be made.

# Features

Database Integration: Retrieves messages from the three most popular discord channels once an hour and adds them to the database.

Suggestion: Records to a database table when the command is used. Example: !suggest myideahere

Lookup: Retrieve player data by name and tagline when '!lookup gameName#tagline' is used.

Cutoffs: Retrieves from Riot API the cutoff League Points number for a particular region depending on how many spots are available in that region for Challenger & Grandmaster.

Malding/Fault/Psyop: Retrieves a random message fromt he database and outputs it when the command is used. This database table updates hourly.

Augment Lookup: Pulls Augment data directly from tactics.tools when '!aug AugmentName' is used. Image is pull from Riot API.

Roll Shop: Simulates rolling Teamfight Tactic's shops based on the requested level and outputs a rectangle shop sized image with your output units. Command is '!roll#'. The # is the level you wish to roll at.

On-Message: Bot responses with a temperament system based on the contextual words. This is a very basic 'personality' attempt and will likely be expanded upon further. Activation involves typing the bot's name or tagging it.

Misc: Any one line jokes or small functions will be housed in here. Check the misc file to read through these.

Streamer: These commands will output a line said by the streamer, an emoji/sticker or a clip of that streamer. Example: '!soju'

Stickers & Emojis: Outputs a specific sticker or emoji. Example: '!frog'

# Prerequisites

Python: Version 3.12.0 or higher.

Discord.py: The bot uses py-cord for Discord API interactions.

Heroku: For app deployment.

Check requirements modules for specific modules.

# Contributing
Contributions are welcome! Please open an issue or submit a pull request if you have improvements or fixes.

# License
This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the LICENSE file for details.

# Contact
For any questions or support, please contact ztk.cmg@gmail.com