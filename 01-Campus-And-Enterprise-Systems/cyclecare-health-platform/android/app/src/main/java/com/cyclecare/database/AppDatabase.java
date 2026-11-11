package com.cyclecare.database;

import android.content.Context;
import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;

import com.cyclecare.database.dao.PeriodLogDao;
import com.cyclecare.database.dao.SyncQueueDao;
import com.cyclecare.database.entity.PeriodLogEntity;
import com.cyclecare.database.entity.SyncQueueEntity;

@Database(entities = {PeriodLogEntity.class, SyncQueueEntity.class}, version = 1, exportSchema = false)
public abstract class AppDatabase extends RoomDatabase {
    public abstract PeriodLogDao periodLogDao();
    public abstract SyncQueueDao syncQueueDao();

    private static volatile AppDatabase INSTANCE;

    public static AppDatabase getInstance(final Context context) {
        if (INSTANCE == null) {
            synchronized (AppDatabase.class) {
                if (INSTANCE == null) {
                    INSTANCE = Room.databaseBuilder(context.getApplicationContext(),
                            AppDatabase.class, "cyclecare_local.db")
                            .fallbackToDestructiveMigration()
                            .build();
                }
            }
        }
        return INSTANCE;
    }
}
