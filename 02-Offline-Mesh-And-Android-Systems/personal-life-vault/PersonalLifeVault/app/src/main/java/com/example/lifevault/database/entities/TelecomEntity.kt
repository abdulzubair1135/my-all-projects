package com.example.lifevault.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "local_telecom",
    indices = [
        Index(value = ["clientEventId"], unique = true),
        Index(value = ["timestamp"]),
        Index(value = ["type", "timestamp"])
    ]
)
data class TelecomEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val clientEventId: String,
    val type: String, // 'sms' | 'call'
    val party: String?,
    val body: String?,
    val duration: Long?,
    val timestamp: Long,
    val createdAt: Long = System.currentTimeMillis()
)
