package io.github.yukileafx.yukibot.command

import com.jagrosh.jdautilities.command.Command
import com.jagrosh.jdautilities.command.CommandEvent
import io.github.yukileafx.yukibot.popup
import io.github.yukileafx.yukibot.talk.TalkManager
import java.awt.Color

class NoYomiCommand(private val manager: TalkManager) : Command() {

    init {
        name = "noyomi"
    }

    override fun execute(event: CommandEvent) {
        val vc = event.member.voiceState?.channel
        if (vc != null) {
            manager.disconnect(vc)
            manager.forgetAll(vc)
            event.channel.popup(Color.GREEN, "${vc.name} の読み上げを終了しました。 :pleading_face:")
        } else {
            event.channel.popup(Color.RED, "まずボイスチャンネルに接続してください。")
        }
    }
}
