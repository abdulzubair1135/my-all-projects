package com.recoverx.discovery

import com.recoverx.data.entities.FileCategory
import java.util.Locale

object FileCategorizer {

    private val IMAGE_EXTENSIONS = setOf("jpg", "jpeg", "png", "webp", "gif", "bmp", "heic", "heif", "svg", "raw", "dng")
    private val VIDEO_EXTENSIONS = setOf("mp4", "mkv", "3gp", "webm", "mov", "avi", "flv", "wmv", "ts")
    private val AUDIO_EXTENSIONS = setOf("mp3", "wav", "aac", "ogg", "flac", "m4a", "wma", "opus", "amr")
    private val DOC_EXTENSIONS = setOf("pdf", "txt", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "csv", "json", "xml", "html", "epub")
    private val ARCHIVE_EXTENSIONS = setOf("zip", "rar", "7z", "tar", "gz", "bz2", "xz")

    fun categorizeByExtension(extension: String?): FileCategory {
        val ext = extension?.lowercase(Locale.ROOT) ?: return FileCategory.OTHER
        return when {
            IMAGE_EXTENSIONS.contains(ext) -> FileCategory.IMAGES
            VIDEO_EXTENSIONS.contains(ext) -> FileCategory.VIDEOS
            AUDIO_EXTENSIONS.contains(ext) -> FileCategory.AUDIO
            DOC_EXTENSIONS.contains(ext) -> FileCategory.DOCUMENTS
            ARCHIVE_EXTENSIONS.contains(ext) -> FileCategory.ARCHIVES
            else -> FileCategory.OTHER
        }
    }

    fun categorize(mimeType: String?, displayName: String?): FileCategory {
        val ext = getExtension(displayName)
        val extCategory = categorizeByExtension(ext)
        if (extCategory != FileCategory.OTHER) return extCategory

        val mime = mimeType?.lowercase(Locale.ROOT) ?: return FileCategory.OTHER
        return when {
            mime.startsWith("image/") -> FileCategory.IMAGES
            mime.startsWith("video/") -> FileCategory.VIDEOS
            mime.startsWith("audio/") -> FileCategory.AUDIO
            mime.startsWith("text/") || mime.contains("pdf") || mime.contains("document") || mime.contains("sheet") -> FileCategory.DOCUMENTS
            mime.contains("zip") || mime.contains("compressed") || mime.contains("archive") -> FileCategory.ARCHIVES
            else -> FileCategory.OTHER
        }
    }

    fun getExtension(name: String?): String? {
        if (name.isNullOrBlank()) return null
        val dot = name.lastIndexOf('.')
        if (dot < 0 || dot == name.length - 1) return null
        return name.substring(dot + 1).lowercase(Locale.ROOT)
    }

    fun isKnownMimeMismatch(extension: String?, detectedExtension: String?): Boolean {
        if (extension == null || detectedExtension == null) return false
        val ext = extension.lowercase(Locale.ROOT)
        val detected = detectedExtension.lowercase(Locale.ROOT)
        if (ext == detected) return false

        // Common image variations are not considered mismatches
        if ((ext == "jpeg" && detected == "jpg") || (ext == "jpg" && detected == "jpeg")) return false
        return true
    }
}
