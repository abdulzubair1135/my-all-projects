package com.projectx2.porncontroller.core.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "focus_sessions")
data class FocusSession(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val targetMinutes: Int,
    val actualMinutesCompleted: Int,
    val startedAt: Long,
    val endedAt: Long = System.currentTimeMillis(),
    val wasSuccessful: Boolean = true,
    val distractionAttemptsBlocked: Int = 0
)
