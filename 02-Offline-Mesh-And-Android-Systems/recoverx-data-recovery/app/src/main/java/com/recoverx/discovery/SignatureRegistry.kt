package com.recoverx.discovery

import com.recoverx.data.entities.FileCategory
import java.io.InputStream

data class SignatureInfo(
    val formatName: String,
    val category: FileCategory,
    val mimeType: String,
    val standardExtension: String
)

object SignatureRegistry {

    private val JPEG_MAGIC = byteArrayOf(0xFF.toByte(), 0xD8.toByte(), 0xFF.toByte())
    private val PNG_MAGIC = byteArrayOf(0x89.toByte(), 0x50.toByte(), 0x4E.toByte(), 0x47.toByte(), 0x0D.toByte(), 0x0A.toByte(), 0x1A.toByte(), 0x0A.toByte())
    private val GIF87_MAGIC = "GIF87a".toByteArray(Charsets.US_ASCII)
    private val GIF89_MAGIC = "GIF89a".toByteArray(Charsets.US_ASCII)
    private val PDF_MAGIC = "%PDF".toByteArray(Charsets.US_ASCII)
    private val ZIP_MAGIC = byteArrayOf(0x50.toByte(), 0x4B.toByte(), 0x03.toByte(), 0x04.toByte())
    private val WEBP_RIFF = "RIFF".toByteArray(Charsets.US_ASCII)
    private val WEBP_WEBP = "WEBP".toByteArray(Charsets.US_ASCII)

    fun inspectHeader(stream: InputStream): SignatureInfo? {
        val buffer = ByteArray(32)
        val read = stream.read(buffer, 0, buffer.size)
        if (read < 4) return null

        // Check JPEG
        if (matchesPrefix(buffer, JPEG_MAGIC)) {
            return SignatureInfo("JPEG Image", FileCategory.IMAGES, "image/jpeg", "jpg")
        }

        // Check PNG
        if (read >= 8 && matchesPrefix(buffer, PNG_MAGIC)) {
            return SignatureInfo("PNG Image", FileCategory.IMAGES, "image/png", "png")
        }

        // Check GIF
        if (read >= 6 && (matchesPrefix(buffer, GIF87_MAGIC) || matchesPrefix(buffer, GIF89_MAGIC))) {
            return SignatureInfo("GIF Image", FileCategory.IMAGES, "image/gif", "gif")
        }

        // Check PDF
        if (matchesPrefix(buffer, PDF_MAGIC)) {
            return SignatureInfo("PDF Document", FileCategory.DOCUMENTS, "application/pdf", "pdf")
        }

        // Check ZIP
        if (matchesPrefix(buffer, ZIP_MAGIC)) {
            return SignatureInfo("ZIP Archive", FileCategory.ARCHIVES, "application/zip", "zip")
        }

        // Check WEBP (RIFF....WEBP)
        if (read >= 12 && matchesPrefix(buffer, WEBP_RIFF) && matchesAt(buffer, 8, WEBP_WEBP)) {
            return SignatureInfo("WebP Image", FileCategory.IMAGES, "image/webp", "webp")
        }

        // Check MP4 (offset 4 has 'ftyp')
        if (read >= 8) {
            val ftyp = "ftyp".toByteArray(Charsets.US_ASCII)
            if (matchesAt(buffer, 4, ftyp)) {
                return SignatureInfo("MP4 Video", FileCategory.VIDEOS, "video/mp4", "mp4")
            }
        }

        return null
    }

    private fun matchesPrefix(data: ByteArray, magic: ByteArray): Boolean {
        if (data.size < magic.size) return false
        for (i in magic.indices) {
            if (data[i] != magic[i]) return false
        }
        return true
    }

    private fun matchesAt(data: ByteArray, offset: Int, magic: ByteArray): Boolean {
        if (data.size < offset + magic.size) return false
        for (i in magic.indices) {
            if (data[offset + i] != magic[i]) return false
        }
        return true
    }
}
