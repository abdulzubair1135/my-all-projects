package com.example.emergencyrecorder.storage

import android.net.Uri

data class RecordingItem(
    val id: Long,
    val uri: Uri,
    val displayName: String,
    val dateAddedMs: Long,
    val durationMs: Long,
    val sizeBytes: Long
)
