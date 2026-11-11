package com.example.emergencyrecorder.storage

import android.content.ContentUris
import android.content.ContentValues
import android.content.Context
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.os.StatFs
import android.provider.MediaStore
import android.util.Log
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object RecordingStorage {

    private const val TAG = "RecordingStorage"
    private const val RELATIVE_SUBDIRECTORY = "Recordings/EmergencyRecorder"
    private const val MIME_TYPE_AUDIO_M4A = "audio/mp4"

    // Minimum free disk space required before starting recording (15 MB)
    private const val MIN_FREE_SPACE_BYTES = 15 * 1024 * 1024L

    fun hasSufficientStorage(context: Context): Boolean {
        return try {
            val path = context.getExternalFilesDir(null) ?: Environment.getExternalStorageDirectory()
            val stat = StatFs(path.path)
            val availableBytes = stat.availableBlocksLong * stat.blockSizeLong
            availableBytes > MIN_FREE_SPACE_BYTES
        } catch (e: Exception) {
            Log.e(TAG, "Error checking free space", e)
            true
        }
    }

    fun generateUniqueFilename(prefix: String = "Emergency"): String {
        val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
        return "${prefix}_$timestamp.m4a"
    }

    fun createPendingAudioFile(context: Context, prefix: String = "Emergency"): Uri? {
        val filename = generateUniqueFilename(prefix)
        val values = ContentValues().apply {
            put(MediaStore.Audio.Media.DISPLAY_NAME, filename)
            put(MediaStore.Audio.Media.MIME_TYPE, MIME_TYPE_AUDIO_M4A)
            put(MediaStore.Audio.Media.DATE_ADDED, System.currentTimeMillis() / 1000)

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                put(MediaStore.Audio.Media.RELATIVE_PATH, RELATIVE_SUBDIRECTORY)
                put(MediaStore.Audio.Media.IS_PENDING, 1)
            }
        }

        return try {
            val uri = context.contentResolver.insert(MediaStore.Audio.Media.EXTERNAL_CONTENT_URI, values)
            Log.d(TAG, "Created pending audio record: $uri ($filename)")
            uri
        } catch (e: Exception) {
            Log.e(TAG, "Failed to create MediaStore entry", e)
            null
        }
    }

    fun finalizeAudioFile(context: Context, uri: Uri) {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val values = ContentValues().apply {
                    put(MediaStore.Audio.Media.IS_PENDING, 0)
                }
                context.contentResolver.update(uri, values, null, null)
                Log.d(TAG, "Finalized audio record (is_pending=0): $uri")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to finalize MediaStore record: $uri", e)
        }
    }

    fun renameAudioFile(context: Context, uri: Uri, newDisplayName: String) {
        try {
            val values = ContentValues().apply {
                put(MediaStore.Audio.Media.DISPLAY_NAME, newDisplayName)
            }
            context.contentResolver.update(uri, values, null, null)
            Log.i(TAG, "Renamed audio record to: $newDisplayName")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to rename audio record at $uri", e)
        }
    }

    fun discardPendingAudioFile(context: Context, uri: Uri) {
        try {
            context.contentResolver.delete(uri, null, null)
            Log.d(TAG, "Discarded/deleted pending audio record: $uri")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to delete discarded audio record: $uri", e)
        }
    }

    fun deleteAudioFile(context: Context, uri: Uri): Boolean {
        return try {
            val rows = context.contentResolver.delete(uri, null, null)
            rows > 0
        } catch (e: Exception) {
            Log.e(TAG, "Failed to delete audio file: $uri", e)
            false
        }
    }

    fun queryAllRecordings(context: Context): List<RecordingItem> {
        val recordings = mutableListOf<RecordingItem>()

        val projection = arrayOf(
            MediaStore.Audio.Media._ID,
            MediaStore.Audio.Media.DISPLAY_NAME,
            MediaStore.Audio.Media.DATE_ADDED,
            MediaStore.Audio.Media.DURATION,
            MediaStore.Audio.Media.SIZE
        )

        // Select recordings starting with Emergency_ or Call_
        val selection = "(${MediaStore.Audio.Media.DISPLAY_NAME} LIKE 'Emergency_%.m4a' OR ${MediaStore.Audio.Media.DISPLAY_NAME} LIKE 'Call_%.m4a')"
        val sortOrder = "${MediaStore.Audio.Media.DATE_ADDED} DESC"

        try {
            context.contentResolver.query(
                MediaStore.Audio.Media.EXTERNAL_CONTENT_URI,
                projection,
                selection,
                null,
                sortOrder
            )?.use { cursor ->
                val idColumn = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media._ID)
                val nameColumn = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media.DISPLAY_NAME)
                val dateColumn = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media.DATE_ADDED)
                val durationColumn = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media.DURATION)
                val sizeColumn = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media.SIZE)

                while (cursor.moveToNext()) {
                    val id = cursor.getLong(idColumn)
                    val name = cursor.getString(nameColumn) ?: "Recording_$id"
                    val dateAddedSec = cursor.getLong(dateColumn)
                    val durationMs = cursor.getLong(durationColumn)
                    val sizeBytes = cursor.getLong(sizeColumn)

                    val contentUri = ContentUris.withAppendedId(
                        MediaStore.Audio.Media.EXTERNAL_CONTENT_URI,
                        id
                    )

                    recordings.add(
                        RecordingItem(
                            id = id,
                            uri = contentUri,
                            displayName = name,
                            dateAddedMs = dateAddedSec * 1000,
                            durationMs = durationMs,
                            sizeBytes = sizeBytes
                        )
                    )
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error querying recordings", e)
        }

        return recordings
    }
}
