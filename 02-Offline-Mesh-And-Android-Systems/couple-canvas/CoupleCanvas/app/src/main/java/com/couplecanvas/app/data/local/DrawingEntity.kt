package com.couplecanvas.app.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "drawings")
data class DrawingEntity(
    @PrimaryKey val id: String,
    val title: String,
    val createdAt: Long,
    val updatedAt: Long,
    val partnerName: String?,
    val previewImagePath: String?,
    val operationsJson: String // Serialized JSON of List<CanvasOperation>
)

@Entity(tableName = "user_profile")
data class UserProfileEntity(
    @PrimaryKey val userId: String,
    val displayName: String,
    val partnerName: String?,
    val createdTimestamp: Long
)
