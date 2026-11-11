package com.recoverx.core.storage

import android.content.Context
import android.os.Environment
import android.os.StatFs
import android.os.storage.StorageManager
import java.io.File

data class StorageAssessment(
    val totalInternalBytes: Long,
    val availableInternalBytes: Long,
    val usedInternalBytes: Long,
    val hasRemovableStorage: Boolean,
    val removableVolumes: List<String>
)

object StorageInspector {

    fun assessStorage(context: Context): StorageAssessment {
        val dataDir = Environment.getDataDirectory()
        val stat = StatFs(dataDir.path)
        val blockSize = stat.blockSizeLong
        val totalBlocks = stat.blockCountLong
        val availableBlocks = stat.availableBlocksLong

        val totalBytes = totalBlocks * blockSize
        val availableBytes = availableBlocks * blockSize
        val usedBytes = (totalBytes - availableBytes).coerceAtLeast(0L)

        val storageManager = context.getSystemService(Context.STORAGE_SERVICE) as? StorageManager
        val removableList = mutableListOf<String>()
        var hasRemovable = false

        if (storageManager != null) {
            val volumes = storageManager.storageVolumes
            for (vol in volumes) {
                if (vol.isRemovable) {
                    hasRemovable = true
                    removableList.add(vol.getDescription(context) ?: "External SD Card")
                }
            }
        }

        return StorageAssessment(
            totalInternalBytes = totalBytes,
            availableInternalBytes = availableBytes,
            usedInternalBytes = usedBytes,
            hasRemovableStorage = hasRemovable,
            removableVolumes = removableList
        )
    }

    fun formatBytes(bytes: Long): String {
        if (bytes < 0) return "0 B"
        val kb = bytes / 1024.0
        val mb = kb / 1024.0
        val gb = mb / 1024.0
        val tb = gb / 1024.0

        return when {
            tb >= 1.0 -> String.format("%.2f TB", tb)
            gb >= 1.0 -> String.format("%.2f GB", gb)
            mb >= 1.0 -> String.format("%.2f MB", mb)
            kb >= 1.0 -> String.format("%.2f KB", kb)
            else -> "$bytes B"
        }
    }
}
