package com.projectflow.android.service;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.core.app.NotificationCompat;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;
import com.projectflow.android.R;
import com.projectflow.android.ui.MainActivity;
import com.projectflow.android.ui.TaskDetailsActivity;

public class ProjectFlowFirebaseMessagingService extends FirebaseMessagingService {

    private static final String TAG = "ProjectFlowFCM";
    public static final String CHANNEL_ID = "projectflow_notifications_channel";
    public static final String CHANNEL_NAME = "ProjectFlow Alerts & Tasks";

    @Override
    public void onNewToken(@NonNull String token) {
        super.onNewToken(token);
        Log.d(TAG, "Refreshed FCM Token: " + token);
        // Persist token in SharedPreferences
        getSharedPreferences("projectflow_prefs", MODE_PRIVATE)
                .edit()
                .putString("fcm_token", token)
                .apply();
    }

    @Override
    public void onMessageReceived(@NonNull RemoteMessage remoteMessage) {
        super.onMessageReceived(remoteMessage);
        Log.d(TAG, "From: " + remoteMessage.getFrom());

        String title = "ProjectFlow Intelligence";
        String messageBody = "New workspace update";
        String taskId = null;
        String priority = "MEDIUM";

        // Handle notification payload
        if (remoteMessage.getNotification() != null) {
            if (remoteMessage.getNotification().getTitle() != null) {
                title = remoteMessage.getNotification().getTitle();
            }
            if (remoteMessage.getNotification().getBody() != null) {
                messageBody = remoteMessage.getNotification().getBody();
            }
        }

        // Handle data payload
        if (!remoteMessage.getData().isEmpty()) {
            if (remoteMessage.getData().containsKey("title")) {
                title = remoteMessage.getData().get("title");
            }
            if (remoteMessage.getData().containsKey("message")) {
                messageBody = remoteMessage.getData().get("message");
            }
            if (remoteMessage.getData().containsKey("taskId")) {
                taskId = remoteMessage.getData().get("taskId");
            }
            if (remoteMessage.getData().containsKey("priority")) {
                priority = remoteMessage.getData().get("priority");
            }
        }

        String type = remoteMessage.getData().get("type");
        if ("RISK_ALERT".equalsIgnoreCase(type) || "CRITICAL".equalsIgnoreCase(priority)) {
            ProjectFlowNotificationHelper.showRiskNotification(this, title, messageBody, priority);
        } else if ("CHAT_MESSAGE".equalsIgnoreCase(type) || remoteMessage.getData().containsKey("channel")) {
            String channel = remoteMessage.getData().get("channel");
            String senderName = remoteMessage.getData().get("senderName");
            ProjectFlowNotificationHelper.showChatNotification(this, title, messageBody, channel, senderName);
        } else {
            ProjectFlowNotificationHelper.showTaskNotification(this, title, messageBody, taskId, priority);
        }
    }
}
