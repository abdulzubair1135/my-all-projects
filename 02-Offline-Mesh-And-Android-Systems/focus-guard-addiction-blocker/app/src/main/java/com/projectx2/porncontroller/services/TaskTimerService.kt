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

class TaskTimerService : Service() {

    companion object {
        const val CHANNEL_ID = "task_timer_channel"
        const val NOTIFICATION_ID = 3001

        const val ACTION_START = "com.projectx2.porncontroller.START_TASK"
        const val ACTION_PAUSE = "com.projectx2.porncontroller.PAUSE_TASK"
        const val ACTION_RESUME = "com.projectx2.porncontroller.RESUME_TASK"
        const val ACTION_COMPLETE = "com.projectx2.porncontroller.COMPLETE_TASK"
        const val ACTION_CANCEL = "com.projectx2.porncontroller.CANCEL_TASK"

        const val EXTRA_TASK_ID = "extra_task_id"
        const val EXTRA_TASK_TITLE = "extra_task_title"
        const val EXTRA_DURATION_SECONDS = "extra_duration_seconds"

        private val _remainingSecondsFlow = MutableStateFlow(0)
        val remainingSecondsFlow: StateFlow<Int> = _remainingSecondsFlow.asStateFlow()

        private val _activeTaskIdFlow = MutableStateFlow<Long?>(null)
        val activeTaskIdFlow: StateFlow<Long?> = _activeTaskIdFlow.asStateFlow()

        private val _isPausedFlow = MutableStateFlow(false)
        val isPausedFlow: StateFlow<Boolean> = _isPausedFlow.asStateFlow()
    }

    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)
    private var timerJob: Job? = null

    private var currentTaskId: Long = 0
    private var currentTaskTitle: String = ""
    private var initialDurationSeconds: Int = 60
    private var remainingSeconds: Int = 60

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> {
                currentTaskId = intent.getLongExtra(EXTRA_TASK_ID, 0)
                currentTaskTitle = intent.getStringExtra(EXTRA_TASK_TITLE) ?: "Replacement Activity"
                initialDurationSeconds = intent.getIntExtra(EXTRA_DURATION_SECONDS, 60)
                startTask()
            }
            ACTION_PAUSE -> pauseTimer()
            ACTION_RESUME -> resumeTimer()
            ACTION_COMPLETE -> completeTask()
            ACTION_CANCEL -> cancelTask()
        }
        return START_NOT_STICKY
    }

    private fun startTask() {
        remainingSeconds = initialDurationSeconds
        _remainingSecondsFlow.value = remainingSeconds
        _activeTaskIdFlow.value = currentTaskId
        _isPausedFlow.value = false

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ServiceCompat.startForeground(
                this,
                NOTIFICATION_ID,
                buildNotification("$currentTaskTitle - ${formatTime(remainingSeconds)}"),
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE
            )
        } else {
            startForeground(NOTIFICATION_ID, buildNotification("$currentTaskTitle - ${formatTime(remainingSeconds)}"))
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

                if (remainingSeconds % 5 == 0 || remainingSeconds < 5) {
                    updateNotification("$currentTaskTitle - ${formatTime(remainingSeconds)}")
                }
            }

            if (remainingSeconds <= 0) {
                completeTask()
            }
        }
    }

    private fun pauseTimer() {
        timerJob?.cancel()
        _isPausedFlow.value = true
        updateNotification("Paused: $currentTaskTitle - ${formatTime(remainingSeconds)}")
    }

    private fun resumeTimer() {
        _isPausedFlow.value = false
        startCountdown()
    }

    private fun completeTask() {
        timerJob?.cancel()
        val app = application as? PornControllerApp
        app?.let {
            CoroutineScope(Dispatchers.IO).launch {
                it.repository.recordTaskCompletion(
                    taskId = currentTaskId,
                    title = currentTaskTitle,
                    durationSec = initialDurationSeconds - remainingSeconds
                )
            }
        }
        finishService()
    }

    private fun cancelTask() {
        timerJob?.cancel()
        finishService()
    }

    private fun finishService() {
        _activeTaskIdFlow.value = null
        _remainingSecondsFlow.value = 0
        _isPausedFlow.value = false
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
            .setContentTitle("Replacement Task")
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
                getString(R.string.task_channel_name),
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = getString(R.string.task_channel_desc)
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
