package com.projectx2.porncontroller.core.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "habit_streaks")
data class HabitStreak(
    @PrimaryKey val id: Int = 1,
    val currentStreakDays: Int = 0,
    val longestStreakDays: Int = 0,
    val lastCleanDate: String = "", // "YYYY-MM-DD"
    val totalCleanDays: Int = 0
)
