package com.projectflow.android.service;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.widget.RemoteViews;
import androidx.core.app.NotificationCompat;
import androidx.core.app.Person;
import com.projectflow.android.R;
import com.projectflow.android.ui.MainActivity;
import com.projectflow.android.ui.TaskDetailsActivity;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * Enterprise Notification Management Engine for ProjectFlow Intelligence.
 * Handles Android 8.0 - 15+ Notification Channels, Heads-up Banners,
 * Sound & Vibration profiles, Task Deep-linking, and Quick Actions.
 */
public class ProjectFlowNotificationHelper {

    public static final String CHANNEL_TASKS = "projectflow_tasks_channel";
    public static final String CHANNEL_RISKS = "projectflow_risks_channel";
    public static final String CHANNEL_GENERAL = "projectflow_general_channel";
    public static final String CHANNEL_CHAT = "projectflow_chat_channel";

    /**
     * Initializes all enterprise notification channels on app startup.
     */
    public static void initChannels(Context context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm == null) return;

            // 1. Task Assignments & Status Channel
            NotificationChannel taskChannel = new NotificationChannel(
                    CHANNEL_TASKS,
                    "Task Assignments & Delegations",
                    NotificationManager.IMPORTANCE_HIGH
            );
            taskChannel.setDescription("Real-time notifications when tasks are assigned, updated, or completed.");
            taskChannel.enableLights(true);
            taskChannel.setLightColor(Color.parseColor("#47745A")); // Forest Green
            taskChannel.enableVibration(true);
            taskChannel.setVibrationPattern(new long[]{0, 250, 150, 250});
            nm.createNotificationChannel(taskChannel);

            // 2. Schedule Risk & Deadline Alerts Channel
            NotificationChannel riskChannel = new NotificationChannel(
                    CHANNEL_RISKS,
                    "Project Risks & Delay Alerts",
                    NotificationManager.IMPORTANCE_HIGH
            );
            riskChannel.setDescription("Urgent alerts triggered by the deterministic schedule risk engine.");
            riskChannel.enableLights(true);
            riskChannel.setLightColor(Color.parseColor("#B7473C")); // Rust Red
            riskChannel.enableVibration(true);
            riskChannel.setVibrationPattern(new long[]{0, 350, 200, 350});
            nm.createNotificationChannel(riskChannel);

            // 3. Team Chat & Direct Discussions Channel
            NotificationChannel chatChannel = new NotificationChannel(
                    CHANNEL_CHAT,
                    "Team Discussions & Chat Alerts",
                    NotificationManager.IMPORTANCE_HIGH
            );
            chatChannel.setDescription("Instant heads-up notifications for team messages and mentions.");
            chatChannel.enableLights(true);
            chatChannel.setLightColor(Color.parseColor("#795B43")); // Earth Tone
            chatChannel.enableVibration(true);
            chatChannel.setVibrationPattern(new long[]{0, 200, 100, 200});
            nm.createNotificationChannel(chatChannel);

            // 4. General Workspace Channel
            NotificationChannel generalChannel = new NotificationChannel(
                    CHANNEL_GENERAL,
                    "Workspace & Team Updates",
                    NotificationManager.IMPORTANCE_DEFAULT
            );
            generalChannel.setDescription("Team announcements and general collaboration updates.");
            nm.createNotificationChannel(generalChannel);
        }
    }

    /**
     * Displays an actionable task assignment or update notification in the system tray.
     */
    public static void showTaskNotification(Context context, String title, String message, String taskId, String priority) {
        initChannels(context);

        Intent intent;
        if (taskId != null && !taskId.isEmpty()) {
            intent = new Intent(context, TaskDetailsActivity.class);
            intent.putExtra("task_id", taskId);
            intent.putExtra("task_title", title);
            intent.putExtra("task_desc", message);
            intent.putExtra("task_priority", priority != null ? priority : "MEDIUM");
        } else {
            intent = new Intent(context, MainActivity.class);
            intent.putExtra("navigate_to", "TASK");
            intent.putExtra("task_title", title);
            intent.putExtra("task_desc", message);
            intent.putExtra("task_priority", priority != null ? priority : "MEDIUM");
        }
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);

        PendingIntent contentPendingIntent = PendingIntent.getActivity(
                context,
                (int) System.currentTimeMillis(),
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        Uri defaultSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        Bitmap logoBitmap = BitmapFactory.decodeResource(context.getResources(), R.drawable.logo_clean);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, CHANNEL_TASKS)
                .setSmallIcon(R.drawable.ic_stat_logo)
                .setLargeIcon(logoBitmap)
                .setContentTitle(title)
                .setContentText(message)
                .setStyle(new NotificationCompat.BigTextStyle().bigText(message))
                .setSound(defaultSound)
                .setColor(Color.parseColor("#795B43"))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setAutoCancel(true)
                .setContentIntent(contentPendingIntent);

        // Add Quick Action: View Task
        if (taskId != null && !taskId.isEmpty()) {
            builder.addAction(R.drawable.ic_stat_logo, "View Task", contentPendingIntent);
        }

        NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) {
            int notifId = (taskId != null) ? taskId.hashCode() : (int) System.currentTimeMillis();
            nm.notify(notifId, builder.build());
        }
    }

    /**
     * Displays an urgent schedule risk or critical delay notification with brand logo.
     */
    public static void showRiskNotification(Context context, String title, String riskDetail, String severity) {
        initChannels(context);

        Intent intent = new Intent(context, MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        intent.putExtra("navigate_to", "TASKS");

        PendingIntent pendingIntent = PendingIntent.getActivity(
                context,
                (int) System.currentTimeMillis(),
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        Uri defaultSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        Bitmap logoBitmap = BitmapFactory.decodeResource(context.getResources(), R.drawable.logo_clean);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, CHANNEL_RISKS)
                .setSmallIcon(R.drawable.ic_stat_logo)
                .setLargeIcon(logoBitmap)
                .setContentTitle(title)
                .setContentText(riskDetail)
                .setStyle(new NotificationCompat.BigTextStyle()
                        .setBigContentTitle("⚠️ " + title)
                        .bigText(riskDetail))
                .setSound(defaultSound)
                .setColor(Color.parseColor("#B7473C"))
                .setPriority(NotificationCompat.PRIORITY_MAX)
                .setAutoCancel(true)
                .setContentIntent(pendingIntent);

        NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) {
            nm.notify((int) System.currentTimeMillis(), builder.build());
        }
    }

    public static void showChatNotification(Context context, String title, String message, String channelName, String senderName) {
        initChannels(context);

        String ch = (channelName != null && !channelName.isEmpty()) ? channelName : "general";
        String sender = (senderName != null && !senderName.isEmpty()) ? senderName : "System Administrator";

        Intent intent = new Intent(context, MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        intent.putExtra("navigate_to", "CHAT");
        intent.putExtra("chat_channel", ch);
        intent.putExtra("chat_title", sender);
        intent.putExtra("chat_type", ch.startsWith("dm_") ? "DIRECT" : "GROUP");

        int reqCode = Math.abs(ch.hashCode());
        PendingIntent pendingIntent = PendingIntent.getActivity(
                context,
                reqCode,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        Uri defaultSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

        boolean isDirect = ch.startsWith("dm_");
        String channelDisplay = isDirect ? "Direct Chat" : "#" + ch;
        String displayTitle = isDirect ? sender : ("#" + ch + " • " + sender);
        String formattedTime = new SimpleDateFormat("hh:mm a", Locale.getDefault()).format(new Date());

        RemoteViews collapsedView = new RemoteViews(context.getPackageName(), R.layout.notification_chat_collapsed);
        collapsedView.setTextViewText(R.id.notifSenderName, sender);
        collapsedView.setTextViewText(R.id.notifChannelTag, isDirect ? "Direct Chat" : "#" + ch);
        collapsedView.setTextViewText(R.id.notifTime, formattedTime);
        collapsedView.setTextViewText(R.id.notifMessage, message != null ? message : "");
        collapsedView.setOnClickPendingIntent(R.id.rootNotifCollapsed, pendingIntent);

        RemoteViews expandedView = new RemoteViews(context.getPackageName(), R.layout.notification_chat_expanded);
        expandedView.setTextViewText(R.id.notifExpandedSender, sender);
        expandedView.setTextViewText(R.id.notifExpandedChannel, isDirect ? "Direct Chat" : "#" + ch);
        expandedView.setTextViewText(R.id.notifExpandedTime, formattedTime);
        expandedView.setTextViewText(R.id.notifExpandedMessage, message != null ? message : "");
        expandedView.setOnClickPendingIntent(R.id.rootNotifExpanded, pendingIntent);
        expandedView.setOnClickPendingIntent(R.id.btnOpenChat, pendingIntent);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, CHANNEL_CHAT)
                .setSmallIcon(R.drawable.ic_stat_logo)
                .setCustomContentView(collapsedView)
                .setCustomBigContentView(expandedView)
                .setStyle(new NotificationCompat.DecoratedCustomViewStyle())
                .setContentTitle(displayTitle)
                .setContentText(message)
                .setSubText(channelDisplay)
                .setSound(defaultSound)
                .setVibrate(new long[]{0, 200, 100, 200})
                .setColor(Color.parseColor("#795B43"))
                .setPriority(NotificationCompat.PRIORITY_MAX)
                .setCategory(NotificationCompat.CATEGORY_MESSAGE)
                .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
                .setAutoCancel(true)
                .setContentIntent(pendingIntent);

        NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) {
            int notifId = 10000 + Math.abs(ch.hashCode() % 10000);
            nm.notify(notifId, builder.build());
        }
    }
}
