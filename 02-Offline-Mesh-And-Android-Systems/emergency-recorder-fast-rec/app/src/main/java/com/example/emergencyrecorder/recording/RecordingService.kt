package com.example.emergencyrecorder.recording

import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.media.AudioDeviceInfo
import android.media.AudioManager
import android.net.Uri
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.PowerManager
import android.util.Log
import com.example.emergencyrecorder.feedback.HapticFeedbackManager
import com.example.emergencyrecorder.notification.RecordingNotificationManager
import com.example.emergencyrecorder.settings.AppSettings
import com.example.emergencyrecorder.storage.RecordingStorage

class RecordingService : Service() {

    private lateinit var notificationManager: RecordingNotificationManager
    private lateinit var hapticFeedback: HapticFeedbackManager
    private lateinit var appSettings: AppSettings
    private var audioRecorderEngine: AudioRecorderEngine? = null

    private var activeUri: Uri? = null
    private var startTimeMs: Long = 0L
    private var currentPrefix: String = "Emergency"
    private var wakeLock: PowerManager.WakeLock? = null

    private val handler = Handler(Looper.getMainLooper())
    private val durationTicker = object : Runnable {
        override fun run() {
            if (startTimeMs > 0) {
                val elapsedSec = (System.currentTimeMillis() - startTimeMs) / 1000
                notificationManager.updateNotification(elapsedSec)

                // Check auto-stop timer if configured
                val autoStopMin = appSettings.autoStopMinutes
                if (autoStopMin > 0 && elapsedSec >= (autoStopMin * 60)) {
                    Log.i(TAG, "Auto-stop limit reached ($autoStopMin min). Stopping recording.")
                    stopActiveRecording()
                    return
                }

                handler.postDelayed(this, 1000)
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "RecordingService onCreate")
        notificationManager = RecordingNotificationManager(this)
        notificationManager.createNotificationChannel()
        hapticFeedback = HapticFeedbackManager(this)
        appSettings = AppSettings.getInstance(this)

        audioRecorderEngine = AudioRecorderEngine(this) { errorMsg ->
            handleRecordingError(errorMsg)
        }

        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "EmergencyRecorder:AudioCaptureWakeLock"
        ).apply {
            setReferenceCounted(false)
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action
        Log.d(TAG, "onStartCommand action: $action")

        when (action) {
            ACTION_START -> {
                val prefix = intent.getStringExtra(EXTRA_PREFIX) ?: "Emergency"
                startActiveRecording(prefix)
            }
            ACTION_STOP -> {
                stopActiveRecording()
            }
            else -> {
                Log.w(TAG, "Unknown action $action, stopping service")
                stopSelf()
            }
        }

        return START_NOT_STICKY
    }

    private fun startActiveRecording(prefix: String = "Emergency") {
        if (activeUri != null) {
            Log.w(TAG, "startActiveRecording called but already recording")
            return
        }
        this.currentPrefix = prefix

        // 1. Promote to Foreground immediately
        val initialNotification = notificationManager.buildForegroundNotification(0)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                RecordingNotificationManager.NOTIFICATION_ID,
                initialNotification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE
            )
        } else {
            startForeground(RecordingNotificationManager.NOTIFICATION_ID, initialNotification)
        }

        // 2. Acquire wake lock
        wakeLock?.acquire(3 * 60 * 60 * 1000L /* 3 hours max safeguard */)

        // 3. Create pending media entry
        val uri = RecordingStorage.createPendingAudioFile(this, prefix)
        if (uri == null) {
            handleRecordingError("Failed to create file in MediaStore.")
            return
        }
        activeUri = uri

        val isCall = prefix.startsWith("Call")
        if (isCall && appSettings.isAutoSpeakerOnCallEnabled) {
            enableSpeakerphone(true)
        }

        // 4. Start recording engine
        val started = audioRecorderEngine?.startRecording(uri, isCall = isCall) == true
        if (!started) {
            // Error callback inside audioRecorderEngine will handle failure cleanup
            if (isCall) enableSpeakerphone(false)
            return
        }

        startTimeMs = System.currentTimeMillis()
        RecordingController.notifyRecordingStarted(startTimeMs, uri)
        hapticFeedback.vibrateStart()

        // 5. Start duration notification updates
        handler.removeCallbacks(durationTicker)
        handler.postDelayed(durationTicker, 1000)
        Log.i(TAG, "Recording active on $uri with prefix $prefix")
    }

    private fun stopActiveRecording() {
        Log.d(TAG, "stopActiveRecording invoked")
        handler.removeCallbacks(durationTicker)

        val uri = activeUri
        val engineSuccess = audioRecorderEngine?.stopRecording() ?: false

        if (uri != null) {
            if (engineSuccess) {
                // If this is a call recording, query CallLog for the completed call's Contact Name and Number
                if (currentPrefix.startsWith("Call")) {
                    try {
                        val latest = com.example.emergencyrecorder.call.ContactHelper.getLatestCallDetails(this)
                        if (latest != null && (!latest.name.isNullOrBlank() || !latest.number.isNullOrBlank())) {
                            val nameTag = if (!latest.name.isNullOrBlank()) {
                                com.example.emergencyrecorder.call.ContactHelper.sanitizeForFilename(latest.name)
                            } else "Unknown"

                            val numTag = if (!latest.number.isNullOrBlank()) {
                                com.example.emergencyrecorder.call.ContactHelper.sanitizeForFilename(latest.number)
                            } else "Call"

                            val timestamp = java.text.SimpleDateFormat("yyyyMMdd_HHmmss", java.util.Locale.US).format(java.util.Date(startTimeMs))
                            val updatedFilename = "Call_${nameTag}_${numTag}_$timestamp.m4a"
                            RecordingStorage.renameAudioFile(this, uri, updatedFilename)
                            Log.i(TAG, "Finalized call recording filename to: $updatedFilename")
                        }
                    } catch (e: Exception) {
                        Log.e(TAG, "Error updating call filename on stop", e)
                    }
                }

                RecordingStorage.finalizeAudioFile(this, uri)
                Log.i(TAG, "Recording saved successfully: $uri")
            } else {
                RecordingStorage.discardPendingAudioFile(this, uri)
                Log.w(TAG, "Discarded empty/corrupted recording: $uri")
            }
        }

        if (currentPrefix.startsWith("Call")) {
            enableSpeakerphone(false)
        }

        activeUri = null
        startTimeMs = 0L
        currentPrefix = "Emergency"

        RecordingController.notifyRecordingStopped()
        hapticFeedback.vibrateStop()

        releaseWakeLock()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun enableSpeakerphone(enable: Boolean) {
        try {
            val audioManager = getSystemService(Context.AUDIO_SERVICE) as AudioManager
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                if (enable) {
                    val speaker = audioManager.availableCommunicationDevices.find {
                        it.type == AudioDeviceInfo.TYPE_BUILTIN_SPEAKER
                    }
                    if (speaker != null) {
                        audioManager.setCommunicationDevice(speaker)
                        Log.i(TAG, "Communication device set to builtin speaker for 2-way call audio capture")
                    }
                } else {
                    audioManager.clearCommunicationDevice()
                    Log.i(TAG, "Communication device cleared")
                }
            } else {
                @Suppress("DEPRECATION")
                audioManager.isSpeakerphoneOn = enable
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error configuring speakerphone: ${e.message}")
        }
    }

    private fun handleRecordingError(message: String) {
        Log.e(TAG, "handleRecordingError: $message")
        handler.removeCallbacks(durationTicker)
        enableSpeakerphone(false)

        val uri = activeUri
        if (uri != null) {
            RecordingStorage.discardPendingAudioFile(this, uri)
            activeUri = null
        }
        startTimeMs = 0L

        audioRecorderEngine?.releaseResources()
        RecordingController.notifyRecordingError(message)
        hapticFeedback.vibrateError()

        releaseWakeLock()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun releaseWakeLock() {
        try {
            if (wakeLock?.isHeld == true) {
                wakeLock?.release()
            }
        } catch (ignored: Exception) {}
    }

    override fun onDestroy() {
        Log.d(TAG, "RecordingService onDestroy")
        enableSpeakerphone(false)
        handler.removeCallbacks(durationTicker)
        audioRecorderEngine?.releaseResources()
        audioRecorderEngine = null
        releaseWakeLock()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        private const val TAG = "RecordingService"
        const val ACTION_START = "com.example.emergencyrecorder.action.START_RECORDING"
        const val ACTION_STOP = "com.example.emergencyrecorder.action.STOP_RECORDING"
        const val EXTRA_PREFIX = "com.example.emergencyrecorder.extra.PREFIX"
    }
}
