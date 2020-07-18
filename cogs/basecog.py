from discord.ext import commands


class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        user = self.bot.user
        appinfo = await self.bot.application_info()
        owner = appinfo.owner
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
