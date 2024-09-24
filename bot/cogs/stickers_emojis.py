import discord
from discord.ext import commands

class StickersEmojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def frog(self, ctx):
        guild = ctx.guild
        try:
            # Fetch the sticker from the guild
            sticker = await guild.fetch_sticker(1113791679787450428)
            # Send the sticker
            await ctx.send(stickers=[sticker])
        except discord.NotFound:
            print("Sticker not found.")
        except discord.Forbidden:
            print("I don't have permission to use that sticker.")
        except discord.HTTPException as e:
            print(f"An error occurred: {e}")

    @commands.command()
    async def chris(self, ctx):
        guild = ctx.guild
        try:
            # Fetch the sticker from the guild
            sticker = await guild.fetch_sticker(1209514391381352489)
            # Send the sticker
            await ctx.send(stickers=[sticker])
        except discord.NotFound:
            print("Sticker not found.")
        except discord.Forbidden:
            print("I don't have permission to use that sticker.")
        except discord.HTTPException as e:
            print(f"An error occurred: {e}")

    @commands.command(name="69420")
    async def sixninefourtwenty(self, ctx):
        guild = ctx.guild
        try:
            # Fetch the sticker from the guild
            sticker = await guild.fetch_sticker(1284025743856369705)
            # Send the sticker
            await ctx.send(stickers=[sticker])
        except discord.NotFound:
            print("Sticker not found.")
        except discord.Forbidden:
            print("I don't have permission to use that sticker.")
        except discord.HTTPException as e:
            print(f"An error occurred: {e}")

    @commands.command()
    async def xdd(self, ctx):
        # Emoji ID of the specific emoji
        emoji_id = 1113493059175469056
        # Retrieve the emoji object from the server using the ID
        emoji = discord.utils.get(ctx.guild.emojis, id=emoji_id)

        if emoji:
            await ctx.send(f'{emoji}')
        else:
            print("Emoji not found or not available in this server.")

def setup(bot):
    bot.add_cog(StickersEmojis(bot))
