import discord
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from collections import deque
from discord.ext import commands
from discord.ext import tasks


class YomiageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.binds = {}
        self.queues = {}
        self.url_prefix = "https://www.yukumo.net/api/v2/aqtk1/koe.mp3?type=f1&kanji="
        self.dir = Path("yomiage")

        self.dir.mkdir(exist_ok=True)
        self.audio_player.start()

    def cog_check(self, ctx):
        return ctx.guild

    def get_voice_client(self, vc_id):
        vclients = self.bot.voice_clients
        return discord.utils.find(lambda c: c.channel.id == vc_id, vclients)

    async def get_audio(self, text):
        print(f"音声の取得中: {text}")

        url = self.url_prefix + urllib.parse.quote(text)
        fname = str(uuid.uuid4()) + ".mp3"
        p = self.dir / fname
        urllib.request.urlretrieve(url, p)
        src = await discord.FFmpegOpusAudio.from_probe(p)

        def after(error):
            p.unlink(missing_ok=True)

        return text, src, after

    @tasks.loop(seconds=0.2)
    async def audio_player(self):
        if not self.bot.is_ready():
            return

        for vc_id in self.queues.keys():
            vclient = self.get_voice_client(vc_id)

            if not vclient or not vclient.is_connected():
                continue

            if vclient.is_playing():
                continue

            q = self.queues[vc_id]
            if q:
                audio = q.popleft()
                text, src, after = audio

                print(f"再生中: {text}")
                vclient.play(src, after=after)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for vc_id in [k for k, v in self.binds.items() if message.channel.id in v]:
            vclient = self.get_voice_client(vc_id)
            vc = vclient.channel

            audio = await self.get_audio(message.content)
            self.queues.setdefault(vc.id, deque([]))
            self.queues[vc.id].append(audio)

    @commands.command(help="チャットの読み上げを開始します。")
    async def yomi(self, ctx):
        if not ctx.author.voice:
            await ctx.send("まずボイスチャンネルに接続してください。")
            return

        vc = ctx.author.voice.channel

        if not ctx.guild.voice_client:
            await vc.connect()
            await ctx.send("ボイスチャンネルに接続しました。")

        self.binds.setdefault(vc.id, [])

        if ctx.channel.id not in self.binds[vc.id]:
            self.binds[vc.id].append(ctx.channel.id)
            await ctx.send(f"ボイスチャンネルと {ctx.channel.mention} をリンクさせました。")

    @commands.command(help="チャットの読み上げを終了します。")
    async def noyomi(self, ctx):
        if not ctx.author.voice:
            await ctx.send("まずボイスチャンネルに接続してください。")
            return

        vc = ctx.author.voice.channel
        vclient = self.get_voice_client(vc.id)

        if vclient and vclient.is_connected():
            await vclient.disconnect(force=True)
            await ctx.send("ボイスチャンネルから切断しました。")

        self.binds.pop(vc.id, None)

        for audio in self.queues.get(vc.id):
            _, src, after = audio
            src.cleanup()
            after(None)

        self.queues.pop(vc.id, None)
