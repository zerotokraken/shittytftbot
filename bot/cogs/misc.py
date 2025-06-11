import discord
from discord.ext import commands
import aiohttp
import random
from datetime import timedelta
import psycopg2
import os


class MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database_url = os.environ.get('DATABASE_URL')  # Get the database URL from environment variables

    # Function to connect to the database and fetch the image
    def fetch_image_from_db(self, image_name):
        try:
            # Establish connection to PostgreSQL
            conn = psycopg2.connect(self.database_url, sslmode='require')

            with conn.cursor() as cursor:
                # Fetch the image data from the database
                cursor.execute("SELECT image_data FROM images WHERE image_name = %s", (image_name,))
                result = cursor.fetchone()

                if result is not None:
                    image_data = result[0]  # Extract binary image data
                    return image_data
                else:
                    print(f"No image found with the name '{image_name}'.")
                    return None

        except psycopg2.Error as e:
            print(f"Error fetching image from the database: {e}")
            return None

        finally:
            if conn:
                conn.close()

    # Command to post an image from the database
    @commands.command()
    async def vuhra(self, ctx):
        image_name = 'vuhra'  # The name of the image to fetch from the database
        image_data = self.fetch_image_from_db(image_name)

        if image_data is not None:
            # Save the image data to a temporary file
            temp_filename = f"{image_name}.png"
            with open(temp_filename, 'wb') as f:
                f.write(image_data)

            # Send the image file in the Discord channel
            await ctx.send(file=discord.File(temp_filename))

            # Remove the temporary file after sending
            os.remove(temp_filename)
        else:
            print(f"Image '{image_name}' not found in the database.")

    # Command to post an image from the database
    @commands.command()
    async def fam(self, ctx):
        image_name = 'family'  # The name of the image to fetch from the database
        image_data = self.fetch_image_from_db(image_name)

        if image_data is not None:
            # Save the image data to a temporary file
            temp_filename = f"{image_name}.png"
            with open(temp_filename, 'wb') as f:
                f.write(image_data)

            # Send the image file in the Discord channel
            await ctx.send(file=discord.File(temp_filename))

            # Remove the temporary file after sending
            os.remove(temp_filename)
        else:
            print(f"Image '{image_name}' not found in the database.")

    # Command to post an image from the database
    @commands.command()
    async def lowroll(self, ctx):
        image_name = 'lowroll'  # The name of the image to fetch from the database
        image_data = self.fetch_image_from_db(image_name)

        if image_data is not None:
            # Save the image data to a temporary file
            temp_filename = f"{image_name}.png"
            with open(temp_filename, 'wb') as f:
                f.write(image_data)

            # Send the image file in the Discord channel
            await ctx.send(file=discord.File(temp_filename))

            # Remove the temporary file after sending
            os.remove(temp_filename)
        else:
            print(f"Image '{image_name}' not found in the database.")

    @commands.command()
    async def vuhramald(self, ctx):
        random_seconds = random.randint(1, 86400)
        time_delta = timedelta(seconds=random_seconds)
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours} hours, {minutes} minutes, {seconds} seconds"
        await ctx.send(f"Vuhra is about to mald in {time_str}")


    @commands.command()
    async def noob(self, ctx):
        members = [member for member in ctx.guild.members if not member.bot]
        if members:
            noob_user = random.choice(members)
            await ctx.send(f'{noob_user.name} is a noob', delete_after=30)

    # Miscellaneous commands
    @commands.command()
    async def catseal(self, ctx):
        await ctx.send("Hey does anyone here want to kiss a little")

    @commands.command()
    async def eif(self, ctx):
        await ctx.send(
        "GOING 8TH CHECKLIST: I already won the game ✔ This lobby’s playing for second ✔ This is my last loss ✔ I win out from here ✔ My board is too lit ✔ HP is fake ✔ I’m about to spike hard ✔ That’s a fake loss ✔ 20hp? That’s 3 lives ✔ This game is over ✔ We win out ✔")

    @commands.command()
    async def unik(self, ctx):
        await ctx.send("i'm the best hyperroll player on this server dont @ me")

    @commands.command()
    async def ztk(self, ctx):
        await ctx.send("If ZTK has a million fans, then I am one of them. If ZTK has ten fans, then I am one of them. If ZTK has only one fan then that is me. If ZTK has no fans, then that means I am no longer on earth. If the world is against ZTK, then I am against the world")

    @commands.command()
    async def mods(self, ctx):
        await ctx.send("do these mods do anything around here? honestly")

    @commands.command()
    async def coaching(self, ctx):
        await ctx.send(
            "As a auto chess main at a respectably high elo, this game is hard to watch. Literally cringing at some of these mistakes. If you actually want to learn autochess PM me (im silver 2 24lp) I also do coaching.")

    @commands.command()
    async def goodmorning(self, ctx):
        author = ctx.author.display_name
        await ctx.send(
            f"dishsoap? good knowledge. setsuko? good scaling. robin? good tourney placements. emily? good content. kiyoon? good org. milk? good tech. {author}? good morning it's another 6.x masterclass")

    @commands.command()
    async def avp(self, ctx):
        random_number = random.uniform(1.0, 8.0)
        await ctx.send(f'That spot averages a {random_number:.1f} trust')

    @commands.command()
    async def pivot(self, ctx):
        await ctx.send("oh fuck oh fuck i'm a known pivoter")

    @commands.command()
    async def deafen(self, ctx):
        await ctx.send("no scout no pivot /deafen")

    @commands.command()
    async def socks(self, ctx):
        await ctx.send(
            "stats say ur eif, but im pretty sure the stats also dont account for people that are not 6 bastion experts")

    @commands.command()
    async def hero(self, ctx):
        await ctx.send("these hero augments are not fucking balanced man")

    @commands.command()
    async def hyperroll(self, ctx):
        await ctx.send("unik is the last hope for NA hyperroll")

    @commands.command(name="2021")
    async def nolife(self, ctx):
        await ctx.send("top 1 leaderboards got no life tbh bro")
        await ctx.send("they still sweating their balls off since 2021")

    @commands.command()
    async def erhm(self, ctx):
        await ctx.send("what the sigma")

    @commands.command()
    async def saki(self, ctx):
        await ctx.send("where the heck is saki")

    @commands.command()
    async def utrash(self, ctx):
        await ctx.send("yea, u trash")


    @commands.command()
    async def lobby(self, ctx):
        await ctx.send("she's waiting down in the lobby")

    @commands.command()
    async def mortdog(self, ctx):
        await ctx.send("ah man i'm getting mortdogged again")

    @commands.command()
    async def riot(self, ctx):
        await ctx.send("like no one is even balancing the game")

    @commands.command()
    async def krugs(self, ctx):
        await ctx.send("it's okay to lose by 1 krug")

    @commands.command()
    async def hit(self, ctx):
        await ctx.send('Just hit bro')

    @commands.command()
    async def metatft(self, ctx):
        await ctx.send('it’s never your fault just screenshot the metatft rng summary and blame game')

    @commands.command(name="jials", aliases=["galbia"])
    async def jials(self, ctx):
        await ctx.send("galbia or jials, they're essentially the same person to me")

    @commands.command()
    async def hawktuah(self, ctx):
        await ctx.send("You gotta give 'em that hawk tuah and spit on that thang")

    @commands.command()
    async def ye(self, ctx):
        await ctx.send("ye")

    @commands.command()
    async def boombot(self, ctx):
        await ctx.send("BOOOOOOOOM BOT")

    @commands.command()
    async def regions(self, ctx):
        await ctx.send("The available regions are: NA1, EUN1, EUW1, BR1, JP1, KR1, LA1, LA2, ME1, OC1, PH2, RU, SG2, TH2, TR1, TW2, VN2")

    @commands.command()
    async def saida(self, ctx):
        lines_saida = [
            "https://clips.twitch.tv/ConcernedPoliteFlyShadyLulu-ZYsvLju7ZH8kualJ?embedo",
            "https://clips.twitch.tv/EnjoyableGlamorousWalletHeyGuys-04szKrShCTmHm74L?embedo",
            "https://clips.twitch.tv/BrainyRacyPoxOSsloth-3hAamOJIS7cvqKyn?embed0",
            "https://clips.twitch.tv/embed?clip=EasyGrotesquePicklesTTours-L6zOHcrbOuODEY6f?embed0",
        ]
        selected_line_saida = random.choice(lines_saida)
        await ctx.send(f'{selected_line_saida}')

    @commands.command()
    async def toxic(self, ctx):
        await ctx.send(f"{ctx.author.display_name}, I'm not sure what's going on but it seems like all of your posts have a layer of toxicness that really isn't helpful or should be a part of the tft community.\n\nYou clearly enjoy the game or you wouldn't be playing it this long, but what makes you feel like you need to communicate like this? You're a skilled player, and I wish you could set a better example.\n\nIf you think stuff needs changed, let us know, and we usually respond within a patch or two at the most.")

async def setup(bot):
    await bot.add_cog(MiscCommands(bot))
