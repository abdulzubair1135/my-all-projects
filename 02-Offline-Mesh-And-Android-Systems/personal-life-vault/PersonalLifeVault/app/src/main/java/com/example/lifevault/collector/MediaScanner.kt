package com.example.lifevault.collector

import android.content.ContentUris
import android.content.Context
import android.os.Build
import android.provider.MediaStore
import com.example.lifevault.repository.VaultRepository

class MediaScanner(
    private val context: Context,
    private val repository: VaultRepository
) {

    suspend fun scanNewMedia(sinceTimestampMs: Long = System.currentTimeMillis() - 20 * 86400000L) {
        val sinceSec = sinceTimestampMs / 1000L

        // 1. TOP PRIORITY: Scan Audio Recordings & Calls (Last 20 days, newest first)
        scanCollection(
            collectionUri = MediaStore.Audio.Media.EXTERNAL_CONTENT_URI,
            sinceSeconds = sinceSec,
            isAudio = true
        )

        // 2. Scan Captured Photos
        scanCollection(
            collectionUri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
            sinceSeconds = sinceSec,
            isAudio = false
        )

        // 3. Scan Captured Videos
        scanCollection(
            collectionUri = MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
            sinceSeconds = sinceSec,
            isAudio = false
        )
    }

    private suspend fun scanCollection(
        collectionUri: android.net.Uri,
        sinceSeconds: Long,
        isAudio: Boolean
    ) {
        try {
            val projection = mutableListOf(
                MediaStore.MediaColumns._ID,
                MediaStore.MediaColumns.DISPLAY_NAME,
                MediaStore.MediaColumns.MIME_TYPE,
                MediaStore.MediaColumns.SIZE,
                MediaStore.MediaColumns.DATE_MODIFIED
            )
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                projection.add(MediaStore.MediaColumns.RELATIVE_PATH)
            }

            val selection = "${MediaStore.MediaColumns.DATE_MODIFIED} > ?"
            val selectionArgs = arrayOf(sinceSeconds.toString())

            val cursor = context.contentResolver.query(
                collectionUri,
                projection.toTypedArray(),
                selection,
                selectionArgs,
                "${MediaStore.MediaColumns.DATE_MODIFIED} DESC"
            )

            cursor?.use { c ->
                val idIdx = c.getColumnIndex(MediaStore.MediaColumns._ID)
                val nameIdx = c.getColumnIndex(MediaStore.MediaColumns.DISPLAY_NAME)
                val mimeIdx = c.getColumnIndex(MediaStore.MediaColumns.MIME_TYPE)
                val sizeIdx = c.getColumnIndex(MediaStore.MediaColumns.SIZE)
                val dateIdx = c.getColumnIndex(MediaStore.MediaColumns.DATE_MODIFIED)
                val relIdx = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    c.getColumnIndex(MediaStore.MediaColumns.RELATIVE_PATH)
                } else -1

                while (c.moveToNext()) {
                    val id = if (idIdx >= 0) c.getLong(idIdx) else continue
                    val contentUri = ContentUris.withAppendedId(collectionUri, id)
                    val name = if (nameIdx >= 0) c.getString(nameIdx) else "unnamed_media"
                    val mime = if (mimeIdx >= 0) c.getString(mimeIdx) ?: "application/octet-stream" else "application/octet-stream"
                    val size = if (sizeIdx >= 0) c.getLong(sizeIdx) else 0L
                    val dateModifiedMs = if (dateIdx >= 0) c.getLong(dateIdx) * 1000L else System.currentTimeMillis()
                    val relPath = if (relIdx >= 0) c.getString(relIdx) else null

                    if (size > 0) {
                        repository.enqueueMedia(
                            uri = contentUri.toString(),
                            displayName = name,
                            mimeType = mime,
                            size = size,
                            timestamp = dateModifiedMs,
                            relativePath = relPath
                        )
                    }
                }
            }
        } catch (_: SecurityException) {
            // Permission not yet granted
        } catch (_: Exception) {
            // Ignore cursor exceptions
        }
    }
}
