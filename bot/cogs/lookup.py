import discord
from discord.ext import commands
import aiohttp
import json
import os

class Lookup(commands.Cog):

    def __init__(self, bot, set_number):
        self.bot = bot
        self.set_number = set_number
        self.session = None
        self.unit_special_cases = {}
        self.item_special_cases = {}
        self.load_special_cases()

    def load_special_cases(self):
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        try:
            with open(os.path.join(config_dir, 'units.json'), 'r') as f:
                self.unit_special_cases = json.load(f)
            with open(os.path.join(config_dir, 'items.json'), 'r') as f:
                self.item_special_cases = json.load(f)
        except Exception as e:
            print(f"Error loading config files: {e}")

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    @commands.command(name='lookup')
    async def lookup_item(self, ctx, *args):
        """Look up item stats. Examples: 
        .lookup rfc (lookup item stats)
        .lookup Ashe rfc (lookup item stats for specific unit)"""
        
        if not args:
            await ctx.send("Please provide an item name or unit and item names")
            return

        # Handle item-only lookup
        if len(args) == 1:
            item_name = args[0]
            item_key = item_name.replace(" ", "").lower()
            
            # Handle radiant items
            words = item_key.split()
            is_radiant = "radiant" in words
            if is_radiant:
                # Remove "radiant" from the search
                words.remove("radiant")
                item_key = "".join(words)
                
            # Check if the base item name is in special cases
            if item_key in self.item_special_cases:
                base_item = self.item_special_cases[item_key]
                if is_radiant:
                    # Handle special radiant mappings
                    if base_item == "PowerGauntlet":
                        item_name = "TrapClaw"
                    elif base_item == "MadredsBloodrazor":
                        item_name = "GiantSlayer"
                    elif base_item == "UnstableConcoction":
                        item_name = "HandOfJustice"
                    else:
                        item_name = f"5{base_item}Radiant"
                else:
                    item_name = base_item
            else:
                if is_radiant:
                    # Capitalize the first letter of each word for the base item name
                    base_name = " ".join(word.capitalize() for word in words)
                    item_name = f"5{base_name}Radiant"

            url = "https://d3.tft.tools/stats2/general/1100/15163/1"

            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()

                if 'items' in data:
                    for item in data['items']:
                        if item_name.lower() in item['itemId'].lower():
                            place = item.get('place', 'N/A')
                            if place != 'N/A':
                                await ctx.send(f"AVP: {place:.2f}")
                                return
                    
                    await ctx.send(f"No data found for {item_name}")
                else:
                    await ctx.send("Error: Unexpected data format from API")
                
            except aiohttp.ClientError as e:
                await ctx.send(f"Error occurred while fetching data: {str(e)}")
            return

        # Handle unit + item lookup
        unit_name, item_name = args[0], args[1]
        unit_key = unit_name.replace(" ", "").lower()
        item_key = item_name.replace(" ", "").lower()

        if unit_key in self.unit_special_cases:
            unit_name = self.unit_special_cases[unit_key]
        else:
            unit_name = unit_name.capitalize()

        # Handle radiant items
        words = item_key.split()
        is_radiant = "radiant" in words
        if is_radiant:
            # Remove "radiant" from the search
            words.remove("radiant")
            item_key = "".join(words)
            
        # Check if the base item name is in special cases
        if item_key in self.item_special_cases:
            base_item = self.item_special_cases[item_key]
            if is_radiant:
                # Handle special radiant mappings
                if base_item == "PowerGauntlet":
                    item_name = "TrapClaw"
                elif base_item == "MadredsBloodrazor":
                    item_name = "GiantSlayer"
                elif base_item == "UnstableConcoction":
                    item_name = "HandOfJustice"
                else:
                    item_name = f"5{base_item}Radiant"
            else:
                item_name = base_item
        
        # For radiant items, use the stats2/general endpoint
        if is_radiant:
            url = "https://d3.tft.tools/stats2/general/1100/15163/1"
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()

                if 'items' in data:
                    for item in data['items']:
                        if item_name.lower() in item['itemId'].lower():
                            place = item.get('place', 'N/A')
                            if place != 'N/A':
                                await ctx.send(f"AVP: {place:.2f}")
                                return
                    
                    await ctx.send(f"No data found for {item_name}")
                else:
                    await ctx.send("Error: Unexpected data format from API")
            except aiohttp.ClientError as e:
                await ctx.send(f"Error occurred while fetching data: {str(e)}")
        else:
            # For non-radiant items, use the combos/explorer endpoint
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
                    
                    await ctx.send(f"No data found for {item_name} on {unit_name}")
                
            except aiohttp.ClientError as e:
                await ctx.send(f"Error occurred: {str(e)}")

async def setup(bot, set_number):
    await bot.add_cog(Lookup(bot, set_number))
