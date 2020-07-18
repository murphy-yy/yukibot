import os
import cogs.managecog
from discord.ext import commands


if __name__ == "__main__":
    token = os.environ["TOKEN"]
    print("準備中...")
    bot = commands.Bot(command_prefix="/", description="YukiBot v2.0")
    bot.add_cog(cogs.managecog.ManageCog(bot))
    print("起動中...")
    bot.run(token)
