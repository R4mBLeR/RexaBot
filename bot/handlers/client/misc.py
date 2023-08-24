from discord.ext import commands
import random


class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='flip')
    async def flip(self, ctx):
        await ctx.send(random.choice(['Орёл', 'Решка']))

    @commands.command(name='random')
    async def rand(self, ctx):
        await ctx.send(random.randint(1, 100))

    @commands.command(name='randrange')
    async def randrange(self, ctx, a: int, b: int):
        await ctx.send(random.randint(a, b))
