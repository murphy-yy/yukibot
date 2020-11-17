import colour
import discord
from discord.ext import commands

import commands_better


class YukiBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.playing = 'v5 | 動画切り抜きコマンドの追加'
        self.color_role_name = 'すごい染料'

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} ({self.bot.user.id}) としてのログインが完了！')

        game = discord.Game(self.playing)
        await self.bot.change_presence(activity=game)
        print(f'プレイ中のゲームを "{self.playing}" に変更しました。')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send(f'エラーが発生しました。{error}')

    @commands.command(help='このボットを終了します。')
    @commands.check(commands_better.owner_only)
    async def stop(self, ctx):
        await ctx.send('ボットを停止しています。 :scream:')
        await ctx.bot.logout()

    @commands.command(usage='[ニックネーム]', help='サーバー内でのボットの名前を変更します。')
    @commands.check(commands_better.guild_only)
    async def im(self, ctx, name: str = None):
        await ctx.me.edit(nick=name)

        if ctx.me.nick is None:
            await ctx.send('ボットの名前がリセットされました。 :cold_sweat:')
        else:
            await ctx.send(f'私は「{ctx.me.nick}」になりました。')

    @commands.command(usage='[カラーコード]', help='サーバー内での名前の色を変更します。 例: /color #ff0000')
    @commands.check(commands_better.guild_only)
    async def color(self, ctx, color_object: str = None):
        color_roles = [r for r in ctx.author.roles
                       if r.name == self.color_role_name]

        if color_object is None:
            for r in color_roles:
                await r.delete()

            await ctx.send('名前の色がリセットされました。 :sparkles:')
        else:
            color_input = colour.Color(color_object)
            color_value = int(color_input.get_hex_l()[1:], 16)
            color = discord.Color(color_value)

            if len(color_roles) > 0:
                role = color_roles.pop(0)
                await role.edit(color=color)
            else:
                role = await ctx.guild.create_role(name=self.color_role_name, color=color)
                await ctx.author.add_roles(role)

            await ctx.send(f'名前の色を {color_input.get_hex_l()} ({color_value}) に変更しました。 :paintbrush:')
