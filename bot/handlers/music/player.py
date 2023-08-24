import discord
from yt_dlp import YoutubeDL
from asyncio import sleep


YDL_OPTIONS = {'format': 'bestaudio', 'skip_download': 'True', 'extract_flat': True,
               'simulate': 'True', 'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

queues = {}
players = {}
music = {}


def download_song(song_url):
    with YoutubeDL(YDL_OPTIONS) as ydlp:
        info = ydlp.extract_info(song_url, download=False)
    return info


class Song:
    def __init__(self, url, title, duration, SourceUrl, download):
        self.url = url
        self.title = title
        self.duration = "%02d:%02d" % (duration // 60, duration % 60)
        self.SourceUrl = SourceUrl
        self.download = download


async def PlayMusic(ctx, player):
    id = player.guild.id
    while len(queues[id]) > 0:
        song = queues[id][0]
        if not song.download:
            song.SourceUrl = download_song(
                song.url)['url']
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
