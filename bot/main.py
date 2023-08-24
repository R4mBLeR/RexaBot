import config
import discord
from discord.ext import commands
from handlers.client.img import Img
from handlers.client.misc import Misc
from handlers.music.commands import MusicCommands
from discord.ext.commands import CommandNotFound

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)


def cogs_init():
    bot.add_cog(Img(bot))
    bot.add_cog(Misc(bot))
    bot.add_cog(MusicCommands(bot))


@bot.event
async def on_ready():
    cogs_init()
    print('Бот запущен')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

if (__name__ == "__main__"):
    bot.run(config.TOKEN)
