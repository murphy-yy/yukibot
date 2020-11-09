import os
import pathlib
import tempfile
import traceback
import urllib
import xml.etree.ElementTree
from queue import Queue

import discord
from discord.ext import commands

import cog_youtube
import cog_yukibot
import commands_better


class YukiBotTTS(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.data = {}
        self.emoji_t9n = self.emoji_translation()

    def emoji_translation(self):
        url = 'https://raw.githubusercontent.com/unicode-org/cldr/master/common/annotations/ja.xml'
        data = urllib.request.urlopen(url).read().decode()
        root = xml.etree.ElementTree.fromstring(data)
        tags = root.find('annotations').iter('annotation')
        return {x.attrib['cp']: x.text for x in tags if x.attrib.get('type') == 'tts' and not x.attrib['cp'] in ['、', '。']}

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

            for emoji, t9n in self.emoji_t9n.items():
                line = line.replace(emoji, t9n)

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
            mp3 = pathlib.Path(tempfile.NamedTemporaryFile(suffix='.mp3').name)

            try:
                urllib.request.urlretrieve(url, mp3)
            except urllib.error.HTTPError:
                print(traceback.format_exc())
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
    @commands.check(commands_better.guild_only)
    async def yomi(self, ctx):
        vc = ctx.author.voice.channel if ctx.author.voice else None

        if vc is None:
            await ctx.send('まずボイスチャンネルに接続してください。')
        else:
            self.remember(vc, ctx.channel)
            await self.connect(vc)
            await ctx.send(f'{vc.name} にて {ctx.channel.mention} の読み上げを開始しました。 :sound:')

    @commands.command(help='チャットの読み上げを終了します。')
    @commands.check(commands_better.guild_only)
    async def noyomi(self, ctx):
        vc = ctx.author.voice.channel if ctx.author.voice else None

        if vc is None:
            await ctx.send('まずボイスチャンネルに接続してください。')
        else:
            await self.disconnect(vc)
            self.forget_all(vc)
            await ctx.send(f'{vc.name} の読み上げを終了しました。 :pleading_face:')


if __name__ == '__main__':
    token = os.environ['TOKEN']

    bot = commands.Bot('/', help_command=commands_better.Help())
    bot.add_cog(YukiBotTTS(bot))
    bot.add_cog(cog_yukibot.YukiBot(bot))
    bot.add_cog(cog_youtube.YouTube(bot))
    bot.run(token)
