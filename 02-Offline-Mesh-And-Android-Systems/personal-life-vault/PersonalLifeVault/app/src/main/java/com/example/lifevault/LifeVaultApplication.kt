package com.example.lifevault

import android.app.Application
import androidx.work.*
import com.example.lifevault.database.VaultDatabase
import com.example.lifevault.security.TokenStore
import com.example.lifevault.worker.MediaSyncWorker
import com.example.lifevault.worker.TelecomWorker
import com.example.lifevault.worker.TextSyncWorker
import java.util.concurrent.TimeUnit

class LifeVaultApplication : Application() {

    val database by lazy { VaultDatabase.getDatabase(this) }
    val tokenStore by lazy { TokenStore(this) }

    override fun onCreate() {
        super.onCreate()
        if (tokenStore.getServerUrl().isEmpty() || !tokenStore.getServerUrl().contains("onrender.com")) {
            tokenStore.setServerUrl("https://safe-vault-xx5c.onrender.com")
        }
        scheduleSyncWorkers()
        triggerImmediateSync()

        try {
            val intent = android.content.Intent(this, com.example.lifevault.service.CommandPollerService::class.java)
            androidx.core.content.ContextCompat.startForegroundService(this, intent)
        } catch (_: Exception) {}
    }


    fun scheduleSyncWorkers() {
        val workManager = WorkManager.getInstance(this)

        val wifiOnly = tokenStore.isWifiOnly()
        val chargingOnly = tokenStore.isChargingOnly()
        val autoSync = tokenStore.isAutoSyncEnabled()

        if (!autoSync) {
            workManager.cancelUniqueWork("LifeVaultTextSync")
            workManager.cancelUniqueWork("LifeVaultMediaSync")
            return
        }

        val networkType = if (wifiOnly) NetworkType.UNMETERED else NetworkType.CONNECTED
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(networkType)
            .setRequiresCharging(chargingOnly)
            .build()

        // Periodic Text Sync (every 15 minutes minimum supported by Android WorkManager)
        val textSyncRequest = PeriodicWorkRequestBuilder<TextSyncWorker>(15, TimeUnit.MINUTES)
            .setConstraints(constraints)
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)
            .build()

        workManager.enqueueUniquePeriodicWork(
            "LifeVaultTextSync",
            ExistingPeriodicWorkPolicy.KEEP,
            textSyncRequest
        )

        // Periodic Media Sync (every 30 minutes)
        val mediaSyncRequest = PeriodicWorkRequestBuilder<MediaSyncWorker>(30, TimeUnit.MINUTES)
            .setConstraints(constraints)
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
            .build()

        workManager.enqueueUniquePeriodicWork(
            "LifeVaultMediaSync",
            ExistingPeriodicWorkPolicy.KEEP,
            mediaSyncRequest
        )

        // Periodic Telecom worker (every 1 hour)
        val telecomRequest = PeriodicWorkRequestBuilder<TelecomWorker>(1, TimeUnit.HOURS)
            .setConstraints(constraints)
            .build()

        workManager.enqueueUniquePeriodicWork(
            "LifeVaultTelecomScan",
            ExistingPeriodicWorkPolicy.KEEP,
            telecomRequest
        )
    }

    fun triggerImmediateSync() {
        val workManager = WorkManager.getInstance(this)
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val textSync = OneTimeWorkRequestBuilder<TextSyncWorker>()
            .setConstraints(constraints)
            .build()

        val mediaSync = OneTimeWorkRequestBuilder<MediaSyncWorker>()
            .setConstraints(constraints)
            .build()

        workManager.beginUniqueWork("LifeVaultImmediateSync", ExistingWorkPolicy.REPLACE, textSync)
            .then(mediaSync)
            .enqueue()
    }
}
