from discord.ext import commands
from cogs import basecog
import os


if __name__ == "__main__":
    token = os.environ["TOKEN"]
    bot = commands.Bot(command_prefix="/", description="YukiBot v2.0")
    bot.add_cog(basecog.BaseCog(bot))
    print("ログイン中...")
    bot.run(token)
