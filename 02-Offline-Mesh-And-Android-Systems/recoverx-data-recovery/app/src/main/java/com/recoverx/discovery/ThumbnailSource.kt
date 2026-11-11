package com.recoverx.discovery

import android.content.ContentResolver
import android.content.ContentUris
import android.content.Context
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import androidx.core.content.ContextCompat
import com.recoverx.data.entities.CandidateClassification
import com.recoverx.data.entities.DiscoveredItem
import com.recoverx.data.entities.FileCategory
import com.recoverx.data.entities.ReadabilityStatus
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileInputStream

class ThumbnailSource(private val context: Context) {

    suspend fun discoverThumbnails(
        sessionId: Long,
        onProgress: ((count: Int, name: String) -> Unit)? = null
    ): List<DiscoveredItem> = withContext(Dispatchers.IO) {
        val list = mutableListOf<DiscoveredItem>()
        val seenPaths = mutableSetOf<String>()

        // 1. Filesystem scan for actual thumbnail caches (.thumbnails) and trash directories
        val baseDirs = mutableListOf<File>()
        
        // Primary external storage
        val primaryStorage = Environment.getExternalStorageDirectory()
        if (primaryStorage != null && primaryStorage.exists()) {
            baseDirs.add(primaryStorage)
        }

        // Secondary / Removable storage (SD cards)
        val externalFilesDirs = ContextCompat.getExternalFilesDirs(context, null)
        for (f in externalFilesDirs) {
            var root = f
            while (root?.parentFile != null && root.parentFile?.canRead() == true && root.parentFile?.name != "Android") {
                root = root.parentFile
            }
            if (root != null && root.exists() && !baseDirs.contains(root)) {
                baseDirs.add(root)
            }
        }

        // Specific high-yield thumbnail & trash subdirectories
        val relativeCandidatePaths = listOf(
            "Pictures/.thumbnails",
            "DCIM/.thumbnails",
            "Movies/.thumbnails",
            "ShareKaroLite/.thumbnails",
            "Music/.thumbnails",
            "Download/.thumbnails",
            ".thumbnails",
            "LOST.DIR",
            "Pictures/.trash",
            "Pictures/.trashed",
            "DCIM/.trash",
            "DCIM/.trashed"
        )

        for (base in baseDirs) {
            for (rel in relativeCandidatePaths) {
                val candidateDir = File(base, rel)
                if (candidateDir.exists() && candidateDir.isDirectory) {
                    scanCandidateDirectory(candidateDir, sessionId, list, seenPaths, onProgress)
                }
            }
        }

        // 2. Also search for any files starting with ".trashed-" in standard media folders
        val mediaFolders = listOf(
            File(primaryStorage, "Pictures"),
            File(primaryStorage, "DCIM/Camera"),
            File(primaryStorage, "Movies"),
            File(primaryStorage, "Download")
        )

        for (folder in mediaFolders) {
            if (folder.exists() && folder.isDirectory) {
                folder.listFiles { f -> f.isFile && f.name.startsWith(".trashed") }?.forEach { trashedFile ->
                    if (!seenPaths.contains(trashedFile.absolutePath) && trashedFile.length() > 0) {
                        seenPaths.add(trashedFile.absolutePath)
                        val ext = trashedFile.extension.lowercase()
                        val isVideo = ext in listOf("mp4", "mkv", "3gp", "webm")
                        val isAudio = ext in listOf("mp3", "m4a", "wav", "aac")
                        val cat = if (isVideo) FileCategory.VIDEOS else if (isAudio) FileCategory.AUDIO else FileCategory.IMAGES

                        list.add(
                            DiscoveredItem(
                                sessionId = sessionId,
                                uriString = Uri.fromFile(trashedFile).toString(),
                                displayName = trashedFile.name.substringAfterLast("-").ifBlank { trashedFile.name },
                                mimeType = if (isVideo) "video/$ext" else if (isAudio) "audio/$ext" else "image/$ext",
                                sizeBytes = trashedFile.length(),
                                dateModifiedMs = trashedFile.lastModified(),
                                category = cat,
                                classification = CandidateClassification.MEDIA_TRASH,
                                readability = ReadabilityStatus.READABLE,
                                relativePath = trashedFile.parentFile?.name ?: "Trash",
                                originalExtension = ext,
                                detectedExtension = ext,
                                isMimeMismatch = false
                            )
                        )
                    }
                }
            }
        }

        // 3. Fallback: MediaStore.Images.Thumbnails legacy table (for Android 9 and older)
        if (list.size < 50) {
            queryLegacyMediaStoreThumbnails(sessionId, list, seenPaths)
        }

        // Sort candidates: most recently modified first
        list.sortByDescending { it.dateModifiedMs }

        // Cap to 2500 highest quality candidates to keep UI performant
        if (list.size > 2500) {
            list.subList(0, 2500)
        } else {
            list
        }
    }

    private fun scanCandidateDirectory(
        dir: File,
        sessionId: Long,
        results: MutableList<DiscoveredItem>,
        seenPaths: MutableSet<String>,
        onProgress: ((count: Int, name: String) -> Unit)?
    ) {
        val files = dir.listFiles() ?: return

        for (file in files) {
            if (!file.isFile || file.length() <= 0L) continue
            if (seenPaths.contains(file.absolutePath)) continue
            seenPaths.add(file.absolutePath)

            val name = file.name
            if (name == ".nomedia" || name == ".database_uuid") continue

            val ext = file.extension.lowercase()
            val isKnownImage = ext in listOf("jpg", "jpeg", "png", "webp", "gif", "bmp")
            val isKnownVideo = ext in listOf("mp4", "mkv", "3gp", "mov", "avi")

            val isImage = isKnownImage || (!isKnownVideo && hasImageMagicBytes(file))
            val isVideo = isKnownVideo || (!isImage && hasVideoMagicBytes(file))

            val cat = if (isImage) {
                FileCategory.IMAGES
            } else if (isVideo) {
                FileCategory.VIDEOS
            } else {
                FileCategory.OTHER
            }

            val isTrash = dir.name.contains("trash", ignoreCase = true) || name.startsWith(".trashed")
            val isLostDir = dir.name.equals("LOST.DIR", ignoreCase = true)

            val classification = when {
                isTrash -> CandidateClassification.MEDIA_TRASH
                isLostDir -> CandidateClassification.SIGNATURE_CARVED
                else -> CandidateClassification.THUMBNAIL_ONLY
            }

            val mime = when {
                isImage -> if (ext.isNotBlank()) "image/$ext" else "image/jpeg"
                isVideo -> if (ext.isNotBlank()) "video/$ext" else "video/mp4"
                else -> "application/octet-stream"
            }

            results.add(
                DiscoveredItem(
                    sessionId = sessionId,
                    uriString = Uri.fromFile(file).toString(),
                    displayName = name,
                    mimeType = mime,
                    sizeBytes = file.length(),
                    dateModifiedMs = file.lastModified(),
                    category = cat,
                    classification = classification,
                    readability = ReadabilityStatus.READABLE,
                    relativePath = dir.name,
                    originalExtension = ext.ifBlank { if (isImage) "jpg" else "bin" },
                    detectedExtension = ext.ifBlank { if (isImage) "jpg" else "bin" },
                    isMimeMismatch = false
                )
            )

            if (results.size % 25 == 0) {
                onProgress?.invoke(results.size, name)
            }
        }
    }

    private fun hasImageMagicBytes(file: File): Boolean {
        if (file.length() < 8) return false
        return try {
            FileInputStream(file).use { stream ->
                val header = ByteArray(8)
                val read = stream.read(header)
                if (read < 4) return false
                // JPEG: FF D8 FF
                if (header[0] == 0xFF.toByte() && header[1] == 0xD8.toByte() && header[2] == 0xFF.toByte()) return true
                // PNG: 89 50 4E 47
                if (header[0] == 0x89.toByte() && header[1] == 0x50.toByte() && header[2] == 0x4E.toByte() && header[3] == 0x47.toByte()) return true
                // GIF: 47 49 46 38
                if (header[0] == 0x47.toByte() && header[1] == 0x49.toByte() && header[2] == 0x46.toByte()) return true
                false
            }
        } catch (e: Exception) {
            false
        }
    }

    private fun hasVideoMagicBytes(file: File): Boolean {
        if (file.length() < 12) return false
        return try {
            FileInputStream(file).use { stream ->
                val header = ByteArray(12)
                val read = stream.read(header)
                if (read < 12) return false
                // MP4: [....]ftyp
                header[4] == 0x66.toByte() && header[5] == 0x74.toByte() && header[6] == 0x79.toByte() && header[7] == 0x70.toByte()
            }
        } catch (e: Exception) {
            false
        }
    }

    private fun queryLegacyMediaStoreThumbnails(
        sessionId: Long,
        list: MutableList<DiscoveredItem>,
        seenPaths: MutableSet<String>
    ) {
        val contentResolver: ContentResolver = context.contentResolver
        try {
            val projection = arrayOf(
                MediaStore.Images.Thumbnails._ID,
                MediaStore.Images.Thumbnails.IMAGE_ID,
                MediaStore.Images.Thumbnails.WIDTH,
                MediaStore.Images.Thumbnails.HEIGHT
            )

            val cursor = contentResolver.query(
                MediaStore.Images.Thumbnails.EXTERNAL_CONTENT_URI,
                projection,
                null,
                null,
                null
            )

            cursor?.use { c ->
                val idCol = c.getColumnIndex(MediaStore.Images.Thumbnails._ID)
                val imgIdCol = c.getColumnIndex(MediaStore.Images.Thumbnails.IMAGE_ID)
                val widthCol = c.getColumnIndex(MediaStore.Images.Thumbnails.WIDTH)
                val heightCol = c.getColumnIndex(MediaStore.Images.Thumbnails.HEIGHT)

                while (c.moveToNext()) {
                    val id = c.getLong(idCol)
                    val imgId = if (imgIdCol != -1) c.getLong(imgIdCol) else 0L
                    val w = if (widthCol != -1) c.getInt(widthCol) else 0
                    val h = if (heightCol != -1) c.getInt(heightCol) else 0
                    val thumbUri = ContentUris.withAppendedId(MediaStore.Images.Thumbnails.EXTERNAL_CONTENT_URI, id)

                    if (!seenPaths.contains(thumbUri.toString())) {
                        seenPaths.add(thumbUri.toString())
                        list.add(
                            DiscoveredItem(
                                sessionId = sessionId,
                                uriString = thumbUri.toString(),
                                displayName = "Thumbnail_${imgId}_${w}x${h}.jpg",
                                mimeType = "image/jpeg",
                                sizeBytes = 0L,
                                dateModifiedMs = System.currentTimeMillis(),
                                category = FileCategory.IMAGES,
                                classification = CandidateClassification.THUMBNAIL_ONLY,
                                readability = ReadabilityStatus.READABLE,
                                relativePath = ".thumbnails",
                                originalExtension = "jpg",
                                detectedExtension = "jpg",
                                isMimeMismatch = false
                            )
                        )
                    }
                }
            }
        } catch (e: Exception) {
            // Ignored
        }
    }
}

