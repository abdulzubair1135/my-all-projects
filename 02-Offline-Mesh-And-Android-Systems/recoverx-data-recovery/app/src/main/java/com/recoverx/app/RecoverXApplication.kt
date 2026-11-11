package com.recoverx.app

import android.app.Application
import android.content.Context
import com.recoverx.data.database.RecoverXDatabaseHelper
import com.recoverx.recovery.RecoveryManager
import com.recoverx.scanner.ScanCoordinator

class AppContainer(context: Context) {
    val dbHelper: RecoverXDatabaseHelper = RecoverXDatabaseHelper(context)
    val scanCoordinator: ScanCoordinator = ScanCoordinator(context, dbHelper)
    val recoveryManager: RecoveryManager = RecoveryManager(context, dbHelper)
}

class RecoverXApplication : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}
