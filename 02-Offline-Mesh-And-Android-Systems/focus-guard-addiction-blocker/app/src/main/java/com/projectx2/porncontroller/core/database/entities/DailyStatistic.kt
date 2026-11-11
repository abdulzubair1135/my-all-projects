package com.projectx2.porncontroller.core.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "daily_statistics",
    indices = [Index(value = ["dateString"], unique = true)]
)
data class DailyStatistic(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val dateString: String, // "YYYY-MM-DD"
    val blockedDomainsCount: Int = 0,
    val blockedKeywordsCount: Int = 0,
    val completedTasksCount: Int = 0,
    val focusMinutesTotal: Int = 0,
    val interventionsAvoidedCount: Int = 0
)
