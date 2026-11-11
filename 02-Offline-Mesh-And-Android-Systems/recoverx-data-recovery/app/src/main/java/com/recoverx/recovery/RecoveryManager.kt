package com.recoverx.recovery

import android.content.Context
import android.net.Uri
import android.os.Environment
import androidx.documentfile.provider.DocumentFile
import com.recoverx.core.storage.StorageInspector
import com.recoverx.data.database.RecoverXDatabaseHelper
import com.recoverx.data.entities.DiscoveredItem
import com.recoverx.data.entities.RecoveryRecord
import com.recoverx.data.entities.RecoveryStatus
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.withContext
import java.io.File

data class RecoveryExecutionState(
    val isRunning: Boolean = false,
    val currentItemName: String = "",
    val progressBytes: Long = 0L,
    val totalBytes: Long = 0L,
    val lastRecord: RecoveryRecord? = null,
    val error: String? = null
)

class RecoveryManager(
    private val context: Context,
    private val dbHelper: RecoverXDatabaseHelper
) {
    private val _state = MutableStateFlow(RecoveryExecutionState())
    val state: StateFlow<RecoveryExecutionState> = _state

    suspend fun restoreItem(
        item: DiscoveredItem,
        destinationTreeUri: Uri? = null
    ): RecoveryRecord = withContext(Dispatchers.IO) {
        val startTime = System.currentTimeMillis()
        _state.value = RecoveryExecutionState(
            isRunning = true,
            currentItemName = item.displayName,
            totalBytes = item.sizeBytes
        )

        var record = RecoveryRecord(
            itemId = item.id,
            originalName = item.displayName,
            sourceUri = item.uriString,
            destinationUri = null,
            destinationPath = null,
            startTimeMs = startTime,
            status = RecoveryStatus.IN_PROGRESS
        )
        val recordId = dbHelper.insertRecoveryRecord(record)
        record = record.copy(id = recordId)

        try {
            // Check storage space
            val assessment = StorageInspector.assessStorage(context)
            if (item.sizeBytes > 0 && assessment.availableInternalBytes < item.sizeBytes + 10 * 1024 * 1024) {
                record = record.copy(
                    endTimeMs = System.currentTimeMillis(),
                    status = RecoveryStatus.INSUFFICIENT_STORAGE,
                    errorMessage = "Available storage is below safe threshold for restoration."
                )
                dbHelper.updateRecoveryRecord(record)
                _state.value = RecoveryExecutionState(isRunning = false, lastRecord = record, error = record.errorMessage)
                return@withContext record
            }

            // Determine destination: SAF Document or App Recovered folder
            val destUri: Uri
            val destPath: String

            if (destinationTreeUri != null) {
                val treeDoc = DocumentFile.fromTreeUri(context, destinationTreeUri)
                    ?: throw IllegalStateException("Destination folder is not accessible.")

                val existingNames = treeDoc.listFiles().mapNotNull { it.name }.toSet()
                val uniqueName = CollisionResolver.resolveUniqueName(existingNames, item.displayName)
                val newFile = treeDoc.createFile(item.mimeType, uniqueName)
                    ?: throw IllegalStateException("Failed to create destination file in chosen folder.")

                destUri = newFile.uri
                destPath = "${treeDoc.name}/$uniqueName"
            } else {
                val recoveryDir = File(context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), "RecoverX_Restored")
                if (!recoveryDir.exists()) recoveryDir.mkdirs()

                val uniqueFile = CollisionResolver.resolveUniqueFile(recoveryDir, item.displayName)
                destUri = Uri.fromFile(uniqueFile)
                destPath = uniqueFile.absolutePath
            }

            // Perform streaming copy
            val sourceUri = Uri.parse(item.uriString)
            val bytesWritten = StreamingRestorer.streamCopy(
                context = context,
                sourceUri = sourceUri,
                destUri = destUri,
                totalExpectedBytes = item.sizeBytes
            ) { progress ->
                _state.value = _state.value.copy(
                    progressBytes = progress.bytesWritten
                )
            }

            // Verify integrity
            val validation = IntegrityValidator.validateRestoredFile(
                context = context,
                restoredUri = destUri,
                expectedBytes = item.sizeBytes,
                expectedExtension = item.originalExtension
            )

            val finalStatus = if (validation.isValid) {
                if (validation.hasWarning) RecoveryStatus.COMPLETED_WITH_WARNINGS else RecoveryStatus.COMPLETED
            } else {
                RecoveryStatus.FAILED
            }

            record = record.copy(
                destinationUri = destUri.toString(),
                destinationPath = destPath,
                endTimeMs = System.currentTimeMillis(),
                status = finalStatus,
                bytesWritten = bytesWritten,
                validationSummary = validation.summary,
                errorMessage = if (!validation.isValid) validation.summary else null
            )
            dbHelper.updateRecoveryRecord(record)

            _state.value = RecoveryExecutionState(
                isRunning = false,
                currentItemName = item.displayName,
                progressBytes = bytesWritten,
                totalBytes = item.sizeBytes,
                lastRecord = record
            )

        } catch (e: Exception) {
            record = record.copy(
                endTimeMs = System.currentTimeMillis(),
                status = if (e is kotlinx.coroutines.CancellationException) RecoveryStatus.CANCELLED else RecoveryStatus.FAILED,
                errorMessage = e.localizedMessage ?: "Unknown restoration error."
            )
            dbHelper.updateRecoveryRecord(record)
            _state.value = RecoveryExecutionState(
                isRunning = false,
                lastRecord = record,
                error = record.errorMessage
            )
        }

        record
    }
}
