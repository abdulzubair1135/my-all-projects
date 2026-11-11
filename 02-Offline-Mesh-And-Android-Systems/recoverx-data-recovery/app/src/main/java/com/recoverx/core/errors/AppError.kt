package com.recoverx.core.errors

sealed class AppError(
    val category: String,
    val userFriendlyMessage: String,
    val actionableGuidance: String,
    val isFatal: Boolean = false
) {
    class PermissionDenied(details: String = "") : AppError(
        category = "PERMISSION",
        userFriendlyMessage = "Storage permission was not granted.",
        actionableGuidance = "Grant access in Application Settings to allow RecoverX to discover files."
    )

    class PartialAccessRestricted : AppError(
        category = "PERMISSION",
        userFriendlyMessage = "Only partial media access is granted.",
        actionableGuidance = "Some files cannot be scanned until full media permissions are granted."
    )

    class StorageSpaceLow(val requiredBytes: Long, val availableBytes: Long) : AppError(
        category = "STORAGE",
        userFriendlyMessage = "Insufficient destination storage for recovery.",
        actionableGuidance = "Free up device storage or select an alternative folder."
    )

    class SourceUnavailable(val uri: String) : AppError(
        category = "IO",
        userFriendlyMessage = "Source file or folder is no longer accessible.",
        actionableGuidance = "The original file may have been moved, renamed, or unmounted."
    )

    class WriteFailed(val reason: String) : AppError(
        category = "IO",
        userFriendlyMessage = "Failed to write recovered file: $reason",
        actionableGuidance = "Check destination folder permissions and try again."
    )

    class CorruptedStream(val details: String) : AppError(
        category = "FORMAT",
        userFriendlyMessage = "File stream appears truncated or corrupt.",
        actionableGuidance = "Partial recovery may be attempted, but data integrity cannot be guaranteed."
    )

    class OperationCancelled : AppError(
        category = "USER_ACTION",
        userFriendlyMessage = "Operation was cancelled by user.",
        actionableGuidance = "You can restart the scan or restoration at any time."
    )
}
