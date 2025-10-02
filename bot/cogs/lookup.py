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
        self.patch_number = None
        self.load_special_cases()

    async def get_latest_patch(self):
        try:
            async with self.session.get('https://d3.tft.tools/combos/config') as response:
                response.raise_for_status()
                data = await response.json()
                if 'patches' in data and len(data['patches']) > 0:
                    return data['patches'][0]
                raise ValueError("No patch numbers found in config")
        except Exception as e:
            print(f"Error fetching latest patch: {e}")
            return 15190  # Fallback to default patch number

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
        self.patch_number = await self.get_latest_patch()

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

        # Handle trait lookup (when first arg is a number)
        if args[0].isdigit():
            # Combine args into trait format (e.g., "7 mighty mech" -> "7 mighty mech")
            trait_key = " ".join(args).lower()
            
            # Check if trait exists in our config
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            try:
                with open(os.path.join(config_dir, 'traits.json'), 'r') as f:
                    traits_config = json.load(f)
                    if trait_key not in traits_config:
                        await ctx.send(f"Unknown trait: {trait_key}")
                        return
                    
                    trait_info = traits_config[trait_key]
                    trait_name = trait_info[0]
                    trait_tier = trait_info[1]

                    # Use base URL for trait stats
                    url = f"https://d3.tft.tools/combos/base/1100/{self.patch_number}/1"

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

                        if 'traits' in data:
                            for trait_data in data['traits']:
                                if isinstance(trait_data, list) and len(trait_data) == 3:
                                    current_trait, current_tier, stats = trait_data
                                    if current_trait == trait_name and current_tier == trait_tier:
                                        delta = stats.get('delta', 'N/A')
                                        if delta != 'N/A':
                                            # Format to 2 decimal places and add + for positive numbers
                                            delta_formatted = '{:+.2f}'.format(delta)
                                            await ctx.send(f"Delta: {delta_formatted}")
                                            return
                            
                            await ctx.send(f"No data found for {trait_key}")
                        else:
                            await ctx.send("Error: Unexpected data format from API")
                        
                    except aiohttp.ClientError as e:
                        await ctx.send(f"Error occurred while fetching data: {str(e)}")
                    return

            except Exception as e:
                await ctx.send(f"Error loading traits config: {str(e)}")
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
            url = f"https://d3.tft.tools/combos/base/1100/{self.patch_number}/1"

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
            url = f"https://d3.tft.tools/combos/explorer/1100/{self.patch_number}/1"

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

                if 'base' in data:
                    base_stats = data['base']
                    place = base_stats.get('place', 0)
                    count = base_stats.get('count', 0)
                    if count > 0:
                        avg_placement = place / count
                        await ctx.send(f"Average Placement ({star_level}★): {avg_placement:.2f}")
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

            url = f"https://d3.tft.tools/stats2/general/1100/{self.patch_number}/1"

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
                
            except aiohttp.ClientError as e:
                await ctx.send(f"Error occurred while fetching data: {str(e)}")
            return

        # Handle unit + item lookup
        unit_name = args[0]
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
        url = f"https://d3.tft.tools/combos/explorer/1100/{self.patch_number}/1"

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
