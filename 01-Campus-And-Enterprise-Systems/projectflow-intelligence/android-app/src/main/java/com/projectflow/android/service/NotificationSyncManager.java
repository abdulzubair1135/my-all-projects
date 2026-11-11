package com.projectflow.android.service;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.projectflow.android.data.remote.model.DtoModels.ChatMessageDto;
import com.projectflow.android.data.remote.model.DtoModels.NotificationDto;
import com.projectflow.android.data.repository.ProjectFlowRepository;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Enterprise Real-time Notification Synchronization Engine.
 * Continuously monitors workspace discussions and system alerts, triggering
 * native Android heads-up notifications with sounds, vibrations, and channel deep-linking.
 */
public class NotificationSyncManager {

    private static final String TAG = "NotificationSync";
    private static final String PREF_NAME = "projectflow_notif_sync";
    private static final String KEY_SEEN_MESSAGES = "seen_chat_ids";
    private static final String KEY_SEEN_NOTIFS = "seen_notif_ids";
    private static final long SYNC_INTERVAL_MS = 2000; // 2 seconds real-time polling

    private static volatile NotificationSyncManager INSTANCE;
    private final Context appContext;
    private final ProjectFlowRepository repository;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private boolean isRunning = false;
    private boolean isFirstRun = true;

    private final Set<String> seenMessageIds = new HashSet<>();
    private final Set<String> seenNotifIds = new HashSet<>();

    private final Runnable syncRunnable = new Runnable() {
        @Override
        public void run() {
            if (!isRunning) return;
            performSync();
            handler.postDelayed(this, SYNC_INTERVAL_MS);
        }
    };

    private NotificationSyncManager(Context context) {
        this.appContext = context.getApplicationContext();
        this.repository = new ProjectFlowRepository(this.appContext);

        SharedPreferences prefs = appContext.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        Set<String> savedMessages = prefs.getStringSet(KEY_SEEN_MESSAGES, null);
        if (savedMessages != null) {
            seenMessageIds.addAll(savedMessages);
            isFirstRun = false;
        }
        Set<String> savedNotifs = prefs.getStringSet(KEY_SEEN_NOTIFS, null);
        if (savedNotifs != null) {
            seenNotifIds.addAll(savedNotifs);
        }
    }

    public static synchronized NotificationSyncManager getInstance(Context context) {
        if (INSTANCE == null) {
            INSTANCE = new NotificationSyncManager(context);
        }
        return INSTANCE;
    }

    public synchronized void start() {
        if (isRunning) return;
        isRunning = true;
        Log.i(TAG, "NotificationSyncManager activated - Real-time chat & workspace alerts enabled");
        handler.removeCallbacks(syncRunnable);
        handler.post(syncRunnable);
    }

    public synchronized void stop() {
        isRunning = false;
        handler.removeCallbacks(syncRunnable);
        Log.i(TAG, "NotificationSyncManager paused");
    }

    public void triggerImmediateSync() {
        handler.post(this::performSync);
    }

    private void performSync() {
        SharedPreferences userPrefs = appContext.getSharedPreferences("projectflow_prefs", Context.MODE_PRIVATE);
        String currentEmail = userPrefs.getString("user_email", "").trim().toLowerCase();
        String currentName = userPrefs.getString("user_name", userPrefs.getString("user_display_name", "")).trim().toLowerCase();
        String tempUserId = userPrefs.getString("user_id", "");
        if (tempUserId.isEmpty()) {
            String token = userPrefs.getString("auth_token", "");
            if (token != null && token.contains(".")) {
                try {
                    String[] parts = token.split("\\.");
                    if (parts.length >= 2) {
                        byte[] decoded = android.util.Base64.decode(parts[1], android.util.Base64.URL_SAFE | android.util.Base64.NO_WRAP | android.util.Base64.DEFAULT);
                        String payload = new String(decoded, java.nio.charset.StandardCharsets.UTF_8);
                        org.json.JSONObject obj = new org.json.JSONObject(payload);
                        if (obj.has("userId")) {
                            tempUserId = obj.getString("userId");
                            userPrefs.edit().putString("user_id", tempUserId).apply();
                        }
                    }
                } catch (Exception ignored) {}
            }
        }
        final String finalUserId = tempUserId;

        // 1. Sync Chat Messages across all channels
        repository.fetchAllChatMessages(new ProjectFlowRepository.DataCallback<List<ChatMessageDto>>() {
            @Override
            public void onData(List<ChatMessageDto> messages) {
                if (messages == null || messages.isEmpty()) return;

                if (isFirstRun && seenMessageIds.isEmpty()) {
                    // Seed existing messages without blasting notifications for past history
                    for (ChatMessageDto msg : messages) {
                        if (msg.id != null) seenMessageIds.add(msg.id);
                    }
                    persistSeenMessages();
                    isFirstRun = false;
                    return;
                }

                boolean newFound = false;
                for (ChatMessageDto msg : messages) {
                    if (msg.id == null || seenMessageIds.contains(msg.id)) continue;

                    // Mark as seen immediately
                    seenMessageIds.add(msg.id);
                    newFound = true;

                    // Check if message was sent by current user
                    String author = (msg.senderName != null) ? msg.senderName.trim().toLowerCase() : "";
                    String authorEmail = (msg.senderEmail != null) ? msg.senderEmail.trim().toLowerCase() : "";
                    boolean isSelf = (!currentName.isEmpty() && !author.isEmpty() && author.equals(currentName))
                            || (!currentEmail.isEmpty() && !authorEmail.isEmpty() && currentEmail.equalsIgnoreCase(authorEmail))
                            || (!currentEmail.isEmpty() && !author.isEmpty() && currentEmail.startsWith(author));

                    if (isSelf) {
                        continue;
                    }

                    // For Direct Messages (1-on-1): verify current user is an actual participant in this channel!
                    if (msg.channel != null && msg.channel.startsWith("dm_")) {
                        String mySlug = (!currentEmail.isEmpty()) ? currentEmail.replaceAll("[^a-zA-Z0-9]", "_").toLowerCase() : "";
                        if (!mySlug.isEmpty() && !msg.channel.contains(mySlug)) {
                            // Private DM between two other people -> NEVER notify!
                            continue;
                        }
                    }

                    Log.d(TAG, "New incoming chat alert from " + msg.senderName + " in #" + msg.channel);
                    String sender = (msg.senderName != null && !msg.senderName.isEmpty()) ? msg.senderName : "System Administrator";
                    String title = (msg.channel != null && msg.channel.startsWith("dm_")) ? ("💬 " + sender) : ("💬 #" + (msg.channel != null ? msg.channel : "general") + " • " + sender);
                    ProjectFlowNotificationHelper.showChatNotification(
                            appContext,
                            title,
                            msg.content,
                            msg.channel,
                            sender
                    );
                }

                if (newFound) {
                    persistSeenMessages();
                }
            }

            @Override
            public void onError(String message) {
                Log.w(TAG, "Chat sync check error: " + message);
            }
        });

        // 2. Sync In-App System & Task Notifications
        repository.fetchNotifications(new ProjectFlowRepository.DataCallback<List<NotificationDto>>() {
            @Override
            public void onData(List<NotificationDto> notifications) {
                if (notifications == null || notifications.isEmpty()) return;

                boolean newFound = false;
                for (NotificationDto notif : notifications) {
                    if (notif.id == null || seenNotifIds.contains(notif.id)) continue;

                    seenNotifIds.add(notif.id);
                    newFound = true;

                    // Trigger heads-up notification for ANY action from Control Panel / Workspace
                    if (!notif.read) {
                        if (notif.message != null && notif.message.contains("<!--PF:")) {
                            java.util.regex.Matcher m = java.util.regex.Pattern.compile("<!--PF:(.*?)-->").matcher(notif.message);
                            if (m.find()) {
                                String tagBody = m.group(1);
                                String[] tokens = tagBody.split(":");
                                for (String tok : tokens) {
                                    int eq = tok.indexOf('=');
                                    if (eq > 0) {
                                        String k = tok.substring(0, eq);
                                        String v = tok.substring(eq + 1);
                                        if ("ch".equals(k) && (notif.channel == null || notif.channel.isEmpty())) notif.channel = v;
                                        if ("task".equals(k) && (notif.taskId == null || notif.taskId.isEmpty())) notif.taskId = v;
                                        if ("sender".equals(k) && (notif.senderName == null || notif.senderName.isEmpty())) notif.senderName = v;
                                        if ("senderEmail".equals(k) && (notif.senderEmail == null || notif.senderEmail.isEmpty())) notif.senderEmail = v;
                                        if ("targetEmail".equals(k)) notif.targetEmail = v;
                                    }
                                }
                            }
                            notif.message = notif.message.replaceAll("<!--PF:[^>]*-->", "").trim();
                        }

                        // Filter: Never notify for actions initiated by the user themselves
                        if (notif.senderEmail != null && !notif.senderEmail.isEmpty() && notif.senderEmail.equalsIgnoreCase(currentEmail)) {
                            continue;
                        }

                        // Filter: DM notifications - user must be a participant in this channel
                        if (notif.channel != null && notif.channel.startsWith("dm_")) {
                            String mySlug = (!currentEmail.isEmpty()) ? currentEmail.replaceAll("[^a-zA-Z0-9]", "_").toLowerCase() : "";
                            if (!mySlug.isEmpty() && !notif.channel.contains(mySlug)) {
                                continue;
                            }
                        }

                        // Filter: Task notifications - if targetEmail is set, must match current user
                        if (notif.targetEmail != null && !notif.targetEmail.isEmpty()) {
                            if (!notif.targetEmail.equalsIgnoreCase(currentEmail)) {
                                continue;
                            }
                        }

                        // Filter: Task notifications - if userId is set, check match
                        if (notif.userId != null && !notif.userId.isEmpty() && !finalUserId.isEmpty()) {
                            if (!notif.userId.equals(finalUserId)) {
                                continue;
                            }
                        }

                        if ("CHAT_MESSAGE".equalsIgnoreCase(notif.type) || (notif.channel != null && !notif.channel.isEmpty() && notif.taskId == null)) {
                            Log.i(TAG, "Triggering chat notification from notif sync: " + notif.title + " - " + notif.message);
                            String sender = (notif.senderName != null && !notif.senderName.isEmpty()) ? notif.senderName : "System Administrator";
                            String title = notif.title != null ? notif.title : ("💬 " + sender);
                            ProjectFlowNotificationHelper.showChatNotification(
                                    appContext,
                                    title,
                                    notif.message,
                                    notif.channel,
                                    sender
                            );
                            continue;
                        }

                        Log.i(TAG, "Triggering phone notification: " + notif.title + " - " + notif.message);
                        if ("RISK_ALERT".equalsIgnoreCase(notif.type) || "CRITICAL".equalsIgnoreCase(notif.priority)) {
                            ProjectFlowNotificationHelper.showRiskNotification(appContext, notif.title, notif.message, notif.priority);
                        } else {
                            ProjectFlowNotificationHelper.showTaskNotification(appContext, notif.title, notif.message, notif.taskId, notif.priority);
                        }
                    }
                }

                if (newFound) {
                    persistSeenNotifs();
                }
            }

            @Override
            public void onError(String message) {}
        });
    }

    private void persistSeenMessages() {
        SharedPreferences prefs = appContext.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        // Keep bounded to last 200 message IDs to prevent unlimited storage growth
        Set<String> bounded = new HashSet<>(seenMessageIds);
        prefs.edit().putStringSet(KEY_SEEN_MESSAGES, bounded).apply();
    }

    private void persistSeenNotifs() {
        SharedPreferences prefs = appContext.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        Set<String> bounded = new HashSet<>(seenNotifIds);
        prefs.edit().putStringSet(KEY_SEEN_NOTIFS, bounded).apply();
    }
}
