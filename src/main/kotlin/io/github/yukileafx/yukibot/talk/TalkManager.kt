package io.github.yukileafx.yukibot.talk

import com.sedmelluq.discord.lavaplayer.player.DefaultAudioPlayerManager
import com.sedmelluq.discord.lavaplayer.source.AudioSourceManagers
import io.github.yukileafx.yukibot.emoji
import net.dv8tion.jda.api.entities.TextChannel
import net.dv8tion.jda.api.entities.VoiceChannel
import net.dv8tion.jda.api.events.message.guild.GuildMessageReceivedEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter
import java.io.File
import java.net.URL
import java.net.URLEncoder
import java.nio.file.Files

class TalkManager : ListenerAdapter() {

    private val worker = DefaultAudioPlayerManager().also { AudioSourceManagers.registerLocalSource(it) }
    private val binds = mutableMapOf<String, Set<String>>().withDefault { setOf() }
    private val schedulers = mutableMapOf<String, TrackScheduler>()

    fun remember(vc: VoiceChannel, read: TextChannel) {
        binds[vc.id] = binds.getValue(vc.id).toMutableSet().apply { add(read.id) }
        println(binds)
    }

    fun forgetAll(vc: VoiceChannel) {
        binds.remove(vc.id)
        println(binds)
    }

    fun connect(vc: VoiceChannel) {
        schedulers.getOrPut(vc.guild.id) {
            val audioPlayer = worker.createPlayer()
            vc.guild.audioManager.sendingHandler = AudioPlayerSendHandler(audioPlayer)
            TrackScheduler(audioPlayer).also { audioPlayer.addListener(it) }
        }
        println(schedulers)
        vc.guild.audioManager.openAudioConnection(vc)
    }

    fun disconnect(vc: VoiceChannel) {
        vc.guild.audioManager.closeAudioConnection()
        schedulers.remove(vc.guild.id)
        println(schedulers)
    }

    private fun queue(vc: VoiceChannel, localPath: String) {
        val scheduler = schedulers[vc.guild.id] ?: return
        worker.loadItem(localPath, TrackLoadHandler(scheduler))
    }

    private fun String.toYukkuriVoiceURL(): String {
        val encodedText = URLEncoder.encode(this, Charsets.UTF_8.name())
        return "https://www.yukumo.net/api/v2/aqtk1/koe.mp3?type=f1&kanji=$encodedText"
    }

    private fun String.downloadMp3(): File {
        val mp3 = Files.createTempFile("yomi", ".mp3").toFile()
        val data = URL(this).readBytes()
        mp3.writeBytes(data)
        return mp3
    }

    private fun File.toOpusWithFFmpeg(): File {
        val opus = parentFile.resolve("$nameWithoutExtension.opus")
        val command = listOf(
            "ffmpeg",
            "-i", "$this",
            "-y",
            "-ar", "48000",
            "-ac", "2",
            "-acodec", "libopus",
            "-ab", "96k",
            "$opus"
        )
        val process = ProcessBuilder(command).start().also { it.waitFor() }
        check(process.exitValue() == 0) {
            System.err.println(process.errorStream.reader().readText())
            command
        }
        delete()
        return opus
    }

    override fun onGuildMessageReceived(event: GuildMessageReceivedEvent) {
        if (event.author.isBot) {
            return
        }
        val vcList = binds
            .filterValues { it.contains(event.channel.id) }
            .keys
            .mapNotNull { event.jda.getVoiceChannelById(it) }
            .ifEmpty { return }
        println("${event.message}")
        val opus = event.message.contentDisplay.toYukkuriVoiceURL().downloadMp3().toOpusWithFFmpeg()
        println("${":clock1:".emoji()} リクエスト中: $opus (${event.message.id}) -> $vcList")
        vcList.forEach { vc -> queue(vc, "$opus") }
    }
}
