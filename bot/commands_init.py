from discord.ext import commands
from handlers.client import misc, img
from handlers.music import player


def init(bot: commands.Bot):
    misc.setup(bot)
    img.setup(bot)
    player.setup(bot)
