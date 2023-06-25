import pprint
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord import Member
from discord.utils import get
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
from asyncio import sleep
import random
import config
import xmltodict
import requests

bot = commands.Bot(command_prefix='>')

YDL_OPTIONS = {'format': 'worstaudio/best',
               'noplaylist': 'True', 'simulate': 'True', 'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
queue = []


class Songs:
    def __init__(self, url, title, duration, SourceUrl):
        self.url = url
        self.title = title
        self.duration = "%02d:%02d" % (duration // 60, duration % 60)
        self.SourceUrl = SourceUrl


@bot.event
async def on_ready():
    print('Бот запущен')


# Music block
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
    song = Songs(URL, title, duration, SourceUrl)
    queue.append(song)

    if not vc.is_playing() and not vc.is_paused():
        await PlayMusic(ctx)
    else:
        embed = discord.Embed(
            title=f'Добавлено в очередь: {title}', description=URL, colour=0xDE6D07)
        embed.set_footer(text="%02d:%02d" % (duration // 60, duration % 60))
        await ctx.send(embed=embed)


async def PlayMusic(ctx):
    while len(queue) > 0:
        song = queue[0]
        vc.play(discord.FFmpegPCMAudio(
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


# command block
@bot.command(name='ban')
@has_permissions(ban_members=True)
async def ban(ctx, member: Member = None, *, reason=None):
    if member == None:
        await ctx.send('Укажите пользователя')
        return
    if reason == None:
        await ctx.send('Укажите причину для бана')
        return
    await member.send(f'Вы были забанены на сервере {ctx.guild.name} по причине: {reason}')
    await ctx.send(f'{member.mention} был забанен {ctx.author.mention} по причине: {reason}')
    await member.ban(reason=reason)


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("Недостаточно прав для выполнения данной команды")


@bot.command(name='kick')
@has_permissions(kick_members=True)
async def kick(ctx, member: Member = None, *, reason=None):
    if member == None:
        await ctx.send('Укажите пользователя')
        return
    if reason == None:
        await ctx.send('Укажите причину кика')
        return
    await member.send(f'Вы были кикнуты на сервере {ctx.guild.name} по причине: {reason}')
    await ctx.send(f'{member.mention} был кикнут {ctx.author.mention} по причине: {reason}')
    await member.kick(reason=reason)


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("Недостаточно прав для выполнения данной команды")


@bot.command(name='unban')
@has_permissions(ban_members=True)
async def unban(ctx, *, member: str):
    if member.startswith('@'):
        member = member.replace('@', '')
    banned_users = await ctx.guild.bans()

    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')


@kick.error
async def unban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("Недостаточно прав для выполнения данной команды")
times = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400,
    'w': 604800,
}


@bot.command(name='mute', pass_context=True)
@has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, amout: str, *, reason=None):
    role = get(ctx.guild.roles, name='Muted')
    time = times[amout[len(amout)-1]]
    amout = amout.replace(amout[len(amout)-1], "")
    await member.add_roles(role)
    if reason == None:
        await ctx.send(f"{member.mention} был замучен {ctx.author.mention}")
        return
    await ctx.send(f"{member.mention} был замучен {ctx.author.mention} по причине: {reason}")
    await sleep(int(amout)*time)
    await member.remove_roles(role)


@mute.error
async def mute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("Недостаточно прав для выполнения данной команды")


@bot.command(name='unmute', pass_context=True)
@has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = get(ctx.guild.roles, name='Muted')
    await member.remove_roles(role)
    await ctx.send(f"{member.mention} был размучен {ctx.author.mention}")


@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("Недостаточно прав для выполнения данной команды")


@bot.command(name="clear")
@has_permissions(manage_messages=True)
async def clear(ctx, amount: int = None):
    if amount == None:
        await ctx.send('Укажите кол-во сообщений для удаления')
        return
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send('Успешно удалено {} сообщений'.format(amount))
    await sleep(1)
    await ctx.channel.purge(limit=1)


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("Недостаточно прав для выполнения данной команды")

# fun commands


@bot.command(name='flip')
async def flip(ctx):
    await ctx.send(random.choice(['Орёл', 'Решка']))


@bot.command(name='random')
async def rand(ctx, a=0, b=0):
    if a == 0:
        await ctx.send('Твоё случайное число: ', random.randint(1, 100))
        return
    if b == 0:
        await ctx.send('Твоё случайное число: ', random.randint(1, b))
        return
    await ctx.send('Твоё случайное число: ', random.randint(a, b))


@bot.command(name='gif')
async def gif(ctx, tag=None):
    if tag == None:
        response = requests.get(
            "https://g.tenor.com/v1/search?limit=50&key=O4UDCVI14VWL")
    else:
        payload = {'q': tag, 'key': "O4UDCVI14VWL"}
        response = requests.get(
            "https://g.tenor.com/v1/search?limit=50", params=payload)
    response = response.json()
    gif = random.choice(response["results"])
    url = gif['media'][0]['gif']['url']
    embed = discord.Embed(title=gif['content_description'], color=0x00ff00)
    embed.set_image(url=url)
    await ctx.send(embed=embed)


@bot.command(name='anime')
async def anime(ctx, tag=None):
    if tag == None:
        response = requests.get(
            "https://safebooru.org/index.php?page=dapi&s=post&q=index&limit=100")
    else:
        payload = {'tags': tag}
        response = requests.get(
            "https://safebooru.org/index.php?page=dapi&s=post&q=index&limit=100", params=payload)
    response = xmltodict.parse(response.text)
    art = random.choice(response['posts']['post'])
    url = art['@file_url']
    embed = discord.Embed(color=0xac00e6)
    embed.set_image(url=url)
    await ctx.send(embed=embed)

bot.run(config.TOKEN)
