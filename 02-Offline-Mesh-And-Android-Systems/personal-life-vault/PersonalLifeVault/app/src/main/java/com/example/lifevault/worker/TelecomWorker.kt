package com.example.lifevault.worker

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.lifevault.LifeVaultApplication
import com.example.lifevault.collector.TelecomCollector
import com.example.lifevault.repository.VaultRepository

class TelecomWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val app = applicationContext as LifeVaultApplication
        val repository = VaultRepository(applicationContext, app.database, app.tokenStore)
        val collector = TelecomCollector(applicationContext, repository)

        return try {
            collector.scanSmsLogs()
            collector.scanCallLogs()
            repository.syncTextQueue()
            Result.success()
        } catch (_: Exception) {
            Result.success()
        }
    }
}
