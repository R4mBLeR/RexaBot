import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
from asyncio import sleep
import asyncio
from .utils import Song, YDL_OPTIONS, FFMPEG_OPTIONS

queues = {}
players = {}
music = {}


async def PlayMusic(ctx, player):
    id = player.guild.id
    while len(queues[id]) > 0:
        song = queues[id][0]
        player.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/ffmpeg.exe",
                                           source=song.SourceUrl, **FFMPEG_OPTIONS))
        embed = discord.Embed(
            title=f'Сейчас играет: {song.title}', description=song.url, colour=0x00FF00)
        embed.set_footer(text=song.duration)
        await ctx.send(embed=embed)
        while player.is_playing() or player.is_paused():
            await sleep(1)
        queues[id].pop(0)


async def get_player(ctx):
    if (ctx.guild.id not in players):
        players[ctx.guild.id] = await ctx.message.author.voice.channel.connect()
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    return players[ctx.guild.id]


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


async def send_embed(ctx, title, color):
    embed = discord.Embed(
        title=title, colour=color)
    await ctx.send(embed=embed)


def setup(bot: commands.Bot):

    @bot.command(name='play')
    async def play(ctx, *, URL: str = None):
        if not await ctx_in_voice(ctx):
            return
        if URL == None:
            await ctx.send('Укажите ссылку или название песни')
            return
        player = await get_player(ctx)
        if not player.channel.id == ctx.message.author.voice.channel.id:
            if len(player.channel.members) == 1 or len(queues[player.guild.id]) == 0:
                music[ctx.guild.id].cancel()
                players[ctx.guild.id].stop()
                await players[ctx.guild.id].disconnect()
                players.pop(ctx.guild.id)
                queues.pop(ctx.guild.id)
                player = await get_player(ctx)
            else:
                await send_embed(ctx, 'Музыка играет в другом канале', 0xFF0000)
                return
        if not URL.startswith('https'):
            videosSearch = VideosSearch(URL, limit=1)
            URL = videosSearch.result()['result'][0]['link']
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(URL, download=False)
        SourceUrl = info['formats'][0]['url']
        title = info.get('title', None)
        duration = info.get('duration', None)
        song = Song(URL, title, duration, SourceUrl)
        queues[player.guild.id].append(song)
        if not player.is_playing() and not player.is_paused():
            music[ctx.guild.id] = asyncio.create_task(PlayMusic(ctx, player))
        else:
            embed = discord.Embed(
                title=f'Добавлено в очередь: {title}', description=URL, colour=0xDE6D07)
            embed.set_footer(text="%02d:%02d" %
                             (duration // 60, duration % 60))
            await ctx.send(embed=embed)
    # music control commands

    @bot.command(name='pause')
    async def pause(ctx):
        if not await ctx_in_voice(ctx):
            return
        if not await bot_in_ctx_voice(ctx):
            return
        player = await get_player(ctx)
        if player.is_playing():
            await send_embed(ctx, 'Пауза поставлена', 0x00FF00)
            player.pause()
        elif player.is_paused():
            await send_embed(ctx, 'Музыка уже на паузе', 0xFF0000)
        elif len(queues[player.guild.id]) == 0:
            await send_embed(ctx, 'Музыка сейчас не играет', 0xFF0000)

    @bot.command(name='resume')
    async def resume(ctx):
        if not await ctx_in_voice(ctx):
            return
        if not await bot_in_ctx_voice(ctx):
            return
        player = await get_player(ctx)
        if player.is_paused():
            await send_embed(ctx, 'Проигрывание трека возобновлено', 0x00FF00)
            player.resume()
        elif player.is_playing():
            await send_embed(ctx, 'Проигрывание уже возобновлено', 0xFF0000)
        elif len(queues[player.guild.id]) == 0:
            await send_embed(ctx, 'Музыка сейчас не играет', 0xFF0000)

    @bot.command(name='skip')
    async def stop(ctx):
        if not await ctx_in_voice(ctx):
            return
        if not await bot_in_ctx_voice(ctx):
            return
        player = await get_player(ctx)
        if len(queues[player.guild.id]) > 0:
            song = queues[player.guild.id][0]
            embed = discord.Embed(
                title='Песня скипнута:', description=song.title, colour=0xFF0000)
            player.stop()
            await ctx.send(embed=embed)
        elif len(queues[player.guild.id]) == 0:
            await send_embed(ctx, 'Музыка сейчас не играет', 0xFF0000)

    @bot.command(name='song')
    async def song(ctx):
        if not ctx.guild.id in queues:
            await send_embed(ctx, 'Музыка сейчас не играет', 0xFF0000)
        else:
            song = queues[ctx.guild.id][0]
            embed = discord.Embed(title='Текущая песня:',
                                  description=f'{song.title}\n{song.url}', colour=0x00FF00)
            embed.set_footer(text=f'Длительность {song.duration}')
            await ctx.send(embed=embed)

    @bot.command(name='queue')
    async def _queue(ctx):
        queue_ = ""
        if not ctx.guild.id in queues or len(queues[ctx.guild.id]) == 0:
            embed = discord.Embed(
                title='Очередь пуста', colour=0xFF0000)
            await ctx.send(embed=embed)
        else:
            for i in range(len(queues[ctx.guild.id])):
                song = queues[ctx.guild.id][i]
                queue_ = queue_+song.title+'          '+song.duration+'\n'
            embed = discord.Embed(
                title='Текущая очередь:', description=queue_, colour=0x00FF00)
            await ctx.send(embed=embed)

    @bot.command(name='disconnect')
    async def disconnect(ctx):
        if not await ctx_in_voice(ctx):
            return
        if not await bot_in_ctx_voice(ctx):
            return
        else:
            player = await get_player(ctx)
            await get_player(ctx)
            player.stop()
            queues[ctx.guild.id] = []
            await player.disconnect()
            players.pop(ctx.guild.id)
