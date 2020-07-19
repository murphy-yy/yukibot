from colour import Color
from discord.ext import commands


class ColorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_name = "すごい染料"

    def get_color(self, text):
        try:
            return Color(text)
        except ValueError:
            pass

    def rgb2int(self, rgb):
        r, g, b = rgb
        return (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)

    @commands.command(help="名前に色を付けます。")
    async def color(self, ctx):
        await ctx.send("何色にしますか？\n<https://www.google.com/search?q=color+picker>")

        def check(re):
            return (
                re.author.id == ctx.author.id
                and re.channel.id == ctx.channel.id
                and self.get_color(re.content)
            )

        re = await self.bot.wait_for("message", check=check)
        color = self.get_color(re.content)
        hex_l = color.get_hex_l()
        int_color = self.rgb2int(color.get_rgb())
        await ctx.send(f"名前の色を {hex_l} ({int_color}) に変更しました。 (テスト)")

