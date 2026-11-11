package com.example.emergencyrecorder

import android.app.Application
import com.example.emergencyrecorder.notification.RecordingNotificationManager

class EmergencyRecorderApp : Application() {

    override fun onCreate() {
        super.onCreate()
        val notificationManager = RecordingNotificationManager(this)
        notificationManager.createNotificationChannel()
    }
}
