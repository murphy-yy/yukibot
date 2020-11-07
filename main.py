import os
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import quote
from urllib.request import urlretrieve

import discord
from colour import Color
from discord.ext import commands
from tenacity import retry, stop_after_attempt


async def guild_only(ctx):
    if ctx.guild is None:
        raise commands.CheckFailure('DMでこのコマンドは許可されていません。')
    return True


class YukiBotHelp(commands.DefaultHelpCommand):

    def __init__(self):
        super().__init__()
        self.no_category = 'カテゴリ未分類'
        self.command_attrs['help'] = 'このヘルプを表示します。'

    def get_ending_note(self):
        return (f'コマンドの詳細は {self.clean_prefix}{self.invoked_with} コマンド名 と入力してください。\n'
                f'カテゴリの詳細も {self.clean_prefix}{self.invoked_with} カテゴリ名 と入力することができます。')


class YukiBotTTS():

    def __init__(self, bot):
        self.bot = bot
        self.bind_map = {}
        self.queue = {}

    def remember(self, vc, channel):
        self.bind_map.setdefault(vc.id, set([]))
        self.bind_map[vc.id].add(channel.id)
        print(self.bind_map)

    def forgetAll(self, vc):
        self.bind_map.pop(vc.id, None)
        print(self.bind_map)

    async def connect(self, vc):
        client = vc.guild.voice_client
        if client is None:
            await vc.connect()

    async def disconnect(self, vc):
        client = vc.guild.voice_client
        if client is not None:
            await client.disconnect()

    def get_vc(self, channel):
        for vc_id in self.bind_map.keys():
            if channel.id in self.bind_map[vc_id]:
                return self.bot.get_channel(vc_id)

    def play(self, vc, audio=None):
        client = vc.guild.voice_client

        if audio is not None:
            self.queue.setdefault(vc.id, [])
            self.queue[vc.id].append(audio)

        print(self.queue)

        if not client.is_connected() or client.is_playing():
            return

        if len(self.queue[vc.id]) > 0:
            audio = self.queue[vc.id].pop(0)
            client = vc.guild.voice_client
            client.play(audio, after=lambda l: self.play(vc))

    def request(self, vc, text):
        lines = text.splitlines()
        for line in lines:
            effect = 'echo' if len(line) > 40 else 'none'
            boyomi = 'true' if len(line) > 40 else 'false'
            speed = 100 + (len(line) - 20) if len(line) > 20 else 100
            kanji = quote(line)

            url = ('https://www.yukumo.net/api/v2/aqtk1/koe.mp3'
                   '?type=f1'
                   f'&effect={effect}'
                   f'&boyomi={boyomi}'
                   f'&speed={speed}'
                   f'&kanji={kanji}')
            mp3 = Path(NamedTemporaryFile(suffix='.mp3').name)
            urlretrieve(url, mp3)

            audio = discord.FFmpegPCMAudio(mp3)
            self.play(vc, audio)


class YukiBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.color_role_name = 'すごい染料'
        self.tts = YukiBotTTS(self.bot)

    @commands.Cog.listener()
    async def on_ready(self):
        game = discord.Game('v5 | 動画切り抜きコマンドの追加')
        await self.bot.change_presence(activity=game)

        print(f'{self.bot.user} でログイン完了！')

        app_info = await self.bot.application_info()
        self.owner = app_info.owner
        print(f'オーナーは {self.owner} です！')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        vc = self.tts.get_vc(message.channel)
        if vc is not None:
            self.tts.request(vc, message.content)

    @commands.command(help='このボットを終了します。 (管理者のみ)')
    async def stop(self, ctx):
        if ctx.author.id == self.owner.id:
            await ctx.send('ボットを停止しています。 :scream:')
            await self.bot.logout()
        else:
            await ctx.send(f'このボットのオーナー {self.owner.mention} にお願いしてください。 :weary:')

    @commands.command(usage='[ニックネーム]', help='サーバー内でのボットの名前を変更します。')
    @commands.check(guild_only)
    async def im(self, ctx, nick=None):
        bot_member = ctx.guild.get_member(self.bot.user.id)
        await bot_member.edit(nick=nick)

        if nick is None:
            await ctx.send(f'ボットの名前がリセットされました。 :cold_sweat:')
        else:
            await ctx.send(f'私は「{bot_member.nick}」になりました。')

    @commands.command(usage='[カラーコード]', help='サーバー内での名前の色を変更します。 例: /color #ff0000')
    @commands.check(guild_only)
    async def color(self, ctx, value: Color = None):
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

    @commands.command(help='チャットの読み上げを開始します。')
    @commands.check(guild_only)
    async def yomi(self, ctx):
        vc = ctx.author.voice.channel if ctx.author.voice else None

        if vc is None:
            await ctx.send('まずボイスチャンネルに接続してください。')
        else:
            self.tts.remember(vc, ctx.channel)
            await self.tts.connect(vc)
            await ctx.send(f'{vc.name} にて {ctx.channel.mention} の読み上げを開始しました。 :sound:')

    @commands.command(help='チャットの読み上げを終了します。')
    @commands.check(guild_only)
    async def noyomi(self, ctx):
        vc = ctx.author.voice.channel if ctx.author.voice else None

        if vc is None:
            await ctx.send('まずボイスチャンネルに接続してください。')
        else:
            await self.tts.disconnect(vc)
            self.tts.forgetAll(vc)
            await ctx.send(f'{vc.name} の読み上げを終了しました。 :pleading_face:')

    @commands.command(usage='<動画ソース> <秒数>', help='5秒間の動画切り抜きを作成します。 例: /p5 JGwWNGJdvx8 3:30')
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
bot = commands.Bot('/', help_command=YukiBotHelp())
bot.add_cog(YukiBot(bot))
bot.run(token)
