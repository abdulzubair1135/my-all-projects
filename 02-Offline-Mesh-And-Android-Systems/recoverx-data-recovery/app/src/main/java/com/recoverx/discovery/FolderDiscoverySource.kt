package com.recoverx.discovery

import android.content.Context
import android.net.Uri
import androidx.documentfile.provider.DocumentFile
import com.recoverx.data.entities.CandidateClassification
import com.recoverx.data.entities.DiscoveredItem
import com.recoverx.data.entities.FileCategory
import com.recoverx.data.entities.ReadabilityStatus
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.isActive
import kotlinx.coroutines.withContext
import kotlin.coroutines.coroutineContext

class FolderDiscoverySource(private val context: Context) {

    suspend fun scanTree(
        treeUri: Uri,
        sessionId: Long,
        maxDepth: Int = 8,
        onProgress: (scanned: Int, currentName: String) -> Unit
    ): List<DiscoveredItem> = withContext(Dispatchers.IO) {
        val results = mutableListOf<DiscoveredItem>()
        val rootDoc = DocumentFile.fromTreeUri(context, treeUri) ?: return@withContext emptyList()

        var scannedCount = 0

        suspend fun traverse(doc: DocumentFile, depth: Int) {
            if (depth > maxDepth || !coroutineContext.isActive) return

            val files = try {
                doc.listFiles()
            } catch (e: Exception) {
                emptyArray()
            }

            for (file in files) {
                if (!coroutineContext.isActive) return

                if (file.isDirectory) {
                    traverse(file, depth + 1)
                } else if (file.isFile) {
                    scannedCount++
                    val name = file.name ?: "Unnamed_${file.uri.lastPathSegment}"
                    val mime = file.type ?: "application/octet-stream"
                    val size = file.length()
                    val dateModified = file.lastModified()
                    val ext = FileCategorizer.getExtension(name)

                    // Inspect signature for magic byte mismatch or carved detection
                    var detectedExt: String? = null
                    var isMismatch = false
                    var classification = CandidateClassification.EXISTING_FILE

                    try {
                        context.contentResolver.openInputStream(file.uri)?.use { stream ->
                            val sig = SignatureRegistry.inspectHeader(stream)
                            if (sig != null) {
                                detectedExt = sig.standardExtension
                                if (FileCategorizer.isKnownMimeMismatch(ext, detectedExt)) {
                                    isMismatch = true
                                    classification = CandidateClassification.SIGNATURE_CARVED
                                }
                            }
                        }
                    } catch (e: Exception) {
                        // Inaccessible or unreadable stream
                    }

                    val category = if (detectedExt != null) {
                        FileCategorizer.categorizeByExtension(detectedExt)
                    } else {
                        FileCategorizer.categorize(mime, name)
                    }

                    results.add(
                        DiscoveredItem(
                            sessionId = sessionId,
                            uriString = file.uri.toString(),
                            displayName = name,
                            mimeType = mime,
                            sizeBytes = size,
                            dateModifiedMs = dateModified,
                            category = category,
                            classification = classification,
                            readability = if (file.canRead()) ReadabilityStatus.READABLE else ReadabilityStatus.PERMISSION_RESTRICTED,
                            relativePath = doc.name,
                            originalExtension = ext,
                            detectedExtension = detectedExt,
                            isMimeMismatch = isMismatch
                        )
                    )

                    if (scannedCount % 10 == 0) {
                        onProgress(scannedCount, name)
                    }
                }
            }
        }

        traverse(rootDoc, 0)
        results
    }
}
