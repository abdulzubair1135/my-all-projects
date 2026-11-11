package com.recoverx.data.entities

enum class ScanType {
    QUICK,
    ADVANCED,
    CUSTOM_FOLDER
}

enum class FileCategory(val displayName: String) {
    IMAGES("Photos & Images"),
    VIDEOS("Videos"),
    AUDIO("Audio"),
    DOCUMENTS("Documents"),
    ARCHIVES("Archives"),
    DOWNLOADS("Downloads"),
    OTHER("Other Files")
}

enum class CandidateClassification(val title: String, val isDirectRecovery: Boolean) {
    EXISTING_FILE("Accessible File", false),
    ALTERNATE_COPY("Alternate Copy / Backup", true),
    THUMBNAIL_ONLY("Cached Thumbnail Only", true),
    MEDIA_TRASH("Accessible Trash Item", true),
    CORRUPTED_FILE("Partially Corrupted File", false),
    SIGNATURE_CARVED("Signature Matched (Carved)", true),
    NOT_RECOVERABLE("Not Recoverable", false)
}

enum class ReadabilityStatus {
    READABLE,
    PARTIALLY_READABLE,
    CORRUPTED,
    PERMISSION_RESTRICTED,
    UNKNOWN
}

enum class RecoveryStatus {
    IDLE,
    PENDING,
    IN_PROGRESS,
    COMPLETED,
    COMPLETED_WITH_WARNINGS,
    PARTIAL,
    FAILED,
    CANCELLED,
    SOURCE_UNAVAILABLE,
    INSUFFICIENT_STORAGE
}
