package io.github.yukileafx.yukibot.command

import com.jagrosh.jdautilities.command.Command
import com.jagrosh.jdautilities.command.CommandEvent
import io.github.yukileafx.yukibot.popup
import java.awt.Color

class ColorCommand : Command() {

    private val roleName = "すごい染料"

    init {
        name = "color"
    }

    override fun execute(event: CommandEvent) {
        if (event.args.isBlank()) {
            event.member.roles
                .filter { it.name == roleName }
                .forEach { it.delete().queue() }
            event.channel.popup(null, "名前の色がリセットされました。 :sparkles:")
        } else {
            val input = event.args.split(" ").first()
            val color = kotlin.runCatching { Color.decode(input) }
                .onFailure { event.reactError() }
                .getOrElse { return }
            event.member.roles
                .filter { it.name == roleName }
                .forEach { it.delete().queue() }
            event.guild.createRole().setName(roleName).setColor(color).queue { role ->
                event.guild.addRoleToMember(event.member, role).queue()
            }
            event.channel.popup(color, "名前の色を $input (${color.rgb}) に変更しました。 :paintbrush:")
        }
    }
}
