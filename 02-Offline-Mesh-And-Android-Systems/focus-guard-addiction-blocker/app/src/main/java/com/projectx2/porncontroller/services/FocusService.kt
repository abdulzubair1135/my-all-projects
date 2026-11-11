package com.projectx2.porncontroller.services

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import com.projectx2.porncontroller.MainActivity
import com.projectx2.porncontroller.PornControllerApp
import com.projectx2.porncontroller.R
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class FocusService : Service() {

    companion object {
        const val CHANNEL_ID = "focus_timer_channel"
        const val NOTIFICATION_ID = 2001

        const val ACTION_START = "com.projectx2.porncontroller.START_FOCUS"
        const val ACTION_PAUSE = "com.projectx2.porncontroller.PAUSE_FOCUS"
        const val ACTION_RESUME = "com.projectx2.porncontroller.RESUME_FOCUS"
        const val ACTION_STOP = "com.projectx2.porncontroller.STOP_FOCUS"
        const val EXTRA_DURATION_MINUTES = "extra_duration_minutes"

        private val _remainingSecondsFlow = MutableStateFlow(0)
        val remainingSecondsFlow: StateFlow<Int> = _remainingSecondsFlow.asStateFlow()

        private val _isRunningFlow = MutableStateFlow(false)
        val isRunningFlow: StateFlow<Boolean> = _isRunningFlow.asStateFlow()

        private val _isPausedFlow = MutableStateFlow(false)
        val isPausedFlow: StateFlow<Boolean> = _isPausedFlow.asStateFlow()
    }

    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)
    private var timerJob: Job? = null

    private var targetMinutes = 25
    private var totalSeconds = 25 * 60
    private var remainingSeconds = 25 * 60
    private var startedAt = 0L

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> {
                targetMinutes = intent.getIntExtra(EXTRA_DURATION_MINUTES, 25)
                startFocusSession(targetMinutes)
            }
            ACTION_PAUSE -> pauseTimer()
            ACTION_RESUME -> resumeTimer()
            ACTION_STOP -> stopFocusSession(cancelled = true)
        }
        return START_NOT_STICKY
    }

    private fun startFocusSession(minutes: Int) {
        startedAt = System.currentTimeMillis()
        totalSeconds = minutes * 60
        remainingSeconds = totalSeconds
        _remainingSecondsFlow.value = remainingSeconds
        _isRunningFlow.value = true
        _isPausedFlow.value = false

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ServiceCompat.startForeground(
                this,
                NOTIFICATION_ID,
                buildNotification("Focus Session Active - ${formatTime(remainingSeconds)}"),
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE
            )
        } else {
            startForeground(NOTIFICATION_ID, buildNotification("Focus Session Active - ${formatTime(remainingSeconds)}"))
        }

        startCountdown()
    }

    private fun startCountdown() {
        timerJob?.cancel()
        timerJob = serviceScope.launch {
            while (remainingSeconds > 0 && isActive) {
                delay(1000L)
                remainingSeconds--
                _remainingSecondsFlow.value = remainingSeconds

                if (remainingSeconds % 5 == 0 || remainingSeconds < 10) {
                    updateNotification("Focus Session Active - ${formatTime(remainingSeconds)}")
                }
            }

            if (remainingSeconds <= 0) {
                completeFocusSession()
            }
        }
    }

    private fun pauseTimer() {
        timerJob?.cancel()
        _isPausedFlow.value = true
        updateNotification("Focus Session Paused - ${formatTime(remainingSeconds)}")
    }

    private fun resumeTimer() {
        _isPausedFlow.value = false
        startCountdown()
    }

    private fun completeFocusSession() {
        val app = application as? PornControllerApp
        app?.let {
            CoroutineScope(Dispatchers.IO).launch {
                it.repository.recordFocusSession(
                    targetMin = targetMinutes,
                    actualMin = targetMinutes,
                    startedAt = startedAt,
                    successful = true
                )
            }
        }
        stopFocusSession(cancelled = false)
    }

    private fun stopFocusSession(cancelled: Boolean) {
        if (cancelled && startedAt > 0) {
            val minutesSpent = (totalSeconds - remainingSeconds) / 60
            if (minutesSpent > 1) {
                val app = application as? PornControllerApp
                app?.let {
                    CoroutineScope(Dispatchers.IO).launch {
                        it.repository.recordFocusSession(
                            targetMin = targetMinutes,
                            actualMin = minutesSpent,
                            startedAt = startedAt,
                            successful = false
                        )
                    }
                }
            }
        }

        timerJob?.cancel()
        _isRunningFlow.value = false
        _isPausedFlow.value = false
        _remainingSecondsFlow.value = 0
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun formatTime(seconds: Int): String {
        val m = seconds / 60
        val s = seconds % 60
        return String.format("%02d:%02d", m, s)
    }

    private fun buildNotification(text: String): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Focus Mode")
            .setContentText(text)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun updateNotification(text: String) {
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.notify(NOTIFICATION_ID, buildNotification(text))
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                getString(R.string.focus_channel_name),
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = getString(R.string.focus_channel_desc)
                setShowBadge(false)
            }
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        serviceJob.cancel()
        super.onDestroy()
    }
}
