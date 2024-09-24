import discord
from discord.ext import commands
import aiohttp
import random
from datetime import timedelta

class MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to post an image from a URL
    @commands.command()
    async def vuhra(self, ctx):
        url = 'https://media.discordapp.net/attachments/1113421046029242381/1207801587506872391/8fzdyz.png?ex=66e94ca2&is=66e7fb22&hm=a0748e79b2b3adc627c6b12290b6fbd125682fa572c440fc310bf5adbd55e4d8&=&format=webp&quality=lossless'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    with open('temp_image.png', 'wb') as f:
                        f.write(image_data)
                    await ctx.send(file=discord.File('temp_image.png'))
                    os.remove('temp_image.png')  # Optionally delete the temporary file
                else:
                    print('Failed to fetch the image.')

    @commands.command()
    async def vuhramald(self, ctx):
        random_seconds = random.randint(1, 86400)
        time_delta = timedelta(seconds=random_seconds)
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours} hours, {minutes} minutes, {seconds} seconds"
        await ctx.send(f"Vuhra is about to mald in {time_str}")

    # Command to list all commands in alphabetical order
    @commands.command()
    async def shittycommands(self, ctx):
        commands_list = sorted(self.bot.commands, key=lambda c: c.name)
        command_names = [f'`{command.name}` {command.description}' for command in commands_list]
        response = '\n'.join(command_names) or 'No commands available.'
        await ctx.send(f'Available commands:\n{response}')

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
        await ctx.send("ZTK is a filthy highroller")

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

    @commands.command()
    async def erhm(self, ctx):
        await ctx.send("what the sigma")

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

def setup(bot):
    bot.add_cog(MiscCommands(bot))
