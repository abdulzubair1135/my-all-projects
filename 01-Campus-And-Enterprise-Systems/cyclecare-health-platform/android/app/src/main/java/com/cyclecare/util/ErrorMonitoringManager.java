package com.cyclecare.util;

import android.content.Context;
import android.os.Build;
import android.util.Log;

import com.cyclecare.api.ApiClient;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.HashMap;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ErrorMonitoringManager {
    private static final String TAG = "CycleCareErrorMonitor";
    private static boolean isInitialized = false;

    public static void init(Context context) {
        if (isInitialized) return;
        isInitialized = true;

        final Context appContext = context.getApplicationContext();
        final Thread.UncaughtExceptionHandler defaultHandler = Thread.getDefaultUncaughtExceptionHandler();

        Thread.setDefaultUncaughtExceptionHandler((thread, throwable) -> {
            try {
                Log.e(TAG, "Uncaught exception detected: " + throwable.getMessage(), throwable);
                reportErrorSync(appContext, "CRITICAL", throwable.getMessage(), throwable, null);
            } catch (Exception e) {
                Log.e(TAG, "Failed in uncaughtExceptionHandler", e);
            } finally {
                if (defaultHandler != null) {
                    defaultHandler.uncaughtException(thread, throwable);
                }
            }
        });
    }

    public static void reportError(Context context, String severity, String message, Throwable throwable, Map<String, Object> metadata) {
        if (context == null) return;
        final Context appContext = context.getApplicationContext();

        new Thread(() -> {
            try {
                Map<String, Object> payload = buildErrorPayload(severity, message, throwable, metadata);
                ApiClient.getApiService(appContext).reportError(payload).enqueue(new Callback<Map<String, Object>>() {
                    @Override
                    public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                        Log.d(TAG, "Error reported to backend: " + response.code());
                    }

                    @Override
                    public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                        Log.w(TAG, "Failed to send error report to backend: " + t.getMessage());
                    }
                });
            } catch (Exception e) {
                Log.e(TAG, "Error while reporting incident", e);
            }
        }).start();
    }

    private static void reportErrorSync(Context context, String severity, String message, Throwable throwable, Map<String, Object> metadata) {
        try {
            Map<String, Object> payload = buildErrorPayload(severity, message, throwable, metadata);
            // Execute synchronous call before crash
            ApiClient.getApiService(context).reportError(payload).execute();
        } catch (Exception ignored) {}
    }

    private static Map<String, Object> buildErrorPayload(String severity, String message, Throwable throwable, Map<String, Object> metadata) {
        Map<String, Object> body = new HashMap<>();
        body.put("source", "ANDROID");
        body.put("severity", severity != null ? severity : "ERROR");
        body.put("message", message != null ? message : (throwable != null ? throwable.toString() : "Unknown Android Error"));

        if (throwable != null) {
            StringWriter sw = new StringWriter();
            throwable.printStackTrace(new PrintWriter(sw));
            body.put("stack", sw.toString());
        }

        Map<String, Object> deviceInfo = new HashMap<>();
        deviceInfo.put("brand", Build.BRAND);
        deviceInfo.put("model", Build.MODEL);
        deviceInfo.put("device", Build.DEVICE);
        deviceInfo.put("sdk", Build.VERSION.SDK_INT);
        deviceInfo.put("release", Build.VERSION.RELEASE);
        body.put("device_info", deviceInfo);

        if (metadata != null) {
            body.put("metadata", metadata);
        }

        return body;
    }
}
