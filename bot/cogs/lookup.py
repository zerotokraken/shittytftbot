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

        # Check if first arg is a unit
        first_arg = args[0].replace(" ", "").lower()
        is_unit = first_arg in self.unit_special_cases or args[0][0].isupper()

        # Handle item-only lookup
        if len(args) == 1 or not is_unit:
            # If we have multiple args but first isn't a unit, combine them
            item_name = " ".join(args)
            item_key = item_name.replace(" ", "").lower()
            
            # Check if it's in special cases
            if item_key in self.item_special_cases:
                item_name = self.item_special_cases[item_key]
            else:
                # If not in special cases, just capitalize
                item_name = item_key.capitalize()

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

        # Handle unit name
        if unit_key in self.unit_special_cases:
            unit_name = self.unit_special_cases[unit_key]
        else:
            unit_name = unit_name.capitalize()
        formatted_unit_name = f"TFT{self.set_number}_{unit_name}"

        # Handle item name
        if item_key in self.item_special_cases:
            item_name = self.item_special_cases[item_key]
        else:
            # If not in special cases, just capitalize
            item_name = item_key.capitalize()
        
        # For unit + item lookups, use the combos/explorer endpoint
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
                        
                        # Exact match for both unit and item
                        if current_unit == formatted_unit_name and current_item == item_name:
                            delta = item_stats.get('delta', 'N/A')
                            if delta != 'N/A':
                                # Format to 2 decimal places and add + for positive numbers
                                delta_formatted = '{:+.2f}'.format(delta)
                                await ctx.send(f"Delta: {delta_formatted}")
                            else:
                                await ctx.send(f"Delta: {delta}")
                            return
                
                # Debug output
                first_item = data['unitItems'][0] if data.get('unitItems') and data['unitItems'] else None
                debug_msg = f"Looking for:\nUnit: {formatted_unit_name}\nItem: {item_name}\n"
                if first_item:
                    debug_msg += f"\nFirst item in response:\nUnit: {first_item[0]}\nItem: {first_item[2]}"
                debug_msg += "\nNo matching data found."
                await ctx.send(debug_msg)
            
        except aiohttp.ClientError as e:
            await ctx.send(f"Error occurred: {str(e)}")

async def setup(bot, set_number):
    await bot.add_cog(Lookup(bot, set_number))
