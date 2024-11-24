import discord
from discord.ext import commands

class TeamCodesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def comps(self, ctx):
        """Sends an embed with a list of team names and codes."""
        # Python dictionary for the team data
        teams = [
            { "name": "Rebel +1", "code": "0119042c110f183b1b2b00TFTSet13" },
            { "name": "Black Rose", "code": "01382617101d2123092200TFTSet13" },
            { "name": "Sent Heimer", "code": "011718042b1e2919110b00TFTSet13" },
            { "name": "Camille RR/Ambushers", "code": "01061908160f18371b1f00TFTSet13" },
            { "name": "4 Emissary", "code": "01313324140b3002153700TFTSet13" },
            { "name": "Bruiser +1 Twitch", "code": "01122c0a260e10341a0700TFTSet13" },
            { "name": "Kog RR", "code": "010c03392738131c150f00TFTSet13" },
            { "name": "Family RR", "code": "010c0628273514371f0d00TFTSet13" },
            { "name": "Enforcer +1", "code": "01122d1804330237070800TFTSet13" }
        ]

        # Create the embed
        embed = discord.Embed(
            title="Top Comps",
            description="Import into team planner",
            color=discord.Color.blue(),
        )

        # Add fields for each team
        for team in teams:
            embed.add_field(name=team["name"], value=f"Code: `{team['code']}`", inline=False)

        # Send the embed
        await ctx.send(embed=embed)

# Setup the cog
async def setup(bot):
    await bot.add_cog(TeamCodesCog(bot))
