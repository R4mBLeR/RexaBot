import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord import Member
from discord.utils import get
from asyncio import sleep


def setup(bot: commands.Bot):
    print('admin is setup')

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
