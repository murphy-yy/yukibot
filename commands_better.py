from discord.ext import commands


async def guild_only(ctx):
    if ctx.guild is None:
        raise commands.CheckFailure('DMでこのコマンドは許可されていません。')
    return True


async def owner_only(ctx):
    if not (await ctx.bot.is_owner(ctx.author)):
        raise commands.CheckFailure('あなたはこのボットのオーナーではありません。 :weary:')
    return True


class Help(commands.DefaultHelpCommand):

    def __init__(self):
        super().__init__()
        self.no_category = 'カテゴリ未分類'
        self.command_attrs['help'] = 'このヘルプを表示します。'

    def get_ending_note(self):
        return (f'コマンドの詳細は {self.clean_prefix}{self.invoked_with} コマンド名 と入力してください。\n'
                f'カテゴリの詳細も {self.clean_prefix}{self.invoked_with} カテゴリ名 と入力することができます。')
