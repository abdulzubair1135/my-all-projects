package com.example.nearmeshchat;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.NetworkRequest;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.TimeUnit;

import androidx.annotation.NonNull;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class AapdaSetuSyncManager {

    private static final String TAG = "AapdaSetuSync";
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");

    public interface SyncListener {
        void onSyncCompleted(int count);
    }

    private final Context context;
    private final MeshDatabase db;
    private final OkHttpClient client;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private SyncListener syncListener;

    public static final String RENDER_BACKEND = "https://sahay-2tvh.onrender.com/api";
    public static final String CLOUDFLARE_BACKEND = "https://sahay-2tvh.onrender.com/api";
    public static final String LOCAL_BACKEND = "http://127.0.0.1:5000/api";

    public AapdaSetuSyncManager(Context context, MeshDatabase db) {
        this.context = context.getApplicationContext();
        this.db = db;
        this.client = new OkHttpClient.Builder()
                .connectTimeout(5, TimeUnit.SECONDS)
                .readTimeout(8, TimeUnit.SECONDS)
                .writeTimeout(8, TimeUnit.SECONDS)
                .build();

        registerNetworkCallback();
    }

    public void setSyncListener(SyncListener listener) {
        this.syncListener = listener;
    }

    public String getBackendBaseUrl() {
        SharedPreferences prefs = context.getSharedPreferences("aapdasetu_config", Context.MODE_PRIVATE);
        return prefs.getString("backend_url", RENDER_BACKEND);
    }

    public void setBackendBaseUrl(String url) {
        context.getSharedPreferences("aapdasetu_config", Context.MODE_PRIVATE)
                .edit()
                .putString("backend_url", url)
                .apply();
    }

    public boolean isInternetAvailable() {
        ConnectivityManager cm = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
        if (cm == null) return false;
        Network network = cm.getActiveNetwork();
        if (network == null) return false;
        NetworkCapabilities capabilities = cm.getNetworkCapabilities(network);
        return capabilities != null && (
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ||
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ||
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) ||
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_VPN)
        );
    }

    private void registerNetworkCallback() {
        try {
            ConnectivityManager cm = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
            if (cm != null) {
                NetworkRequest request = new NetworkRequest.Builder()
                        .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
                        .build();

                cm.registerNetworkCallback(request, new ConnectivityManager.NetworkCallback() {
                    @Override
                    public void onAvailable(Network network) {
                        Log.d(TAG, "Network restored. Triggering offline emergency sync queue...");
                        triggerSyncQueue();
                    }
                });
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to register network callback: " + e.getMessage());
        }
    }

    public void triggerSyncQueue() {
        if (!isInternetAvailable()) {
            Log.d(TAG, "Sync skipped: No active internet connection.");
            return;
        }

        new Thread(() -> {
            List<LocalSosModel> pending = db.getPendingSOS();
            if (pending.isEmpty()) return;

            try {
                JSONObject payload = new JSONObject();
                JSONArray sosArray = new JSONArray();

                for (LocalSosModel s : pending) {
                    JSONObject item = new JSONObject();
                    item.put("eventId", s.eventId);
                    item.put("originDeviceId", s.originDeviceId);
                    item.put("userId", s.userId);
                    item.put("userName", s.userName);
                    item.put("userPhone", s.userPhone);
                    item.put("type", s.type);
                    item.put("severity", s.severity);
                    item.put("description", s.description);
                    item.put("peopleCount", s.peopleCount);
                    item.put("injuredCount", s.injuredCount);
                    item.put("latitude", s.latitude);
                    item.put("longitude", s.longitude);
                    item.put("accuracy", s.accuracy);
                    item.put("hopCount", s.hopCount);
                    item.put("createdAt", s.createdAt);
                    sosArray.put(item);
                }

                payload.put("sosEvents", sosArray);

                RequestBody body = RequestBody.create(payload.toString(), JSON);

                boolean synced = trySyncUrl(getBackendBaseUrl() + "/sync", body, pending);
                if (!synced) {
                    String fallback = getBackendBaseUrl().contains("127.0.0.1") ? CLOUDFLARE_BACKEND : LOCAL_BACKEND;
                    trySyncUrl(fallback + "/sync", RequestBody.create(payload.toString(), JSON), pending);
                }
            } catch (Exception e) {
                Log.e(TAG, "Sync request failed: " + e.getMessage());
            }
        }).start();
    }

    private boolean trySyncUrl(String url, RequestBody body, List<LocalSosModel> pending) {
        try {
            Request request = new Request.Builder().url(url).post(body).build();
            Response response = client.newCall(request).execute();
            if (response.isSuccessful() && response.body() != null) {
                String resStr = response.body().string();
                JSONObject resObj = new JSONObject(resStr);
                if (resObj.optBoolean("success", false)) {
                    for (LocalSosModel s : pending) {
                        db.markSOSSynced(s.eventId);
                    }
                    Log.d(TAG, "Successfully synced " + pending.size() + " emergency SOS records via " + url);
                    if (syncListener != null) {
                        mainHandler.post(() -> syncListener.onSyncCompleted(pending.size()));
                    }
                    return true;
                }
            }
        } catch (Exception e) {
            Log.w(TAG, "Sync to " + url + " failed: " + e.getMessage());
        }
        return false;
    }

    public void uploadRelayedSOS(LocalSosModel sos, String fromPeer) {
        if (!isInternetAvailable()) return;

        new Thread(() -> {
            try {
                JSONObject payload = new JSONObject();
                payload.put("eventId", sos.eventId);
                payload.put("originDeviceId", sos.originDeviceId);
                payload.put("relayDeviceId", "Android_Relay_" + android.os.Build.MODEL);
                payload.put("fromDeviceId", fromPeer);
                payload.put("hopCount", sos.hopCount);
                payload.put("type", sos.type);
                payload.put("severity", sos.severity);
                payload.put("description", sos.description);
                payload.put("peopleCount", sos.peopleCount);
                payload.put("injuredCount", sos.injuredCount);
                payload.put("latitude", sos.latitude);
                payload.put("longitude", sos.longitude);
                payload.put("accuracy", sos.accuracy);
                payload.put("createdAt", sos.createdAt);

                RequestBody body = RequestBody.create(payload.toString(), JSON);
                Request request = new Request.Builder()
                        .url(getBackendBaseUrl() + "/relay")
                        .post(body)
                        .build();

                Response response = client.newCall(request).execute();
                if (response.isSuccessful()) {
                    db.markSOSSynced(sos.eventId);
                    Log.d(TAG, "Successfully relayed peer SOS to cloud backend: " + sos.eventId);
                }
            } catch (Exception e) {
                Log.e(TAG, "Failed to upload relayed SOS: " + e.getMessage());
            }
        }).start();
    }

    public void sendOnlineSOS(LocalSosModel sos, Callback callback) {
        try {
            JSONObject json = new JSONObject();
            json.put("eventId", sos.eventId);
            json.put("originDeviceId", sos.originDeviceId);
            json.put("userName", sos.userName);
            json.put("userPhone", sos.userPhone);
            json.put("type", sos.type);
            json.put("severity", sos.severity);
            json.put("description", sos.description);
            json.put("peopleCount", sos.peopleCount);
            json.put("injuredCount", sos.injuredCount);
            json.put("latitude", sos.latitude);
            json.put("longitude", sos.longitude);
            json.put("accuracy", sos.accuracy);
            json.put("source", "ONLINE");

            RequestBody body = RequestBody.create(json.toString(), JSON);
            String primaryUrl = getBackendBaseUrl() + "/sos";
            Request request = new Request.Builder()
                    .url(primaryUrl)
                    .post(body)
                    .build();

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(@NonNull Call call, @NonNull IOException e) {
                    Log.w(TAG, "Primary SOS URL failed: " + e.getMessage() + ", trying fallback...");
                    String fallbackUrl = (primaryUrl.contains("127.0.0.1") ? CLOUDFLARE_BACKEND : LOCAL_BACKEND) + "/sos";
                    Request fallbackRequest = new Request.Builder()
                            .url(fallbackUrl)
                            .post(RequestBody.create(json.toString(), JSON))
                            .build();
                    client.newCall(fallbackRequest).enqueue(callback);
                }

                @Override
                public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                    if (response.isSuccessful()) {
                        callback.onResponse(call, response);
                    } else {
                        String fallbackUrl = (primaryUrl.contains("127.0.0.1") ? CLOUDFLARE_BACKEND : LOCAL_BACKEND) + "/sos";
                        Request fallbackRequest = new Request.Builder()
                                .url(fallbackUrl)
                                .post(RequestBody.create(json.toString(), JSON))
                                .build();
                        client.newCall(fallbackRequest).enqueue(callback);
                    }
                }
            });
        } catch (Exception e) {
            Log.e(TAG, "Failed to create online SOS JSON: " + e.getMessage());
        }
    }
}