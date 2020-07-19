import discord
from colour import Color
from discord.ext import commands


class ColorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_name = "すごい染料"

    def cog_check(self, ctx):
        return ctx.guild

    def get_color(self, text):
        try:
            return Color(text)
        except ValueError:
            pass

    def rgb2int(self, rgb):
        r, g, b = rgb
        return (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)

    def color_roles_of(self, member):
        return [r for r in member.roles if r.name == self.role_name]

    def empty_color_roles(self, guild):
        return [r for r in guild.roles if r.name == self.role_name and not r.members]

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
        hx = color.get_hex_l()
        i = self.rgb2int(color.get_rgb())
        member = discord.utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)

        p = await ctx.send("`(1/3)` 古い権限を削除しています...")
        for r in self.color_roles_of(member):
            await r.delete()

        await p.edit(content="`(2/3)` 新しい権限を作成しています...")
        r = await ctx.guild.create_role(name=self.role_name, color=discord.Colour(i))

        await p.edit(content="`(3/3)` 権限を付与しています...")
        await member.add_roles(r)

        await p.edit(content=f"名前の色を {hx} ({i}) に変更しました。")

    @commands.command(help="名前の色をリセットします。")
    async def resetcolor(self, ctx):
        member = discord.utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)

        p = await ctx.send("色の権限を削除しています...")
        for r in self.color_roles_of(member):
            await r.delete()
        await p.edit(content="名前の色をリセットしました！")

    @commands.command(help="不要な色の権限を削除します。")
    async def cleanupcolor(self, ctx):
        p = await ctx.send("不要な色の権限を削除しています...")
        targets = self.empty_color_roles(ctx.guild)
        for r in targets:
            await r.delete()
        await p.edit(content=f"不要な {len(targets)} 個の {self.role_name} を削除しました。")
