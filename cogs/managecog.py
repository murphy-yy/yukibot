import pprint

from discord.ext import commands


class ManageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} でログイン完了！")

    @commands.command(help="このボットを終了します。 (管理者のみ)")
    async def stop(self, ctx):
        if await self.bot.is_owner(ctx.author):
            print(f"{ctx.author} からの命令により終了中...")
            await ctx.send("ボットを終了しています...")
            await self.bot.logout()
        else:
            await ctx.send("ボットを終了するにはこのボットの管理者である必要があります！")

    @commands.command(help="このボットのデバッグ情報をコンソールに出力します。 (管理者のみ)")
    async def dump(self, ctx):
        if await self.bot.is_owner(ctx.author):
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint([cog.__dict__ for cog in self.bot.cogs.values()])
