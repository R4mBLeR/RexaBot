import config
import discord
from discord.ext import commands
from commands_init import init

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)


@bot.event
async def on_ready():
    init(bot)
    print('Бот запущен')


if (__name__ == "__main__"):
    bot.run(config.TOKEN)
