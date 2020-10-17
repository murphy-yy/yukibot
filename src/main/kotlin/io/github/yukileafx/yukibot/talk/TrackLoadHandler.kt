package io.github.yukileafx.yukibot.talk

import com.sedmelluq.discord.lavaplayer.player.AudioLoadResultHandler
import com.sedmelluq.discord.lavaplayer.tools.FriendlyException
import com.sedmelluq.discord.lavaplayer.track.AudioPlaylist
import com.sedmelluq.discord.lavaplayer.track.AudioTrack

class TrackLoadHandler(private val scheduler: TrackScheduler) : AudioLoadResultHandler {

    override fun trackLoaded(track: AudioTrack) {
        scheduler.queue(track)
    }

    override fun playlistLoaded(playlist: AudioPlaylist) {
        playlist.tracks.forEach { scheduler.queue(it) }
    }

    override fun noMatches() {
    }

    override fun loadFailed(e: FriendlyException) {
        e.printStackTrace()
    }
}
