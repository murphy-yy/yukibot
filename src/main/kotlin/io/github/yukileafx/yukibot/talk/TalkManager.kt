package io.github.yukileafx.yukibot.talk

import com.sedmelluq.discord.lavaplayer.player.DefaultAudioPlayerManager
import com.sedmelluq.discord.lavaplayer.source.AudioSourceManagers
import net.dv8tion.jda.api.entities.TextChannel
import net.dv8tion.jda.api.entities.VoiceChannel
import net.dv8tion.jda.api.events.message.guild.GuildMessageReceivedEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter
import java.io.File
import java.net.URL
import java.net.URLEncoder
import java.util.*

class TalkManager : ListenerAdapter() {

    private val worker = DefaultAudioPlayerManager().also { AudioSourceManagers.registerLocalSource(it) }
    private val binds = mutableMapOf<String, Set<String>>().withDefault { setOf() }
    private val schedulers = mutableMapOf<String, TrackScheduler>()
    private val dataDir = File(System.getProperty("java.io.tmpdir"), "yomi")

    fun bind(vc: VoiceChannel, read: TextChannel) {
        binds[vc.id] = binds.getValue(vc.id).toMutableSet().apply { add(read.id) }
        println(binds)
    }

    fun setup(vc: VoiceChannel) {
        schedulers.getOrPut(vc.guild.id) {
            val audioPlayer = worker.createPlayer()
            vc.guild.audioManager.sendingHandler = AudioPlayerSendHandler(audioPlayer)
            TrackScheduler(audioPlayer).also { audioPlayer.addListener(it) }
        }
        println(schedulers)
        vc.guild.audioManager.openAudioConnection(vc)
    }

    fun remove(vc: VoiceChannel) {
        vc.guild.audioManager.closeAudioConnection()
        schedulers.remove(vc.guild.id)
        println(schedulers)
        binds.remove(vc.id)
        println(binds)
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
        val mp3 = dataDir.also { it.mkdirs() }.resolve("${UUID.randomUUID()}.mp3")
        mp3.writeBytes(URL(this).readBytes())
        return mp3
    }

    private fun File.toOpusWithFFmpeg(): File {
        val opus = dataDir.also { it.mkdirs() }.resolve("${UUID.randomUUID()}.opus")
        ProcessBuilder(listOf("ffmpeg", "-i", "\"$this\"", "-acodec", "libopus", "\"$opus\""))
            .redirectOutput(ProcessBuilder.Redirect.INHERIT)
            .redirectError(ProcessBuilder.Redirect.INHERIT)
            .start()
            .waitFor()
        delete()
        return opus
    }

    override fun onGuildMessageReceived(event: GuildMessageReceivedEvent) {
        if (event.author.isBot) {
            return
        }
        binds.filterValues { it.contains(event.channel.id) }.map { it.key }.forEach { vcId ->
            val vc = event.jda.getVoiceChannelById(vcId) ?: return
            val src = event.message.contentDisplay.toYukkuriVoiceURL().downloadMp3().toOpusWithFFmpeg()
            queue(vc, src.path)
        }
    }
}
