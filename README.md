# yukibot

高性能Discordボット

## 🚀 起動

ギルドIDを指定するとコマンドの反映が高速になります。

```bash
TOKEN="ボットのトークン" python -u main.py [ギルドID...]
```

## 🐳 Dockerで起動する

```bash
docker run -d --restart=always --name yukibot -e TOKEN="ボットのトークン" ghcr.io/yukileafx/yukibot:latest
```

また、[Watchtower](https://github.com/containrrr/watchtower)を使用して自動更新することもできます。

```bash
docker run -d --restart=always --name watchtower -v /var/run/docker.sock:/var/run/docker.sock containrrr/watchtower --interval 300
```
