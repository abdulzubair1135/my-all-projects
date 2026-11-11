package com.example.meshlink.mesh;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.media.AudioAttributes;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;

import androidx.annotation.Nullable;
import androidx.core.app.NotificationCompat;

import com.example.meshlink.R;
import com.example.meshlink.calls.VideoCallActivity;
import com.example.meshlink.calls.VoiceCallActivity;
import com.example.meshlink.chat.ChatActivity;
import com.example.meshlink.data.ChatMessageModel;
import com.example.meshlink.data.LocalSosModel;
import com.example.meshlink.main.MainActivity;

public class MeshForegroundService extends Service implements MeshCoordinator.MeshEventListener {

    private static final String TAG = "MeshForegroundService";
    public static final String CHANNEL_BG = "mesh_bg_channel";
    public static final String CHANNEL_SOS = "mesh_sos_channel";
    public static final String CHANNEL_CALL = "mesh_call_channel";
    public static final String CHANNEL_CHAT = "mesh_chat_channel";
    private static final int NOTIFICATION_ID = 8881;

    private MeshCoordinator meshCoordinator;

    public static void startService(Context context) {
        try {
            Intent intent = new Intent(context, MeshForegroundService.class);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent);
            } else {
                context.startService(intent);
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to start MeshForegroundService: " + e.getMessage());
        }
    }

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "Creating MeshForegroundService for background killed-app alerts");
        createNotificationChannels();

        Notification notification = createBgNotification();
        startForeground(NOTIFICATION_ID, notification);

        meshCoordinator = MeshCoordinator.getInstance(this);
        meshCoordinator.addListener(this);
        meshCoordinator.startMesh();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (meshCoordinator != null) {
            meshCoordinator.startMesh();
        }
        return START_STICKY;
    }

    private void createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm == null) return;

            // 1. Background Service Channel
            NotificationChannel bgChan = new NotificationChannel(
                    CHANNEL_BG,
                    "Nexus Mesh Service Status",
                    NotificationManager.IMPORTANCE_LOW
            );
            bgChan.setDescription("Keeps P2P Mesh discovery active in background");
            nm.createNotificationChannel(bgChan);

            // 2. SOS Emergency Channel
            NotificationChannel sosChan = new NotificationChannel(
                    CHANNEL_SOS,
                    "Critical Emergency SOS Alerts",
                    NotificationManager.IMPORTANCE_HIGH
            );
            sosChan.setDescription("High-priority emergency alerts from nearby mesh nodes");
            Uri alarmSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM);
            if (alarmSound == null) alarmSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
            sosChan.setSound(alarmSound, new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_ALARM)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build());
            sosChan.enableVibration(true);
            sosChan.setVibrationPattern(new long[]{0, 500, 200, 500, 200, 1000});
            nm.createNotificationChannel(sosChan);

            // 3. Incoming Call Channel
            NotificationChannel callChan = new NotificationChannel(
                    CHANNEL_CALL,
                    "P2P Incoming Calls",
                    NotificationManager.IMPORTANCE_HIGH
            );
            callChan.setDescription("Ringtone alerts for incoming P2P voice & video calls");
            Uri ringtone = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_RINGTONE);
            callChan.setSound(ringtone, new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_NOTIFICATION_RINGTONE)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build());
            callChan.enableVibration(true);
            nm.createNotificationChannel(callChan);

            // 4. Chat Messages Channel
            NotificationChannel chatChan = new NotificationChannel(
                    CHANNEL_CHAT,
                    "Mesh Chat Messages",
                    NotificationManager.IMPORTANCE_DEFAULT
            );
            chatChan.setDescription("Notifications for incoming mesh text and media messages");
            nm.createNotificationChannel(chatChan);
        }
    }

    private Notification createBgNotification() {
        Intent openAppIntent = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(
                this, 0, openAppIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        return new NotificationCompat.Builder(this, CHANNEL_BG)
                .setContentTitle("Nexus MeshLink Active")
                .setContentText("Listening for off-grid P2P messages, calls & emergency SOS...")
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentIntent(pi)
                .setOngoing(true)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .build();
    }

    @Override
    public void onIncomingCall(String callId, String callerName, String callerId, String callType, String callerIp) {
        Log.d(TAG, "Background alert: Incoming " + callType + " call from " + callerName);
        boolean isVideo = "video".equalsIgnoreCase(callType);

        Intent fullScreenIntent = new Intent(this, com.example.meshlink.calls.IncomingCallActivity.class);
        fullScreenIntent.putExtra("PEER_NAME", callerName);
        fullScreenIntent.putExtra("CALLER_NAME", callerName);
        fullScreenIntent.putExtra("PEER_ID", callerId);
        fullScreenIntent.putExtra("CALLER_ID", callerId);
        fullScreenIntent.putExtra("CALL_ID", callId);
        fullScreenIntent.putExtra("PEER_IP", callerIp);
        fullScreenIntent.putExtra("CALLER_IP", callerIp);
        fullScreenIntent.putExtra("CALL_TYPE", callType);
        fullScreenIntent.putExtra("IS_INCOMING", true);
        fullScreenIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);

        PendingIntent fullScreenPendingIntent = PendingIntent.getActivity(
                this, (int) System.currentTimeMillis(), fullScreenIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, CHANNEL_CALL)
                .setSmallIcon(android.R.drawable.ic_menu_call)
                .setContentTitle(isVideo ? "📹 Incoming P2P Video Call" : "📞 Incoming P2P Voice Call")
                .setContentText("From: " + callerName + " (Direct Offline Mesh)")
                .setPriority(NotificationCompat.PRIORITY_MAX)
                .setCategory(NotificationCompat.CATEGORY_CALL)
                .setFullScreenIntent(fullScreenPendingIntent, true)
                .setContentIntent(fullScreenPendingIntent)
                .setAutoCancel(true);

        NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) {
            nm.notify(9001, builder.build());
        }
    }

    @Override
    public void onSosReceived(LocalSosModel sos) {
        Log.d(TAG, "Background alert: CRITICAL SOS from " + sos.userName);
        Intent intent = new Intent(this, MainActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);

        PendingIntent pi = PendingIntent.getActivity(
                this, (int) System.currentTimeMillis(), intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, CHANNEL_SOS)
                .setSmallIcon(android.R.drawable.ic_dialog_alert)
                .setContentTitle("🚨 CRITICAL SOS ALERT")
                .setContentText("From " + sos.userName + ": " + sos.description)
                .setStyle(new NotificationCompat.BigTextStyle()
                        .bigText("Victim: " + sos.userName + "\nHops: " + sos.hopCount + "\nMessage: " + sos.description + "\nLocation: " + sos.latitude + ", " + sos.longitude))
                .setPriority(NotificationCompat.PRIORITY_MAX)
                .setCategory(NotificationCompat.CATEGORY_ALARM)
                .setContentIntent(pi)
                .setAutoCancel(true);

        NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) {
            nm.notify((int) System.currentTimeMillis(), builder.build());
        }
    }

    @Override
    public void onMessageReceived(ChatMessageModel message) {
        Intent intent = new Intent(this, ChatActivity.class);
        intent.putExtra("PEER_ID", message.sender);
        intent.putExtra("DISPLAY_NAME", message.sender);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

        PendingIntent pi = PendingIntent.getActivity(
                this, (int) System.currentTimeMillis(), intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, CHANNEL_CHAT)
                .setSmallIcon(android.R.drawable.ic_menu_send)
                .setContentTitle("💬 " + message.sender)
                .setContentText(message.content)
                .setPriority(NotificationCompat.PRIORITY_DEFAULT)
                .setContentIntent(pi)
                .setAutoCancel(true);

        NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) {
            nm.notify(message.sender.hashCode(), builder.build());
        }
    }

    @Override
    public void onPeerFound(String endpointId, String peerName) {}

    @Override
    public void onPeerLost(String endpointId) {}

    @Override
    public void onPeerConnected(String endpointId, String peerName) {}

    @Override
    public void onPeerDisconnected(String endpointId) {}

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (meshCoordinator != null) {
            meshCoordinator.removeListener(this);
        }
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
