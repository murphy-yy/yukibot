import os

from discord.ext import commands

import cog_thiscoin
import cog_yomiage
import cog_youtube
import cog_yukibot
import commands_better

if __name__ == '__main__':
    token = os.environ['TOKEN']

    bot = commands.Bot('/', help_command=commands_better.Help())
    bot.add_cog(cog_yukibot.YukiBot(bot))
    bot.add_cog(cog_youtube.YouTube())
    bot.add_cog(cog_thiscoin.ThisCoin())
    bot.add_cog(cog_yomiage.Yomiage(bot))
    bot.run(token)
