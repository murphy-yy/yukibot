import pathlib
import subprocess
import tempfile

import discord
from discord.ext import commands


class YouTube(commands.Cog):

    @commands.command(usage='<動画ソース> <秒数>', help='5秒間の動画切り抜きを作成します。 例: /p5 JGwWNGJdvx8 3:30')
    async def p5(self, ctx, src, start_time):
        full = pathlib.Path(tempfile.NamedTemporaryFile(suffix='.mp4').name)
        edited = pathlib.Path(tempfile.NamedTemporaryFile(suffix='.mp4').name)

        progress = await ctx.send('ダウンロード中...')
        subprocess.check_call(
            f'youtube-dl -f best -o {full} -- {src}', shell=True)

        await progress.edit(content='変換中...')
        subprocess.check_call(
            f'ffmpeg -ss {start_time} -i {full} -t 0:05 {edited}', shell=True)

        await progress.delete()

        upload = discord.File(edited)
        await ctx.send(file=upload)
