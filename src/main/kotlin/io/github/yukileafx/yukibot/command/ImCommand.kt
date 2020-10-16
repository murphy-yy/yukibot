package io.github.yukileafx.yukibot.command

import com.jagrosh.jdautilities.command.Command
import com.jagrosh.jdautilities.command.CommandEvent
import io.github.yukileafx.yukibot.popup
import java.awt.Color

class ImCommand : Command() {

    init {
        name = "im"
    }

    override fun execute(event: CommandEvent) {
        val nick = event.args
        event.selfMember.modifyNickname(nick).queue()
        if (nick.isBlank()) {
            event.channel.popup(Color.RED, "ボットの名前がリセットされました。 :cold_sweat:")
        } else {
            event.channel.popup(Color.GREEN, "私は「$nick」になりました。")
        }
    }
}
