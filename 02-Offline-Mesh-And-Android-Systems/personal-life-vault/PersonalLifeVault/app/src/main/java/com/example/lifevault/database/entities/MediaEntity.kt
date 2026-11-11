package com.example.lifevault.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "local_media",
    indices = [
        Index(value = ["uri"], unique = true),
        Index(value = ["fileHash"]),
        Index(value = ["timestamp"])
    ]
)
data class MediaEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val uri: String,
    val displayName: String,
    val mimeType: String,
    val size: Long,
    val timestamp: Long,
    val relativePath: String?,
    val fileHash: String?,
    val createdAt: Long = System.currentTimeMillis()
)
