package com.projectx2.porncontroller.core.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "detection_events")
data class DetectionEvent(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val type: String, // "DOMAIN" or "KEYWORD"
    val triggerSource: String, // e.g. domain name or keyword
    val appPackage: String? = null,
    val timestamp: Long = System.currentTimeMillis(),
    val interventionShown: Boolean = true,
    val actionTaken: String = "PENDING" // "RETURNED", "BREAK", "TASK", "DISMISSED"
)
