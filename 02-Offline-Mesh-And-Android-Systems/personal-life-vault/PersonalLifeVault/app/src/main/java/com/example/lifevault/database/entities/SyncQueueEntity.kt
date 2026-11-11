package com.example.lifevault.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

enum class SyncStatus {
    PENDING,
    UPLOADING,
    SYNCED,
    FAILED
}

enum class DataType {
    NOTIFICATION,
    TELECOM,
    SENSOR,
    MEDIA
}

@Entity(
    tableName = "sync_queue",
    indices = [
        Index(value = ["syncStatus"]),
        Index(value = ["dataType"]),
        Index(value = ["createdAt"])
    ]
)
data class SyncQueueEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val dataType: String, // from DataType
    val payloadJson: String,
    val createdAt: Long = System.currentTimeMillis(),
    var syncStatus: String = SyncStatus.PENDING.name,
    var retryCount: Int = 0,
    var lastError: String? = null
)
