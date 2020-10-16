package io.github.yukileafx.yukibot.command

import com.jagrosh.jdautilities.command.Command
import com.jagrosh.jdautilities.command.CommandEvent

class HelpCommand : Command() {

    private val helpText = javaClass.getResource("/help.txt").readText()

    init {
        name = "help"
        guildOnly = false
    }

    override fun execute(event: CommandEvent) {
        event.reply(helpText)
    }
}
