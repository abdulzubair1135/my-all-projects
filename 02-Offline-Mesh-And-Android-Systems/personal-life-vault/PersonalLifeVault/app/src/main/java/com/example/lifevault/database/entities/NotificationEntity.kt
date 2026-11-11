package com.example.lifevault.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "local_notifications",
    indices = [
        Index(value = ["clientEventId"], unique = true),
        Index(value = ["timestamp"])
    ]
)
data class NotificationEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val clientEventId: String,
    val appName: String,
    val title: String?,
    val content: String?,
    val timestamp: Long,
    val createdAt: Long = System.currentTimeMillis()
)
