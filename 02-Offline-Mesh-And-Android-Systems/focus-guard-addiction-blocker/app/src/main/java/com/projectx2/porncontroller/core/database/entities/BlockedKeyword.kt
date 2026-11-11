package com.projectx2.porncontroller.core.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "blocked_keywords",
    indices = [Index(value = ["keyword"], unique = true)]
)
data class BlockedKeyword(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val keyword: String,
    val isExactMatchOnly: Boolean = false,
    val isEnabled: Boolean = true,
    val hitCount: Int = 0,
    val repetitionThreshold: Int = 2,
    val createdAt: Long = System.currentTimeMillis()
)
