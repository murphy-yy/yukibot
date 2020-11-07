import os
import subprocess
import tempfile
import urllib
from pathlib import Path
from queue import Queue
from xml.etree import ElementTree

import discord
import urllib3
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


class YukiBotTTS(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.data = {}
        self.emoji_t9n = {}

        http = urllib3.PoolManager()
        r = http.request(
            'GET', 'https://raw.githubusercontent.com/unicode-org/cldr/master/common/annotations/ja.xml')
        data = r.data.decode('utf-8')
        xml = ElementTree.fromstring(data)
        for a in xml.find('annotations').iter('annotation'):
            if a.attrib.get('type') == 'tts':
                self.emoji_t9n[a.attrib['cp']] = a.text

    def remember(self, vc, channel):
        self.data.setdefault(vc.id, {'channels': set([]), 'queue': Queue()})
        self.data[vc.id]['channels'].add(channel.id)

    def forget_all(self, vc):
        self.data.pop(vc.id, None)

    async def connect(self, vc):
        client = vc.guild.voice_client
        if client is None:
            await vc.connect()

    async def disconnect(self, vc):
        client = vc.guild.voice_client
        if client is not None:
            await client.disconnect()

    def get_vc(self, channel):
        for vc_id, value in self.data.items():
            if channel.id in value['channels']:
                return self.bot.get_channel(vc_id)

    def play(self, vc, audio=None):
        q = self.data[vc.id]['queue']
        client = vc.guild.voice_client

        if audio is not None:
            q.put(audio)

        if not client.is_connected() or client.is_playing():
            return

        if not q.empty():
            audio = q.get()
            client = vc.guild.voice_client
            client.play(audio, after=lambda l: self.play(vc))

    async def request(self, vc, text):
        for line in text.splitlines():
            if len(line.strip()) == 0:
                continue

            print(line)
            for emoji, t9n in self.emoji_t9n.items():
                line = line.replace(emoji, t9n)
            print(line)

            params = {}

            if len(line) > 20:
                params['speed'] = 100 + (len(line) - 20)

            if len(line) > 40:
                params['effect'] = 'echo'
                params['boyomi'] = 'true'

            params['type'] = 'f1'
            params['kanji'] = line

            qs = urllib.parse.urlencode(params)
            url = f'https://www.yukumo.net/api/v2/aqtk1/koe.mp3?{qs}'
            mp3 = Path(tempfile.NamedTemporaryFile(suffix='.mp3').name)

            try:
                urllib.request.urlretrieve(url, mp3)
            except urllib.error.HTTPError as e:
                print(e)
                continue

            audio = await discord.FFmpegOpusAudio.from_probe(mp3)
            self.play(vc, audio)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        vc = self.get_vc(message.channel)
        if vc is not None:
            await self.request(vc, message.content)

    @commands.command(help='チャットの読み上げを開始します。')
    @commands.check(guild_only)
    async def yomi(self, ctx):
        vc = ctx.author.voice.channel if ctx.author.voice else None

        if vc is None:
            await ctx.send('まずボイスチャンネルに接続してください。')
        else:
            self.remember(vc, ctx.channel)
            await self.connect(vc)
            await ctx.send(f'{vc.name} にて {ctx.channel.mention} の読み上げを開始しました。 :sound:')

    @commands.command(help='チャットの読み上げを終了します。')
    @commands.check(guild_only)
    async def noyomi(self, ctx):
        vc = ctx.author.voice.channel if ctx.author.voice else None

        if vc is None:
            await ctx.send('まずボイスチャンネルに接続してください。')
        else:
            await self.disconnect(vc)
            self.forget_all(vc)
            await ctx.send(f'{vc.name} の読み上げを終了しました。 :pleading_face:')


class YukiBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.color_role_name = 'すごい染料'

    @commands.Cog.listener()
    async def on_ready(self):
        game = discord.Game('v5 | 動画切り抜きコマンドの追加')
        await self.bot.change_presence(activity=game)

        print(f'{self.bot.user} でログイン完了！')

        app_info = await self.bot.application_info()
        self.owner = app_info.owner
        print(f'オーナーは {self.owner} です！')

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

    @commands.command(usage='<動画ソース> <秒数>', help='5秒間の動画切り抜きを作成します。 例: /p5 JGwWNGJdvx8 3:30')
    async def p5(self, ctx, src, start_time):
        full = Path(tempfile.NamedTemporaryFile(suffix='.mp4').name)
        edited = Path(tempfile.NamedTemporaryFile(suffix='.mp4').name)

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
bot.add_cog(YukiBotTTS(bot))
bot.run(token)
