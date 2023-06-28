from discord.ext import commands
import random


def setup(bot: commands.Bot):
    print('misc is setup')

    @bot.command(name='flip')
    async def flip(ctx):
        await ctx.send(random.choice(['Орёл', 'Решка']))

    @bot.command(name='random')
    async def rand(ctx):
        await ctx.send(random.randint(1, 100))

    @bot.command(name='randrange')
    async def randrange(ctx, a: int, b: int):
        await ctx.send(random.randint(a, b))
