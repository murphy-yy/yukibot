package io.github.yukileafx.yukibot.command

import com.jagrosh.jdautilities.command.Command
import com.jagrosh.jdautilities.command.CommandEvent
import io.github.yukileafx.yukibot.popup
import io.github.yukileafx.yukibot.talk.TalkManager
import java.awt.Color

class YomiCommand(private val manager: TalkManager) : Command() {

    init {
        name = "yomi"
    }

    override fun execute(event: CommandEvent) {
        val vc = event.member.voiceState?.channel
        if (vc != null) {
            val read = event.textChannel
            manager.bind(vc, read)
            manager.setup(vc)
            event.channel.popup(Color.CYAN, "${vc.name} にて ${read.asMention} の読み上げを開始しました。 :sound:")
        } else {
            event.channel.popup(Color.RED, "まずボイスチャンネルに接続してください。")
        }
    }
}
