import os
import pickle

import discord

client = discord.Client()


@client.event
async def on_ready():
    guild_ids = [g.id for g in client.guilds]

    with open("guild.pickle", "wb") as fp:
        pickle.dump(guild_ids, fp)

    await client.logout()
    print("サーバーの取得が正常に完了")


token = os.environ["TOKEN"]
client.run(token)
