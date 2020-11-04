import os
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

import discord
from discord.ext import commands
from tenacity import retry, stop_after_attempt


class Worker(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.help_msg = Path('help.txt').read_text()

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
