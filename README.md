# yukibot

高性能Discordボット

## ✨ 機能

- Discordのベータ機能、[スラッシュコマンド](https://discord.com/developers/docs/interactions/slash-commands)に対応済み！
- 自分の名前に色を付けよう！
- マイクラサーバーの接続をチェック！

[今すぐ招待する](https://discord.com/api/oauth2/authorize?client_id=733861628738666526&permissions=268435456&scope=bot%20applications.commands)

## 🚀 起動

ギルドIDを指定するとコマンドの反映が高速になります。

```bash
TOKEN="ボットのトークン" python -u main.py [ギルドID...]
```

## 🐳 Dockerで起動する

```bash
docker run -d \
  --restart=always \
  --name yukibot \
  -e TOKEN="ボットのトークン" \
  ghcr.io/yukileafx/yukibot:latest
```

また、[Watchtower](https://github.com/containrrr/watchtower)を使用して自動更新することもできます。

```bash
docker run -d \
  --restart=always \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
    --interval 300
```
