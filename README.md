# yukibot

高性能Discordボット

## 🚀 起動

```bash
TOKEN="ボットのトークン" bash run.sh
```

## 🐳 Dockerで起動する

### 🔨 ビルド

```bash
docker build -t yukibot .
```

### 🏃 実行

```bash
docker run -d --restart=always --name yukibot -e TOKEN="ボットのトークン" yukibot
```
