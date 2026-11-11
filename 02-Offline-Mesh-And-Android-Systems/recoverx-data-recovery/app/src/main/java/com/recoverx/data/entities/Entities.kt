package com.recoverx.data.entities

data class ScanSession(
    val id: Long = 0,
    val scanType: ScanType,
    val startTimeMs: Long,
    val endTimeMs: Long = 0,
    val status: String,
    val sourcesInspected: String,
    val filesInspected: Int = 0,
    val candidateCount: Int = 0,
    val errorCount: Int = 0
)

data class DiscoveredItem(
    val id: Long = 0,
    val sessionId: Long,
    val uriString: String,
    val displayName: String,
    val mimeType: String,
    val sizeBytes: Long,
    val dateModifiedMs: Long,
    val category: FileCategory,
    val classification: CandidateClassification,
    val readability: ReadabilityStatus,
    val relativePath: String? = null,
    val originalExtension: String? = null,
    val detectedExtension: String? = null,
    val isMimeMismatch: Boolean = false,
    val hashSha256: String? = null
)

data class RecoveryRecord(
    val id: Long = 0,
    val itemId: Long,
    val originalName: String,
    val sourceUri: String,
    val destinationUri: String?,
    val destinationPath: String?,
    val startTimeMs: Long,
    val endTimeMs: Long = 0,
    val status: RecoveryStatus,
    val bytesWritten: Long = 0,
    val validationSummary: String? = null,
    val errorMessage: String? = null
)

data class ScanErrorRecord(
    val id: Long = 0,
    val sessionId: Long,
    val source: String,
    val errorCategory: String,
    val message: String,
    val timestampMs: Long
)
