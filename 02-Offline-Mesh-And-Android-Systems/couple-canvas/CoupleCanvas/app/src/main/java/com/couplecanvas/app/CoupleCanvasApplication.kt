package com.couplecanvas.app

import android.app.Application
import com.google.android.gms.ads.MobileAds
import com.couplecanvas.app.data.local.CoupleCanvasDatabase
import com.couplecanvas.app.data.datastore.UserPreferencesRepository

class CoupleCanvasApplication : Application() {

    val database: CoupleCanvasDatabase by lazy {
        CoupleCanvasDatabase.getDatabase(this)
    }

    val userPreferencesRepository: UserPreferencesRepository by lazy {
        UserPreferencesRepository(this)
    }

    override fun onCreate() {
        super.onCreate()
        // Initialize MobileAds SDK safely
        try {
            MobileAds.initialize(this) {}
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
