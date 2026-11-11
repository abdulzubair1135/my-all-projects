package com.example.emergencyrecorder.accessibility

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.os.SystemClock
import android.util.Log
import android.view.KeyEvent
import android.view.accessibility.AccessibilityEvent
import com.example.emergencyrecorder.recording.RecordingController
import com.example.emergencyrecorder.settings.AppSettings

class VolumeKeyAccessibilityService : AccessibilityService() {

    private lateinit var appSettings: AppSettings
    private lateinit var detector: DoublePressDetector

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "VolumeKeyAccessibilityService onCreate")
        appSettings = AppSettings.getInstance(this)
        detector = DoublePressDetector(
            windowMs = appSettings.doublePressIntervalMs
        )
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.i(TAG, "Accessibility Service Connected and active.")

        // Ensure key event filtering flag is explicitly set
        val info = serviceInfo ?: AccessibilityServiceInfo()
        info.flags = info.flags or AccessibilityServiceInfo.FLAG_REQUEST_FILTER_KEY_EVENTS
        serviceInfo = info

        detector.updateWindow(appSettings.doublePressIntervalMs)
    }

    override fun onKeyEvent(event: KeyEvent): Boolean {
        // Only process Volume Down key
        if (event.keyCode != KeyEvent.KEYCODE_VOLUME_DOWN) {
            return false
        }

        // Check if master shortcut is enabled in user settings
        if (!appSettings.isShortcutEnabled) {
            return false
        }

        // Only process key-down transitions, ignore auto-repeat events
        if (event.action == KeyEvent.ACTION_DOWN) {
            if (event.repeatCount != 0) {
                // Ignore key repeat when held down
                return false
            }

            // Update window setting in case user changed it in Settings
            detector.updateWindow(appSettings.doublePressIntervalMs)

            val now = SystemClock.elapsedRealtime()
            val triggered = detector.onKeyDown(now)

            Log.i(TAG, "Volume Down pressed (clean click). Triggered=$triggered")

            if (triggered) {
                Log.i(TAG, "EMERGENCY TRIGGER: Double-press Volume Down detected! Toggling recording.")
                RecordingController.toggleRecording(applicationContext)
                // Consume this triggering key event so it doesn't accidentally trigger OEM volume slider UI
                return true
            }
        }

        // Return false to let normal single volume button presses pass through to the OS audio system
        return false
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Intentionally no-op: This service does not inspect, read, or track any window or UI content.
    }

    override fun onInterrupt() {
        Log.w(TAG, "Accessibility Service interrupted")
        detector.reset()
    }

    override fun onDestroy() {
        Log.d(TAG, "VolumeKeyAccessibilityService onDestroy")
        detector.reset()
        super.onDestroy()
    }

    companion object {
        private const val TAG = "VolumeKeyAccessService"
    }
}
