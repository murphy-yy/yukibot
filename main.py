import argparse
import base64
import pathlib
import tempfile

import colour
import discord
from discord_slash import SlashCommand, SlashCommandOptionType
from discord_slash.utils import manage_commands

import minecraft_status
import proc

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


async def upload_base64_image(favicon, channel):
    offset = len("data:image/png;base64,")
    data = base64.b64decode(favicon[offset:])

    with tempfile.NamedTemporaryFile(suffix=".png") as fp:
        fp.write(data)
        uploaded = await channel.send(file=discord.File(fp.name))

    return uploaded.attachments[0].url


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

    status = await minecraft_status.connect(address)

    icon_url = await upload_base64_image(status.favicon, ctx.channel)

    embed = discord.Embed(title=f":white_check_mark: {address} の接続情報")
    embed.set_thumbnail(url=icon_url)
    embed.add_field(
        name="プレイヤー", value=f"{status.players.online} / {status.players.max}"
    )
    embed.add_field(name="バージョン", value=status.version.name or "なし")
    embed.add_field(name="説明", value=status.clean_description or "なし", inline=False)
    embed.add_field(name="細かい説明", value=status.information or "なし")
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


@slash.slash(
    name="vthumbnail",
    guild_ids=args.guild_id,
    description="動画のサムネイルを取得します。",
    options=[
        manage_commands.create_option(
            "url",
            "動画のURL",
            SlashCommandOptionType.STRING,
            True,
        )
    ],
)
async def _vthumbnail(ctx, url):
    await ctx.send(content=f":face_with_monocle: 動画のサムネイルを取得しています…", hidden=True)

    thumbnail = await proc.call(["youtube-dl", "--no-playlist", "--get-thumbnail", url])

    await ctx.send(content=thumbnail)


@slash.slash(
    name="vshot",
    guild_ids=args.guild_id,
    description="動画の指定された時間を一枚の画像にします。",
    options=[
        manage_commands.create_option(
            "url",
            "動画のURL",
            SlashCommandOptionType.STRING,
            True,
        ),
        manage_commands.create_option(
            "timestamp",
            "画像にする時間",
            SlashCommandOptionType.STRING,
            True,
        ),
    ],
)
async def _vshot(ctx, url, timestamp):
    await ctx.send(content=f":frame_photo: 画像を生成しています…", hidden=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        output = pathlib.Path(tmpdir, "image.jpg")

        await proc.call(
            [
                "youtube-dl",
                "--no-playlist",
                "-f",
                "(bestvideo/best)[height<=720]",
                "--exec",
                f"ffmpeg -y -ss {timestamp} -i {{}} -vframes 1 {output}; rm -f {{}}",
                url,
            ],
            cwd=tmpdir,
        )

        await ctx.channel.send(file=discord.File(output))


@slash.slash(
    name="vget",
    guild_ids=args.guild_id,
    description="動画を取得します。",
    options=[
        manage_commands.create_option(
            "url",
            "動画のURL",
            SlashCommandOptionType.STRING,
            True,
        ),
        manage_commands.create_option(
            "codec",
            "動画のフォーマット",
            SlashCommandOptionType.STRING,
            False,
            choices=[
                manage_commands.create_choice("m4a|mp4|mp4", "mp4 (m4a+mp4)"),
                manage_commands.create_choice("webm|webm|webm", "webm (webm+webm)"),
            ],
        ),
        manage_commands.create_option(
            "quality",
            "画質",
            SlashCommandOptionType.INTEGER,
            False,
            choices=[
                manage_commands.create_choice(144, "144p"),
                manage_commands.create_choice(240, "240p"),
                manage_commands.create_choice(360, "360p"),
                manage_commands.create_choice(480, "480p"),
                manage_commands.create_choice(720, "720p (HD)"),
                manage_commands.create_choice(1080, "1080p (HD)"),
            ],
        ),
        manage_commands.create_option(
            "crop",
            "切り抜きを行うかどうか",
            SlashCommandOptionType.BOOLEAN,
            False,
        ),
        manage_commands.create_option(
            "crop_start",
            "切り抜きを開始する時間 (例: 1:20)",
            SlashCommandOptionType.STRING,
            False,
        ),
        manage_commands.create_option(
            "crop_duration",
            "切り抜く期間 (例: 0:30)",
            SlashCommandOptionType.STRING,
            False,
        ),
    ],
)
async def _vget(
    ctx,
    url,
    codec="m4a|mp4|mp4",
    quality=360,
    crop=True,
    crop_start="0:00",
    crop_duration="0:30",
):
    await ctx.send(content=f":inbox_tray: 動画を取得しています…", hidden=True)

    acodec, vcodec, output_format = codec.split("|")

    with tempfile.TemporaryDirectory() as tmpdir:
        await proc.call(
            [
                "youtube-dl",
                "--no-playlist",
                "-f",
                f"bestvideo[ext={vcodec}][height<={quality}]+bestaudio[ext={acodec}]/best[ext={output_format}][height<={quality}]",
                "--merge-output-format",
                output_format,
                url,
            ],
            cwd=tmpdir,
        )

        workdir = pathlib.Path(tmpdir)

        if crop:
            for src in workdir.iterdir():
                await proc.call(
                    [
                        "ffmpeg",
                        "-ss",
                        crop_start,
                        "-i",
                        src,
                        "-to",
                        crop_duration,
                        "-async",
                        "1",
                        src.with_suffix("").name + "-cropped" + src.suffix,
                    ],
                    cwd=tmpdir,
                )
                src.unlink()

        for output in workdir.iterdir():
            await ctx.channel.send(file=discord.File(output))


client.run(args.token)
