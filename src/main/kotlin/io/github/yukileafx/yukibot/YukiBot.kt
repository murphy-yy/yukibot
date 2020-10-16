package io.github.yukileafx.yukibot

import net.dv8tion.jda.api.EmbedBuilder
import net.dv8tion.jda.api.JDABuilder
import net.dv8tion.jda.api.entities.Activity
import net.dv8tion.jda.api.entities.ApplicationInfo
import net.dv8tion.jda.api.events.ReadyEvent
import net.dv8tion.jda.api.events.message.MessageReceivedEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter
import java.awt.Color

fun main() {
    val token = System.getenv("TOKEN")

    val jda = JDABuilder.createLight(token)
        .addEventListeners(Listener())
        .setActivity(Activity.playing("v4.0 | Kotlin アップデート！"))
        .build()
    jda.awaitReady()
}

class Listener : ListenerAdapter() {

    private lateinit var appInfo: ApplicationInfo
    private val prefix = "/"
    private val helpText = javaClass.getResource("/help.txt").readText()
    private val colorRoleName = "すごい染料"

    override fun onReady(event: ReadyEvent) {
        println("${event.jda.selfUser} でログイン完了！")
        appInfo = event.jda.retrieveApplicationInfo().complete()
    }

    override fun onMessageReceived(event: MessageReceivedEvent) {
        if (event.author.isBot) return

        val text = event.message.contentRaw
        if (!text.startsWith(prefix)) return
        val parts = text.split(" ")
        val name = parts[0].removePrefix(prefix)
        val args = parts.drop(1)
        println("${event.author}: $text")
        println("\t$parts -> $prefix + $name + $args")

        when (name) {
            "stop" -> {
                if (event.author == appInfo.owner) {
                    event.channel.sendMessage(
                        EmbedBuilder()
                            .setDescription("ボットを停止しています。 :scream:")
                            .setColor(Color.GREEN)
                            .build()
                    ).queue()

                    event.jda.shutdown()
                } else {
                    event.channel.sendMessage(
                        EmbedBuilder()
                            .setDescription("このボットのオーナー ${appInfo.owner.asMention} にお願いしてください。 :weary:")
                            .setColor(Color.RED)
                            .build()
                    ).queue()
                }
            }
            "help" -> {
                event.channel.sendMessage(helpText).queue()
            }
            "im" -> {
                if (!event.isFromGuild) return

                val nick = args.joinToString(" ")

                event.guild.modifyNickname(event.guild.selfMember, nick).queue()

                if (nick.isBlank()) {
                    event.channel.sendMessage(
                        EmbedBuilder()
                            .setDescription("ボットの名前がリセットされました。 :cold_sweat:")
                            .setColor(Color.RED)
                            .build()
                    ).queue()
                } else {
                    event.channel.sendMessage(
                        EmbedBuilder()
                            .setDescription("私は「$nick」になりました。")
                            .setColor(Color.GREEN)
                            .build()
                    ).queue()
                }
            }
            "color" -> {
                if (!event.isFromGuild) return

                if (args.isEmpty()) {
                    event.member!!.roles.filter { it.name == colorRoleName }.forEach { it.delete().queue() }

                    event.channel.sendMessage(
                        EmbedBuilder()
                            .setDescription("名前の色がリセットされました。 :sparkles:")
                            .build()
                    ).queue()
                } else {
                    var hex = args.first().removePrefix("0x").removePrefix("#")
                    if (!hex.matches(Regex("[0-9a-fA-F]{3,6}"))) return
                    if (hex.length == 3) {
                        hex = hex.map { it.toString().repeat(2) }.joinToString("")
                    }
                    val value = hex.toInt(16)

                    event.member!!.roles.filter { it.name == colorRoleName }.forEach { it.delete().queue() }

                    event.guild.createRole().setName(colorRoleName).setColor(value).queue { role ->
                        event.guild.addRoleToMember(event.member!!, role).queue()
                    }

                    event.channel.sendMessage(
                        EmbedBuilder()
                            .setDescription("名前の色を #$hex ($value) に変更しました。 :paintbrush:")
                            .setColor(value)
                            .build()
                    ).queue()
                }
            }
        }
    }
}
