import discord
from discord.ext import commands
from discord.utils import get
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
from asyncio import sleep
from .utils import Song, YDL_OPTIONS, FFMPEG_OPTIONS

queue = []


async def PlayMusic(ctx):
    while len(queue) > 0:
        song = queue[0]
        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/ffmpeg.exe",
                                       source=song.SourceUrl, **FFMPEG_OPTIONS))
        embed = discord.Embed(
            title=f'Сейчас играет: {song.title}', description=song.url, colour=0x00FF00)
        embed.set_footer(text=song.duration)
        await ctx.send(embed=embed)
        while vc.is_playing() or vc.is_paused():
            await sleep(1)
        if not vc.is_playing():
            queue.pop(0)
    await sleep(60)
    print(len(queue))
    if len(queue) == 0:
        await vc.disconnect()


def setup(bot: commands.Bot):
    print('music is setup')

    @bot.command(name='play')
    async def play(ctx, *, URL: str = None):
        global vc
        global voice_channel
        if not ctx.message.author.voice:
            await ctx.send('Вы не в голосовом канале')
            return
        if URL == None:
            await ctx.send('Укажите ссылку')
            return

        try:
            Temp = voice_channel.id
        except NameError:
            voice_channel = ctx.message.author.voice.channel
            vc = await voice_channel.connect()

        if not vc.is_connected():
            voice_channel = ctx.message.author.voice.channel
            vc = await voice_channel.connect()
        if not vc.is_playing() and ctx.message.author.voice.channel.id != voice_channel.id:
            await vc.disconnect()
            voice_channel = ctx.message.author.voice.channel
            vc = await voice_channel.connect()
        elif ctx.message.author.voice.channel.id != voice_channel.id:
            await ctx.send('Музыка играет в другом канале')
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
        queue.append(song)

        if not vc.is_playing() and not vc.is_paused():
            await PlayMusic(ctx)
        else:
            embed = discord.Embed(
                title=f'Добавлено в очередь: {title}', description=URL, colour=0xDE6D07)
            embed.set_footer(text="%02d:%02d" %
                             (duration // 60, duration % 60))
            await ctx.send(embed=embed)

    # music control commands

    @bot.command(name='pause')
    async def pause(ctx):
        if voice_channel.id != ctx.message.author.voice.channel.id:
            await ctx.send('Вы не в голосовом канале')
        else:
            if vc.is_playing():
                vc.pause()
            elif vc.is_paused():
                await ctx.send('Музыка уже на паузе')
            elif len(queue) == 0:
                await ctx.send('Музыка сейчас не играет')

    @bot.command(name='resume')
    async def resume(ctx):
        if voice_channel.id != ctx.message.author.voice.channel.id:
            await ctx.send('Вы не в голосовом канале')
        else:
            if vc.is_paused():
                vc.resume()
            elif len(queue) == 0:
                await ctx.send('Музыка сейчас не играет')

    @bot.command(name='skip')
    async def stop(ctx):
        if voice_channel.id != ctx.message.author.voice.channel.id:
            await ctx.send('Вы не в голосовом канале')
        else:
            if len(queue) > 0:
                song = queue[0]
                embed = discord.Embed(
                    title='Песня скипнута:', description=song.title, colour=0xFF0000)
                vc.stop()
                await ctx.send(embed=embed)
            elif len(queue) == 0:
                await ctx.send('Музыка сейчас не играет')

    @bot.command(name='song')
    async def song(ctx):
        if len(queue) == 0:
            embed = discord.Embed(
                title='В данный момент музыка не воспроизводится', colour=0xFF0000)
            await ctx.send(embed=embed)
        else:
            song = queue[0]
            embed = discord.Embed(title='Текущая песня:',
                                  description=f'{song.title}\n{song.url}', colour=0x00FF00)
            embed.set_footer(text=f'Длительность {song.duration}')
            await ctx.send(embed=embed)

    @bot.command(name='queue')
    async def _queue(ctx):
        queue_ = ""
        if len(queue) == 0:
            embed = discord.Embed(
                title='Очередь пуста', colour=0xFF0000)
            await ctx.send(embed=embed)
        else:
            for i in range(len(queue)):
                song = queue[i]
                queue_ = queue_+song.title+'          '+song.duration+'\n'
            embed = discord.Embed(
                title='Текущая очередь:', description=queue_, colour=0x00FF00)
            await ctx.send(embed=embed)
