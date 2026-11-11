package com.recoverx

import com.recoverx.data.entities.FileCategory
import com.recoverx.discovery.FileCategorizer
import com.recoverx.recovery.CollisionResolver
import org.junit.Assert.*
import org.junit.Test

class FileCategorizerTest {

    @Test
    fun testCategorizeByExtension() {
        assertEquals(FileCategory.IMAGES, FileCategorizer.categorizeByExtension("jpg"))
        assertEquals(FileCategory.IMAGES, FileCategorizer.categorizeByExtension("png"))
        assertEquals(FileCategory.VIDEOS, FileCategorizer.categorizeByExtension("mp4"))
        assertEquals(FileCategory.AUDIO, FileCategorizer.categorizeByExtension("mp3"))
        assertEquals(FileCategory.DOCUMENTS, FileCategorizer.categorizeByExtension("pdf"))
        assertEquals(FileCategory.ARCHIVES, FileCategorizer.categorizeByExtension("zip"))
        assertEquals(FileCategory.OTHER, FileCategorizer.categorizeByExtension("bin"))
    }

    @Test
    fun testGetExtension() {
        assertEquals("jpg", FileCategorizer.getExtension("photo.jpg"))
        assertEquals("pdf", FileCategorizer.getExtension("document.final.PDF"))
        assertNull(FileCategorizer.getExtension("noextension"))
        assertNull(FileCategorizer.getExtension("endingwithdot."))
    }

    @Test
    fun testMimeMismatchDetection() {
        // Disguised files
        assertTrue(FileCategorizer.isKnownMimeMismatch("txt", "jpg"))
        assertTrue(FileCategorizer.isKnownMimeMismatch("dat", "png"))

        // Equivalent formats
        assertFalse(FileCategorizer.isKnownMimeMismatch("jpg", "jpeg"))
        assertFalse(FileCategorizer.isKnownMimeMismatch("jpeg", "jpg"))
        assertFalse(FileCategorizer.isKnownMimeMismatch("png", "png"))
    }
}

class CollisionResolverTest {

    @Test
    fun testResolveUniqueNameWithNoConflict() {
        val existing = setOf("file1.jpg", "file2.jpg")
        val unique = CollisionResolver.resolveUniqueName(existing, "file3.jpg")
        assertEquals("file3.jpg", unique)
    }

    @Test
    fun testResolveUniqueNameWithConflict() {
        val existing = setOf("photo.jpg", "photo (1).jpg")
        val unique = CollisionResolver.resolveUniqueName(existing, "photo.jpg")
        assertEquals("photo (2).jpg", unique)
    }

    @Test
    fun testResolveUniqueNameWithoutExtension() {
        val existing = setOf("archive", "archive (1)")
        val unique = CollisionResolver.resolveUniqueName(existing, "archive")
        assertEquals("archive (2)", unique)
    }
}
