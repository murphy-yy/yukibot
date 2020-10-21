package io.github.yukileafx.yukibot.talk

import com.sedmelluq.discord.lavaplayer.player.AudioPlayer
import com.sedmelluq.discord.lavaplayer.player.event.AudioEventAdapter
import com.sedmelluq.discord.lavaplayer.tools.FriendlyException
import com.sedmelluq.discord.lavaplayer.track.AudioTrack
import com.sedmelluq.discord.lavaplayer.track.AudioTrackEndReason
import io.github.yukileafx.yukibot.emoji

class TrackScheduler(private val audioPlayer: AudioPlayer) : AudioEventAdapter() {

    private val trackList = mutableListOf<AudioTrack>()

    fun queue(track: AudioTrack) {
        if (audioPlayer.playingTrack == null) {
            audioPlayer.playTrack(track)
        } else {
            trackList.add(track)
        }
    }

    override fun onTrackStart(player: AudioPlayer, track: AudioTrack) {
        println("${":arrow_forward:".emoji()} 再生中: ${track.info.uri}")
    }

    override fun onTrackEnd(player: AudioPlayer, track: AudioTrack, endReason: AudioTrackEndReason) {
        if (endReason.mayStartNext) {
            val nextTrack = trackList.removeFirstOrNull() ?: return
            audioPlayer.playTrack(nextTrack)
        }
    }

    override fun onTrackException(player: AudioPlayer, track: AudioTrack, e: FriendlyException) {
        e.printStackTrace()
    }
}
