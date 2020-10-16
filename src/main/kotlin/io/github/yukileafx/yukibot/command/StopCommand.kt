package io.github.yukileafx.yukibot.command

import com.jagrosh.jdautilities.command.Command
import com.jagrosh.jdautilities.command.CommandEvent
import io.github.yukileafx.yukibot.popup
import java.awt.Color

class StopCommand : Command() {

    init {
        name = "stop"
        guildOnly = false
    }

    override fun execute(event: CommandEvent) {
        if (event.isOwner) {
            event.channel.popup(Color.GREEN, "ボットを停止しています。 :scream:")
            event.jda.shutdown()
        } else {
            val owner = event.jda.getUserById(event.client.ownerId) ?: return
            event.channel.popup(Color.RED, "このボットのオーナー ${owner.asMention} にお願いしてください。 :weary:")
        }
    }
}
