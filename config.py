#!/usr/bin/env python

import os

TOKEN = os.environ["TOKEN"]

COMMAND_PREFIX = "/"

MESSAGE_TO_COMMAND = {
    "!sh shovel": "yomi start",
    "!sh s": "yomi start",
    "!sh end": "yomi stop",
    "!sh e": "yomi stop",
    "!sh end_channel": "yomi unlink",
    "!sh ec": "yomi unlink",
    "/resetcolor": "color reset",
}

YOMIAGE_SOUND_URL = (
    "https://www.yukumo.net/api/v2/aqtk1/koe.mp3?type=f1&kanji=" + "<ENCODED_TEXT>"
)

COLOR_ROLE_NAME = "すごい染料"

HELP_MESSAGE = """
```
/help - このメッセージを表示します。
/stop - このボットを終了します。 (管理者のみ)
/dump - このボットのデバッグ情報をコンソールに出力します。 (管理者のみ)
/yomi start - ボイスチャンネルでメッセージの読み上げを開始します。
/yomi link - ボイスチャンネルにチャンネルをリンクします。
/yomi unlink - ボイスチャンネルからリンクを解除します。
/yomi stop - ボイスチャンネルでメッセージの読み上げを停止します。
/color - 名前に色を付けます。
/color reset - 名前の色をリセットします。
/color cleanup - 不要な色を削除します。
```
"""
