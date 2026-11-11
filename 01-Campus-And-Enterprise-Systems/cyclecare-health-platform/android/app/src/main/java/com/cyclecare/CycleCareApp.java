package com.cyclecare;

import android.app.Application;
import android.content.SharedPreferences;
import android.os.Build;
import android.util.Log;

import com.cyclecare.api.ApiClient;
import com.cyclecare.util.ErrorMonitoringManager;
import com.google.firebase.messaging.FirebaseMessaging;

import java.util.HashMap;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class CycleCareApp extends Application {
    private static final String TAG = "CycleCareApp";

    @Override
    public void onCreate() {
        super.onCreate();

        // 1. Initialize Global Error & Crash Monitoring
        ErrorMonitoringManager.init(this);

        // 2. Fetch or sync FCM Device Token
        syncDevicePushToken();
    }

    private void syncDevicePushToken() {
        try {
            FirebaseMessaging.getInstance().getToken().addOnCompleteListener(task -> {
                if (!task.isSuccessful() || task.getResult() == null) {
                    Log.w(TAG, "Fetching FCM registration token failed", task.getException());
                    return;
                }

                String token = task.getResult();
                Log.d(TAG, "FCM Device Token retrieved: " + token);

                SharedPreferences prefs = getSharedPreferences("cyclecare_prefs", MODE_PRIVATE);
                prefs.edit().putString("fcm_device_token", token).apply();

                Map<String, Object> req = new HashMap<>();
                req.put("token", token);
                req.put("platform", "ANDROID");
                req.put("device_model", Build.MODEL);
                req.put("os_version", "Android " + Build.VERSION.RELEASE);

                ApiClient.getApiService(CycleCareApp.this).registerDeviceToken(req).enqueue(new Callback<Map<String, Object>>() {
                    @Override
                    public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                        Log.d(TAG, "Push token registered with backend: " + response.code());
                    }

                    @Override
                    public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                        Log.w(TAG, "Failed registering push token with backend: " + t.getMessage());
                    }
                });
            });
        } catch (Exception e) {
            Log.w(TAG, "Firebase messaging initialization deferred: " + e.getMessage());
        }
    }
}
