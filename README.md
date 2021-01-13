# yukibot

高性能Discordボット

## 🚀 起動

ギルドIDを指定するとコマンドの反映が高速になります。

```bash
TOKEN="ボットのトークン" python -u main.py [ギルドID...]
```

## 🐳 Dockerで起動する

```bash
docker run -d --name yukibot -e TOKEN="ボットのトークン" ghcr.io/yukileafx/yukibot:latest
```
