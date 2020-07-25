import os
from cogs.managecog import ManageCog
from cogs.colorcog import ColorCog
from cogs.yomiagecog import YomiageCog
from discord.ext import commands


if __name__ == "__main__":
    token = os.environ["TOKEN"]

    print("準備中...")
    bot = commands.Bot(
        command_prefix="/", description="YukiBot v2.0 β3 [2020/07/26 更新]"
    )
    bot.add_cog(ManageCog(bot))
    bot.add_cog(ColorCog(bot))
    bot.add_cog(YomiageCog(bot))

    print("起動中...")
    bot.run(token)
