package com.example.lifevault.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.example.lifevault.database.dao.*
import com.example.lifevault.database.entities.*

@Database(
    entities = [
        NotificationEntity::class,
        TelecomEntity::class,
        SensorEntity::class,
        MediaEntity::class,
        SyncQueueEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class VaultDatabase : RoomDatabase() {

    abstract fun notificationDao(): NotificationDao
    abstract fun telecomDao(): TelecomDao
    abstract fun sensorDao(): SensorDao
    abstract fun mediaDao(): MediaDao
    abstract fun syncQueueDao(): SyncQueueDao

    companion object {
        @Volatile
        private var INSTANCE: VaultDatabase? = null

        fun getDatabase(context: Context): VaultDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    VaultDatabase::class.java,
                    "life_vault_local.db"
                ).fallbackToDestructiveMigration().build()
                INSTANCE = instance
                instance
            }
        }
    }
}
