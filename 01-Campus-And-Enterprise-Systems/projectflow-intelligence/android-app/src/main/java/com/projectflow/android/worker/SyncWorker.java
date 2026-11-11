package com.projectflow.android.worker;

import android.content.Context;
import androidx.annotation.NonNull;
import androidx.work.Worker;
import androidx.work.WorkerParameters;
import com.projectflow.android.data.local.AppDatabase;
import com.projectflow.android.data.local.SyncQueueEntity;
import com.projectflow.android.data.remote.ApiClient;
import com.projectflow.android.data.remote.ApiService;

import java.util.List;

public class SyncWorker extends Worker {

    public SyncWorker(@NonNull Context context, @NonNull WorkerParameters workerParams) {
        super(context, workerParams);
    }

    @NonNull
    @Override
    public Result doWork() {
        Context context = getApplicationContext();
        AppDatabase db = AppDatabase.getInstance(context);
        ApiService api = ApiClient.getService(context);

        List<SyncQueueEntity> pending = db.syncQueueDao().getPendingSync();
        for (SyncQueueEntity item : pending) {
            // Process queue
            db.syncQueueDao().deleteById(item.id);
        }

        return Result.success();
    }
}
