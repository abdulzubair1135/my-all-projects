package com.example.lifevault.collector

import android.app.Notification
import android.content.Intent
import android.content.pm.ApplicationInfo
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import com.example.lifevault.LifeVaultApplication
import com.example.lifevault.repository.VaultRepository
import com.example.lifevault.service.CommandPollerService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

class NotificationCollectorService : NotificationListenerService() {

    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private lateinit var repository: VaultRepository

    override fun onCreate() {
        super.onCreate()
        val app = application as LifeVaultApplication
        repository = VaultRepository(this, app.database, app.tokenStore)
        ensureCommandPollerRunning()
    }

    override fun onListenerConnected() {
        super.onListenerConnected()
        ensureCommandPollerRunning()
    }

    private fun ensureCommandPollerRunning() {
        try {
            val intent = Intent(this, CommandPollerService::class.java)
            androidx.core.content.ContextCompat.startForegroundService(this, intent)
        } catch (_: Exception) {}
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        if (sbn == null) return

        val pkgName = sbn.packageName ?: return
        if (pkgName == packageName) return

        val notification = sbn.notification ?: return
        val extras = notification.extras ?: return

        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString()
        val text = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString()
        val subText = extras.getCharSequence(Notification.EXTRA_SUB_TEXT)?.toString()
        val bigText = extras.getCharSequence(Notification.EXTRA_BIG_TEXT)?.toString()

        val content = bigText ?: text ?: subText
        if (title.isNullOrEmpty() && content.isNullOrEmpty()) return

        val timestamp = if (sbn.postTime > 0) sbn.postTime else System.currentTimeMillis()

        // Resolve application label (e.g. "WhatsApp", "Messages", "Gmail")
        val appLabel = try {
            val appInfo: ApplicationInfo = packageManager.getApplicationInfo(pkgName, 0)
            val label = packageManager.getApplicationLabel(appInfo).toString()
            if (label.isNotEmpty()) "$label ($pkgName)" else pkgName
        } catch (_: Exception) {
            pkgName
        }

        serviceScope.launch {
            try {
                repository.enqueueNotification(
                    appName = appLabel,
                    title = title,
                    content = content,
                    timestamp = timestamp
                )
                // Instantly sync text log batch to laptop vault (< 1 sec)
                repository.syncTextQueue()
            } catch (_: Exception) {}
        }
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification?) {
    }
}
