import discord
from discord.ext import commands
import requests
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
import math
import aiohttp
import asyncio

class Last(commands.Cog):
    def __init__(self, bot, apikey, latest_version):
        self.bot = bot
        self.apikey = apikey
        self.version = latest_version
        self.headers = {"X-Riot-Token": self.apikey}
        
        # Trait style colors (based on TFT in-game colors)
        self.TRAIT_COLORS = {
            0: '#5f5f5f',  # Gray for inactive
            1: '#bf8f3f',  # Bronze
            2: '#7e7e7e',  # Silver
            3: '#ffd700',  # Gold
            4: '#ff4de1'   # Chromatic/Prismatic
        }

        # Champion rarity colors
        self.RARITY_COLORS = {
            0: '#808080',  # Gray for 1-cost
            1: '#11b288',  # Green for 2-cost
            2: '#207ac7',  # Blue for 3-cost
            3: '#c440da',  # Purple for 4-cost
            4: '#ffb93b',  # Gold for 5-cost
            6: '#ff8c00'   # Orange for special units
        }

        # Placement colors
        self.PLACEMENT_COLORS = {
            1: '#FFD700',  # Gold
            2: '#c440da',  # Purple
            3: '#207ac7',  # Blue
            4: '#00FF00',  # Green
            5: '#808080',  # Gray
            6: '#808080',
            7: '#808080',
            8: '#808080'
        }

        # Load font for trait numbers
        self.font = ImageFont.load_default()

    def draw_number(self, draw, number, x, y, size, color):
        """Draw a large number using vector paths"""
        # Define number paths (normalized to 100x100 grid)
        number_paths = {
            '1': [(40, 20), (60, 20), (60, 80), (40, 80)],
            '2': [(30, 20), (70, 20), (70, 50), (30, 50), (30, 80), (70, 80)],
            '3': [(30, 20), (70, 20), (70, 80), (30, 80), (70, 50), (30, 50)],
            '4': [(30, 20), (30, 50), (70, 50), (70, 20), (70, 80)],
            '5': [(70, 20), (30, 20), (30, 50), (70, 50), (70, 80), (30, 80)],
            '6': [(70, 20), (30, 20), (30, 80), (70, 80), (70, 50), (30, 50)],
            '7': [(30, 20), (70, 20), (70, 80)],
            '8': [(30, 20), (70, 20), (70, 80), (30, 80), (30, 20), (30, 50), (70, 50)],
            '9': [(70, 80), (70, 20), (30, 20), (30, 50), (70, 50)]
        }

        # Scale the path to desired size
        scale = size / 100
        path = number_paths.get(str(number))
        if path:
            # Scale and offset points
            scaled_path = [(x + px * scale, y + py * scale) for px, py in path]
            # Draw the path
            draw.line(scaled_path, fill=color, width=int(size/10))

    def draw_large_text(self, draw, text, x, y, color, scale=2):
        """Draw text at a larger scale"""
        # Get original text size
        text_bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Create a temporary image for the text
        text_img = Image.new('RGBA', (text_width * scale, text_height * scale), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        
        # Draw text in white
        text_draw.text((0, 0), text, font=self.font, fill='white')
        
        # Scale up the text
        text_img = text_img.resize((text_width * scale, text_height * scale), Image.NEAREST)
        
        # Convert white to desired color
        if color != 'white':
            data = text_img.getdata()
            new_data = []
            for item in data:
                if item[3] > 0:  # If pixel is not transparent
                    # Convert hex color to RGB if needed
                    if isinstance(color, str) and color.startswith('#'):
                        r = int(color[1:3], 16)
                        g = int(color[3:5], 16)
                        b = int(color[5:7], 16)
                        new_data.append((r, g, b, item[3]))
                    else:
                        new_data.append((*color, item[3]))
                else:
                    new_data.append(item)
            text_img.putdata(new_data)
        
        # Paste onto main image
        draw._image.paste(text_img, (x, y), text_img)

    async def get_tactician_data(self):
        """Get TFT tactician data"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://ddragon.leagueoflegends.com/cdn/{self.version}/data/en_US/tft-tactician.json") as response:
                    if response.status == 200:
                        return await response.json()
            return None
        except Exception as e:
            print(f"Error getting tactician data: {str(e)}")
            return None

    async def get_tactician_icon(self, companion_data):
        """Get tactician icon based on companion data"""
        try:
            print(f"Companion data received: {companion_data}")
            
            tactician_data = await self.get_tactician_data()
            if not tactician_data:
                return None
            
            item_id = str(companion_data.get('item_ID'))
            print(f"Looking for tactician with item ID: {item_id}")
            
            tactician = tactician_data['data'].get(item_id)
            if not tactician:
                print(f"Could not find tactician with item ID: {item_id}")
                return None
            
            image_data = tactician['image']
            icon_url = f"https://ddragon.leagueoflegends.com/cdn/{self.version}/img/tft-tactician/{image_data['full']}"
            
            return await self.download_image(icon_url)
        except Exception as e:
            print(f"Error getting tactician icon: {str(e)}")
            return None

    async def get_puuid(self, name, tag, region):
        """Get PUUID from Riot ID"""
        url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['puuid']
                else:
                    raise Exception(f"Failed to get PUUID: {response.status}")

    async def get_last_match_id(self, puuid, region):
        """Get the last match ID for a player"""
        url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data[0]
                else:
                    raise Exception(f"Failed to get match history: {response.status}")

    async def get_match_details(self, match_id, region):
        """Get details for a specific match"""
        url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/{match_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get match details: {response.status}")

    def clean_name(self, name):
        """Clean champion name for URL"""
        name = name.replace("TFT15_", "").replace("tft15_", "")
        
        # Special cases
        special_cases = {
            "drmundo": "DrMundo",
            "leesin": "LeeSin",
            "twistedfate": "TwistedFate",
            "kogmaw": "KogMaw",
            "reksai": "RekSai",
            "masteryi": "MasterYi"
        }
        
        name_lower = name.lower()
        if name_lower in special_cases:
            return special_cases[name_lower]
        
        return name

    async def download_image(self, url):
        """Download an image from URL and return as PIL Image"""
        try:
            print(f"Downloading image from: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.read()
                        return Image.open(BytesIO(data))
            return None
        except Exception as e:
            print(f"Failed to download image from {url}: {str(e)}")
            return None

    def draw_star(self, draw, x, y, size):
        """Draw a star shape using polygon"""
        outer_radius = size / 2
        inner_radius = size / 4
        points = []
        
        for i in range(10):
            angle = math.pi / 5 * i - math.pi / 2
            radius = outer_radius if i % 2 == 0 else inner_radius
            points.append((
                x + radius * math.cos(angle),
                y + radius * math.sin(angle)
            ))
        
        draw.polygon(points, fill='white')

    def draw_star_background(self, draw, x, y, width, height, num_stars):
        """Draw a rounded rectangle background with stars"""
        draw.rectangle([x, y, x + width, y + height], fill='#607D8B')
        
        star_size = height - 4
        star_spacing = (width - star_size * num_stars) / (num_stars + 1)
        
        for i in range(num_stars):
            star_x = x + star_spacing * (i + 1) + star_size * i + star_size/2
            star_y = y + height/2
            self.draw_star(draw, star_x, star_y, star_size)

    def draw_bordered_rectangle(self, draw, x, y, width, height, border_color, fill_color=None, border_width=2):
        """Draw a rectangle with a border"""
        draw.rectangle([x, y, x + width, y + height], outline=border_color, fill=fill_color)
        for i in range(border_width):
            draw.rectangle([x + i, y + i, x + width - i, y + height - i], outline=border_color)

    def get_trait_image_name(self, trait_id):
        """Get the correct trait image name from the trait data"""
        trait_data = {
            "TFT15_Bastion": "Trait_Icon_9_Bastion.png",
            "TFT15_BattleAcademia": "Trait_Icon_15_BattleClub.TFT_Set15.png",
            "TFT15_Destroyer": "Trait_Icon_15_Destroyer.TFT_Set15.png",
            "TFT15_DragonFist": "Trait_Icon_15_DragonFist.TFT_Set15.png",
            "TFT15_Edgelord": "Trait_Icon_10_Edgelord.png",
            "TFT15_Empyrean": "Trait_Icon_15_Empyrean.TFT_Set15.png",
            "TFT15_Heavyweight": "Trait_Icon_15_Heavyweight.TFT_Set15.png",
            "TFT15_Spellslinger": "Trait_Icon_15_Sorcerer.TFT_Set15.png",
            "TFT15_MonsterTrainer": "Trait_Icon_15_MonsterTrainer.TFT_Set15.png",
            "TFT15_OldMentor": "Trait_Icon_15_OldMentor.TFT_Set15.png",
            "TFT15_Prodigy": "Trait_Icon_15_Prodigy.TFT_Set15.png",
            "TFT15_Protector": "Trait_Icon_6_Protector.png",
            "TFT15_Juggernaut": "Trait_Icon_9_Juggernaut.png",
            "TFT15_Sniper": "Trait_Icon_6_Sniper.png",
            "TFT15_SoulFighter": "Trait_Icon_15_SoulFighter.TFT_Set15.png",
            "TFT15_StarGuardian": "Trait_Icon_8_StarGuardian.png",
            "TFT15_SupremeCells": "Trait_Icon_15_SupremeCells.TFT_Set15.png",
            "TFT15_SentaiRanger": "Trait_Icon_15_RoboRangers.TFT_Set15.png",
            "TFT15_Luchador": "Trait_Icon_15_RingKings.TFT_Set15.png",
            "TFT15_GemForce": "Trait_Icon_15_GemForce.TFT_Set15.png",
            "TFT15_TheCrew": "Trait_Icon_15_StarCrew.TFT_Set15.png",
            "TFT15_Captain": "Trait_Icon_15_RogueCaptain.TFT_Set15.png",
            "TFT15_Rosemother": "Trait_Icon_15_Rosemother.TFT_Set15.png",
            "TFT15_Strategist": "Trait_Icon_9_Strategist.png",
            "TFT15_Duelist": "Trait_Icon_8_Duelist.png",
            "TFT15_ElTigre": "Trait_Icon_15_TheChamp.TFT_Set15.png"
        }
        return trait_data.get(trait_id)

    async def draw_trait_icon(self, draw, img, x, y, trait_id, trait_style, num_units):
        """Draw a trait icon with count and background"""
        image_name = self.get_trait_image_name(trait_id)
        if not image_name:
            return False
        
        icon_url = f"https://ddragon.leagueoflegends.com/cdn/{self.version}/img/tft-trait/{image_name}"
        icon_img = await self.download_image(icon_url)
        
        if icon_img:
            try:
                icon_img = icon_img.resize((32, 32))
                bg_color = self.TRAIT_COLORS.get(trait_style, '#5f5f5f')
                draw.rectangle([x, y, x + 32, y + 32], fill=bg_color)
                img.paste(icon_img, (x, y), icon_img)
                
                count_text = str(num_units)
                text_bbox = draw.textbbox((0, 0), count_text, font=self.font)
                text_width = text_bbox[2] - text_bbox[0]
                draw.text((x + 32 - text_width - 2, y + 32 - 14), count_text, fill='black', font=self.font)
                
                return True
            except Exception as e:
                print(f"Error processing trait icon {trait_id}: {str(e)}")
                return False
        return False

    async def create_match_image(self, match_data, puuid):
        """Create a horizontal image showing placement, units with stars and items"""
        # Find player data
        player_data = None
        for participant in match_data['info']['participants']:
            if participant['puuid'] == puuid:
                player_data = participant
                break
        
        if not player_data:
            raise Exception("Player not found in match data")
        
        # Calculate dimensions
        unit_width = 100
        unit_spacing = 20
        left_margin = 300  # Increased from 200 to give more space for summoner icon
        right_margin = 20
        num_units = len(player_data['units'])
        width = left_margin + (unit_width + unit_spacing) * num_units + right_margin
        height = 200
        
        # Create image
        img = Image.new('RGB', (width, height), color='#36393F')
        draw = ImageDraw.Draw(img)
        
        # Draw placement box
        placement = player_data['placement']
        placement_color = self.PLACEMENT_COLORS.get(placement, '#808080')
        
        # Create darker background color
        bg_color = placement_color
        if bg_color.startswith('#'):
            r = int(bg_color[1:3], 16)
            g = int(bg_color[3:5], 16)
            b = int(bg_color[5:7], 16)
            bg_color = f'#{r//2:02x}{g//2:02x}{b//2:02x}'
        
        box_size = 100  # Increased from 65 for larger text
        box_x = 20
        box_y = height//4 - 30
        
        # Draw placement box
        draw.rectangle([box_x, box_y, box_x + box_size, box_y + box_size], 
                      fill=bg_color, outline=placement_color)
        draw.rectangle([box_x+1, box_y+1, box_x + box_size-1, box_y + box_size-1], 
                      outline=placement_color)
        
        # Draw placement number
        text = str(placement)
        number_size = 60  # Size of the number
        text_x = box_x + (box_size - number_size) // 2
        text_y = box_y + (box_size - number_size) // 2
        self.draw_number(draw, text, text_x, text_y, number_size, placement_color)
        
        # Draw summoner icon
        icon_size = 100  # Increased from 65 to match placement box
        icon_x = box_x + box_size + 20
        icon_y = box_y
        
        icon_img = await self.get_tactician_icon(player_data.get('companion', {}))
        if icon_img:
            try:
                icon_img = icon_img.resize((icon_size, icon_size))
                mask = Image.new('L', (icon_size, icon_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse([0, 0, icon_size, icon_size], fill=255)
                img.paste(icon_img, (icon_x, icon_y), mask)
            except Exception as e:
                print(f"Error processing summoner icon: {str(e)}")
                draw.ellipse([icon_x, icon_y, icon_x + icon_size, icon_y + icon_size], fill='#2F3136')
        else:
            draw.ellipse([icon_x, icon_y, icon_x + icon_size, icon_y + icon_size], fill='#2F3136')
        
        # Draw level
        level_text = str(player_data['level'])
        number_size = 30  # Smaller size for level number
        
        circle_size = number_size + 12
        circle_x = icon_x + icon_size - circle_size - 2
        circle_y = icon_y + icon_size - circle_size - 2
        
        draw.ellipse([circle_x, circle_y, circle_x + circle_size, circle_y + circle_size], 
                     fill='#2F3136')
        draw.ellipse([circle_x, circle_y, circle_x + circle_size, circle_y + circle_size], 
                     outline='white', width=1)
        
        # Draw level text
        text_x = circle_x + (circle_size - number_size) // 2
        text_y = circle_y + (circle_size - number_size) // 2
        self.draw_number(draw, level_text, text_x, text_y, number_size, 'white')
        
        # Draw units
        unit_start_x = left_margin
        y_pos = 20
        
        for i, unit in enumerate(player_data['units']):
            champion_name = self.clean_name(unit['character_id'])
            unit_stars = unit['tier']
            items = unit.get('itemNames', [])
            rarity = unit['rarity']
            
            champ_url = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/characters/tft15_{champion_name.lower()}/skins/base/images/tft15_{champion_name.lower()}_mobile.tft_set15.png"
            champ_img = await self.download_image(champ_url)
            
            if champ_img:
                try:
                    x_pos = unit_start_x + (unit_width + unit_spacing) * i
                    
                    # Draw stars
                    if unit_stars > 0:
                        star_width = 44
                        star_height = 17
                        star_x = x_pos + (80 - star_width) // 2
                        star_y = y_pos - star_height - 3
                        self.draw_star_background(draw, star_x, star_y, star_width, star_height, unit_stars)
                    
                    # Draw champion border
                    border_color = self.RARITY_COLORS.get(rarity, '#FFFFFF')
                    self.draw_bordered_rectangle(draw, x_pos-2, y_pos-2, 84, 84, border_color)
                    
                    # Place champion
                    champ_img = champ_img.resize((80, 80))
                    img.paste(champ_img, (x_pos, y_pos))
                    
                    # Draw items
                    if items:
                        item_y = y_pos + 55
                        item_x = x_pos + (80 - len(items) * 27) // 2
                        for j, item_name in enumerate(items):
                            item_id = item_name.replace("TFT_Item_", "").replace("Artifact_", "")
                            item_url = f"https://ddragon.leagueoflegends.com/cdn/{self.version}/img/tft-item/TFT_Item_{item_id}.png"
                            item_img = await self.download_image(item_url)
                            
                            if item_img:
                                try:
                                    item_img = item_img.resize((25, 25))
                                    img.paste(item_img, (item_x + j * 27, item_y))
                                except Exception as e:
                                    print(f"Error processing item image {item_name}: {str(e)}")
                
                except Exception as e:
                    print(f"Error processing unit {champion_name}: {str(e)}")
        
        # Draw traits
        traits_y = y_pos + 110
        traits_x = left_margin  # Start traits from the same position as units
        trait_spacing = 4
        active_traits = [trait for trait in player_data.get('traits', []) if trait.get('tier_current', 0) > 0]
        active_traits.sort(key=lambda x: (-x['tier_current'], -x['style'], x['name']))
        for trait in active_traits:
            if traits_x + 32 + trait_spacing > width:
                break
            
            if await self.draw_trait_icon(draw, img, traits_x, traits_y, trait['name'], trait['style'], trait['num_units']):
                traits_x += 32 + trait_spacing

        # Save and return image bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr

    @commands.command(name='last')
    async def last_match(self, ctx):
        """Show your last TFT match"""
        try:
            # Get user settings
            conn = self.bot.get_cog('UserSettings').get_db_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('SELECT tft_name, tft_tag, region FROM tft_settings WHERE discord_id = %s', (ctx.author.id,))
                result = cursor.fetchone()
                if not result:
                    await ctx.send("Please set your TFT name and region first using `.set_name` and `.set_region`")
                    return
                
                name, tag, region = result
            finally:
                cursor.close()
                conn.close()

            # Add loading reaction
            message = await ctx.send("Fetching your last match...")
            
            # Get match data
            puuid = await self.get_puuid(name, tag, region)
            match_id = await self.get_last_match_id(puuid, region)
            match_data = await self.get_match_details(match_id, region)
            
            # Create and send image
            img_bytes = await self.create_match_image(match_data, puuid)
            await message.delete()
            await ctx.send(file=discord.File(img_bytes, 'last_match.png'))
            
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

async def setup(bot, apikey, latest_version):
    await bot.add_cog(Last(bot, apikey, latest_version))
