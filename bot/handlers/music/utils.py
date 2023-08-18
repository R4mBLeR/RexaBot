from asyncio import sleep
import discord
from yt_dlp import YoutubeDL


YDL_OPTIONS = {'format': 'bestaudio', 'skip_download': 'True', 'extract_flat': True,
               'simulate': 'True', 'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

queues = {}
players = {}
music = {}


class Song:
    def __init__(self, url, title, duration, SourceUrl, download):
        self.url = url
        self.title = title
        self.duration = "%02d:%02d" % (duration // 60, duration % 60)
        self.SourceUrl = SourceUrl
        self.download = download


def download_song(song_url):
    with YoutubeDL(YDL_OPTIONS) as ydlp:
        info = ydlp.extract_info(song_url, download=False)
    return info['url']


def add_song(video, guild_id, download):
    if download:
        webpage_url = video['webpage_url']
        SourceUrl = video['url']
    else:
        webpage_url = video['url']
        SourceUrl = None
    title = video['title']
    duration = video['duration']
    song = Song(webpage_url, title, duration, SourceUrl, download)
    queues[guild_id].append(song)


async def PlayMusic(ctx, player):
    id = player.guild.id
    while len(queues[id]) > 0:
        song = queues[id][0]
        if not song.download:
            song.SourceUrl = download_song(
                song.url)
            song.download = True
        player.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/ffmpeg.exe",
                                           source=song.SourceUrl, **FFMPEG_OPTIONS))
        embed = discord.Embed(
            title=f'Сейчас играет: {song.title}', description=song.url, colour=0x00FF00)
        embed.set_footer(text=song.duration)
        await ctx.send(embed=embed)
        while player.is_playing() or player.is_paused():
            await sleep(1)
        queues[id].pop(0)


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
