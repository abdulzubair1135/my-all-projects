package com.projectx2.porncontroller.utils

import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlin.math.PI
import kotlin.math.exp
import kotlin.math.sin

object IntroAudioPlayer {
    private const val SAMPLE_RATE = 44100
    private const val DURATION_SECONDS = 1.6
    private const val TAG = "IntroAudioPlayer"

    /**
     * Synthesizes and plays a rich futuristic calm startup chord (Cmaj9 cyber chime).
     * 100% offline, pure mathematical sound synthesis using AudioTrack.
     */
    suspend fun playIntroChime() = withContext(Dispatchers.Default) {
        try {
            val totalSamples = (SAMPLE_RATE * DURATION_SECONDS).toInt()
            val audioBuffer = ShortArray(totalSamples)

            // Frequencies for a soothing futuristic chord: C4, G4, B4, E5
            val freqs = doubleArrayOf(261.63, 392.00, 493.88, 659.25)
            val weights = doubleArrayOf(0.35, 0.25, 0.20, 0.20)

            for (i in 0 until totalSamples) {
                val t = i.toDouble() / SAMPLE_RATE
                // Exponential decay envelope with quick smooth attack
                val attack = if (t < 0.05) (t / 0.05) else 1.0
                val decay = exp(-2.2 * t)
                val envelope = attack * decay

                var sampleVal = 0.0
                for (j in freqs.indices) {
                    val phase = 2.0 * PI * freqs[j] * t
                    // Fundamental + subtle 2nd harmonic shimmer
                    val osc = sin(phase) + 0.15 * sin(2.0 * phase)
                    sampleVal += osc * weights[j]
                }

                val finalVal = (sampleVal * envelope * Short.MAX_VALUE * 0.75).toInt()
                audioBuffer[i] = finalVal.coerceIn(Short.MIN_VALUE.toInt(), Short.MAX_VALUE.toInt()).toShort()
            }

            val bufferSize = AudioTrack.getMinBufferSize(
                SAMPLE_RATE,
                AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_16BIT
            )

            val audioTrack = AudioTrack.Builder()
                .setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                        .build()
                )
                .setAudioFormat(
                    AudioFormat.Builder()
                        .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                        .setSampleRate(SAMPLE_RATE)
                        .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                        .build()
                )
                .setBufferSizeInBytes(maxOf(bufferSize, audioBuffer.size * 2))
                .setTransferMode(AudioTrack.MODE_STATIC)
                .build()

            audioTrack.write(audioBuffer, 0, audioBuffer.size)
            audioTrack.play()

            // Release after playback
            withContext(Dispatchers.IO) {
                Thread.sleep((DURATION_SECONDS * 1000).toLong() + 200)
                try {
                    audioTrack.stop()
                    audioTrack.release()
                } catch (_: Exception) {}
            }
        } catch (e: Exception) {
            Log.w(TAG, "Audio intro playback failed or audio service unavailable", e)
        }
    }
}
