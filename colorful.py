#!/usr/bin/env python3

import discord

token = ''
role_name = 'すごい染料'

class Bot(discord.Client):
    async def on_ready(self):
        print(self.user, 'でログイン完了！')

        global owner
        owner = (await self.application_info()).owner
        print('オーナーは', owner, 'です！')

    async def on_message(self, message):
        if message.author.bot:
            return

        channel = message.channel
        member = message.guild.get_member(message.author.id)

        if message.content == '/stop':
            if message.author.id == owner.id:
                print(message.author, 'からの命令によりシャットダウン中...')
                await channel.send('OK...')
                await self.logout()

        if message.content == '/color':
            await channel.send('何色にしますか？6文字(HEX)で答えてください。\n<https://www.google.com/search?q=color+picker>')

            def color_check(reply):
                if message.author.id == reply.author.id and reply.channel == channel:
                    s = reply.content
                    if s.encode('utf-8').isalnum() and len(s) == 6:
                        try:
                            int(s, 16)
                            return True
                        except ValueError:
                            pass
                return False

            hex = (await self.wait_for('message', check=color_check)).content
            progress = await channel.send(f'25% -> #{hex} に決定！')

            await progress.edit(content='50% -> 古い権限の修正中...')
            for role in member.roles:
                if role.name == role_name:
                    print(member, 'から', role, 'を削除中...')
                    await role.delete()

            await progress.edit(content='75% -> 新しい権限の準備中...')
            role = await message.guild.create_role(name=role_name, color=discord.Colour(int(hex, 16)))

            await member.add_roles(role)
            await progress.edit(content=f'100% -> 名前の色を #{hex} に変更完了！ ({member})')

        if message.content == '/resetcolor':
            progress = await channel.send('名前の色をリセット中...')
            for role in member.roles:
                if role.name == role_name:
                    print(member, 'から', role, 'を削除中...')
                    await role.delete()
            await progress.edit(content='名前の色をリセットしました！')

print('ログイン中...')
bot = Bot()
bot.run(token)
