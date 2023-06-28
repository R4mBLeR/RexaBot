from discord.ext import commands
from handlers.client import misc, img
from handlers.admin import admin
from handlers.music import player


def init(bot: commands.Bot):
    misc.setup(bot)
    img.setup(bot)
    admin.setup(bot)
    player.setup(bot)
