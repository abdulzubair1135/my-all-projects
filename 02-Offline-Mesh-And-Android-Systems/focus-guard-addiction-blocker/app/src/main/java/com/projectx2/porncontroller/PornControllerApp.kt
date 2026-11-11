package com.projectx2.porncontroller

import android.app.Application
import com.projectx2.porncontroller.core.database.AppDatabase
import com.projectx2.porncontroller.core.preferences.PreferenceManager
import com.projectx2.porncontroller.data.repository.PornControllerRepository

class PornControllerApp : Application() {

    lateinit var database: AppDatabase
        private set

    lateinit var preferenceManager: PreferenceManager
        private set

    lateinit var repository: PornControllerRepository
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this

        database = AppDatabase.getInstance(this)
        preferenceManager = PreferenceManager(this)
        repository = PornControllerRepository(database, preferenceManager)
    }

    companion object {
        lateinit var instance: PornControllerApp
            private set
    }
}
