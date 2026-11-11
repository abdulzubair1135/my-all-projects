package com.projectflow.android;

import android.app.Application;
import android.content.Context;
import android.content.SharedPreferences;
import androidx.appcompat.app.AppCompatDelegate;

public class ProjectFlowApplication extends Application {

    @Override
    public void onCreate() {
        super.onCreate();

        // Enforce light mode as the default on app startup
        SharedPreferences prefs = getSharedPreferences("projectflow_prefs", Context.MODE_PRIVATE);
        String theme = prefs.getString("app_theme", "light");

        if ("dark".equalsIgnoreCase(theme)) {
            AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES);
        } else if ("system".equalsIgnoreCase(theme)) {
            AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM);
        } else {
            // Default to Light Mode!
            AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO);
        }

        // Initialize Enterprise Notification Channels
        com.projectflow.android.service.ProjectFlowNotificationHelper.initChannels(this);

        // Start Real-Time Notification & Workspace Sync Engine
        com.projectflow.android.service.NotificationSyncManager.getInstance(this).start();

        // Register Firebase Cloud Messaging (FCM) Push Token with Render Server
        try {
            com.google.firebase.messaging.FirebaseMessaging.getInstance().getToken().addOnCompleteListener(task -> {
                if (task.isSuccessful() && task.getResult() != null) {
                    String token = task.getResult();
                    android.util.Log.d("ProjectFlowFCM", "Active Firebase device push token: " + token);
                    prefs.edit().putString("fcm_token", token).apply();

                    new Thread(() -> {
                        try {
                            java.util.Map<String, String> body = new java.util.HashMap<>();
                            body.put("fcmToken", token);
                            String email = prefs.getString("user_email", "admin@projectflow.io");
                            body.put("email", email);
                            com.projectflow.android.data.remote.ApiClient.getService(this).registerFcmToken(body).execute();
                            android.util.Log.d("ProjectFlowFCM", "Firebase token synced with Render backend successfully.");
                        } catch (Exception e) {
                            android.util.Log.w("ProjectFlowFCM", "Token sync error: " + e.getMessage());
                        }
                    }).start();
                }
            });
        } catch (Exception e) {
            android.util.Log.w("ProjectFlowFCM", "Firebase messaging initialization: " + e.getMessage());
        }
    }
}
