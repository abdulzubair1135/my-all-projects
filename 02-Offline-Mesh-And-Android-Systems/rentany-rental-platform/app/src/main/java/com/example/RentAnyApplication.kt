package com.example

import android.app.Application
import com.example.data.AppDatabase
import com.example.data.RentRepository

class RentAnyApplication : Application() {
    val database by lazy { AppDatabase.getDatabase(this) }
    val repository by lazy { RentRepository(database) }
}
