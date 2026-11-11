package com.cyclecare.notifications;

import android.util.Log;
import androidx.annotation.NonNull;
import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import java.util.Map;

public class CycleCareMessagingService extends FirebaseMessagingService {
    private static final String TAG = "CycleCareFCM";

    @Override
    public void onNewToken(@NonNull String token) {
        super.onNewToken(token);
        Log.d(TAG, "New Firebase Device Token: " + token);
        getSharedPreferences("cyclecare_prefs", MODE_PRIVATE)
                .edit()
                .putString("fcm_device_token", token)
                .apply();

        // Register new token with CycleCare backend
        try {
            java.util.Map<String, Object> req = new java.util.HashMap<>();
            req.put("token", token);
            req.put("platform", "ANDROID");
            req.put("device_model", android.os.Build.MODEL);
            req.put("os_version", "Android " + android.os.Build.VERSION.RELEASE);
            com.cyclecare.api.ApiClient.getApiService(this).registerDeviceToken(req).enqueue(new retrofit2.Callback<Map<String, Object>>() {
                @Override
                public void onResponse(retrofit2.Call<Map<String, Object>> call, retrofit2.Response<Map<String, Object>> response) {
                    Log.d(TAG, "Device token updated on backend: " + response.code());
                }
                @Override
                public void onFailure(retrofit2.Call<Map<String, Object>> call, Throwable t) {}
            });
        } catch (Exception ignored) {}
    }

    @Override
    public void onMessageReceived(@NonNull RemoteMessage remoteMessage) {
        super.onMessageReceived(remoteMessage);
        Log.d(TAG, "Message received from: " + remoteMessage.getFrom());

        String title = "New care essential available";
        String body = "Check out the latest addition to CycleCare Store.";
        String productId = null;
        String imageUrl = null;
        String deepLink = null;

        if (remoteMessage.getNotification() != null) {
            title = remoteMessage.getNotification().getTitle();
            body = remoteMessage.getNotification().getBody();
            if (remoteMessage.getNotification().getImageUrl() != null) {
                imageUrl = remoteMessage.getNotification().getImageUrl().toString();
            }
        }

        Map<String, String> data = remoteMessage.getData();
        if (data != null && !data.isEmpty()) {
            if (data.containsKey("title")) title = data.get("title");
            if (data.containsKey("body")) body = data.get("body");
            if (data.containsKey("product_id")) productId = data.get("product_id");
            if (data.containsKey("image_url")) imageUrl = data.get("image_url");
            if (data.containsKey("deep_link")) deepLink = data.get("deep_link");

            // Handle User-to-User Circle Care Chat messages
            if ("CHAT".equalsIgnoreCase(data.get("type")) || data.containsKey("sender_name") || data.containsKey("connection_id")) {
                String senderName = data.get("sender_name");
                String messageText = data.get("message_text");
                if (messageText == null) messageText = body;
                String connectionId = data.get("connection_id");
                String senderId = data.get("sender_id");
                new DiscreetNotificationManager(this).showChatNotification(senderName, messageText, connectionId, senderId);
                return;
            }
        }

        DiscreetNotificationManager manager = new DiscreetNotificationManager(this);

        if (productId != null || deepLink != null) {
            manager.showProductNotification(title, body, productId, imageUrl, deepLink);
        } else {
            manager.showReminderNotification(title, body);
        }
    }
}
