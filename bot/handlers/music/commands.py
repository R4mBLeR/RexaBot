import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
import asyncio
from .utils import bot_is_playing, bot_in_ctx_voice, ctx_in_voice, can_call_command, get_player, send_embed, disconnect_player, add_song
from .player import PlayMusic, queues, music, download_song


class MusicCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='play')
    async def play(self, ctx, *, URL: str = None):
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
        info = download_song(URL)
        if '_type' in info:
            if info['_type'] == 'url':
                URL = info['url']
                info = download_song(URL)
            if info['_type'] == 'playlist':
                for video in info['entries']:
                    if not video['title'] == '[Deleted video]' and not video['uploader_id'] == None:
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

    @commands.command(name='pause')
    async def pause(self, ctx):
        if not await can_call_command(ctx):
            return
        player = await get_player(ctx)
        if player.is_playing():
            await send_embed(ctx, 'Пауза поставлена', 0x00FF00)
            player.pause()
        elif player.is_paused():
            await send_embed(ctx, 'Музыка уже на паузе', 0xFF0000)

    @commands.command(name='resume')
    async def resume(self, ctx):
        if not await can_call_command(ctx):
            return
        player = await get_player(ctx)
        if player.is_paused():
            await send_embed(ctx, 'Проигрывание трека возобновлено', 0x00FF00)
            player.resume()
        elif player.is_playing():
            await send_embed(ctx, 'Проигрывание уже возобновлено', 0xFF0000)

    @commands.command(name='skip')
    async def stop(self, ctx):
        if not await can_call_command(ctx):
            return
        player = await get_player(ctx)
        if len(queues[player.guild.id]) > 0:
            song = queues[player.guild.id][0]
            embed = discord.Embed(
                title='Песня скипнута:', description=song.title, colour=0xFF0000)
            player.stop()
            await ctx.send(embed=embed)

    @commands.command(name='song')
    async def song(self, ctx):
        if not await bot_is_playing(ctx):
            return
        else:
            song = queues[ctx.guild.id][0]
            embed = discord.Embed(title='Текущая песня:',
                                  description=song.title, colour=0x00FF00)
            embed.set_footer(text=song.duration)
            await ctx.send(embed=embed)

    @commands.command(name='queue')
    async def _queue(self, ctx):
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

    @commands.command(name='stop')
    async def disconnect(self, ctx):
        if not await ctx_in_voice(ctx):
            return
        if not await bot_in_ctx_voice(ctx):
            return
        else:
            await disconnect_player(ctx)
