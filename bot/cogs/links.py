import discord
from discord.ext import commands

class GuideCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to list resources with custom descriptions
    @commands.command()
    async def links(self, ctx):
        # Define a static list of resources with custom descriptions and URLs
        statistics_data = {
            'Tactics Tools': ('Comps & statistics. Well known for their explorer tool', 'https://tactics.tools/'),
            'MetaTFT': ('Comps & statistics. Well known for their overlay desktop app', 'https://www.metatft.com/'),
            'LoL Chess': ('Comps & statistics. Commonly used to review player stats', 'https://lolchess.gg/')
        }

        guides = {
            'TFT Handbook': ('Comps, strategy & guides maintained by Robinsongz', 'https://tfthandbook.com/'),
            'TFT Academy': ('Tierlists, podcasts by Frodan & Dishsoap', 'https://tftacademy.com/'),
            'Voids1n Meta Report': ('Meta guide & coaching by Voids1n', 'https://voids1n.com/'),
            'Sologesang Tierlist': ('Tierlist & guide by Sologesang', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQXGfKXwmtXV3JXkkvFW9kcvXtWdEpXq-5uohygcek-qM19CvuWTZYf5VwrgXqwMBVLhVomP0yp_jEZ/pubhtml')
        }

        discords = {
            'Competitive TFT': ('Competitive TFT Discord', 'https://discord.com/invite/competitive-tft-1113421046029242378'),
            'Mortdog': ('Mortdog\'s server for TFT', 'https://discord.gg/mortdog'),
            'TFT Official Discord': ('Official Riot Discord for TFT', 'https://discord.gg/TeamfightTactics'),
            'TFT Esports Discord': ('Competitive events and announcements', 'https://discord.gg/xqV5K4gw5s')
        }

        reddit = {
            'Teamfight Tactics': ('Official Teamfight Tactics Reddit', 'https://www.reddit.com/r/TeamfightTactics/'),
            'Competitive TFT': ('Competitive TFT Reddit', 'https://www.reddit.com/r/CompetitiveTFT/')
        }

        esports = {
            'EMEA TFT Esports': ('Competitive events, ladder snapshots & signups', 'https://emeatftesports.teamfighttactics.leagueoflegends.com/'),
            'America TFT Esports': ('Competitive events, ladder snapshots & signups', 'https://americastftesports.teamfighttactics.leagueoflegends.com/'),
            'APAC TFT Esports': ('Competitive events, ladder snapshots & signups', 'https://apactftesports.teamfighttactics.leagueoflegends.com/'),
            'TFT Liquipedia': ('Past events and player history', 'https://liquipedia.net/tft/Main_Page')
        }

        youtube = {
            'Teamfight Tactics': ('Official Teamfight Tactics YouTube', 'https://www.youtube.com/@playtft'),
            'Frodan': ('Caster, Coach & Challenger Player', 'https://www.youtube.com/@FrodanTV'),
            'Mortdog': ('Gameplay Director for TFT', 'https://www.youtube.com/@MortdogTFT'),
            'Dishsoap': ('The GOAT', 'https://www.youtube.com/@dishsoaptft'),
            'k3soju': ('Challenger player, streamer & known pivoter', 'https://www.youtube.com/@k3soju'),
            'Water Park Tactics': ('General TFT Challenger Guides', 'https://www.youtube.com/@WaterParkTactics')
        }

        # Prepare the responses for each category with links
        statistics_data_response = '\n'.join([f'[{name}]({url}) - {desc}' for name, (desc, url) in statistics_data.items()])
        guides_response = '\n'.join([f'[{name}]({url}) - {desc}' for name, (desc, url) in guides.items()])
        discords_response = '\n'.join([f'[{name}]({url}) - {desc}' for name, (desc, url) in discords.items()])
        reddit_response = '\n'.join([f'[{name}]({url}) - {desc}' for name, (desc, url) in reddit.items()])
        esports_response = '\n'.join([f'[{name}]({url}) - {desc}' for name, (desc, url) in esports.items()])
        youtube_response = '\n'.join([f'[{name}]({url}) - {desc}' for name, (desc, url) in youtube.items()])

        # Create an embed message
        embed = discord.Embed(
            title="TFT Resources",
            color=discord.Color.red()  # Customize the color as you prefer
        )

        # Add fields for each category
        embed.add_field(name="Statistics", value=statistics_data_response, inline=False)
        embed.add_field(name="Guides", value=guides_response, inline=False)
        embed.add_field(name="Discord", value=discords_response, inline=False)
        embed.add_field(name="Reddit", value=reddit_response, inline=False)
        embed.add_field(name="Esports", value=esports_response, inline=False)
        embed.add_field(name="YouTube", value=youtube_response, inline=False)

        # Send the embed response
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GuideCommand(bot))