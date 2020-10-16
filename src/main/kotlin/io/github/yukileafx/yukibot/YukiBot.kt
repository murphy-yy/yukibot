package io.github.yukileafx.yukibot

import net.dv8tion.jda.api.EmbedBuilder
import net.dv8tion.jda.api.JDABuilder
import net.dv8tion.jda.api.entities.Activity
import net.dv8tion.jda.api.entities.ApplicationInfo
import net.dv8tion.jda.api.entities.MessageChannel
import net.dv8tion.jda.api.events.ReadyEvent
import net.dv8tion.jda.api.events.message.MessageReceivedEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter
import net.dv8tion.jda.api.requests.restaction.MessageAction
import java.awt.Color

fun main() {
    val token = System.getenv("TOKEN")

    val jda = JDABuilder.createDefault(token)
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

    private fun MessageChannel.popup(color: Color?, text: String): MessageAction {
        return sendMessage(EmbedBuilder().setColor(color).setDescription(text).build())
    }

    private fun String.convertHexToInt(): Int? {
        var hex = replaceFirst(Regex("(#|0[xX])"), "")
        if (!hex.matches(Regex("[0-9a-fA-F]{3,6}")))
            return null
        if (hex.length == 3)
            hex = hex.map { c -> "$c".repeat(2) }.joinToString("")
        return hex.toInt(16)
    }

    override fun onReady(event: ReadyEvent) {
        println("${event.jda.selfUser} でログイン完了！")
        appInfo = event.jda.retrieveApplicationInfo().complete()
    }

    override fun onMessageReceived(event: MessageReceivedEvent) {
        if (event.author.isBot)
            return

        val text = event.message.contentRaw
        if (!text.startsWith(prefix))
            return
        val parts = text.split(" ")
        val name = parts[0].removePrefix(prefix)
        val args = parts.drop(1)
        println("${event.author}: $text")
        println("\t$parts -> $prefix + $name + $args")

        when (name) {
            "stop" -> {
                if (event.author == appInfo.owner) {
                    event.channel.popup(Color.GREEN, "ボットを停止しています。 :scream:").queue()
                    event.jda.shutdown()
                } else {
                    event.channel.popup(Color.RED, "このボットのオーナー ${appInfo.owner.asMention} にお願いしてください。 :weary:").queue()
                }
            }
            "help" -> {
                event.channel.sendMessage(helpText).queue()
            }
            "im" -> {
                if (!event.isFromGuild)
                    return

                val nick = args.joinToString(" ")
                event.guild.modifyNickname(event.guild.selfMember, nick).queue()
                if (nick.isBlank()) {
                    event.channel.popup(Color.RED, "ボットの名前がリセットされました。 :cold_sweat:").queue()
                } else {
                    event.channel.popup(Color.GREEN, "私は「$nick」になりました。").queue()
                }
            }
            "color" -> {
                if (!event.isFromGuild)
                    return

                if (args.isEmpty()) {
                    event.member!!.roles.filter { it.name == colorRoleName }.forEach { it.delete().queue() }
                    event.channel.popup(null, "名前の色がリセットされました。 :sparkles:").queue()
                } else {
                    val hex = args.first()
                    val rgb = hex.convertHexToInt() ?: return
                    val color = Color(rgb)
                    event.member!!.roles.filter { it.name == colorRoleName }.forEach { it.delete().queue() }
                    event.guild.createRole().setName(colorRoleName).setColor(color).queue { role ->
                        event.guild.addRoleToMember(event.member!!, role).queue()
                    }
                    event.channel.popup(color, "名前の色を $hex ($rgb) に変更しました。 :paintbrush:").queue()
                }
            }
            "yomi" -> {
                if (!event.isFromGuild)
                    return

                val read = event.textChannel
                val vc = event.member!!.voiceState?.channel
                if (vc != null) {
                    event.guild.audioManager.openAudioConnection(vc)
                    event.channel.popup(Color.CYAN, "${vc.name} にて ${read.asMention} の読み上げを開始しました。 :sound:").queue()
                } else {
                    event.channel.popup(Color.RED, "まずボイスチャンネルに接続してください。").queue()
                }
            }
        }
    }
}
