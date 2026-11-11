package com.cyclecare.repository;

import android.content.Context;
import androidx.lifecycle.LiveData;

import com.cyclecare.api.ApiClient;
import com.cyclecare.api.ApiService;
import com.cyclecare.database.AppDatabase;
import com.cyclecare.database.dao.PeriodLogDao;
import com.cyclecare.database.dao.SyncQueueDao;
import com.cyclecare.database.entity.PeriodLogEntity;
import com.cyclecare.database.entity.SyncQueueEntity;
import com.cyclecare.models.ApiResponse;
import com.cyclecare.models.PeriodLog;

import java.util.List;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class CycleRepository {
    private PeriodLogDao periodLogDao;
    private SyncQueueDao syncQueueDao;
    private ApiService apiService;
    private ExecutorService executor;

    public CycleRepository(Context context) {
        AppDatabase db = AppDatabase.getInstance(context);
        this.periodLogDao = db.periodLogDao();
        this.syncQueueDao = db.syncQueueDao();
        this.apiService = ApiClient.getApiService(context);
        this.executor = Executors.newSingleThreadExecutor();
    }

    public LiveData<List<PeriodLogEntity>> getLocalPeriodLogs() {
        return periodLogDao.getAllPeriodLogs();
    }

    public void addPeriodLog(String startDate, String endDate, String flow, String notes) {
        final String tempId = UUID.randomUUID().toString();
        final PeriodLogEntity localEntity = new PeriodLogEntity(tempId, startDate, endDate, flow, notes, false);

        executor.execute(() -> {
            // Save to Room offline database first
            periodLogDao.insertPeriodLog(localEntity);

            // Attempt remote API sync
            PeriodLog remoteLog = new PeriodLog(startDate, endDate, flow, notes);
            apiService.addPeriodLog(remoteLog).enqueue(new Callback<ApiResponse<PeriodLog>>() {
                @Override
                public void onResponse(Call<ApiResponse<PeriodLog>> call, Response<ApiResponse<PeriodLog>> response) {
                    if (response.isSuccessful() && response.body() != null && response.body().isSuccess()) {
                        executor.execute(() -> {
                            localEntity.setSynced(true);
                            periodLogDao.insertPeriodLog(localEntity);
                        });
                    } else {
                        // Enqueue sync item for WorkManager retry when online
                        executor.execute(() -> {
                            syncQueueDao.insertSyncItem(new SyncQueueEntity("ADD_PERIOD", startDate + "," + flow, System.currentTimeMillis()));
                        });
                    }
                }

                @Override
                public void onFailure(Call<ApiResponse<PeriodLog>> call, Throwable t) {
                    // Saved offline locally, queue for WorkManager sync
                    executor.execute(() -> {
                        syncQueueDao.insertSyncItem(new SyncQueueEntity("ADD_PERIOD", startDate + "," + flow, System.currentTimeMillis()));
                    });
                }
            });
        });
    }

    public void updatePeriodLog(String logId, String startDate, String endDate, String flow, String notes) {
        final PeriodLogEntity updated = new PeriodLogEntity(logId, startDate, endDate, flow, notes, false);
        executor.execute(() -> {
            // Clear older duplicate entries and insert updated entity
            periodLogDao.clearAll();
            periodLogDao.insertPeriodLog(updated);

            java.util.Map<String, String> body = new java.util.HashMap<>();
            body.put("start_date", startDate);
            body.put("end_date", endDate);
            body.put("flow", flow);
            body.put("notes", notes);

            apiService.updatePeriodLog(logId, body).enqueue(new Callback<java.util.Map<String, Object>>() {
                @Override
                public void onResponse(Call<java.util.Map<String, Object>> call, Response<java.util.Map<String, Object>> response) {
                    if (response.isSuccessful()) {
                        executor.execute(() -> {
                            updated.setSynced(true);
                            periodLogDao.insertPeriodLog(updated);
                        });
                    }
                }

                @Override
                public void onFailure(Call<java.util.Map<String, Object>> call, Throwable t) {}
            });
        });
    }

    public void deletePeriodLog(String logId) {
        executor.execute(() -> {
            periodLogDao.deletePeriodLog(logId);
            periodLogDao.clearAll();

            apiService.deletePeriodLog(logId).enqueue(new Callback<ApiResponse<Void>>() {
                @Override
                public void onResponse(Call<ApiResponse<Void>> call, Response<ApiResponse<Void>> response) {}
                @Override
                public void onFailure(Call<ApiResponse<Void>> call, Throwable t) {}
            });
        });
    }
}
