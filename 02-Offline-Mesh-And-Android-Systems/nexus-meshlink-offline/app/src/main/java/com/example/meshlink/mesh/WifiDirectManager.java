package com.example.meshlink.mesh;

import android.annotation.SuppressLint;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.NetworkInfo;
import android.net.wifi.p2p.WifiP2pConfig;
import android.net.wifi.p2p.WifiP2pDevice;
import android.net.wifi.p2p.WifiP2pDeviceList;
import android.net.wifi.p2p.WifiP2pInfo;
import android.net.wifi.p2p.WifiP2pManager;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;

public class WifiDirectManager implements WifiP2pManager.PeerListListener, WifiP2pManager.ConnectionInfoListener {

    private static final String TAG = "WifiDirectManager";

    public interface WifiDirectListener {
        void onPeersUpdated(List<WifiP2pDevice> peers);
        void onConnected(WifiP2pInfo info);
        void onDisconnected();
    }

    private final Context context;
    private final WifiP2pManager manager;
    private final WifiP2pManager.Channel channel;
    private WifiDirectListener listener;

    private final List<WifiP2pDevice> peers = new ArrayList<>();
    private boolean isReceiverRegistered = false;

    private final BroadcastReceiver receiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context ctx, Intent intent) {
            String action = intent.getAction();
            if (WifiP2pManager.WIFI_P2P_PEERS_CHANGED_ACTION.equals(action)) {
                if (manager != null) {
                    try {
                        manager.requestPeers(channel, WifiDirectManager.this);
                    } catch (SecurityException ignored) {}
                }
            } else if (WifiP2pManager.WIFI_P2P_CONNECTION_CHANGED_ACTION.equals(action)) {
                if (manager == null) return;
                NetworkInfo networkInfo = intent.getParcelableExtra(WifiP2pManager.EXTRA_NETWORK_INFO);
                if (networkInfo != null && networkInfo.isConnected()) {
                    manager.requestConnectionInfo(channel, WifiDirectManager.this);
                } else {
                    if (listener != null) listener.onDisconnected();
                }
            }
        }
    };

    public WifiDirectManager(Context context) {
        this.context = context;
        this.manager = (WifiP2pManager) context.getSystemService(Context.WIFI_P2P_SERVICE);
        this.channel = manager != null ? manager.initialize(context, context.getMainLooper(), null) : null;
    }

    private final Handler handler = new Handler(Looper.getMainLooper());
    private boolean isConnecting = false;

    private final Runnable scanRunnable = new Runnable() {
        @Override
        public void run() {
            discoverPeers();
            handler.postDelayed(this, 12000);
        }
    };

    public void setListener(WifiDirectListener listener) {
        this.listener = listener;
    }

    public void start() {
        if (manager == null || channel == null) return;

        IntentFilter filter = new IntentFilter();
        filter.addAction(WifiP2pManager.WIFI_P2P_STATE_CHANGED_ACTION);
        filter.addAction(WifiP2pManager.WIFI_P2P_PEERS_CHANGED_ACTION);
        filter.addAction(WifiP2pManager.WIFI_P2P_CONNECTION_CHANGED_ACTION);
        filter.addAction(WifiP2pManager.WIFI_P2P_THIS_DEVICE_CHANGED_ACTION);

        if (!isReceiverRegistered) {
            context.registerReceiver(receiver, filter);
            isReceiverRegistered = true;
        }

        handler.removeCallbacks(scanRunnable);
        handler.post(scanRunnable);
    }

    @SuppressLint("MissingPermission")
    public void discoverPeers() {
        if (manager != null && channel != null) {
            try {
                manager.discoverPeers(channel, new WifiP2pManager.ActionListener() {
                    @Override
                    public void onSuccess() {
                        Log.d(TAG, "WiFi Direct peer discovery initiated successfully");
                    }

                    @Override
                    public void onFailure(int reason) {
                        Log.w(TAG, "WiFi Direct discovery failed (reason=" + reason + ")");
                        // Do not aggressively retry on failure to prevent Wi-Fi chip contention with Nearby Connections.
                        // The periodic scanRunnable will trigger again safely.
                    }
                });
            } catch (SecurityException ignored) {}
        }
    }

    @SuppressLint("MissingPermission")
    public void connectToPeer(WifiP2pDevice device) {
        if (manager == null || channel == null || isConnecting) return;

        isConnecting = true;
        WifiP2pConfig config = new WifiP2pConfig();
        config.deviceAddress = device.deviceAddress;
        try {
            manager.connect(channel, config, new WifiP2pManager.ActionListener() {
                @Override
                public void onSuccess() {
                    Log.d(TAG, "Connecting to WiFi Direct peer: " + device.deviceName);
                    handler.postDelayed(() -> isConnecting = false, 8000);
                }

                @Override
                public void onFailure(int reason) {
                    Log.w(TAG, "Connect to peer failed (reason=" + reason + ")");
                    isConnecting = false;
                }
            });
        } catch (SecurityException e) {
            isConnecting = false;
        }
    }

    public void stop() {
        handler.removeCallbacks(scanRunnable);
        if (isReceiverRegistered) {
            try {
                context.unregisterReceiver(receiver);
            } catch (Exception ignored) {}
            isReceiverRegistered = false;
        }
    }

    @Override
    public void onPeersAvailable(WifiP2pDeviceList peerList) {
        peers.clear();
        peers.addAll(peerList.getDeviceList());
        // Do NOT auto-trigger OS Wi-Fi Direct invitation dialogs.
        // Google Nearby Connections manages authenticated, silent peer connections in the background.
        if (listener != null) {
            listener.onPeersUpdated(new ArrayList<>(peers));
        }
    }

    @Override
    public void onConnectionInfoAvailable(WifiP2pInfo info) {
        Log.d(TAG, "WiFi Direct connected. Group Owner: " + info.isGroupOwner + " IP: " + 
                (info.groupOwnerAddress != null ? info.groupOwnerAddress.getHostAddress() : "null"));
        if (listener != null) {
            listener.onConnected(info);
        }
    }

    public List<WifiP2pDevice> getPeers() {
        return new ArrayList<>(peers);
    }
}
