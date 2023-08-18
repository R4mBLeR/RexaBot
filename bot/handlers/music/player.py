import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
import asyncio
from .utils import YDL_OPTIONS, PlayMusic, disconnect_player
from .utils import bot_in_ctx_voice, bot_is_playing, can_call_command, ctx_in_voice, get_player, send_embed, add_song
from .utils import queues, music
from pprint import pprint


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
                await disconnect_player(ctx)
                player = await get_player(ctx)
            else:
                await send_embed(ctx, 'Музыка играет в другом канале', 0xFF0000)
                return
        if not URL.startswith('https'):
            videosSearch = VideosSearch(URL, limit=1)
            URL = videosSearch.result()['result'][0]['link']
        with YoutubeDL(YDL_OPTIONS) as ydlp:
            info = ydlp.extract_info(URL, download=False)
        if 'list' in URL:
            for video in info['entries']:
                add_song(video, player.guild.id, False)
        else:
            add_song(info, player.guild.id, True)
        if not player.is_playing() and not player.is_paused():
            music[ctx.guild.id] = asyncio.create_task(PlayMusic(ctx, player))
        else:
            title = queues[player.guild.id][len(
                queues[player.guild.id])-1].title
            duration = queues[player.guild.id][len(
                queues[player.guild.id])-1].duration
            if 'list' in URL:
                title = info['title']
                duration = ""
            embed = discord.Embed(
                title=f'Добавлено в очередь: {title}', description=URL, colour=0xDE6D07)
            embed.set_footer(text=duration)
            await ctx.send(embed=embed)
    # music control commands

    @bot.command(name='pause')
    async def pause(ctx):
        if not await can_call_command(ctx):
            return
        player = await get_player(ctx)
        if player.is_playing():
            await send_embed(ctx, 'Пауза поставлена', 0x00FF00)
            player.pause()
        elif player.is_paused():
            await send_embed(ctx, 'Музыка уже на паузе', 0xFF0000)

    @bot.command(name='resume')
    async def resume(ctx):
        if not await can_call_command(ctx):
            return
        player = await get_player(ctx)
        if player.is_paused():
            await send_embed(ctx, 'Проигрывание трека возобновлено', 0x00FF00)
            player.resume()
        elif player.is_playing():
            await send_embed(ctx, 'Проигрывание уже возобновлено', 0xFF0000)

    @bot.command(name='skip')
    async def stop(ctx):
        if not await can_call_command(ctx):
            return
        player = await get_player(ctx)
        if len(queues[player.guild.id]) > 0:
            song = queues[player.guild.id][0]
            embed = discord.Embed(
                title='Песня скипнута:', description=song.title, colour=0xFF0000)
            player.stop()
            await ctx.send(embed=embed)

    @bot.command(name='song')
    async def song(ctx):
        if not await bot_is_playing(ctx):
            return
        else:
            song = queues[ctx.guild.id][0]
            embed = discord.Embed(title='Текущая песня:',
                                  description=song.title, colour=0x00FF00)
            embed.set_footer(text=song.duration)
            await ctx.send(embed=embed)

    @bot.command(name='queue')
    async def _queue(ctx):
        queue_ = ""
        if not await bot_is_playing(ctx):
            return
        else:
            rand = len(queues[ctx.guild.id])
            footer = ""
            if rand > 10:
                rand = 10
                footer = f"и ещё {len(queues[ctx.guild.id])-10} песен"
            for i in range(rand):
                song = queues[ctx.guild.id][i]
                queue_ = queue_+song.title+'          '+song.duration+'\n'
            embed = discord.Embed(
                title='Текущая очередь:', description=queue_, colour=0x00FF00)
            embed.set_footer(text=footer)
            await ctx.send(embed=embed)

    @bot.command(name='stop')
    async def disconnect(ctx):
        if not await ctx_in_voice(ctx):
            return
        if not await bot_in_ctx_voice(ctx):
            return
        else:
            await disconnect_player(ctx)
