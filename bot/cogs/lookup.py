import discord
from discord.ext import commands
import aiohttp
import json

class Lookup(commands.Cog):
    # Special cases for unit names and items
    unit_special_cases = {
        "mundo": "DrMundo",
        "drmundo": "DrMundo",
        "leesin": "LeeSin",
        "twistedfate": "TwistedFate",
        "kogmaw": "KogMaw",
        "reksai": "RekSai",
        "masteryi": "MasterYi"
    }

    # Special cases for items
    item_special_cases = {
        "visage": "Redemption",
        "spirit": "Redemption",
        "spirit visage": "Redemption",
        "rageblade": "GuinsoosRageblade",
        "grb": "GuinsoosRageblade",
        "gs": "GiantSlayer",
        "giantslayer": "GiantSlayer",
        "ie": "InfinityEdge",
        "bt": "BloodthirsterShadow",
        "qss": "Quicksilver",
        "hoj": "HandOfJustice",
        "db": "Deathblade",
        "jg": "JeweledGauntlet",
        "jeweled": "JeweledGauntlet",
        "gauntlet": "JeweledGauntlet",
        "rfc": "Artifact_RapidFirecannon",
        "rapidfirecannon": "Artifact_RapidFirecannon",
        "rapid fire cannon": "Artifact_RapidFirecannon",
        "titans": "TitansResolve",
        "warmogs": "WarmogsArmor",
        "dcap": "RabadonsDeathcap",
        "rabadons": "RabadonsDeathcap",
        "deathcap": "RabadonsDeathcap",
        "eon": "GuardianAngel",
        "seekers": "Artifact_SeekersArmguard",
        "seekersarmguard": "Artifact_SeekersArmguard",
        "edge of night": "GuardianAngel",
        "ga": "GuardianAngel",
        "redbuff": "RapidFirecannon",
        "red buff": "RapidFirecannon",
        "manazane": "4OrnnMuramana",
        "manamazane": "4OrnnMuramana",
        "muramana": "4OrnnMuramana",
        "masamune": "4OrnnMuramana",
        "strikers": "PowerGauntlet",
        "flail": "PowerGauntlet",
        "striker's flail": "PowerGauntlet",
        "strikers flail": "PowerGauntlet"
    }

    def __init__(self, bot, set_number):
        self.bot = bot
        self.set_number = set_number
        self.session = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    @commands.command(name='lookup')
    async def lookup_item(self, ctx, unit_name: str, item_name: str):
        """Look up item stats for a specific unit. Example: .lookup Ashe GuinsoosRageblade"""
        # Check for special cases in unit name and item (remove spaces and convert to lowercase)
        unit_key = unit_name.replace(" ", "").lower()
        item_key = item_name.replace(" ", "").lower()

        if unit_key in self.unit_special_cases:
            unit_name = self.unit_special_cases[unit_key]
        else:
            unit_name = unit_name.capitalize()

        if item_key in self.item_special_cases:
            item_name = self.item_special_cases[item_key]
        
        # Format the unit name with TFT set prefix
        formatted_unit_name = f"TFT{self.set_number}_{unit_name}"
        url = "https://d3.tft.tools/combos/explorer/1100/15163/1"

        payload = {
            "uid": "",
            "filters": [
                {
                    "typ": "u",
                    "value": formatted_unit_name,
                    "tier": "0",
                    "exclude": False
                }
            ]
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()

            
            if isinstance(data, dict) and 'unitItems' in data:
                for unit_item in data['unitItems']:
                    if isinstance(unit_item, list) and len(unit_item) >= 4:
                        current_unit = unit_item[0]
                        current_item = unit_item[2]
                        item_stats = unit_item[3]
                        
                        if current_unit == formatted_unit_name and item_name.lower() in current_item.lower():
                            delta = item_stats.get('delta', 'N/A')
                            if delta != 'N/A':
                                # Format to 2 decimal places and add + for positive numbers
                                delta_formatted = '{:+.2f}'.format(delta)
                                await ctx.send(f"Delta: {delta_formatted}")
                            else:
                                await ctx.send(f"Delta: {delta}")
                            return
                
                print(f"No data found for {item_name} on {unit_name}")
            
        except aiohttp.ClientError as e:
            print(f"Error occurred: {e}")

async def setup(bot, set_number):
    await bot.add_cog(Lookup(bot, set_number))
