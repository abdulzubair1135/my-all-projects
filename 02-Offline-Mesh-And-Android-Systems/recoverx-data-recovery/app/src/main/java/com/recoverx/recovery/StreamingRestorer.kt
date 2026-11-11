package com.recoverx.recovery

import android.content.Context
import android.net.Uri
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.isActive
import kotlinx.coroutines.withContext
import java.io.InputStream
import java.io.OutputStream
import kotlin.coroutines.coroutineContext

data class RestorationProgress(
    val bytesWritten: Long,
    val totalBytes: Long,
    val isComplete: Boolean
)

object StreamingRestorer {

    private const val BUFFER_SIZE = 64 * 1024 // 64 KB streaming buffer

    suspend fun streamCopy(
        context: Context,
        sourceUri: Uri,
        destUri: Uri,
        totalExpectedBytes: Long,
        onProgress: (RestorationProgress) -> Unit
    ): Long = withContext(Dispatchers.IO) {
        var totalWritten = 0L

        val inputStream: InputStream = context.contentResolver.openInputStream(sourceUri)
            ?: throw IllegalStateException("Cannot open input stream for source URI: $sourceUri")

        val outputStream: OutputStream = context.contentResolver.openOutputStream(destUri)
            ?: throw IllegalStateException("Cannot open output stream for destination URI: $destUri")

        inputStream.use { input ->
            outputStream.use { output ->
                val buffer = ByteArray(BUFFER_SIZE)
                var bytesRead: Int

                while (input.read(buffer).also { bytesRead = it } != -1) {
                    if (!coroutineContext.isActive) {
                        throw kotlinx.coroutines.CancellationException("Restoration stream cancelled by user.")
                    }

                    output.write(buffer, 0, bytesRead)
                    totalWritten += bytesRead

                    onProgress(
                        RestorationProgress(
                            bytesWritten = totalWritten,
                            totalBytes = totalExpectedBytes,
                            isComplete = false
                        )
                    )
                }
                output.flush()
            }
        }

        onProgress(
            RestorationProgress(
                bytesWritten = totalWritten,
                totalBytes = totalExpectedBytes,
                isComplete = true
            )
        )

        totalWritten
    }
}
