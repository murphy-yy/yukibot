import pprint
from discord.ext import commands


class ManageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        user = self.bot.user
        info = await self.bot.application_info()
        owner = info.owner
        print(f"{user} でログイン完了！ (管理者: {owner})")
        self.owner = owner

    @commands.command(help="このボットを終了します。 (管理者のみ)")
    async def stop(self, ctx):
        if ctx.author.id == self.owner.id:
            print(f"{ctx.author} からの命令により終了中...")
            await ctx.send("ボットを終了しています...")
            await self.bot.logout()
        else:
            await ctx.send("ボットを終了するにはこのボットの管理者である必要があります！")

    @commands.command(help="このボットのデバッグ情報をコンソールに出力します。 (管理者のみ)")
    async def dump(self, ctx):
        if ctx.author.id == self.owner.id:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint([cog.__dict__ for cog in self.bot.cogs.values()])
