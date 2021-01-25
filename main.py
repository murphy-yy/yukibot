import argparse
import base64
import tempfile

import colour
import discord
from discord_slash import SlashCommand, SlashCommandOptionType
from discord_slash.utils import manage_commands
from mcstatus import MinecraftServer

parser = argparse.ArgumentParser()
parser.add_argument("--token", help="ボットのトークンを指定します", required=True)
parser.add_argument("--guild_id", help="ギルドIDを指定してコマンドの反映を高速化できます", nargs="+", type=int)
parser.add_argument("--color_name", help="染料の名前は、ほとんどの場合、変更する必要はありません", default="すごい染料")

args = parser.parse_args()

if args.guild_id:
    print(f"検証用サーバー: {args.guild_id}")

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, auto_register=True, auto_delete=True)


@client.event
async def on_ready():
    print(f"{client.user} ({client.user.id}) でログイン完了")


@client.event
async def on_slash_command_error(ctx, ex):
    await ctx.send(content=f"エラーが発生しました。\n```\n{ex}\n```")


@slash.slash(name="stop", guild_ids=args.guild_id, description="ボットを終了します。")
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
    guild_ids=args.guild_id,
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

    fav_b64_offset = len("data:image/png;base64,")
    fav_data = base64.b64decode(status.favicon[fav_b64_offset:])

    with tempfile.NamedTemporaryFile(suffix=".png") as fp:
        fp.write(fav_data)
        fav = await ctx.channel.send(file=discord.File(fp.name))

    fav_url = fav.attachments[0].url

    embed = discord.Embed(title=f":white_check_mark: {address} の接続情報")
    embed.set_thumbnail(url=fav_url)
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
    await ctx.send(embeds=[embed])


async def delete_roles(roles):
    for role in roles:
        print(f"削除中: {role} ({role.id})")
        await role.delete()


@slash.slash(
    name="color",
    guild_ids=args.guild_id,
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

    roles = [r for r in ctx.author.roles if r.name == args.color_name]

    primary = roles.pop(0) if roles else None

    await delete_roles(roles)

    index = colour.Color(web_color)
    hex = index.get_hex_l()
    value = int(hex[1:], 16)
    color = discord.Color(value)

    if primary:
        await primary.edit(color=color)
    else:
        role = await ctx.guild.create_role(name=args.color_name, color=color)
        await ctx.author.add_roles(role)

    await ctx.send(content=f":paintbrush: 名前の色を {hex} ({value}) に変更しました。")


@slash.slash(name="resetcolor", guild_ids=args.guild_id, description="名前の色をリセットします。")
async def _resetcolor(ctx):
    await ctx.send(content=f":cold_face: 全ての染料を削除しています…", hidden=True)

    roles = [r for r in ctx.author.roles if r.name == args.color_name]

    await delete_roles(roles)

    await ctx.send(content=":sparkles: 名前の色がリセットされました。")


client.run(args.token)
