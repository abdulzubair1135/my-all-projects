package com.recoverx

import com.recoverx.data.entities.FileCategory
import com.recoverx.discovery.SignatureRegistry
import org.junit.Assert.*
import org.junit.Test
import java.io.ByteArrayInputStream

class SignatureRegistryTest {

    @Test
    fun testJpegSignatureIdentification() {
        val jpegHeader = byteArrayOf(0xFF.toByte(), 0xD8.toByte(), 0xFF.toByte(), 0xE0.toByte(), 0x00, 0x10)
        val info = SignatureRegistry.inspectHeader(ByteArrayInputStream(jpegHeader))

        assertNotNull(info)
        assertEquals("JPEG Image", info?.formatName)
        assertEquals(FileCategory.IMAGES, info?.category)
        assertEquals("jpg", info?.standardExtension)
    }

    @Test
    fun testPngSignatureIdentification() {
        val pngHeader = byteArrayOf(
            0x89.toByte(), 0x50.toByte(), 0x4E.toByte(), 0x47.toByte(),
            0x0D.toByte(), 0x0A.toByte(), 0x1A.toByte(), 0x0A.toByte()
        )
        val info = SignatureRegistry.inspectHeader(ByteArrayInputStream(pngHeader))

        assertNotNull(info)
        assertEquals("PNG Image", info?.formatName)
        assertEquals(FileCategory.IMAGES, info?.category)
        assertEquals("png", info?.standardExtension)
    }

    @Test
    fun testPdfSignatureIdentification() {
        val pdfHeader = "%PDF-1.4 header content".toByteArray(Charsets.US_ASCII)
        val info = SignatureRegistry.inspectHeader(ByteArrayInputStream(pdfHeader))

        assertNotNull(info)
        assertEquals("PDF Document", info?.formatName)
        assertEquals(FileCategory.DOCUMENTS, info?.category)
        assertEquals("pdf", info?.standardExtension)
    }

    @Test
    fun testZipSignatureIdentification() {
        val zipHeader = byteArrayOf(0x50.toByte(), 0x4B.toByte(), 0x03.toByte(), 0x04.toByte(), 0x14.toByte(), 0x00)
        val info = SignatureRegistry.inspectHeader(ByteArrayInputStream(zipHeader))

        assertNotNull(info)
        assertEquals("ZIP Archive", info?.formatName)
        assertEquals(FileCategory.ARCHIVES, info?.category)
        assertEquals("zip", info?.standardExtension)
    }

    @Test
    fun testUnknownHeaderReturnsNull() {
        val unknown = byteArrayOf(0x00, 0x01, 0x02, 0x03, 0x04)
        val info = SignatureRegistry.inspectHeader(ByteArrayInputStream(unknown))
        assertNull(info)
    }
}
