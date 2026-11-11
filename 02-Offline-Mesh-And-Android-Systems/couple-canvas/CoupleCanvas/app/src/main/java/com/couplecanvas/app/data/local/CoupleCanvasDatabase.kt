package com.couplecanvas.app.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [DrawingEntity::class, UserProfileEntity::class],
    version = 1,
    exportSchema = false
)
abstract class CoupleCanvasDatabase : RoomDatabase() {
    abstract fun drawingDao(): DrawingDao
    abstract fun userProfileDao(): UserProfileDao

    companion object {
        @Volatile
        private var INSTANCE: CoupleCanvasDatabase? = null

        fun getDatabase(context: Context): CoupleCanvasDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    CoupleCanvasDatabase::class.java,
                    "couple_canvas_db"
                ).fallbackToDestructiveMigration().build()
                INSTANCE = instance
                instance
            }
        }
    }
}
