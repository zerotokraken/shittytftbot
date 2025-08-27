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

        # Check if first arg is a unit (case-insensitive)
        first_arg = args[0].lower()
        first_arg_no_spaces = first_arg.replace(" ", "")
        is_unit = False

        # Check unit special cases case-insensitively
        for unit_key in self.unit_special_cases:
            if first_arg_no_spaces == unit_key.lower():
                is_unit = True
                break
        
        # Also check if it's a champion name (starts with capital)
        if not is_unit:
            is_unit = args[0][0].upper() == args[0][0]

        # Handle unit-only lookup
        if len(args) == 1 and is_unit:
            unit_name = args[0]
            # Format unit name
            unit_key = unit_name.replace(" ", "").lower()
            unit_found = False
            for key, value in self.unit_special_cases.items():
                if unit_key == key.lower():
                    unit_name = value
                    unit_found = True
                    break
            if not unit_found:
                unit_name = unit_name.capitalize()
            formatted_unit_name = f"TFT{self.set_number}_{unit_name}"

            # Use base URL for unit stats
            url = "https://d3.tft.tools/combos/base/1100/15170/1"

            payload = {
                "uid": ""
            }

            headers = {
                'Content-Type': 'application/json'
            }

            try:
                async with self.session.post(url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()

                if 'units' in data:
                    for unit_data in data['units']:
                        if isinstance(unit_data, list) and len(unit_data) == 2:
                            current_unit, stats = unit_data
                            if current_unit == formatted_unit_name:
                                place = stats.get('place', 0)
                                count = stats.get('count', 0)
                                if count > 0:
                                    avg_placement = place / count
                                    await ctx.send(f"Average Placement (any ★): {avg_placement:.2f}")
                                    return
                    
                    await ctx.send(f"No data found for {unit_name}")
                else:
                    await ctx.send("Error: Unexpected data format from API")
                
            except aiohttp.ClientError as e:
                await ctx.send(f"Error occurred while fetching data: {str(e)}")
            return

        # Handle unit + star level lookup
        if len(args) == 2 and is_unit and args[1].isdigit():
            star_level = int(args[1])
            if not 1 <= star_level <= 4:
                await ctx.send("Star level must be between 1 and 4")
                return

            unit_name = args[0]
            # Format unit name
            unit_key = unit_name.replace(" ", "").lower()
            unit_found = False
            for key, value in self.unit_special_cases.items():
                if unit_key == key.lower():
                    unit_name = value
                    unit_found = True
                    break
            if not unit_found:
                unit_name = unit_name.capitalize()
            formatted_unit_name = f"TFT{self.set_number}_{unit_name}"

            # Use base URL for unit stats
            url = "https://d3.tft.tools/combos/explorer/1100/15170/1"

            payload = {
                "uid": "",
                "filters": [
                    {
                        "typ": "u",
                        "value": formatted_unit_name,
                        "tier": str(star_level),
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

                # Debug: Print the response data
                print(f"Star lookup response for {formatted_unit_name} tier {star_level}:")
                print(json.dumps(data, indent=2))

                if 'base' in data:
                    base_stats = data['base']
                    place = base_stats.get('place', 0)
                    count = base_stats.get('count', 0)
                    if count > 0:
                        avg_placement = place / count
                        await ctx.send(f"Average Placement ({star_level}★): {avg_placement:.2f}")
                        # Debug: Print the calculation
                        print(f"Calculation: {place} / {count} = {avg_placement}")
                        return
                    
                    await ctx.send(f"No data found for {star_level}★ {unit_name}")
                else:
                    await ctx.send("Error: Unexpected data format from API")
                
            except aiohttp.ClientError as e:
                await ctx.send(f"Error occurred while fetching data: {str(e)}")
            return

        # Handle item-only lookup
        if len(args) == 1 or not is_unit:
            # If we have multiple args but first isn't a unit, combine them for lookup
            item_key = " ".join(args).lower()
            
            # Check if it's in special cases
            if item_key in self.item_special_cases:
                item_name = self.item_special_cases[item_key]
            else:
                # Try without spaces
                no_spaces_key = item_key.replace(" ", "")
                if no_spaces_key in self.item_special_cases:
                    item_name = self.item_special_cases[no_spaces_key]
                else:
                    # If not in special cases, just capitalize
                    item_name = item_key.capitalize()

            url = "https://d3.tft.tools/stats2/general/1100/15170/1"

            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()

                if 'items' in data:
                    for item in data['items']:
                        if item_name.lower() == item['itemId'].lower():
                            place = item.get('place', 'N/A')
                            if place != 'N/A':
                                await ctx.send(f"AVP: {place:.2f}")
                                return
                    
                    await ctx.send(f"No data found for {item_name}")
                else:
                    await ctx.send("Error: Unexpected data format from API")
                
        item_name = " ".join(args[1:])  # Combine remaining args for item name
        
        # Handle unit name (case-insensitive)
        unit_key = unit_name.replace(" ", "").lower()
        unit_found = False
        for key, value in self.unit_special_cases.items():
            if unit_key == key.lower():
                unit_name = value
                unit_found = True
                break
        if not unit_found:
            unit_name = unit_name.capitalize()
        formatted_unit_name = f"TFT{self.set_number}_{unit_name}"

        # Handle item name
        # Try just the first word first (e.g., "gs")
        item_key = args[1].lower()
        if item_key in self.item_special_cases:
            item_name = self.item_special_cases[item_key]
        else:
            # Try with spaces (e.g., "radiant gs")
            item_key = item_name.lower()
            if item_key in self.item_special_cases:
                item_name = self.item_special_cases[item_key]
            else:
                # Try without spaces (e.g., "radiantgs")
                item_key = item_key.replace(" ", "")
                if item_key in self.item_special_cases:
                    item_name = self.item_special_cases[item_key]
                else:
                    await ctx.send(f"Unknown item: {item_name}")
                    return
        
        # For unit + item lookups, use the combos/explorer endpoint
        url = "https://d3.tft.tools/combos/explorer/1100/15170/1"

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
                        
                        if current_unit == formatted_unit_name and item_name == current_item:
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
