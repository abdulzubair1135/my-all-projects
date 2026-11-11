package com.projectx2.porncontroller.core.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.sqlite.db.SupportSQLiteDatabase
import com.projectx2.porncontroller.core.database.dao.*
import com.projectx2.porncontroller.core.database.entities.*
import com.projectx2.porncontroller.data.local.SeedData
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@Database(
    entities = [
        UserSettings::class,
        BlockedDomain::class,
        BlockedKeyword::class,
        DetectionEvent::class,
        TaskItem::class,
        TaskHistory::class,
        FocusSession::class,
        DailyStatistic::class,
        HabitStreak::class
    ],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userSettingsDao(): UserSettingsDao
    abstract fun blockedDomainDao(): BlockedDomainDao
    abstract fun blockedKeywordDao(): BlockedKeywordDao
    abstract fun detectionEventDao(): DetectionEventDao
    abstract fun taskDao(): TaskDao
    abstract fun focusSessionDao(): FocusSessionDao
    abstract fun dailyStatisticDao(): DailyStatisticDao
    abstract fun habitStreakDao(): HabitStreakDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "porn_controller.db"
                )
                    .addCallback(object : Callback() {
                        override fun onCreate(db: SupportSQLiteDatabase) {
                            super.onCreate(db)
                            // Populate initial seed data in coroutine scope
                            CoroutineScope(Dispatchers.IO).launch {
                                val database = getInstance(context)
                                database.userSettingsDao().updateSettings(SeedData.initialSettings)
                                database.habitStreakDao().updateStreak(SeedData.initialStreak)
                                database.blockedDomainDao().insertDomains(SeedData.defaultDomains)
                                database.blockedKeywordDao().getEnabledKeywords().let {
                                    SeedData.defaultKeywords.forEach { kw ->
                                        database.blockedKeywordDao().insertKeyword(kw)
                                    }
                                }
                                database.taskDao().insertTasks(SeedData.defaultTasks)
                            }
                        }
                    })
                    .fallbackToDestructiveMigration()
                    .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
