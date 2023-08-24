import discord
from .player import Song, queues, players, music


def add_song(video, guild_id, download):
    if download:
        webpage_url = video['webpage_url']
        SourceUrl = video['url']
    else:
        webpage_url = video['url']
        SourceUrl = None
    title = video['title']
    try:
        duration = video['duration']
    except:
        duration = 0
    song = Song(webpage_url, title, duration, SourceUrl, download)
    queues[guild_id].append(song)


async def can_call_command(ctx):
    if not await ctx_in_voice(ctx):
        return False
    if not await bot_in_ctx_voice(ctx):
        return False
    if not await bot_is_playing(ctx):
        return False
    else:
        return True


async def get_player(ctx):
    if (ctx.guild.id not in players):
        players[ctx.guild.id] = await ctx.message.author.voice.channel.connect()
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    return players[ctx.guild.id]


async def disconnect_player(ctx):
    music[ctx.guild.id].cancel()
    players[ctx.guild.id].stop()
    await players[ctx.guild.id].disconnect()
    players.pop(ctx.guild.id)
    queues.pop(ctx.guild.id)


async def ctx_in_voice(ctx):
    if not ctx.message.author.voice:
        await send_embed(ctx, 'Вы не в голосовом канале', 0xFF0000)
        return False
    else:
        return True


async def bot_in_ctx_voice(ctx):
    if not ctx.guild.id in players or not players[ctx.guild.id].channel.id == ctx.message.author.voice.channel.id:
        await send_embed(ctx, 'Бот не находится в этом канале', 0xFF0000)
        return False
    else:
        return True


async def bot_is_playing(ctx):
    if not await bot_in_ctx_voice(ctx):
        return
    if len(queues[ctx.guild.id]) == 0 or not ctx.guild.id in queues:
        await send_embed(ctx, 'Музыка сейчас не играет', 0xFF0000)
        return False
    else:
        return True


async def send_embed(ctx, title, color):
    embed = discord.Embed(
        title=title, colour=color)
    await ctx.send(embed=embed)
