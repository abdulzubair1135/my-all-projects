package com.example.meshlink.ai.server

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.net.wifi.WifiManager
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.example.meshlink.R

class PocketAiServerService : Service(), PocketAiServerController.StateListener {

    companion object {
        private const val TAG = "PocketAiService"
        const val ACTION_START = "com.example.meshlink.ai.server.ACTION_START"
        const val ACTION_STOP = "com.example.meshlink.ai.server.ACTION_STOP"
        private const val NOTIFICATION_ID = 9988
        private const val CHANNEL_ID = "pocketai_server_channel"
        private const val CHANNEL_NAME = "PocketAI Local Server"
    }

    private var httpServer: PocketAiHttpServer? = null
    private var wifiLock: WifiManager.WifiLock? = null
    private lateinit var notificationManager: NotificationManager

    override fun onCreate() {
        super.onCreate()
        notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        createNotificationChannel()

        // Acquire WifiLock to prevent hotspot Wi-Fi chip sleep
        try {
            val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as? WifiManager
            wifiLock = wifiManager?.createWifiLock(
                WifiManager.WIFI_MODE_FULL_HIGH_PERF,
                "PocketAi::WifiLock"
            )?.apply {
                setReferenceCounted(false)
                acquire()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error acquiring WifiLock: ${e.message}")
        }

        PocketAiServerController.addListener(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action ?: ACTION_START

        if (action == ACTION_STOP) {
            stopSelf()
            return START_NOT_STICKY
        }

        val port = PocketAiServerController.getPort(this)
        val ip = NetworkUtils.getPrimaryIpAddress(this)

        val notification = buildNotification(
            title = "PocketAI Server Active",
            text = "Running at http://$ip:$port • Status: Idle",
            isGenerating = false
        )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        if (httpServer == null) {
            PocketAiServerController.notifyServerState(
                PocketAiServerController.ServerState.STARTING,
                ip,
                port
            )
            httpServer = PocketAiHttpServer(this, port).also {
                it.start()
            }
        }

        return START_STICKY
    }

    override fun onDestroy() {
        PocketAiServerController.removeListener(this)

        httpServer?.stop()
        httpServer = null

        try {
            if (wifiLock?.isHeld == true) {
                wifiLock?.release()
            }
        } catch (ignored: Exception) {}

        stopForeground(true)
        super.onDestroy()
        Log.i(TAG, "PocketAiServerService destroyed.")
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Shows live status and control for offline PocketAI server"
                setShowBadge(false)
            }
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(title: String, text: String, isGenerating: Boolean): Notification {
        val openIntent = Intent(this, PocketAiServerActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val openPendingIntent = PendingIntent.getActivity(
            this,
            0,
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val stopIntent = Intent(this, PocketAiServerService::class.java).apply {
            action = ACTION_STOP
        }
        val stopPendingIntent = PendingIntent.getService(
            this,
            1,
            stopIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_nexus_logo)
            .setContentTitle(title)
            .setContentText(text)
            .setOngoing(true)
            .setContentIntent(openPendingIntent)
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "Stop Server", stopPendingIntent)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .build()
    }

    override fun onServerStateChanged(
        state: PocketAiServerController.ServerState,
        ip: String,
        port: Int
    ) {
        if (state == PocketAiServerController.ServerState.RUNNING) {
            val notif = buildNotification(
                title = "PocketAI Server Active",
                text = "Running at http://$ip:$port • Status: Idle",
                isGenerating = false
            )
            notificationManager.notify(NOTIFICATION_ID, notif)
        }
    }

    override fun onInferenceStatusChanged(
        status: PocketAiServerController.InferenceStatus,
        currentPrompt: String?,
        queueSize: Int
    ) {
        val ip = PocketAiServerController.activeIp
        val port = PocketAiServerController.activePort

        when (status) {
            PocketAiServerController.InferenceStatus.IDLE -> {
                val notif = buildNotification(
                    title = "PocketAI Server Active",
                    text = "Running at http://$ip:$port • Status: Idle",
                    isGenerating = false
                )
                notificationManager.notify(NOTIFICATION_ID, notif)
            }
            PocketAiServerController.InferenceStatus.GENERATING -> {
                val snippet = if (!currentPrompt.isNullOrBlank() && currentPrompt.length > 30) {
                    currentPrompt.substring(0, 27) + "..."
                } else {
                    currentPrompt ?: ""
                }
                val notif = buildNotification(
                    title = "⚡ Qwen3 Generating Answer...",
                    text = "Prompt: \"$snippet\" (Queue: $queueSize)",
                    isGenerating = true
                )
                notificationManager.notify(NOTIFICATION_ID, notif)
            }
            PocketAiServerController.InferenceStatus.QUEUED -> {
                val notif = buildNotification(
                    title = "PocketAI Server Active",
                    text = "Queued request ($queueSize in queue)...",
                    isGenerating = false
                )
                notificationManager.notify(NOTIFICATION_ID, notif)
            }
        }
    }

    override fun onRequestLogAdded(entry: PocketAiServerController.RequestLogEntry) {}
    override fun onErrorLogAdded(entry: PocketAiServerController.ErrorLogEntry) {}
    override fun onClientConnected(client: PocketAiServerController.ClientInfo) {}
}
