package com.projectx2.porncontroller.core.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "blocked_domains",
    indices = [Index(value = ["domain"], unique = true)]
)
data class BlockedDomain(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val domain: String,
    val category: String = "Adult Content",
    val isCustom: Boolean = false,
    val isEnabled: Boolean = true,
    val blockedCount: Int = 0,
    val createdAt: Long = System.currentTimeMillis()
)
