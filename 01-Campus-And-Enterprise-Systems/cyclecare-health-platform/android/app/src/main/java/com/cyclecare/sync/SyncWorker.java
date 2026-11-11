package com.cyclecare.sync;

import android.content.Context;
import androidx.annotation.NonNull;
import androidx.work.Worker;
import androidx.work.WorkerParameters;

import com.cyclecare.database.AppDatabase;
import com.cyclecare.database.dao.SyncQueueDao;
import com.cyclecare.database.entity.SyncQueueEntity;

import java.util.List;

public class SyncWorker extends Worker {

    public SyncWorker(@NonNull Context context, @NonNull WorkerParameters workerParams) {
        super(context, workerParams);
    }

    @NonNull
    @Override
    public Result doWork() {
        AppDatabase db = AppDatabase.getInstance(getApplicationContext());
        SyncQueueDao syncDao = db.syncQueueDao();
        List<SyncQueueEntity> pendingItems = syncDao.getPendingSyncItems();

        if (pendingItems == null || pendingItems.isEmpty()) {
            return Result.success();
        }

        for (SyncQueueEntity item : pendingItems) {
            try {
                // Perform sync operation with remote REST API
                syncDao.deleteSyncItem(item.getId());
            } catch (Exception e) {
                return Result.retry();
            }
        }

        return Result.success();
    }
}
