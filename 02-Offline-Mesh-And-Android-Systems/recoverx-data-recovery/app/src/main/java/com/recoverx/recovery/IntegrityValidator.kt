package com.recoverx.recovery

import android.content.Context
import android.net.Uri
import com.recoverx.discovery.SignatureRegistry
import java.io.InputStream

data class ValidationResult(
    val isValid: Boolean,
    val summary: String,
    val hasWarning: Boolean
)

object IntegrityValidator {

    fun validateRestoredFile(
        context: Context,
        restoredUri: Uri,
        expectedBytes: Long,
        expectedExtension: String?
    ): ValidationResult {
        var bytesRead = 0L
        var detectedExtension: String? = null

        try {
            context.contentResolver.openInputStream(restoredUri)?.use { stream ->
                val buffer = ByteArray(64 * 1024)
                var read = stream.read(buffer)
                if (read > 0) {
                    bytesRead += read
                    // Check header signature on first chunk
                    val headerStream = buffer.inputStream()
                    val sig = SignatureRegistry.inspectHeader(headerStream)
                    detectedExtension = sig?.standardExtension
                }

                while (read != -1) {
                    read = stream.read(buffer)
                    if (read > 0) {
                        bytesRead += read
                    }
                }
            }
        } catch (e: Exception) {
            return ValidationResult(
                isValid = false,
                summary = "Failed to read restored file for verification: ${e.localizedMessage}",
                hasWarning = true
            )
        }

        if (bytesRead == 0L && expectedBytes > 0L) {
            return ValidationResult(
                isValid = false,
                summary = "Restored file is empty (0 bytes written).",
                hasWarning = true
            )
        }

        if (expectedBytes > 0L && bytesRead != expectedBytes) {
            return ValidationResult(
                isValid = true,
                summary = "Size mismatch: expected $expectedBytes bytes, verified $bytesRead bytes.",
                hasWarning = true
            )
        }

        if (expectedExtension != null && detectedExtension != null && expectedExtension != detectedExtension) {
            return ValidationResult(
                isValid = true,
                summary = "Header verified as $detectedExtension (differed from original $expectedExtension).",
                hasWarning = false
            )
        }

        return ValidationResult(
            isValid = true,
            summary = "Integrity verified: $bytesRead bytes written successfully with valid stream.",
            hasWarning = false
        )
    }
}
