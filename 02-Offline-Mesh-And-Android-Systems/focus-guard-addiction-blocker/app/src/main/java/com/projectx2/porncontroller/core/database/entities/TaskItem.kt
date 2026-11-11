package com.projectx2.porncontroller.core.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "tasks")
data class TaskItem(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val title: String,
    val description: String,
    val durationSeconds: Int,
    val category: String, // "MINDFULNESS", "PHYSICAL", "PRODUCTIVITY", "CUSTOM"
    val isPhysical: Boolean = false,
    val isEnabled: Boolean = true,
    val completionCount: Int = 0,
    val createdAt: Long = System.currentTimeMillis()
)
