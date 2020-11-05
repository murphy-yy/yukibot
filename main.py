import os
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

import discord
from colour import Color
from discord.ext import commands
from tenacity import retry, stop_after_attempt


class Worker(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.help_msg = Path('help.txt').read_text()
        self.color_role_name = 'すごい染料'

    @commands.Cog.listener()
    async def on_ready(self):
        game = discord.Game('v5-beta1 | 動画切り抜きコマンドの追加')
        await self.bot.change_presence(activity=game)

        print(f'{self.bot.user} でログイン完了！')

        app_info = await self.bot.application_info()
        self.owner = app_info.owner
        print(f'オーナーは {self.owner} です！')

    @commands.command()
    async def help(self, ctx):
        await ctx.send(self.help_msg)

    @commands.command()
    async def stop(self, ctx):
        if ctx.author.id == self.owner.id:
            await ctx.send('ボットを停止しています。 :scream:')
            await self.bot.logout()
        else:
            await ctx.send(f'このボットのオーナー {self.owner.mention} にお願いしてください。 :weary:')

    @commands.command()
    async def im(self, ctx, nick=None):
        if ctx.guild is None:
            return

        bot_member = ctx.guild.get_member(self.bot.user.id)
        await bot_member.edit(nick=nick)

        if nick is None:
            await ctx.send(f'ボットの名前がリセットされました。 :cold_sweat:')
        else:
            await ctx.send(f'私は「{bot_member.nick}」になりました。')

    @commands.command()
    async def color(self, ctx, value: Color = None):
        if ctx.guild is None:
            return

        async def clear():
            for r in ctx.author.roles:
                if r.name == self.color_role_name:
                    await r.delete()

        if value is None:
            await clear()
            await ctx.send('名前の色がリセットされました。 :sparkles:')
        else:
            color32 = int(value.get_hex_l().replace('#', '', 1), 16)
            color = discord.Colour(color32)
            await clear()
            role = await ctx.guild.create_role(name=self.color_role_name, colour=color)
            await ctx.author.add_roles(role)
            await ctx.send(f'名前の色を {value.get_hex_l()} ({color32}) に変更しました。 :paintbrush:')

    @commands.command()
    async def p5(self, ctx, src, start_time):
        full = Path(NamedTemporaryFile(suffix='.mp4').name)
        edited = Path(NamedTemporaryFile(suffix='.mp4').name)

        x1 = f'youtube-dl -f best -o {full} -- {src}'
        x2 = f'ffmpeg -ss {start_time} -i {full} -t 0:05 {edited}'

        @retry(stop=stop_after_attempt(5))
        async def download():
            print(x1)
            subprocess.check_call(x1, shell=True)

        progress = await ctx.send('ダウンロード中...')
        await download()

        await progress.edit(content='変換中...')
        print(x2)
        subprocess.check_call(x2, shell=True)

        await progress.delete()
        upload = discord.File(edited)
        await ctx.send(file=upload)


token = os.environ['TOKEN']
bot = commands.Bot('/', help_command=None)
bot.add_cog(Worker(bot))
bot.run(token)
