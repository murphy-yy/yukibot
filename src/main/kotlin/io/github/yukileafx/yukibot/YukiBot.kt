package io.github.yukileafx.yukibot

import com.jagrosh.jdautilities.command.CommandClientBuilder
import com.vdurmont.emoji.EmojiParser
import io.github.yukileafx.yukibot.command.*
import io.github.yukileafx.yukibot.talk.TalkManager
import net.dv8tion.jda.api.EmbedBuilder
import net.dv8tion.jda.api.JDABuilder
import net.dv8tion.jda.api.entities.Activity
import net.dv8tion.jda.api.entities.MessageChannel
import java.awt.Color

fun main() {
    val token = System.getenv("TOKEN")

    val jda = JDABuilder.createDefault(token)
        .setActivity(Activity.playing("v4.0 | Kotlin アップデート！"))
        .build()
    jda.awaitReady()
    println("${jda.selfUser} でログイン完了！")

    val ownerId = jda.retrieveApplicationInfo().complete().owner.id
    val talkManager = TalkManager()

    val clientBuilder = CommandClientBuilder()
        .setOwnerId(ownerId)
        .setPrefix("/")
        .setEmojis(null, null, ":x:".emoji())
        .useHelpBuilder(false)
        .addCommand(HelpCommand())
        .addCommand(StopCommand())
        .addCommand(ImCommand())
        .addCommand(ColorCommand())
        .addCommand(YomiCommand(talkManager))
        .addCommand(NoYomiCommand(talkManager))
    jda.addEventListener(clientBuilder.build())

    jda.addEventListener(talkManager)
}

fun MessageChannel.popup(color: Color?, text: String) {
    sendMessage(EmbedBuilder().setColor(color).setDescription(text).build()).queue()
}

fun String.emoji(): String {
    return EmojiParser.parseToUnicode(this)
}
