#!/usr/bin/env python

import pprint
import string
import urllib.parse
import urllib.request
import asyncio
import glob
import os

import discord

from config import *
from collections import deque

yomiage_binds = {}

yomiage_queue = {}


async def reset_color(member):
    [await role.delete() for role in member.roles if role.name == COLOR_ROLE_NAME]


async def cleanup_color(guild):
    return len(
        [
            await role.delete()
            for role in guild.roles
            if role.name == COLOR_ROLE_NAME and not len(role.members)
        ]
    )


async def command_worker(botx, message, name, args):
    if name == "help":
        await message.channel.send(HELP_MESSAGE)

    if name == "stop":
        if message.author.id == botx.appinfo.owner.id:
            print(f"{message.author} からの命令により終了中...")
            await message.channel.send("ボットを終了しています...")
            await botx.logout()
        else:
            await message.channel.send("ボットを終了するにはこのボットの管理者である必要があります！")

    if name == "dump":
        if message.author.id == botx.appinfo.owner.id:
            pprint.PrettyPrinter(indent=4).pprint(globals())

    if name == "yomi":
        voice_state = lambda: message.author.voice

        if len(args) >= 1 and args[0] in ["start", "link"]:
            if voice_state():
                voice_channel = voice_state().channel
                voice_client = lambda: voice_channel.guild.voice_client

                if args[0] == "start":
                    if voice_client():
                        await message.channel.send("ボットは既に接続済みです。")
                    else:
                        await voice_channel.connect()
                        await message.channel.send("ボットの接続が完了しました。")

                if voice_client():
                    if message.channel.id in (
                        yomiage_binds.get(voice_channel.id) or []
                    ):
                        await message.channel.send(
                            f"既に ({voice_channel.mention}) へリンク済みです。"
                        )
                    else:
                        yomiage_binds.setdefault(voice_channel.id, set())
                        yomiage_binds[voice_channel.id].add(message.channel.id)
                        await message.channel.send(
                            f"現在のチャンネル ({message.channel.mention}) を ({voice_channel.mention}) へリンクしました。"
                        )
                elif args[0] == "link":
                    await message.channel.send("ボットが接続されていません。")
            else:
                await message.channel.send("ボイスチャンネルに接続してから実行してください。")

        if len(args) >= 1 and args[0] == "unlink":
            unlink_channel = lambda x: [
                y.remove(message.channel.id) for y in x if message.channel.id in y
            ]

            if voice_state():
                voice_channel = voice_state().channel

                unlink_channel([yomiage_binds.get(voice_channel.id) or set()])
                await message.channel.send(
                    f"({voice_channel.mention}) から ({message.channel.mention}) のリンクを解除しました。"
                )
            else:
                unlink_channel(yomiage_binds.values())
                await message.channel.send(
                    f"すべてのボイスチャンネルから ({message.channel.mention}) のリンクを解除しました。"
                )

        if len(args) >= 1 and args[0] == "stop":
            guild = voice_state().channel.guild if voice_state() else message.guild
            voice_client = lambda: guild.voice_client

            for voice_channel in [
                x for x in guild.voice_channels if x.id in yomiage_binds.keys()
            ]:
                yomiage_binds.pop(voice_channel.id)
                await message.channel.send(f"({voice_channel.mention}) のリンクを完全に削除しました。")

            if voice_client():
                await voice_client().disconnect()
                await message.channel.send("ボットの切断が完了しました。")

    if name == "color":
        member = discord.utils.find(
            lambda x: x.id == message.author.id, message.guild.members
        )

        if len(args) >= 1 and args[0] == "reset":
            await reset_color(member)
            await message.channel.send("名前の色をリセットしました！")
            return

        if len(args) >= 1 and args[0] == "cleanup":
            deleted = await cleanup_color(message.guild)
            await message.channel.send(f"不要な {deleted} 個の {COLOR_ROLE_NAME} を削除しました。")
            return

        await message.channel.send(
            "何色にしますか？6文字(HEX)で答えてください。\n<https://www.google.com/search?q=color+picker>"
        )

        def hex_color(content):
            raw = content[1:] if content.startswith("#") else content
            return (
                raw.upper()
                if raw.encode("utf-8").isalnum()
                and len(raw) == 6
                and all(x in set(string.hexdigits) for x in raw)
                else None
            )

        def reply_check(reply):
            return (
                reply.author.id == message.author.id
                and reply.channel.id == message.channel.id
                and hex_color(reply.content)
            )

        reply = await botx.wait_for("message", check=reply_check)
        color = hex_color(reply.content)

        await reset_color(member)
        role = await message.guild.create_role(
            name=COLOR_ROLE_NAME, color=discord.Colour(int(color, 16))
        )
        await member.add_roles(role)
        await message.channel.send(f"色を #{color} に変更しました。")


async def yomiage_queue_worker(botx):
    [os.remove(file) for file in glob.glob("*.mp3") if os.path.isfile(file)]

    while True:
        for voice_channel_id, dq in [(x, y) for x, y in yomiage_queue.items() if y]:
            filename = dq.popleft()

            voice_client = discord.utils.find(
                lambda x: x.channel.id == voice_channel_id, botx.voice_clients
            )

            while voice_client.is_playing():
                await asyncio.sleep(0.05)

            print(f"再生中: {filename}")
            source = await discord.FFmpegOpusAudio.from_probe(filename)
            voice_client.play(source)

            while voice_client.is_playing():
                await asyncio.sleep(0.05)

            print(f"削除中: {filename}")
            if os.path.isfile(filename):
                os.remove(filename)

        await asyncio.sleep(0.05)


class Bot(discord.Client):
    async def on_ready(self):
        user = self.user
        appinfo = await self.application_info()
        print(f"{user} でログイン完了！ (管理者: {appinfo.owner})")

        self.appinfo = appinfo

        await yomiage_queue_worker(self)

    async def on_message(self, message):
        if message.author.bot:
            return

        command = None

        if message.content.startswith(COMMAND_PREFIX):
            command = message.content[len(COMMAND_PREFIX) :]

        if message.content in MESSAGE_TO_COMMAND.keys():
            command = MESSAGE_TO_COMMAND[message.content]

        if command:
            print(f"コマンド {command} を {message.author} が実行しました。")
            commands = command.split()
            await command_worker(self, message, commands[0], commands[1:])
            return

        for voice_channel_id in [
            k for k, v in yomiage_binds.items() if message.channel.id in v
        ]:
            voice_client = discord.utils.find(
                lambda x: x.channel.id == voice_channel_id, self.voice_clients
            )
            voice_channel = voice_client.channel

            print(f"{message.author} の発言を読み上げています。")
            text = message.content
            print(f"  - {text}")
            encoded_text = urllib.parse.quote(text)
            print(f"    -> {encoded_text}")
            url = YOMIAGE_SOUND_URL.replace("<ENCODED_TEXT>", encoded_text)
            print(f"    -> {url}")
            filename = f"{message.id}.mp3"
            print(f"  - {filename}")

            print(f"ダウンロード中: {filename}")
            urllib.request.urlretrieve(url, filename)

            print(f"キューに追加: {filename}")
            yomiage_queue.setdefault(voice_channel.id, deque())
            yomiage_queue[voice_channel.id].append(filename)


print("ログイン中...")
bot = Bot()
bot.run(TOKEN)
