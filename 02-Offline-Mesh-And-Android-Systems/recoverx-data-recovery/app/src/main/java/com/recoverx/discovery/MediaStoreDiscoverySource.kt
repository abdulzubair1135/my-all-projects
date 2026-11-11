package com.recoverx.discovery

import android.content.ContentResolver
import android.content.ContentUris
import android.content.Context
import android.database.Cursor
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import com.recoverx.data.entities.CandidateClassification
import com.recoverx.data.entities.DiscoveredItem
import com.recoverx.data.entities.FileCategory
import com.recoverx.data.entities.ReadabilityStatus
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class MediaStoreDiscoverySource(private val context: Context) {

    suspend fun queryMedia(
        sessionId: Long,
        onProgress: (scanned: Int, currentName: String) -> Unit
    ): List<DiscoveredItem> = withContext(Dispatchers.IO) {
        val results = mutableListOf<DiscoveredItem>()
        val contentResolver = context.contentResolver

        val targets = listOf(
            Pair(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, FileCategory.IMAGES),
            Pair(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, FileCategory.VIDEOS),
            Pair(MediaStore.Audio.Media.EXTERNAL_CONTENT_URI, FileCategory.AUDIO),
            Pair(MediaStore.Files.getContentUri("external"), FileCategory.OTHER)
        )

        var totalScanned = 0

        for ((tableUri, category) in targets) {
            val projection = mutableListOf(
                MediaStore.MediaColumns._ID,
                MediaStore.MediaColumns.DISPLAY_NAME,
                MediaStore.MediaColumns.MIME_TYPE,
                MediaStore.MediaColumns.SIZE,
                MediaStore.MediaColumns.DATE_MODIFIED
            )

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                projection.add(MediaStore.MediaColumns.RELATIVE_PATH)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    projection.add(MediaStore.MediaColumns.IS_TRASHED)
                }
            }

            // Query 1: Explicitly check for TRASHED files on Android 11+ (API 30+)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                try {
                    val trashBundle = android.os.Bundle().apply {
                        putInt(MediaStore.QUERY_ARG_MATCH_TRASHED, MediaStore.MATCH_ONLY)
                    }
                    val trashCursor = contentResolver.query(
                        tableUri,
                        projection.toTypedArray(),
                        trashBundle,
                        null
                    )
                    trashCursor?.use { c ->
                        val idCol = c.getColumnIndex(MediaStore.MediaColumns._ID)
                        val nameCol = c.getColumnIndex(MediaStore.MediaColumns.DISPLAY_NAME)
                        val mimeCol = c.getColumnIndex(MediaStore.MediaColumns.MIME_TYPE)
                        val sizeCol = c.getColumnIndex(MediaStore.MediaColumns.SIZE)
                        val dateCol = c.getColumnIndex(MediaStore.MediaColumns.DATE_MODIFIED)
                        val relPathCol = c.getColumnIndex(MediaStore.MediaColumns.RELATIVE_PATH)

                        while (c.moveToNext()) {
                            totalScanned++
                            val id = c.getLong(idCol)
                            val name = if (nameCol != -1) c.getString(nameCol) ?: "Trash_$id" else "Trash_$id"
                            val mime = if (mimeCol != -1) c.getString(mimeCol) ?: "application/octet-stream" else "application/octet-stream"
                            val size = if (sizeCol != -1) c.getLong(sizeCol) else 0L
                            val dateSec = if (dateCol != -1) c.getLong(dateCol) else 0L
                            val dateMs = dateSec * 1000L
                            val relPath = if (relPathCol != -1) c.getString(relPathCol) else "Trash"
                            val itemUri = ContentUris.withAppendedId(tableUri, id)
                            val detectedCategory = if (category != FileCategory.OTHER) category else FileCategorizer.categorize(mime, name)
                            val ext = FileCategorizer.getExtension(name)

                            results.add(
                                DiscoveredItem(
                                    sessionId = sessionId,
                                    uriString = itemUri.toString(),
                                    displayName = name,
                                    mimeType = mime,
                                    sizeBytes = size,
                                    dateModifiedMs = dateMs,
                                    category = detectedCategory,
                                    classification = CandidateClassification.MEDIA_TRASH,
                                    readability = ReadabilityStatus.READABLE,
                                    relativePath = relPath,
                                    originalExtension = ext,
                                    detectedExtension = ext,
                                    isMimeMismatch = false
                                )
                            )
                        }
                    }
                } catch (e: Exception) {
                    // Trash query not supported or no trashed items
                }
            }

            val cursor: Cursor? = try {
                contentResolver.query(
                    tableUri,
                    projection.toTypedArray(),
                    null,
                    null,
                    "${MediaStore.MediaColumns.DATE_MODIFIED} DESC"
                )
            } catch (e: Exception) {
                null
            }

            cursor?.use { c ->
                val idCol = c.getColumnIndex(MediaStore.MediaColumns._ID)
                val nameCol = c.getColumnIndex(MediaStore.MediaColumns.DISPLAY_NAME)
                val mimeCol = c.getColumnIndex(MediaStore.MediaColumns.MIME_TYPE)
                val sizeCol = c.getColumnIndex(MediaStore.MediaColumns.SIZE)
                val dateCol = c.getColumnIndex(MediaStore.MediaColumns.DATE_MODIFIED)
                val relPathCol = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    c.getColumnIndex(MediaStore.MediaColumns.RELATIVE_PATH)
                } else -1
                val trashCol = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    c.getColumnIndex(MediaStore.MediaColumns.IS_TRASHED)
                } else -1

                while (c.moveToNext()) {
                    totalScanned++
                    val id = c.getLong(idCol)
                    val name = if (nameCol != -1) c.getString(nameCol) ?: "Unknown_$id" else "Unknown_$id"
                    val mime = if (mimeCol != -1) c.getString(mimeCol) ?: "application/octet-stream" else "application/octet-stream"
                    val size = if (sizeCol != -1) c.getLong(sizeCol) else 0L
                    val dateSec = if (dateCol != -1) c.getLong(dateCol) else 0L
                    val dateMs = dateSec * 1000L
                    val relPath = if (relPathCol != -1) c.getString(relPathCol) else null

                    val isTrashed = if (trashCol != -1) c.getInt(trashCol) == 1 else false
                    val itemUri = ContentUris.withAppendedId(tableUri, id)

                    val detectedCategory = if (category != FileCategory.OTHER) category else FileCategorizer.categorize(mime, name)
                    val ext = FileCategorizer.getExtension(name)

                    val classification = if (isTrashed) {
                        CandidateClassification.MEDIA_TRASH
                    } else {
                        CandidateClassification.EXISTING_FILE
                    }

                    results.add(
                        DiscoveredItem(
                            sessionId = sessionId,
                            uriString = itemUri.toString(),
                            displayName = name,
                            mimeType = mime,
                            sizeBytes = size,
                            dateModifiedMs = dateMs,
                            category = detectedCategory,
                            classification = classification,
                            readability = ReadabilityStatus.READABLE,
                            relativePath = relPath,
                            originalExtension = ext,
                            detectedExtension = ext,
                            isMimeMismatch = false
                        )
                    )

                    if (totalScanned % 15 == 0) {
                        onProgress(totalScanned, name)
                    }
                }
            }
        }

        results
    }
}
