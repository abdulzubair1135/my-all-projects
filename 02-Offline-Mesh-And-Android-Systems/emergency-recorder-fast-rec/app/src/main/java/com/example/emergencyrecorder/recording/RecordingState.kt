package com.example.emergencyrecorder.recording

import android.net.Uri

sealed interface RecordingState {

    object Idle : RecordingState

    object Starting : RecordingState

    data class Recording(
        val startTimeMs: Long,
        val outputUri: Uri,
        val elapsedDurationMs: Long = 0L
    ) : RecordingState

    object Stopping : RecordingState

    data class Error(
        val message: String,
        val timestampMs: Long = System.currentTimeMillis()
    ) : RecordingState

    val isRecording: Boolean
        get() = this is Recording

    val canStart: Boolean
        get() = this is Idle || this is Error

    val canStop: Boolean
        get() = this is Recording || this is Starting
}
