package com.example.emergencyrecorder.recording

import android.content.Context
import android.media.MediaRecorder
import android.net.Uri
import android.os.Build
import android.os.ParcelFileDescriptor
import android.util.Log
import com.example.emergencyrecorder.settings.AppSettings

class AudioRecorderEngine(
    private val context: Context,
    private val onError: (String) -> Unit
) {

    private var mediaRecorder: MediaRecorder? = null
    private var pfd: ParcelFileDescriptor? = null
    private var currentUri: Uri? = null

    @Synchronized
    fun startRecording(targetUri: Uri, isCall: Boolean = false): Boolean {
        releaseResources()

        val settings = AppSettings.getInstance(context)
        val quality = settings.recordingQuality

        val sourcesToTry = if (isCall) {
            listOf(
                settings.callAudioSource.source,
                MediaRecorder.AudioSource.VOICE_RECOGNITION,
                MediaRecorder.AudioSource.VOICE_COMMUNICATION,
                MediaRecorder.AudioSource.MIC
            ).distinct()
        } else {
            listOf(MediaRecorder.AudioSource.MIC)
        }

        try {
            val fileDescriptor = context.contentResolver.openFileDescriptor(targetUri, "w")
            if (fileDescriptor == null) {
                onError("Failed to open file descriptor for audio recording.")
                return false
            }
            this.pfd = fileDescriptor
            this.currentUri = targetUri

            var recorderStarted = false
            var lastException: Exception? = null

            for (audioSource in sourcesToTry) {
                try {
                    val recorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                        MediaRecorder(context)
                    } else {
                        @Suppress("DEPRECATION")
                        MediaRecorder()
                    }

                    recorder.apply {
                        setAudioSource(audioSource)
                        setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                        setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                        setAudioChannels(1) // Mono voice channel is universally compatible across all OEMs
                        setAudioSamplingRate(quality.sampleRate)
                        setAudioEncodingBitRate(quality.bitRate)
                        setOutputFile(fileDescriptor.fileDescriptor)

                        setOnErrorListener { _, what, extra ->
                            Log.e(TAG, "MediaRecorder error: what=$what, extra=$extra")
                            onError("Audio recording hardware error: code $what")
                        }

                        setOnInfoListener { _, what, extra ->
                            Log.d(TAG, "MediaRecorder info: what=$what, extra=$extra")
                        }

                        prepare()
                        start()
                    }

                    this.mediaRecorder = recorder
                    Log.i(TAG, "MediaRecorder started successfully with AudioSource: $audioSource on $targetUri")
                    recorderStarted = true
                    break
                } catch (e: Exception) {
                    Log.w(TAG, "Failed to start MediaRecorder with AudioSource $audioSource: ${e.message}")
                    lastException = e
                    try {
                        mediaRecorder?.release()
                    } catch (ignored: Exception) {}
                    mediaRecorder = null
                }
            }

            if (!recorderStarted) {
                val message = when (lastException) {
                    is IllegalStateException -> "Microphone hardware is busy or in use by another application."
                    is java.io.IOException -> "Storage I/O error while preparing audio file."
                    else -> "Failed to initialize microphone: ${lastException?.localizedMessage ?: "unknown error"}"
                }
                releaseResources()
                onError(message)
                return false
            }

            return true

        } catch (e: Exception) {
            Log.e(TAG, "Exception during MediaRecorder start", e)
            val message = when (e) {
                is IllegalStateException -> "Microphone hardware is busy or in use by another application."
                is java.io.IOException -> "Storage I/O error while preparing audio file."
                else -> "Failed to initialize microphone: ${e.localizedMessage ?: "unknown error"}"
            }
            releaseResources()
            onError(message)
            return false
        }
    }

    @Synchronized
    fun stopRecording(): Boolean {
        var success = true
        val recorder = mediaRecorder
        if (recorder != null) {
            try {
                recorder.stop()
                Log.d(TAG, "MediaRecorder stopped successfully")
            } catch (e: RuntimeException) {
                // Occurs if stop() is called immediately before any frame was recorded
                Log.w(TAG, "MediaRecorder stop failed (audio likely too short)", e)
                success = false
            } finally {
                releaseResources()
            }
        }
        return success
    }

    @Synchronized
    fun releaseResources() {
        try {
            mediaRecorder?.reset()
        } catch (ignored: Exception) {}
        try {
            mediaRecorder?.release()
        } catch (ignored: Exception) {}
        mediaRecorder = null

        try {
            pfd?.close()
        } catch (ignored: Exception) {}
        pfd = null
        currentUri = null
    }

    companion object {
        private const val TAG = "AudioRecorderEngine"
    }
}
