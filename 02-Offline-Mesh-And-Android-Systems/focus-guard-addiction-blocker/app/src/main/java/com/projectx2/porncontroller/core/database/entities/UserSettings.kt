package com.projectx2.porncontroller.core.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "user_settings")
data class UserSettings(
    @PrimaryKey val id: Int = 1,
    val isDomainProtectionEnabled: Boolean = true,
    val isKeywordMonitoringEnabled: Boolean = true,
    val interventionCategory: String = "MOTIVATIONAL", // MOTIVATIONAL, STRICT, FUNNY, FRIENDLY
    val customInterventionMessage: String = "Stop wasting your time. Get back to what matters.",
    val repetitionThreshold: Int = 3, // Repetitions to trigger intervention
    val cooldownPeriodMinutes: Int = 5,
    val detectionSensitivity: Float = 0.8f, // 0.5 to 1.0
    val soundIntroEnabled: Boolean = true,
    val soundAlertsEnabled: Boolean = true,
    val hapticAlertsEnabled: Boolean = true,
    val safeBrowsingDns: String = "1.1.1.3", // Cloudflare Family DNS (blocks adult content)
    val hasCompletedOnboarding: Boolean = false
)
