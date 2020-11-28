import pathlib
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from queue import Queue

import discord
from discord.ext import commands

import commands_better


class Yomiage(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channels = {}
        self.sources = {}
        self.emojis = {}

        with tempfile.NamedTemporaryFile(suffix='.xml') as tmp:
            url = 'https://raw.githubusercontent.com/unicode-org/cldr/master/common/annotations/ja.xml'
            urllib.request.urlretrieve(url, tmp.name)
            root = ET.parse(tmp.name)
            for tts in [a for a in root.find('annotations').iter('annotation') if a.attrib.get('type') == 'tts'][57:]:
                self.emojis[tts.attrib['cp']] = tts.text

    def play(self, guild):
        if not (guild.voice_client and guild.voice_client.is_connected()) or guild.voice_client.is_playing():
            return

        queue = self.sources[guild.id]

        if not queue.empty():
            source = queue.get()
            guild.voice_client.play(source, after=lambda _: self.play(guild))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id not in (self.channels.get(message.guild.id) or []):
            return

        print(message)

        text = message.content
        for emoji, tts_text in self.emojis.items():
            text = text.replace(emoji, tts_text)

        encoded_text = urllib.parse.quote(text)
        url = f'https://www.yukumo.net/api/v2/aqtk1/koe.mp3?type=f1&kanji={encoded_text}'

        mp3 = pathlib.Path(tempfile.NamedTemporaryFile(suffix='.mp3').name)
        urllib.request.urlretrieve(url, mp3)
        source = await discord.FFmpegOpusAudio.from_probe(mp3)

        self.sources.setdefault(message.guild.id, Queue())
        self.sources[message.guild.id].put(source)

        self.play(message.guild)

    @commands.command(help='チャットの読み上げを開始します。')
    @commands.check(commands_better.guild_only)
    async def yomi(self, ctx):
        if not ctx.author.voice:
            await ctx.send('まずボイスチャンネルに接続してください。')
            return

        vc = ctx.author.voice.channel

        if not ctx.guild.voice_client:
            await vc.connect()

        self.channels.setdefault(ctx.guild.id, set([]))
        self.channels[ctx.guild.id].add(ctx.channel.id)
        print(self.channels)

        await ctx.send(f'{vc.name} にて {ctx.channel.mention} の読み上げを開始しました。 :sound:')

    @commands.command(help='チャットの読み上げを終了します。')
    @commands.check(commands_better.guild_only)
    async def noyomi(self, ctx):
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()

        self.channels.pop(ctx.guild.id, None)
        print(self.channels)

        await ctx.send(f'すべてのチャンネルの読み上げを終了しました。 :pleading_face:')
