import os

from discord.ext import commands

from cogs.colorcog import ColorCog
from cogs.managecog import ManageCog
from cogs.yomiagecog import YomiageCog

if __name__ == "__main__":
    token = os.environ["TOKEN"]

    print("準備中...")
    bot = commands.Bot("/", description="YukiBot v3 [2020/09/27 更新]")
    bot.add_cog(ManageCog(bot))
    bot.add_cog(ColorCog(bot))
    bot.add_cog(YomiageCog(bot))

    print("起動中...")
    bot.run(token)
