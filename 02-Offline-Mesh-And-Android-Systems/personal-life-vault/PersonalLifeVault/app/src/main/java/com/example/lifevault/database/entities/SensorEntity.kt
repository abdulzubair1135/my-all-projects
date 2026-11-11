package com.example.lifevault.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "local_sensors",
    indices = [
        Index(value = ["clientEventId"], unique = true),
        Index(value = ["timestamp"])
    ]
)
data class SensorEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val clientEventId: String,
    val type: String, // 'battery' | 'steps' | 'network'
    val payloadJson: String,
    val timestamp: Long,
    val createdAt: Long = System.currentTimeMillis()
)
