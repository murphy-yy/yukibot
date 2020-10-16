package io.github.yukileafx.yukibot.command

import com.jagrosh.jdautilities.command.Command
import com.jagrosh.jdautilities.command.CommandEvent
import io.github.yukileafx.yukibot.popup
import java.awt.Color

class YomiCommand(private val binds: MutableMap<String, Set<String>>) : Command() {

    init {
        name = "yomi"
    }

    override fun execute(event: CommandEvent) {
        val vc = event.member.voiceState?.channel
        val read = event.textChannel
        if (vc != null) {
            vc.guild.audioManager.openAudioConnection(vc)
            binds[vc.id] = binds.getValue(vc.id).toMutableSet().apply { add(read.id) }
            println(binds)
            event.channel.popup(Color.CYAN, "${vc.name} にて ${read.asMention} の読み上げを開始しました。 :sound:")
        } else {
            event.channel.popup(Color.RED, "まずボイスチャンネルに接続してください。")
        }
    }
}
