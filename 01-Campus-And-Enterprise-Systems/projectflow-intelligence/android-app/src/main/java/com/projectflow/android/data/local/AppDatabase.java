package com.projectflow.android.data.local;

import android.content.Context;
import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;

@Database(entities = {
        WorkspaceEntity.class,
        ProjectEntity.class,
        TaskEntity.class,
        RiskEntity.class,
        SyncQueueEntity.class
}, version = 2, exportSchema = false)
public abstract class AppDatabase extends RoomDatabase {

    private static volatile AppDatabase INSTANCE;

    public abstract AppDao.WorkspaceDao workspaceDao();
    public abstract AppDao.ProjectDao projectDao();
    public abstract AppDao.TaskDao taskDao();
    public abstract AppDao.RiskDao riskDao();
    public abstract AppDao.SyncQueueDao syncQueueDao();

    public static AppDatabase getInstance(Context context) {
        if (INSTANCE == null) {
            synchronized (AppDatabase.class) {
                if (INSTANCE == null) {
                    INSTANCE = Room.databaseBuilder(
                            context.getApplicationContext(),
                            AppDatabase.class,
                            "projectflow_android.db"
                    ).fallbackToDestructiveMigration().build();
                }
            }
        }
        return INSTANCE;
    }
}
