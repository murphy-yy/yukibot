package io.github.yukileafx.yukibot.talk

import com.sedmelluq.discord.lavaplayer.player.DefaultAudioPlayerManager
import com.sedmelluq.discord.lavaplayer.source.AudioSourceManagers
import net.dv8tion.jda.api.entities.TextChannel
import net.dv8tion.jda.api.entities.VoiceChannel
import net.dv8tion.jda.api.events.message.guild.GuildMessageReceivedEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter
import org.apache.commons.io.FileUtils
import java.io.File
import java.net.URL
import java.net.URLEncoder
import java.util.*

class TalkManager : ListenerAdapter() {

    private val worker = DefaultAudioPlayerManager().also { AudioSourceManagers.registerLocalSource(it) }
    private val binds = mutableMapOf<String, Set<String>>().withDefault { setOf() }
    private val schedulers = mutableMapOf<String, TrackScheduler>()

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
        vc.guild.audioManager.openAudioConnection(vc)
    }

    private fun queue(vc: VoiceChannel, src: String) {
        val scheduler = schedulers[vc.guild.id] ?: return
        worker.loadItem(src, TrackLoadHandler(scheduler))
    }

    private fun String.toSound(): String {
        val encoded = URLEncoder.encode(this, Charsets.UTF_8.name())
        val url = "https://www.yukumo.net/api/v2/aqtk1/koe.mp3?type=f1&kanji=$encoded"
        val dir = File(System.getProperty("java.io.tmpdir"), "yukumo")
        dir.mkdirs()
        val f1 = File(dir, "f1-${UUID.randomUUID()}.mp3")
        FileUtils.copyURLToFile(URL(url), f1)
        val f2 = File(dir, "f2-${UUID.randomUUID()}.wav")
        Runtime.getRuntime().exec("ffmpeg -i \"$f1\" -vn -ac 2 -ar 44100 -acodec pcm_s16le -f wav \"$f2\"").waitFor()
        return f2.path
    }

    override fun onGuildMessageReceived(event: GuildMessageReceivedEvent) {
        if (event.author.isBot) {
            return
        }
        binds.filterValues { it.contains(event.channel.id) }.map { it.key }.forEach { vcId ->
            val vc = event.jda.getVoiceChannelById(vcId) ?: return
            val src = event.message.contentDisplay.toSound()
            queue(vc, src)
        }
    }
}
