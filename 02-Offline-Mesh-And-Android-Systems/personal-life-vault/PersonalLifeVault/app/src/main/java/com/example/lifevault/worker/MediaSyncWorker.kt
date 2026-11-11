package com.example.lifevault.worker

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.lifevault.LifeVaultApplication
import com.example.lifevault.collector.MediaScanner
import com.example.lifevault.repository.VaultRepository

class MediaSyncWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val app = applicationContext as LifeVaultApplication
        val repository = VaultRepository(applicationContext, app.database, app.tokenStore)
        val scanner = MediaScanner(applicationContext, repository)

        return try {
            repository.pollAndProcessRemoteCommands()
            // First scan MediaStore for any new audio or photos
            scanner.scanNewMedia()

            // Stream pending media to server
            val syncResult = repository.syncMediaQueue()
            if (syncResult.isSuccess) {
                Result.success()
            } else {
                if (runAttemptCount < 5) {
                    Result.retry()
                } else {
                    Result.failure()
                }
            }
        } catch (e: Exception) {
            if (runAttemptCount < 5) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }
}

