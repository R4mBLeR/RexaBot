import discord
from discord.ext import commands
import random
import xmltodict
import requests


class Img(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='gif')
    async def gif(self, ctx, tag=None):
        if tag == None:
            response = requests.get(
                "https://g.tenor.com/v1/search?limit=50&key=O4UDCVI14VWL")
        else:
            payload = {'q': tag, 'key': "O4UDCVI14VWL"}
            response = requests.get(
                "https://g.tenor.com/v1/search?limit=50", params=payload)
        response = response.json()
        gif = random.choice(response["results"])
        url = gif['media'][0]['gif']['url']
        embed = discord.Embed(title=gif['content_description'], color=0x00ff00)
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(name='anime')
    async def anime(self, ctx, tag=None):
        if tag == None:
            response = requests.get(
                "https://safebooru.org/index.php?page=dapi&s=post&q=index&limit=100")
        else:
            payload = {'tags': tag}
            response = requests.get(
                "https://safebooru.org/index.php?page=dapi&s=post&q=index&limit=100", params=payload)
        response = xmltodict.parse(response.text)
        art = random.choice(response['posts']['post'])
        url = art['@file_url']
        embed = discord.Embed(color=0xac00e6)
        embed.set_image(url=url)
        await ctx.send(embed=embed)
