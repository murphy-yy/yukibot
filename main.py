import base64
import os
import sys
import tempfile

import colour
import discord
from discord_slash import SlashCommand, SlashCommandOptionType
from discord_slash.utils import manage_commands
from mcstatus import MinecraftServer

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, auto_register=True, auto_delete=True)

guild_ids = [int(id) for id in sys.argv[1:]]

if guild_ids:
    print(f"デバッグサーバー: {guild_ids}")

color_name = "すごい染料"


@client.event
async def on_ready():
    print(f"{client.user} ({client.user.id}) でログイン完了")


@client.event
async def on_slash_command_error(ctx, ex):
    await ctx.send(content=f"エラーが発生しました。\n```\n{ex}\n```")


@slash.slash(name="stop", guild_ids=guild_ids, description="ボットを終了します。")
async def _stop(ctx):
    await ctx.send(content=":scream: ボットを終了しています…", hidden=True)

    await client.logout()


def clean_description(o):
    if isinstance(o, dict):
        if "extra" in o.keys():
            return "".join(map(lambda x: x["text"], o["extra"]))
        else:
            return o["text"]
    else:
        return o


def extract_information(sample):
    return "\n".join(map(lambda p: p.name, sample or []))


@slash.slash(
    name="mcping",
    guild_ids=guild_ids,
    description="マイクラサーバーの接続をチェックします。",
    options=[
        manage_commands.create_option(
            "address", "サーバーのアドレス", SlashCommandOptionType.STRING, True
        )
    ],
)
async def _mcping(ctx, address):
    await ctx.send(content=f":tropical_drink: {address} に接続しています…", hidden=True)

    server = MinecraftServer.lookup(address)
    status = server.status()

    with tempfile.NamedTemporaryFile(suffix=".png") as fp:
        data = base64.b64decode(status.favicon[21:])
        fp.write(data)

        fav = await ctx.channel.send(file=discord.File(fp.name))

    embed = discord.Embed(title=f":white_check_mark: {address} の接続情報")
    embed.set_thumbnail(url=fav.attachments[0].url)
    embed.add_field(
        name="プレイヤー", value=f"{status.players.online} / {status.players.max}"
    )
    embed.add_field(name="バージョン", value=status.version.name or "なし")
    embed.add_field(
        name="説明", value=clean_description(status.description) or "なし", inline=False
    )
    embed.add_field(
        name="細かい説明", value=extract_information(status.players.sample) or "なし"
    )
    embed.set_footer(text=f"{status.latency} ms で処理が完了しました。")
    await ctx.send(content="", embeds=[embed])


@slash.slash(
    name="color",
    guild_ids=guild_ids,
    description="名前の色を変更します。",
    options=[
        manage_commands.create_option(
            "web_color",
            "名前の色 (例: #FF0000、red)",
            SlashCommandOptionType.STRING,
            True,
        )
    ],
)
async def _color(ctx, web_color):
    await ctx.send(content=f":triumph: 不要な染料を削除して新たに付与しています…", hidden=True)

    roles = [r for r in ctx.author.roles if r.name == color_name]
    print(f"編集中: {roles}")

    primary = roles.pop(0) if roles else None

    if roles:
        for role in roles:
            await role.delete()

    index = colour.Color(web_color)
    hex = index.get_hex_l()
    value = int(hex[1:], 16)
    color = discord.Color(value)

    if primary:
        await primary.edit(color=color)
    else:
        role = await ctx.guild.create_role(name=color_name, color=color)
        await ctx.author.add_roles(role)

    await ctx.send(content=f":paintbrush: 名前の色を {hex} ({value}) に変更しました。")


@slash.slash(name="resetcolor", guild_ids=guild_ids, description="名前の色をリセットします。")
async def _resetcolor(ctx):
    await ctx.send(content=f":cold_face: 全ての染料を削除しています…", hidden=True)

    roles = [r for r in ctx.author.roles if r.name == color_name]
    print(f"削除中: {roles}")

    for role in roles:
        await role.delete()

    await ctx.send(content=":sparkles: 名前の色がリセットされました。")


token = os.environ["TOKEN"]
client.run(token)
