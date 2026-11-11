package com.example.meshlink.mesh;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.nsd.NsdManager;
import android.net.nsd.NsdServiceInfo;
import android.os.Handler;
import android.os.Looper;
import android.os.ParcelFileDescriptor;
import android.util.Log;

import androidx.annotation.NonNull;

import com.example.meshlink.data.ChatMessageModel;
import com.example.meshlink.data.LocalSosModel;
import com.example.meshlink.data.MeshDatabase;
import com.example.meshlink.crypto.CryptoManager;
import com.example.meshlink.social.FollowManager;
import com.example.meshlink.browser.LocalHttpServer;
import com.google.android.gms.nearby.Nearby;
import com.google.android.gms.nearby.connection.AdvertisingOptions;
import com.google.android.gms.nearby.connection.ConnectionInfo;
import com.google.android.gms.nearby.connection.ConnectionLifecycleCallback;
import com.google.android.gms.nearby.connection.ConnectionResolution;
import com.google.android.gms.nearby.connection.ConnectionsClient;
import com.google.android.gms.nearby.connection.DiscoveredEndpointInfo;
import com.google.android.gms.nearby.connection.DiscoveryOptions;
import com.google.android.gms.nearby.connection.EndpointDiscoveryCallback;
import com.google.android.gms.nearby.connection.Payload;
import com.google.android.gms.nearby.connection.PayloadCallback;
import com.google.android.gms.nearby.connection.PayloadTransferUpdate;
import com.google.android.gms.nearby.connection.Strategy;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.InterfaceAddress;
import java.net.NetworkInterface;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MeshCoordinator {

    private static final String TAG = "MeshCoordinator";
    private static final String SERVICE_ID = "com.example.meshlink.OFFLINE_MESH";
    private static final String NSD_SERVICE_TYPE = "_nexusmesh._tcp.";
    private static final Strategy STRATEGY = Strategy.P2P_CLUSTER;

    public interface MeshEventListener {
        void onPeerFound(String endpointId, String peerName);
        void onPeerLost(String endpointId);
        void onPeerConnected(String endpointId, String peerName);
        void onPeerDisconnected(String endpointId);
        void onMessageReceived(ChatMessageModel message);
        void onSosReceived(LocalSosModel sos);

        default void onIncomingCall(String callId, String callerName, String callerId, String callType, String callerIp) {}
        default void onCallAccepted(String callId, String peerId) {}
        default void onCallAccepted(String callId, String peerId, String acceptorIp) {}
        default void onCallRejected(String callId, String peerId) {}
        default void onCallEnded(String callId) {}
        default void onMeshRefreshed() {}
        default void onTopologyUpdated() {}
    }

    private static MeshCoordinator instance;
    private final Context context;
    private final ConnectionsClient connectionsClient;
    private final MeshDatabase db;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    private String myNodeId;
    private String myDisplayName;
    private boolean isRunning = false;
    private boolean isAdvertisingActive = false;
    private boolean isDiscoveryActive = false;

    // Discovered & connected peers map: endpointId -> PeerName
    private final Map<String, String> connectedPeers = new ConcurrentHashMap<>();
    private final Map<String, String> discoveredEndpoints = new ConcurrentHashMap<>();
    private final Map<String, String> peerIpAddresses = new ConcurrentHashMap<>();
    private final Set<String> connectingEndpoints = ConcurrentHashMap.newKeySet();
    private final Set<String> seenMessageIds = ConcurrentHashMap.newKeySet();

    // Multi-Hop Mesh Topology Graph & Dynamic Routing Engine
    private final Map<String, Set<String>> topologyAdjacency = new ConcurrentHashMap<>();
    private final Map<String, String> nodeDisplayNames = new ConcurrentHashMap<>();
    private LocalHttpServer localHttpServer;
    private DatagramSocket voiceRelaySocket;
    private Thread voiceRelayThread;

    public static class RouteInfo {
        public final List<String> path;
        public final int hopCount;
        public final String nextHop;

        public RouteInfo(List<String> path) {
            this.path = path != null ? path : Collections.emptyList();
            this.hopCount = this.path.size() > 1 ? this.path.size() - 1 : 1;
            this.nextHop = this.path.size() > 1 ? this.path.get(1) : "";
        }
    }

    private final List<MeshEventListener> listeners = new ArrayList<>();

    private final CryptoManager cryptoManager;
    private final FollowManager followManager;

    // High-speed NSD / Local Sockets Engine
    private NsdManager nsdManager;
    private NsdManager.RegistrationListener nsdRegistrationListener;
    private NsdManager.DiscoveryListener nsdDiscoveryListener;
    private ServerSocket nsdServerSocket;
    private int nsdServerPort = 8888;
    private final Map<String, Socket> nsdPeerSockets = new ConcurrentHashMap<>();
    private final Map<String, PrintWriter> nsdPeerWriters = new ConcurrentHashMap<>();
    private final ExecutorService nsdExecutor = Executors.newCachedThreadPool();

    public static class PendingFileTask {
        public final Payload headerPayload;
        public final Payload filePayload;
        public final String targetName;

        public PendingFileTask(Payload headerPayload, Payload filePayload, String targetName) {
            this.headerPayload = headerPayload;
            this.filePayload = filePayload;
            this.targetName = targetName;
        }
    }
    private final List<PendingFileTask> pendingFileTasks = Collections.synchronizedList(new ArrayList<>());

    // Active Call Exclusivity State (1-to-1 strict direct session)
    private volatile boolean isCallActive = false;
    private volatile String activeCallId = null;
    private volatile String activeCallPeerId = null;
    private volatile String activeCallType = null;

    public synchronized void setCallActive(boolean active, String callId, String peerId, String callType) {
        this.isCallActive = active;
        this.activeCallId = active ? callId : null;
        this.activeCallPeerId = active ? peerId : null;
        this.activeCallType = active ? callType : null;
        Log.d(TAG, "Call active exclusivity: active=" + active + ", peer=" + peerId + ", type=" + callType);
        if (active) {
            closeVoiceRelaySocket();
        stopLocalHttpServer();
        if (localHttpServer != null) {
            localHttpServer.stop();
            localHttpServer = null;
        }
        } else {
            startVoiceRelay();
        try {
            if (localHttpServer == null) {
                localHttpServer = new LocalHttpServer(8888, context, this);
                localHttpServer.start();
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to launch LocalHttpServer: " + e.getMessage());
        }
        }
    }

    public boolean isCallActive() {
        return isCallActive;
    }

    public String getActiveCallPeerId() {
        return activeCallPeerId;
    }

    public String getActiveCallType() {
        return activeCallType;
    }

    public Map<String, Set<String>> getTopologyAdjacency() {
        return new HashMap<>(topologyAdjacency);
    }

    public Map<String, String> getNodeDisplayNames() {
        return new HashMap<>(nodeDisplayNames);
    }

    public RouteInfo computeRouteTo(String targetNameOrId) {
        String cleanTarget = cleanPeerName(targetNameOrId);
        if (isSelfNode("", cleanTarget)) {
            return new RouteInfo(Collections.singletonList(myDisplayName));
        }
        for (String directName : connectedPeers.values()) {
            if (cleanPeerName(directName).equalsIgnoreCase(cleanTarget)) {
                return new RouteInfo(Arrays.asList(myDisplayName, directName));
            }
        }
        Queue<List<String>> queue = new LinkedList<>();
        queue.add(Collections.singletonList(myDisplayName));
        Set<String> visited = new HashSet<>();
        visited.add(cleanPeerName(myDisplayName));

        while (!queue.isEmpty()) {
            List<String> currentPath = queue.poll();
            String lastNode = cleanPeerName(currentPath.get(currentPath.size() - 1));

            Set<String> neighbors = topologyAdjacency.get(lastNode);
            if (neighbors == null && lastNode.equalsIgnoreCase(cleanPeerName(myDisplayName))) {
                neighbors = new HashSet<>(connectedPeers.values());
            }

            if (neighbors != null) {
                for (String neighbor : neighbors) {
                    String cleanNeighbor = cleanPeerName(neighbor);
                    if (cleanNeighbor.equalsIgnoreCase(cleanTarget)) {
                        List<String> newPath = new ArrayList<>(currentPath);
                        newPath.add(neighbor);
                        return new RouteInfo(newPath);
                    }
                    if (!visited.contains(cleanNeighbor) && currentPath.size() < 6) {
                        visited.add(cleanNeighbor);
                        List<String> newPath = new ArrayList<>(currentPath);
                        newPath.add(neighbor);
                        queue.add(newPath);
                    }
                }
            }
        }
        return new RouteInfo(Arrays.asList(myDisplayName, targetNameOrId));
    }

    public String getEndpointForPeer(String peerNameOrId) {
        if (peerNameOrId == null || peerNameOrId.isEmpty()) return null;
        String cleanTarget = cleanPeerName(peerNameOrId);
        for (Map.Entry<String, String> entry : connectedPeers.entrySet()) {
            if (cleanPeerName(entry.getValue()).equalsIgnoreCase(cleanTarget) ||
                entry.getKey().equalsIgnoreCase(peerNameOrId)) {
                return entry.getKey();
            }
        }
        return null;
    }

    public void broadcastTopologyUpdate() {
        try {
            JSONObject obj = new JSONObject();
            obj.put("pkt_type", "TOPOLOGY");
            obj.put("node_id", myNodeId);
            obj.put("name", myDisplayName);
            obj.put("hop_count", 0);

            JSONArray neighbors = new JSONArray();
            for (String peerName : connectedPeers.values()) {
                neighbors.put(peerName);
            }
            obj.put("neighbors", neighbors);

            String json = obj.toString();
            byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
            Payload payload = Payload.fromBytes(bytes);
            for (String ep : connectedPeers.keySet()) {
                if (!ep.startsWith("NSD_")) {
                    try { connectionsClient.sendPayload(ep, payload); } catch (Exception ignored) {}
                }
            }
            broadcastToNsdPeers(json);
        } catch (Exception ignored) {}
    }

    private synchronized void startVoiceRelay() {
        if (voiceRelaySocket != null && !voiceRelaySocket.isClosed()) return;
        voiceRelayThread = new Thread(() -> {
            try {
                voiceRelaySocket = new DatagramSocket(null);
                voiceRelaySocket.setReuseAddress(true);
                voiceRelaySocket.setBroadcast(true);
                voiceRelaySocket.bind(new InetSocketAddress(50005));
                byte[] buffer = new byte[2048];
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                while (isRunning && voiceRelaySocket != null && !voiceRelaySocket.isClosed()) {
                    try {
                        voiceRelaySocket.receive(packet);
                        if (isCallActive) continue;

                        byte[] data = packet.getData();
                        int len = packet.getLength();
                        if (len > 20 && data[0] == 0x56) {
                            int hopCount = data[17] & 0xFF;
                            if (hopCount < 5) {
                                data[17] = (byte) (hopCount + 1);
                                InetAddress senderAddr = packet.getAddress();
                                List<String> bcasts = getSubnetBroadcastAddresses();
                                for (String bcastIp : bcasts) {
                                    try {
                                        InetAddress bcastAddr = InetAddress.getByName(bcastIp);
                                        if (!bcastAddr.equals(senderAddr)) {
                                            DatagramPacket forward = new DatagramPacket(data, len, bcastAddr, 50005);
                                            voiceRelaySocket.send(forward);
                                        }
                                    } catch (Exception ignored) {}
                                }
                            }
                        }
                    } catch (Exception ignored) {}
                }
            } catch (Exception ignored) {}
        });
        voiceRelayThread.start();
    }

    private synchronized void closeVoiceRelaySocket() {
        if (voiceRelaySocket != null) {
            try { voiceRelaySocket.close(); } catch (Exception ignored) {}
            voiceRelaySocket = null;
        }
    }

    public static synchronized MeshCoordinator getInstance(Context context) {
        if (instance == null) {
            instance = new MeshCoordinator(context.getApplicationContext());
        }
        return instance;
    }

    private MeshCoordinator(Context context) {
        this.context = context;
        this.connectionsClient = Nearby.getConnectionsClient(context);
        this.db = new MeshDatabase(context);
        this.cryptoManager = CryptoManager.getInstance(context);
        this.followManager = FollowManager.getInstance(context);

        SharedPreferences prefs = context.getSharedPreferences("meshlink_prefs", Context.MODE_PRIVATE);
        this.myDisplayName = prefs.getString("user_name", "Anonymous");
        this.myNodeId = cryptoManager.getMyMeshId();
        this.nsdManager = (NsdManager) context.getSystemService(Context.NSD_SERVICE);
    }

    public void addListener(MeshEventListener listener) {
        if (!listeners.contains(listener)) listeners.add(listener);
    }

    public void removeListener(MeshEventListener listener) {
        listeners.remove(listener);
    }

    private final Runnable topologyHeartbeatRunnable = new Runnable() {
        @Override
        public void run() {
            if (isRunning) {
                broadcastTopologyUpdate();
                mainHandler.postDelayed(this, 7000);
            }
        }
    };

    // Passive Watchdog (Only restarts advertising/discovery if failed, NEVER stops active connections)
    private final Runnable meshWatchdogRunnable = new Runnable() {
        @Override
        public void run() {
            if (isRunning) {
                if (!isAdvertisingActive) {
                    Log.d(TAG, "Watchdog: Advertising inactive, restarting...");
                    startAdvertising();
                }
                if (!isDiscoveryActive) {
                    Log.d(TAG, "Watchdog: Discovery inactive, restarting...");
                    startDiscovery();
                }
                mainHandler.postDelayed(this, 10000);
            }
        }
    };

    public static String cleanPeerName(String raw) {
        if (raw == null) return "Unknown";
        String s = raw.trim();
        if (s.contains("|")) {
            s = s.substring(0, s.indexOf("|")).trim();
        }
        if (s.startsWith("NexusMesh_")) {
            s = s.substring("NexusMesh_".length()).trim();
        }
        if (s.startsWith("MESH_")) {
            s = s.substring("MESH_".length()).trim();
        }
        return s.isEmpty() ? "Unknown" : s;
    }

    private synchronized void startLocalHttpServer() {
        try {
            if (localHttpServer == null) {
                localHttpServer = new LocalHttpServer(8888, context, this);
                localHttpServer.start();
                Log.d(TAG, "LocalHttpServer initialized on port 8888");
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to start LocalHttpServer: " + e.getMessage());
        }
    }

    private synchronized void stopLocalHttpServer() {
        if (localHttpServer != null) {
            localHttpServer.stop();
            localHttpServer = null;
            Log.d(TAG, "LocalHttpServer stopped");
        }
    }

    public synchronized void startMesh() {
        if (isRunning) return;
        isRunning = true;
        Log.d(TAG, "Starting MeshLink ultra-fast mesh engine as " + myDisplayName + " (" + myNodeId + ")");

        startAdvertising();
        startDiscovery();
        startNsdServer();
        startNsdDiscovery();
        startVoiceRelay();
        startLocalHttpServer();

        mainHandler.removeCallbacks(meshWatchdogRunnable);
        mainHandler.postDelayed(meshWatchdogRunnable, 10000);

        mainHandler.removeCallbacks(topologyHeartbeatRunnable);
        mainHandler.postDelayed(topologyHeartbeatRunnable, 3000);
    }

    public synchronized void stopMesh() {
        if (!isRunning) return;
        isRunning = false;
        isAdvertisingActive = false;
        isDiscoveryActive = false;

        mainHandler.removeCallbacks(meshWatchdogRunnable);
        mainHandler.removeCallbacks(topologyHeartbeatRunnable);
        closeVoiceRelaySocket();

        try {
            connectionsClient.stopAdvertising();
            connectionsClient.stopDiscovery();
            connectionsClient.stopAllEndpoints();
        } catch (Exception ignored) {}

        stopNsdServices();

        connectedPeers.clear();
        discoveredEndpoints.clear();
        connectingEndpoints.clear();
    }

    public synchronized void refreshMesh() {
        Log.d(TAG, "User requested Mesh Refresh. Restarting advertising, discovery and NSD beacons...");
        try {
            connectionsClient.stopAdvertising();
            connectionsClient.stopDiscovery();
        } catch (Exception ignored) {}
        isAdvertisingActive = false;
        isDiscoveryActive = false;

        stopNsdServices();

        startAdvertising();
        startDiscovery();
        startNsdServer();
        startNsdDiscovery();

        // Reload profile and broadcast latest avatar to mesh
        reloadProfile();
        SharedPreferences meshPrefs = context.getSharedPreferences("meshlink_prefs", Context.MODE_PRIVATE);
        String currentPic = meshPrefs.getString("user_profile_pic_base64", "");
        if (!currentPic.isEmpty()) {
            broadcastAvatarUpdate(currentPic);
        }

        // Notify listeners that mesh has been refreshed
        for (MeshEventListener l : listeners) {
            try {
                l.onMeshRefreshed();
            } catch (Exception ignored) {}
        }
    }

    private void startAdvertising() {
        if (!isRunning) return;
        AdvertisingOptions options = new AdvertisingOptions.Builder()
                .setStrategy(STRATEGY)
                .setLowPower(true)
                .build();
        connectionsClient.startAdvertising(
                myDisplayName,
                SERVICE_ID,
                connectionLifecycleCallback,
                options
        ).addOnSuccessListener(unused -> {
            Log.d(TAG, "Nearby BLE Advertising active");
            isAdvertisingActive = true;
        }).addOnFailureListener(e -> {
            String msg = e.getMessage() != null ? e.getMessage() : "";
            if (msg.contains("8001") || msg.contains("ALREADY_ADVERTISING")) {
                isAdvertisingActive = true;
                return;
            }
            Log.e(TAG, "Nearby BLE Advertising error: " + e.getMessage() + ". Retrying in 3s...");
            isAdvertisingActive = false;
            mainHandler.postDelayed(this::startAdvertising, 3000);
        });
    }

    private void startDiscovery() {
        if (!isRunning) return;
        DiscoveryOptions options = new DiscoveryOptions.Builder()
                .setStrategy(STRATEGY)
                .setLowPower(true)
                .build();
        connectionsClient.startDiscovery(
                SERVICE_ID,
                endpointDiscoveryCallback,
                options
        ).addOnSuccessListener(unused -> {
            Log.d(TAG, "Nearby BLE Discovery active");
            isDiscoveryActive = true;
        }).addOnFailureListener(e -> {
            String msg = e.getMessage() != null ? e.getMessage() : "";
            if (msg.contains("8002") || msg.contains("ALREADY_DISCOVERING")) {
                isDiscoveryActive = true;
                return;
            }
            Log.e(TAG, "Nearby BLE Discovery error: " + e.getMessage() + ". Retrying in 3s...");
            isDiscoveryActive = false;
            mainHandler.postDelayed(this::startDiscovery, 3000);
        });
    }

    private void requestConnectionToEndpoint(String endpointId) {
        if (!isRunning || connectedPeers.containsKey(endpointId) || connectingEndpoints.contains(endpointId)) {
            return;
        }

        connectingEndpoints.add(endpointId);
        Log.d(TAG, "Requesting connection to endpoint: " + endpointId);

        connectionsClient.requestConnection(myDisplayName, endpointId, connectionLifecycleCallback)
                .addOnSuccessListener(unused -> Log.d(TAG, "Connection request sent to " + endpointId))
                .addOnFailureListener(e -> {
                    Log.w(TAG, "Request connection failed to " + endpointId + ": " + e.getMessage());
                    connectingEndpoints.remove(endpointId);
                    mainHandler.postDelayed(() -> {
                        if (discoveredEndpoints.containsKey(endpointId) && !connectedPeers.containsKey(endpointId)) {
                            requestConnectionToEndpoint(endpointId);
                        }
                    }, 3000);
                });
    }

    private final EndpointDiscoveryCallback endpointDiscoveryCallback = new EndpointDiscoveryCallback() {
        @Override
        public void onEndpointFound(@NonNull String endpointId, @NonNull DiscoveredEndpointInfo info) {
            String raw = info.getEndpointName();
            String name = cleanPeerName(raw);

            // Strictly ignore discovery of self
            if (isSelfNode("", name)) {
                Log.w(TAG, "Ignoring self Nearby endpoint: " + endpointId);
                return;
            }

            discoveredEndpoints.put(endpointId, name);
            Log.d(TAG, "Found peer endpoint: " + name + " [" + endpointId + "]");

            mainHandler.post(() -> {
                for (MeshEventListener l : listeners) l.onPeerFound(endpointId, name);
            });

            // Bulletproof Tie-break with Auto-Fallback:
            // Prevents race collision if both initiate at same millisecond,
            // BUT guarantees fast connection even if peer (Poco/Xiaomi) discovery is delayed!
            String myClean = cleanPeerName(myDisplayName);
            String peerClean = cleanPeerName(name);
            int cmp = myClean.compareToIgnoreCase(peerClean);
            if (cmp > 0) {
                Log.d(TAG, "Tie-break: " + myClean + " > " + peerClean + ". Waiting up to 1.5s for peer to initiate...");
                mainHandler.postDelayed(() -> {
                    if (isRunning && discoveredEndpoints.containsKey(endpointId)
                            && !connectedPeers.containsKey(endpointId)
                            && !connectingEndpoints.contains(endpointId)) {
                        Log.d(TAG, "Fallback auto-connect: Peer did not initiate in 1.5s. Connecting proactively to " + endpointId);
                        requestConnectionToEndpoint(endpointId);
                    }
                }, 1500);
                return;
            }

            // Only the node with alphabetically smaller name initiates auto connection immediately
            Log.d(TAG, "Tie-break: " + myClean + " <= " + peerClean + ". Initiating immediate connection to " + endpointId);
            requestConnectionToEndpoint(endpointId);
        }

        @Override
        public void onEndpointLost(@NonNull String endpointId) {
            discoveredEndpoints.remove(endpointId);
            connectingEndpoints.remove(endpointId);
            mainHandler.post(() -> {
                for (MeshEventListener l : listeners) l.onPeerLost(endpointId);
            });
        }
    };

    private final ConnectionLifecycleCallback connectionLifecycleCallback = new ConnectionLifecycleCallback() {
        @Override
        public void onConnectionInitiated(@NonNull String endpointId, @NonNull ConnectionInfo info) {
            String rawName = info.getEndpointName();
            String name = cleanPeerName(rawName);
            String peerNodeId = "";
            if (rawName != null && rawName.contains("|")) {
                peerNodeId = rawName.substring(rawName.indexOf("|") + 1).trim();
            }

            // Strictly reject connections from self
            if (isSelfNode(peerNodeId, name)) {
                Log.w(TAG, "Rejecting self Nearby connection: " + endpointId);
                connectionsClient.rejectConnection(endpointId);
                return;
            }

            discoveredEndpoints.put(endpointId, name);
            Log.d(TAG, "Connection initiated with " + endpointId + " (" + name + ")");
            connectingEndpoints.add(endpointId);

            // Auto accept connection
            connectionsClient.acceptConnection(endpointId, payloadCallback)
                    .addOnFailureListener(e -> {
                        Log.e(TAG, "Accept connection error for " + endpointId + ": " + e.getMessage());
                        connectingEndpoints.remove(endpointId);
                    });
        }

        @Override
        public void onConnectionResult(@NonNull String endpointId, @NonNull ConnectionResolution result) {
            connectingEndpoints.remove(endpointId);

            if (result.getStatus().isSuccess()) {
                String name = discoveredEndpoints.containsKey(endpointId) ? cleanPeerName(discoveredEndpoints.get(endpointId)) : "Peer";
                connectedPeers.put(endpointId, name);
                discoveredEndpoints.put(endpointId, name);
                Log.d(TAG, "Peer connected successfully: " + name + " [" + endpointId + "]");

                // Send HELLO handshake packet with public key for E2EE
                sendHelloPacket(endpointId);

                // Drain any pending files for this newly connected peer
                drainPendingFilesForEndpoint(endpointId, name);

                mainHandler.post(() -> {
                    for (MeshEventListener l : listeners) l.onPeerConnected(endpointId, name);
                });
            } else {
                Log.w(TAG, "Connection result failed for " + endpointId + ": " + result.getStatus().getStatusMessage());
                connectedPeers.remove(endpointId);

                // Auto-retry connection after 2 seconds if peer is still in range
                mainHandler.postDelayed(() -> {
                    if (discoveredEndpoints.containsKey(endpointId) && !connectedPeers.containsKey(endpointId)) {
                        requestConnectionToEndpoint(endpointId);
                    }
                }, 2000);
            }
        }

        @Override
        public void onDisconnected(@NonNull String endpointId) {
            connectedPeers.remove(endpointId);
            connectingEndpoints.remove(endpointId);
            Log.d(TAG, "Peer disconnected: " + endpointId);

            mainHandler.post(() -> {
                for (MeshEventListener l : listeners) l.onPeerDisconnected(endpointId);
            });
        }
    };

    private final Map<Long, JSONObject> incomingFileHeaders = new ConcurrentHashMap<>();
    private final Map<Long, Payload> incomingFilePayloads = new ConcurrentHashMap<>();
    private final Set<Long> completedFilePayloadIds = Collections.newSetFromMap(new ConcurrentHashMap<>());

    private final PayloadCallback payloadCallback = new PayloadCallback() {
        @Override
        public void onPayloadReceived(@NonNull String endpointId, @NonNull Payload payload) {
            if (payload.getType() == Payload.Type.BYTES && payload.asBytes() != null) {
                String raw = new String(payload.asBytes(), StandardCharsets.UTF_8);
                handleIncomingPacket(raw, endpointId);
            } else if (payload.getType() == Payload.Type.FILE) {
                long payloadId = payload.getId();
                Log.d(TAG, "Incoming Nearby FILE payload initiated: " + payloadId);
                incomingFilePayloads.put(payloadId, payload);
                if (completedFilePayloadIds.contains(payloadId)) {
                    checkAndCompleteFileTransfer(payloadId);
                }
            }
        }

        @Override
        public void onPayloadTransferUpdate(@NonNull String endpointId, @NonNull PayloadTransferUpdate update) {
            long payloadId = update.getPayloadId();
            if (update.getStatus() == PayloadTransferUpdate.Status.SUCCESS) {
                Log.d(TAG, "Nearby payload transfer SUCCESS: " + payloadId);
                completedFilePayloadIds.add(payloadId);
                checkAndCompleteFileTransfer(payloadId);
            } else if (update.getStatus() == PayloadTransferUpdate.Status.FAILURE) {
                Log.w(TAG, "Nearby payload transfer FAILED: " + payloadId);
                incomingFileHeaders.remove(payloadId);
                incomingFilePayloads.remove(payloadId);
                completedFilePayloadIds.remove(payloadId);
            }
        }
    };

    /* ═══════════════════════════════════════════════════════════════════════════
       HIGH-SPEED NSD (NET SERVICE DISCOVERY) EMBEDDED SOCKET ENGINE
       Provides sub-second (<500ms) connection over local Wi-Fi / Hotspots
       ═══════════════════════════════════════════════════════════════════════════ */

    private DatagramSocket udpDiscoverySocket;
    private Thread udpBeaconSendThread, udpBeaconReceiveThread;

    private void startNsdServer() {
        nsdExecutor.execute(() -> {
            try {
                try {
                    nsdServerSocket = new ServerSocket(8988);
                } catch (Exception e) {
                    nsdServerSocket = new ServerSocket(0);
                }
                nsdServerPort = nsdServerSocket.getLocalPort();
                Log.d(TAG, "NSD Server listening on port " + nsdServerPort);

                registerNsdService();
                startUdpBeaconDiscovery();

                while (isRunning && !nsdServerSocket.isClosed()) {
                    Socket socket = nsdServerSocket.accept();
                    handleNsdSocketConnection(socket, null);
                }
            } catch (Exception e) {
                Log.d(TAG, "NSD Server stopped: " + e.getMessage());
            }
        });
    }

    private void startUdpBeaconDiscovery() {
        nsdExecutor.execute(() -> {
            try {
                if (udpDiscoverySocket == null || udpDiscoverySocket.isClosed()) {
                    udpDiscoverySocket = new DatagramSocket(null);
                    udpDiscoverySocket.setReuseAddress(true);
                    udpDiscoverySocket.setBroadcast(true);
                    try {
                        udpDiscoverySocket.bind(new InetSocketAddress(8988));
                    } catch (Exception bindEx) {
                        Log.w(TAG, "Port 8988 busy for UDP beacon, binding dynamic port: " + bindEx.getMessage());
                        udpDiscoverySocket.bind(new InetSocketAddress(0));
                    }
                }

                // 1. Receiver Thread: Fast P2P Peer IP Discovery
                udpBeaconReceiveThread = new Thread(() -> {
                    byte[] buf = new byte[512];
                    DatagramPacket packet = new DatagramPacket(buf, buf.length);
                    while (isRunning && udpDiscoverySocket != null && !udpDiscoverySocket.isClosed()) {
                        try {
                            udpDiscoverySocket.receive(packet);
                            String data = new String(packet.getData(), 0, packet.getLength(), StandardCharsets.UTF_8);
                            if (data.startsWith("NEXUS_P2P:")) {
                                String[] parts = data.split(":");
                                if (parts.length >= 3) {
                                    String peerNodeId = parts[1];
                                    String peerName = cleanPeerName(parts[2]);
                                    String senderIp = packet.getAddress().getHostAddress();

                                    // Strictly reject packets from own device
                                    if (isSelfNode(peerNodeId, peerName) || isLocalAddress(packet.getAddress())) {
                                        continue;
                                    }

                                    if (senderIp != null && !senderIp.startsWith("127.")) {
                                        peerIpAddresses.put(cleanPeerName(peerName), senderIp);
                                        peerIpAddresses.put(peerNodeId, senderIp);
                                        String epId = "NSD_" + senderIp + ":8988";
                                        if (!nsdPeerSockets.containsKey(epId)) {
                                            Log.d(TAG, "Fast UDP Beacon discovered peer " + peerName + " at " + senderIp + ". Connecting TCP socket...");
                                            connectNsdSocket(senderIp, 8988);
                                        }
                                    }
                                }
                            }
                        } catch (Exception ignored) {}
                    }
                });
                udpBeaconReceiveThread.start();

                // 2. Sender Beacon Thread: Pulse every 1.5s to all local subnets
                udpBeaconSendThread = new Thread(() -> {
                    String payloadStr = "NEXUS_P2P:" + myNodeId + ":" + myDisplayName;
                    byte[] bytes = payloadStr.getBytes(StandardCharsets.UTF_8);

                    while (isRunning && udpDiscoverySocket != null && !udpDiscoverySocket.isClosed()) {
                        try {
                            List<String> targets = getSubnetBroadcastAddresses();
                            for (String tIp : targets) {
                                try {
                                    InetAddress addr = InetAddress.getByName(tIp);
                                    DatagramPacket p = new DatagramPacket(bytes, bytes.length, addr, 8988);
                                    udpDiscoverySocket.send(p);
                                } catch (Exception ignored) {}
                            }
                            Thread.sleep(1500);
                        } catch (InterruptedException e) {
                            break;
                        } catch (Exception ignored) {}
                    }
                });
                udpBeaconSendThread.start();

            } catch (Exception e) {
                Log.d(TAG, "UDP beacon discovery notice: " + e.getMessage());
            }
        });
    }

    private void registerNsdService() {
        if (nsdManager == null) return;

        NsdServiceInfo serviceInfo = new NsdServiceInfo();
        serviceInfo.setServiceName("NexusMesh_" + myNodeId.substring(0, Math.min(8, myNodeId.length())));
        serviceInfo.setServiceType(NSD_SERVICE_TYPE);
        serviceInfo.setPort(nsdServerPort);

        nsdRegistrationListener = new NsdManager.RegistrationListener() {
            @Override
            public void onServiceRegistered(NsdServiceInfo NsdServiceInfo) {
                Log.d(TAG, "NSD Service registered: " + NsdServiceInfo.getServiceName());
            }

            @Override
            public void onRegistrationFailed(NsdServiceInfo arg0, int arg1) {
                Log.e(TAG, "NSD Registration failed: " + arg1);
            }

            @Override
            public void onServiceUnregistered(NsdServiceInfo arg0) {}

            @Override
            public void onUnregistrationFailed(NsdServiceInfo arg0, int arg1) {}
        };

        try {
            nsdManager.registerService(serviceInfo, NsdManager.PROTOCOL_DNS_SD, nsdRegistrationListener);
        } catch (Exception e) {
            Log.e(TAG, "Failed to register NSD service: " + e.getMessage());
        }
    }

    private void startNsdDiscovery() {
        if (nsdManager == null) return;

        nsdDiscoveryListener = new NsdManager.DiscoveryListener() {
            @Override
            public void onDiscoveryStarted(String regType) {
                Log.d(TAG, "NSD Discovery started");
            }

            @Override
            public void onServiceFound(NsdServiceInfo service) {
                if (service.getServiceType().equals(NSD_SERVICE_TYPE) &&
                    !service.getServiceName().contains(myNodeId.substring(0, Math.min(8, myNodeId.length())))) {
                    Log.d(TAG, "NSD Service found: " + service.getServiceName());
                    nsdManager.resolveService(service, new NsdManager.ResolveListener() {
                        @Override
                        public void onResolveFailed(NsdServiceInfo serviceInfo, int errorCode) {
                            Log.e(TAG, "NSD Resolve failed: " + errorCode);
                        }

                        @Override
                        public void onServiceResolved(NsdServiceInfo serviceInfo) {
                            Log.d(TAG, "NSD Service resolved: " + serviceInfo.getHost() + ":" + serviceInfo.getPort());
                            connectNsdSocket(serviceInfo.getHost().getHostAddress(), serviceInfo.getPort());
                        }
                    });
                }
            }

            @Override
            public void onServiceLost(NsdServiceInfo service) {}

            @Override
            public void onDiscoveryStopped(String serviceType) {}

            @Override
            public void onStartDiscoveryFailed(String serviceType, int errorCode) {}

            @Override
            public void onStopDiscoveryFailed(String serviceType, int errorCode) {}
        };

        try {
            nsdManager.discoverServices(NSD_SERVICE_TYPE, NsdManager.PROTOCOL_DNS_SD, nsdDiscoveryListener);
        } catch (Exception e) {
            Log.e(TAG, "Failed to start NSD discovery: " + e.getMessage());
        }
    }

    public void connectDirectToPeer(String hostIp, int port) {
        if (hostIp == null || hostIp.isEmpty()) return;
        connectNsdSocket(hostIp, port > 0 ? port : 8988);
    }

    private void connectNsdSocket(String hostIp, int port) {
        nsdExecutor.execute(() -> {
            try {
                InetAddress addr = InetAddress.getByName(hostIp);
                if (isLocalAddress(addr)) {
                    Log.d(TAG, "Skipping NSD socket connection to self IP: " + hostIp);
                    return;
                }

                String epId = "NSD_" + hostIp + ":" + port;
                if (nsdPeerSockets.containsKey(epId)) return;

                Socket socket = new Socket(hostIp, port);
                handleNsdSocketConnection(socket, epId);
            } catch (Exception e) {
                Log.d(TAG, "Failed to connect NSD socket to " + hostIp + ":" + port + " - " + e.getMessage());
            }
        });
    }


    private void handleNsdSocketConnection(Socket socket, String explicitEpId) {
        nsdExecutor.execute(() -> {
            String epId = explicitEpId != null ? explicitEpId : "NSD_" + socket.getInetAddress().getHostAddress() + ":" + socket.getPort();
            try {
                BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
                PrintWriter writer = new PrintWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8), true);

                nsdPeerSockets.put(epId, socket);
                nsdPeerWriters.put(epId, writer);

                // Send HELLO packet over NSD socket immediately
                sendNsdHelloPacket(writer);

                String line;
                while (isRunning && (line = reader.readLine()) != null) {
                    handleIncomingPacket(line, epId);
                }
            } catch (Exception e) {
                Log.d(TAG, "NSD Socket connection ended for " + epId);
            } finally {
                nsdPeerSockets.remove(epId);
                nsdPeerWriters.remove(epId);
                connectedPeers.remove(epId);
                mainHandler.post(() -> {
                    for (MeshEventListener l : listeners) l.onPeerDisconnected(epId);
                });
                try {
                    socket.close();
                } catch (Exception ignored) {}
            }
        });
    }

    private void sendNsdHelloPacket(PrintWriter writer) {
        try {
            SharedPreferences prefs = context.getSharedPreferences("meshlink_prefs", Context.MODE_PRIVATE);
            JSONObject obj = new JSONObject();
            obj.put("pkt_type", "HELLO");
            obj.put("node_id", myNodeId);
            obj.put("name", myDisplayName);
            obj.put("pub", cryptoManager.getMyPublicKeyBase64());
            obj.put("avatar", prefs.getString("user_emoji", ""));
            obj.put("avatar_pic", prefs.getString("user_profile_pic_base64", ""));
            obj.put("bio", prefs.getString("user_bio", "Mesh Citizen"));
            writer.println(obj.toString());
        } catch (Exception ignored) {}
    }

    private void broadcastToNsdPeers(String packetJson) {
        for (PrintWriter writer : nsdPeerWriters.values()) {
            try {
                writer.println(packetJson);
            } catch (Exception ignored) {}
        }
    }

    private void stopNsdServices() {
        try {
            if (nsdManager != null) {
                if (nsdRegistrationListener != null) nsdManager.unregisterService(nsdRegistrationListener);
                if (nsdDiscoveryListener != null) nsdManager.stopServiceDiscovery(nsdDiscoveryListener);
            }
        } catch (Exception ignored) {}

        try {
            if (nsdServerSocket != null) nsdServerSocket.close();
        } catch (Exception ignored) {}

        if (udpDiscoverySocket != null && !udpDiscoverySocket.isClosed()) {
            try { udpDiscoverySocket.close(); } catch (Exception ignored) {}
            udpDiscoverySocket = null;
        }
        if (udpBeaconSendThread != null) {
            udpBeaconSendThread.interrupt();
            udpBeaconSendThread = null;
        }
        if (udpBeaconReceiveThread != null) {
            udpBeaconReceiveThread.interrupt();
            udpBeaconReceiveThread = null;
        }

        for (Socket s : nsdPeerSockets.values()) {
            try { s.close(); } catch (Exception ignored) {}
        }
        nsdPeerSockets.clear();
        nsdPeerWriters.clear();
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       PACKET HANDLING & MESH ROUTING
       ═══════════════════════════════════════════════════════════════════════════ */

    private void handleIncomingPacket(String jsonStr, String fromEndpoint) {
        try {
            JSONObject obj = new JSONObject(jsonStr);
            String pktType = obj.optString("pkt_type", "MSG");

            if ("TOPOLOGY".equals(pktType)) {
                String nodeId = obj.optString("node_id");
                String nodeName = cleanPeerName(obj.optString("name"));
                int hopCount = obj.optInt("hop_count", 0);
                JSONArray neighborsArr = obj.optJSONArray("neighbors");

                if (nodeId != null && !nodeId.isEmpty() && !isSelfNode(nodeId, nodeName)) {
                    nodeDisplayNames.put(nodeId, nodeName);
                    nodeDisplayNames.put(nodeName, nodeName);
                    Set<String> neighborSet = ConcurrentHashMap.newKeySet();
                    if (neighborsArr != null) {
                        for (int i = 0; i < neighborsArr.length(); i++) {
                            String nb = cleanPeerName(neighborsArr.optString(i));
                            if (!nb.isEmpty()) neighborSet.add(nb);
                        }
                    }
                    topologyAdjacency.put(nodeName, neighborSet);
                    topologyAdjacency.put(nodeId, neighborSet);

                    // Multi-hop gossip relay for topology graph (up to 4 hops)
                    if (hopCount < 4) {
                        obj.put("hop_count", hopCount + 1);
                        relayPacketToPeers(obj.toString(), fromEndpoint);
                    }

                    mainHandler.post(() -> {
                        for (MeshEventListener l : listeners) l.onTopologyUpdated();
                    });
                }
                return;
            }

            if ("HELLO".equals(pktType)) {
                String peerNodeId = obj.optString("node_id");
                String peerName = cleanPeerName(obj.optString("name"));
                String peerPub = obj.optString("pub");
                String avatar = obj.optString("avatar", "");
                String avatarPic = obj.optString("avatar_pic", "");
                String bio = obj.optString("bio", "");

                // Strictly drop HELLO packet from self
                if (isSelfNode(peerNodeId, peerName)) {
                    Log.w(TAG, "Dropped HELLO packet from self: " + peerNodeId + " (" + peerName + ")");
                    if (fromEndpoint != null && fromEndpoint.startsWith("NSD_")) {
                        Socket s = nsdPeerSockets.remove(fromEndpoint);
                        nsdPeerWriters.remove(fromEndpoint);
                        if (s != null) {
                            try { s.close(); } catch (Exception ignored) {}
                        }
                    }
                    return;
                }

                connectedPeers.put(fromEndpoint, peerName);
                discoveredEndpoints.put(fromEndpoint, peerName);

                if (avatarPic != null && !avatarPic.isEmpty()) {
                    savePeerAvatar(peerName, avatarPic);
                    savePeerAvatar(peerNodeId, avatarPic);
                    if (fromEndpoint != null) {
                        savePeerAvatar(fromEndpoint, avatarPic);
                    }
                }

                if (peerPub != null && !peerPub.isEmpty()) {
                    followManager.followPeer(peerNodeId, peerName, peerPub, avatar, bio);
                    Log.d(TAG, "Registered peer key for E2EE: " + peerName + " (" + peerNodeId + ")");
                }

                // Bidirectional avatar sync: reply with our own profile update if we have a photo
                SharedPreferences myPrefs = context.getSharedPreferences("meshlink_prefs", Context.MODE_PRIVATE);
                String myPic = myPrefs.getString("user_profile_pic_base64", "");
                if (myPic != null && !myPic.isEmpty() && fromEndpoint != null) {
                    try {
                        JSONObject up = new JSONObject();
                        up.put("pkt_type", "PROFILE_UPDATE");
                        up.put("node_id", myNodeId);
                        up.put("name", myDisplayName);
                        up.put("avatar_pic", myPic);
                        byte[] b = up.toString().getBytes(StandardCharsets.UTF_8);
                        if (!fromEndpoint.startsWith("NSD_")) {
                            connectionsClient.sendPayload(fromEndpoint, Payload.fromBytes(b));
                        } else if (nsdPeerWriters.containsKey(fromEndpoint)) {
                            nsdPeerWriters.get(fromEndpoint).println(up.toString());
                        }
                    } catch (Exception ignored) {}
                }

                mainHandler.post(() -> {
                    for (MeshEventListener l : listeners) {
                        l.onPeerFound(fromEndpoint, peerName);
                        l.onPeerConnected(fromEndpoint, peerName);
                    }
                });
                return;
            }

            if ("PROFILE_UPDATE".equals(pktType)) {
                String peerName = cleanPeerName(obj.optString("name"));
                String peerNodeId = obj.optString("node_id");
                String avatarPic = obj.optString("avatar_pic");
                if (avatarPic != null && !avatarPic.isEmpty()) {
                    savePeerAvatar(peerName, avatarPic);
                    savePeerAvatar(peerNodeId, avatarPic);
                    if (fromEndpoint != null) {
                        savePeerAvatar(fromEndpoint, avatarPic);
                    }
                    mainHandler.post(() -> {
                        for (MeshEventListener l : listeners) {
                            l.onPeerFound(fromEndpoint, peerName);
                        }
                    });
                }
                return;
            }

            if ("FILE_HEADER".equals(pktType)) {
                long payloadId = obj.optLong("payload_id", -1);
                if (payloadId != -1) {
                    incomingFileHeaders.put(payloadId, obj);
                    Log.d(TAG, "Received FILE_HEADER for payload ID: " + payloadId);
                    checkAndCompleteFileTransfer(payloadId);
                }
                return;
            }

            if ("NSD_FILE_OFFER".equals(pktType)) {
                handleNsdFileOffer(obj, fromEndpoint);
                return;
            }

            if ("MSG".equals(pktType)) {
                String msgId = obj.getString("msg_id");
                if (seenMessageIds.contains(msgId) || db.messageExists(msgId)) {
                    Log.d(TAG, "Duplicate message detected (" + msgId + "), discarding automatically.");
                    return;
                }
                seenMessageIds.add(msgId);

                String sender = obj.getString("sender");
                if (isSelfNode("", sender)) return; // Strictly ignore messages from self

                String target = obj.getString("target");
                int hopCount = obj.optInt("hop_count", 0) + 1;

                boolean isForMe = isSelfNode("", target);
                boolean isBroadcast = "ALL".equalsIgnoreCase(target);

                if (isForMe || isBroadcast) {
                    String rawContent = obj.getString("content");
                    long timestamp = obj.optLong("timestamp", System.currentTimeMillis());
                    String msgType = obj.optString("msg_type", ChatMessageModel.TYPE_TEXT);
                    String mediaPath = obj.optString("media_path", "");
                    String mediaData = obj.optString("media_data", "");
                    String mediaExt = obj.optString("media_ext", ".jpg");

                    // Decode incoming Base64 media data and save locally
                    if (mediaData != null && !mediaData.isEmpty()) {
                        try {
                            byte[] fileBytes = android.util.Base64.decode(mediaData, android.util.Base64.NO_WRAP);
                            File mediaDir = new File(context.getFilesDir(), "mesh_media");
                            if (!mediaDir.exists()) mediaDir.mkdirs();
                            File outFile = new File(mediaDir, "rec_" + msgId + mediaExt);
                            java.io.FileOutputStream fos = new java.io.FileOutputStream(outFile);
                            fos.write(fileBytes);
                            fos.flush();
                            fos.close();
                            mediaPath = outFile.getAbsolutePath();
                            Log.d(TAG, "Saved received media file to: " + mediaPath + " (" + fileBytes.length + " bytes)");
                        } catch (Exception e) {
                            Log.e(TAG, "Failed to save incoming media: " + e.getMessage());
                        }
                    }

                    // Automatic E2EE Decryption if encrypted
                    String decryptedContent = rawContent;
                    if (obj.optBoolean("e2ee", false) || (rawContent != null && rawContent.contains("\"e2ee\":true"))) {
                        decryptedContent = cryptoManager.decryptFromPeer(rawContent);
                    }

                    ChatMessageModel model = new ChatMessageModel(
                            msgId, sender, target, decryptedContent, timestamp,
                            ChatMessageModel.STATUS_DELIVERED, msgType, mediaPath,
                            ChatMessageModel.ROUTE_BLE, hopCount
                    );
                    db.insertOrUpdateMessage(model);

                    // Multi-hop gossip relay for broadcast
                    if (isBroadcast && hopCount < 5) {
                        obj.put("hop_count", hopCount);
                        relayPacketToPeers(obj.toString(), fromEndpoint);
                    }

                    mainHandler.post(() -> {
                        for (MeshEventListener l : listeners) l.onMessageReceived(model);
                    });

                } else {
                    // Intermediate relay node (e.g. C or D forwarding private message from A to B):
                    // 1. DO NOT decrypt! (E2EE prevents reading anyway)
                    // 2. DO NOT save to local DB (no private message stored on intermediate phone)
                    // 3. Smart next-hop forwarding along the mesh
                    if (hopCount < 6) {
                        obj.put("hop_count", hopCount);
                        RouteInfo route = computeRouteTo(target);
                        String nextHop = (route != null && route.nextHop != null) ? route.nextHop : null;
                        String targetEp = (nextHop != null) ? getEndpointForPeer(nextHop) : null;
                        if (targetEp != null && !targetEp.equals(fromEndpoint)) {
                            Log.d(TAG, "Multi-hop Relay: Smart forwarding private msg to nextHop " + nextHop + " (ep=" + targetEp + ")");
                            byte[] bytes = obj.toString().getBytes(StandardCharsets.UTF_8);
                            if (!targetEp.startsWith("NSD_")) {
                                connectionsClient.sendPayload(targetEp, Payload.fromBytes(bytes));
                            } else if (nsdPeerWriters.containsKey(targetEp)) {
                                nsdPeerWriters.get(targetEp).println(obj.toString());
                            }
                        } else {
                            Log.d(TAG, "Multi-hop Relay: Obliviously forwarding encrypted msg from " + sender + " to " + target + " (hop: " + hopCount + ")");
                            relayPacketToPeers(obj.toString(), fromEndpoint);
                        }
                    }
                }

            } else if ("SOS".equals(pktType)) {
                String eventId = obj.getString("event_id");
                if (seenMessageIds.contains(eventId)) return;
                seenMessageIds.add(eventId);

                LocalSosModel sos = new LocalSosModel();
                sos.eventId = eventId;
                sos.originDeviceId = obj.optString("origin_dev");
                sos.userName = obj.optString("user_name");
                sos.userPhone = obj.optString("user_phone");
                sos.type = obj.optString("type", "EMERGENCY");
                sos.severity = obj.optString("severity", "CRITICAL");
                sos.description = obj.optString("description", "");
                sos.latitude = obj.optDouble("latitude", 0.0);
                sos.longitude = obj.optDouble("longitude", 0.0);
                sos.accuracy = (float) obj.optDouble("accuracy", 10.0);
                sos.status = "ACTIVE";
                sos.source = "MESH";
                sos.hopCount = obj.optInt("hop_count", 0) + 1;
                sos.createdAt = obj.optLong("created_at", System.currentTimeMillis());
                sos.synced = false;

                db.insertOrUpdateSOS(sos);

                if (sos.hopCount < 7) {
                    obj.put("hop_count", sos.hopCount);
                    relayPacketToPeers(obj.toString(), fromEndpoint);
                }

                mainHandler.post(() -> {
                    for (MeshEventListener l : listeners) l.onSosReceived(sos);
                });
            } else if ("CALL_OFFER".equals(pktType)) {
                String callId = obj.optString("call_id");
                String callerName = obj.optString("caller_name");
                String callerId = obj.optString("caller_id");
                String targetPeerId = obj.optString("target_peer_id", "");
                String targetPeerName = obj.optString("target_peer_name", "");
                String callType = obj.optString("call_type", "voice");
                String callerIp = obj.optString("caller_ip", "");
                int hopCount = obj.optInt("hop_count", 0);

                boolean isForMe = targetPeerId.isEmpty() || isSelfNode(targetPeerId, targetPeerName);

                if (isForMe) {
                    // Target node: ring and show incoming call UI
                    if (isCallActive) {
                        Log.w(TAG, "Line busy: Rejecting incoming call from " + callerName + " (" + callerId + ")");
                        sendCallReject(callerId, callId, "BUSY");
                        return;
                    }

                    JSONArray candArr = obj.optJSONArray("candidate_ips");
                    if (candArr != null) {
                        for (int i = 0; i < candArr.length(); i++) {
                            String cIp = candArr.optString(i);
                            if (!cIp.isEmpty() && !cIp.startsWith("127.")) {
                                peerIpAddresses.put(cleanPeerName(callerName), cIp);
                                peerIpAddresses.put(callerId, cIp);
                                break;
                            }
                        }
                    }
                    if (callerIp != null && !callerIp.isEmpty() && !callerIp.startsWith("127.")) {
                        peerIpAddresses.put(cleanPeerName(callerName), callerIp);
                        peerIpAddresses.put(callerId, callerIp);
                    }

                    try {
                        Intent incIntent = new Intent(context, com.example.meshlink.calls.IncomingCallActivity.class);
                        incIntent.putExtra("CALL_ID", callId);
                        incIntent.putExtra("CALLER_NAME", callerName);
                        incIntent.putExtra("CALLER_ID", callerId);
                        incIntent.putExtra("CALL_TYPE", callType);
                        incIntent.putExtra("CALLER_IP", callerIp);
                        incIntent.putExtra("HOP_COUNT", hopCount);
                        incIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
                        context.startActivity(incIntent);
                    } catch (Exception err) {
                        Log.e(TAG, "Failed to launch IncomingCallActivity: " + err.getMessage());
                    }

                    mainHandler.post(() -> {
                        for (MeshEventListener l : listeners) l.onIncomingCall(callId, callerName, callerId, callType, callerIp);
                    });
                } else {
                    // Intermediate relay node (D or C): DO NOT ring! Forward CALL_OFFER along the mesh
                    if (hopCount < 5) {
                        obj.put("hop_count", hopCount + 1);
                        Log.d(TAG, "Multi-hop Relay: Forwarding CALL_OFFER from " + callerName + " towards " + targetPeerId + " (hop: " + (hopCount + 1) + ")");
                        relayPacketToPeers(obj.toString(), fromEndpoint);
                    }
                }

            } else if ("CALL_ACCEPT".equals(pktType)) {
                String callId = obj.optString("call_id");
                String peerId = obj.optString("peer_id");
                String peerName = obj.optString("peer_name", "");
                String targetPeerId = obj.optString("target_peer_id", "");
                String targetPeerName = obj.optString("target_peer_name", "");
                String acceptorIp = obj.optString("acceptor_ip", "");
                int hopCount = obj.optInt("hop_count", 0);

                boolean isForMe = targetPeerId.isEmpty() || isSelfNode(targetPeerId, targetPeerName);

                if (isForMe) {
                    JSONArray candArr = obj.optJSONArray("candidate_ips");
                    if (candArr != null) {
                        for (int i = 0; i < candArr.length(); i++) {
                            String cIp = candArr.optString(i);
                            if (!cIp.isEmpty() && !cIp.startsWith("127.")) {
                                if (!peerName.isEmpty()) peerIpAddresses.put(cleanPeerName(peerName), cIp);
                                peerIpAddresses.put(cleanPeerName(peerId), cIp);
                                peerIpAddresses.put(peerId, cIp);
                                if (acceptorIp.isEmpty()) acceptorIp = cIp;
                                break;
                            }
                        }
                    }
                    if (acceptorIp != null && !acceptorIp.isEmpty()) {
                        if (!peerName.isEmpty()) peerIpAddresses.put(cleanPeerName(peerName), acceptorIp);
                        peerIpAddresses.put(cleanPeerName(peerId), acceptorIp);
                        peerIpAddresses.put(peerId, acceptorIp);
                    }

                    final String finalAcceptorIp = acceptorIp;
                    mainHandler.post(() -> {
                        for (MeshEventListener l : listeners) {
                            l.onCallAccepted(callId, peerId, finalAcceptorIp);
                        }
                    });
                } else {
                    // Intermediate relay: forward CALL_ACCEPT to caller
                    if (hopCount < 5) {
                        obj.put("hop_count", hopCount + 1);
                        relayPacketToPeers(obj.toString(), fromEndpoint);
                    }
                }

            } else if ("CALL_REJECT".equals(pktType)) {
                String callId = obj.optString("call_id");
                String peerId = obj.optString("peer_id");
                String targetPeerId = obj.optString("target_peer_id", "");
                String targetPeerName = obj.optString("target_peer_name", "");
                String reason = obj.optString("reason", "DECLINED");
                int hopCount = obj.optInt("hop_count", 0);

                boolean isForMe = targetPeerId.isEmpty() || isSelfNode(targetPeerId, targetPeerName);

                if (isForMe) {
                    mainHandler.post(() -> {
                        if ("BUSY".equalsIgnoreCase(reason)) {
                            android.widget.Toast.makeText(context, "Peer is busy on another call", android.widget.Toast.LENGTH_LONG).show();
                        }
                        for (MeshEventListener l : listeners) l.onCallRejected(callId, peerId);
                    });
                } else {
                    if (hopCount < 5) {
                        obj.put("hop_count", hopCount + 1);
                        relayPacketToPeers(obj.toString(), fromEndpoint);
                    }
                }

            } else if ("CALL_END".equals(pktType)) {
                String callId = obj.optString("call_id");
                String targetPeerId = obj.optString("target_peer_id", "");
                String targetPeerName = obj.optString("target_peer_name", "");
                int hopCount = obj.optInt("hop_count", 0);

                boolean isForMe = targetPeerId.isEmpty() || isSelfNode(targetPeerId, targetPeerName);

                if (isForMe) {
                    mainHandler.post(() -> {
                        for (MeshEventListener l : listeners) l.onCallEnded(callId);
                    });
                } else {
                    if (hopCount < 5) {
                        obj.put("hop_count", hopCount + 1);
                        relayPacketToPeers(obj.toString(), fromEndpoint);
                    }
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Error parsing incoming packet: " + e.getMessage());
        }
    }

    public void sendChatMessage(String target, String content, String msgType, String mediaPath) {
        String msgId = UUID.randomUUID().toString();
        seenMessageIds.add(msgId);
        long now = System.currentTimeMillis();

        ChatMessageModel msg = new ChatMessageModel(
                msgId, myDisplayName, target, content, now,
                ChatMessageModel.STATUS_SENT, msgType, mediaPath,
                ChatMessageModel.ROUTE_BLE, 0
        );
        db.insertOrUpdateMessage(msg);

        try {
            String wireContent = content;
            boolean isE2ee = false;
            if (!"ALL".equals(target)) {
                FollowManager.FollowedPeer peer = followManager.getPeer(target);
                if (peer != null && peer.publicKeyBase64 != null && !peer.publicKeyBase64.isEmpty()) {
                    wireContent = cryptoManager.encryptForPeer(peer.publicKeyBase64, content);
                    isE2ee = true;
                }
            }

            JSONObject obj = new JSONObject();
            obj.put("pkt_type", "MSG");
            obj.put("msg_id", msgId);
            obj.put("sender", myDisplayName);
            obj.put("target", target);
            obj.put("content", wireContent);
            obj.put("e2ee", isE2ee);
            obj.put("timestamp", now);
            obj.put("msg_type", msgType);
            obj.put("media_path", mediaPath);
            obj.put("hop_count", 0);

            String jsonStr = obj.toString();
            byte[] bytes = jsonStr.getBytes(StandardCharsets.UTF_8);
            Payload payload = Payload.fromBytes(bytes);

            if (!"ALL".equalsIgnoreCase(target)) {
                RouteInfo route = computeRouteTo(target);
                String nextHop = (route != null && route.nextHop != null) ? route.nextHop : target;
                String targetEp = getEndpointForPeer(nextHop);
                if (targetEp == null) {
                    targetEp = getEndpointForPeer(target);
                }

                if (targetEp != null) {
                    if (!targetEp.startsWith("NSD_")) {
                        connectionsClient.sendPayload(targetEp, payload);
                    } else if (nsdPeerWriters.containsKey(targetEp)) {
                        nsdPeerWriters.get(targetEp).println(jsonStr);
                    }
                    Log.d(TAG, "Sent MSG (" + msgId + ") via single-path nextHop: " + nextHop + " (ep=" + targetEp + ")");
                    return;
                }
            }

            for (String ep : connectedPeers.keySet()) {
                if (!ep.startsWith("NSD_")) {
                    connectionsClient.sendPayload(ep, payload);
                }
            }
            broadcastToNsdPeers(jsonStr);

        } catch (Exception e) {
            Log.e(TAG, "Failed to send message payload: " + e.getMessage());
        }
    }

    public void sendMediaMessage(String target, String caption, String msgType, String localFilePath, String base64Data) {
        if (localFilePath != null && !localFilePath.isEmpty()) {
            File f = new File(localFilePath);
            if (f.exists() && f.length() > 0) {
                sendFileMessage(target, caption, msgType, f);
                return;
            }
        }
        String msgId = UUID.randomUUID().toString();
        seenMessageIds.add(msgId);
        long now = System.currentTimeMillis();

        ChatMessageModel msg = new ChatMessageModel(
                msgId, myDisplayName, target, caption, now,
                ChatMessageModel.STATUS_SENT, msgType, localFilePath,
                ChatMessageModel.ROUTE_BLE, 0
        );
        db.insertOrUpdateMessage(msg);
    }

    public void sendFileMessage(String target, String caption, String msgType, File file) {
        if (file == null || !file.exists() || file.length() == 0) {
            Log.e(TAG, "Cannot send non-existent or empty file");
            return;
        }

        String msgId = UUID.randomUUID().toString();
        seenMessageIds.add(msgId);
        long now = System.currentTimeMillis();

        ChatMessageModel msg = new ChatMessageModel(
                msgId, myDisplayName, target, caption, now,
                ChatMessageModel.STATUS_SENT, msgType, file.getAbsolutePath(),
                ChatMessageModel.ROUTE_BLE, 0
        );
        db.insertOrUpdateMessage(msg);

        String mediaExt = ChatMessageModel.TYPE_VIDEO.equals(msgType) ? ".mp4" : ".jpg";

        try {
            Payload filePayload = Payload.fromFile(file);
            long payloadId = filePayload.getId();

            JSONObject headerObj = new JSONObject();
            headerObj.put("pkt_type", "FILE_HEADER");
            headerObj.put("payload_id", payloadId);
            headerObj.put("msg_id", msgId);
            headerObj.put("sender", myDisplayName);
            headerObj.put("target", target);
            headerObj.put("content", caption);
            headerObj.put("timestamp", now);
            headerObj.put("msg_type", msgType);
            headerObj.put("media_ext", mediaExt);
            headerObj.put("file_size", file.length());
            headerObj.put("hop_count", 0);

            byte[] headerBytes = headerObj.toString().getBytes(StandardCharsets.UTF_8);
            Payload headerPayload = Payload.fromBytes(headerBytes);

            boolean sentToNearby = false;
            for (String ep : connectedPeers.keySet()) {
                if (!ep.startsWith("NSD_")) {
                    try {
                        connectionsClient.sendPayload(ep, headerPayload);
                        connectionsClient.sendPayload(ep, filePayload);
                        sentToNearby = true;
                        Log.d(TAG, "Sent Nearby file payload (" + file.length() + " bytes) to " + ep);
                    } catch (Exception e) {
                        Log.e(TAG, "Failed sending file to Nearby ep " + ep + ": " + e.getMessage());
                    }
                }
            }

            // Also send over NSD if NSD peers connected
            sendFileOverNsd(headerObj, file);

            if (!sentToNearby) {
                Log.w(TAG, "Target not yet connected for file transfer: " + target + ". Queuing and auto-connecting...");
                pendingFileTasks.add(new PendingFileTask(headerPayload, filePayload, target));

                // Proactively trigger connection to discovered endpoints
                for (Map.Entry<String, String> entry : discoveredEndpoints.entrySet()) {
                    String epId = entry.getKey();
                    String epName = cleanPeerName(entry.getValue());
                    if ("ALL".equalsIgnoreCase(target) || epName.equalsIgnoreCase(cleanPeerName(target))) {
                        Log.d(TAG, "Fast-connecting to discovered peer for pending file: " + epId + " (" + epName + ")");
                        requestConnectionToEndpoint(epId);
                    }
                }
            }

        } catch (Exception e) {
            Log.e(TAG, "Failed preparing file payload: " + e.getMessage());
        }
    }

    private void drainPendingFilesForEndpoint(String endpointId, String peerName) {
        if (endpointId == null || endpointId.startsWith("NSD_")) return;
        synchronized (pendingFileTasks) {
            java.util.Iterator<PendingFileTask> it = pendingFileTasks.iterator();
            while (it.hasNext()) {
                PendingFileTask task = it.next();
                if ("ALL".equalsIgnoreCase(task.targetName) || cleanPeerName(task.targetName).equalsIgnoreCase(cleanPeerName(peerName))) {
                    try {
                        connectionsClient.sendPayload(endpointId, task.headerPayload);
                        connectionsClient.sendPayload(endpointId, task.filePayload);
                        Log.d(TAG, "Drained pending file payload to newly connected peer: " + peerName + " [" + endpointId + "]");
                        it.remove();
                    } catch (Exception e) {
                        Log.e(TAG, "Failed sending drained pending file to " + endpointId + ": " + e.getMessage());
                    }
                }
            }
        }
    }

    private void sendFileOverNsd(JSONObject originalHeader, File file) {
        nsdExecutor.execute(() -> {
            try {
                ServerSocket fileServer = new ServerSocket(0);
                int port = fileServer.getLocalPort();
                fileServer.setSoTimeout(90000);

                JSONObject offer = new JSONObject();
                offer.put("pkt_type", "NSD_FILE_OFFER");
                offer.put("msg_id", originalHeader.getString("msg_id"));
                offer.put("sender", myDisplayName);
                offer.put("sender_ip", getLocalIpAddress());
                offer.put("sender_ips", new JSONArray(getLocalIpCandidates()));
                offer.put("target", originalHeader.optString("target", "ALL"));
                offer.put("content", originalHeader.optString("content", ""));
                offer.put("msg_type", originalHeader.optString("msg_type", ChatMessageModel.TYPE_VIDEO));
                offer.put("media_ext", originalHeader.optString("media_ext", ".mp4"));
                offer.put("file_size", file.length());
                offer.put("nsd_port", port);

                String offerJson = offer.toString();
                byte[] offerBytes = offerJson.getBytes(StandardCharsets.UTF_8);
                Payload offerPayload = Payload.fromBytes(offerBytes);
                for (String ep : connectedPeers.keySet()) {
                    if (!ep.startsWith("NSD_")) {
                        try {
                            connectionsClient.sendPayload(ep, offerPayload);
                        } catch (Exception ignored) {}
                    }
                }
                broadcastToNsdPeers(offerJson);

                Socket clientSocket = fileServer.accept();
                clientSocket.setSendBufferSize(256 * 1024);
                clientSocket.setTcpNoDelay(true);
                try (BufferedInputStream fis = new BufferedInputStream(new FileInputStream(file), 65536);
                     BufferedOutputStream os = new BufferedOutputStream(clientSocket.getOutputStream(), 65536)) {
                    byte[] buf = new byte[65536];
                    int len;
                    while ((len = fis.read(buf)) != -1) {
                        os.write(buf, 0, len);
                    }
                    os.flush();
                }
                clientSocket.close();
                fileServer.close();
                Log.d(TAG, "Direct high-speed file transfer completed successfully for " + file.getName());
            } catch (Exception e) {
                Log.d(TAG, "Direct file send notice: " + e.getMessage());
            }
        });
    }

    private void handleNsdFileOffer(JSONObject offer, String fromEndpoint) {
        nsdExecutor.execute(() -> {
            try {
                String sender = offer.getString("sender");
                if (isSelfNode("", sender)) return;

                String msgId = offer.getString("msg_id");
                if (seenMessageIds.contains(msgId)) return;

                int port = offer.getInt("nsd_port");
                List<String> candidateIps = new ArrayList<>();
                String mainIp = offer.optString("sender_ip", "");
                if (!mainIp.isEmpty()) candidateIps.add(mainIp);
                JSONArray candArr = offer.optJSONArray("sender_ips");
                if (candArr != null) {
                    for (int i = 0; i < candArr.length(); i++) {
                        String cIp = candArr.optString(i);
                        if (!cIp.isEmpty() && !candidateIps.contains(cIp)) {
                            candidateIps.add(cIp);
                        }
                    }
                }
                String peerIp = getPeerIp(sender);
                if (peerIp != null && !peerIp.isEmpty() && !candidateIps.contains(peerIp)) {
                    candidateIps.add(peerIp);
                }
                if (fromEndpoint != null && fromEndpoint.startsWith("NSD_")) {
                    String clean = fromEndpoint.substring(4);
                    int colon = clean.indexOf(':');
                    String epIp = colon != -1 ? clean.substring(0, colon) : clean;
                    if (!candidateIps.contains(epIp)) candidateIps.add(epIp);
                }

                if (candidateIps.isEmpty()) return;

                Log.d(TAG, "Attempting high-speed direct file connection to " + sender + " candidates: " + candidateIps);
                Socket socket = null;
                for (String targetIp : candidateIps) {
                    if (targetIp.startsWith("127.")) continue;
                    try {
                        Socket s = new Socket();
                        s.connect(new InetSocketAddress(targetIp, port), 2500);
                        s.setSoTimeout(60000);
                        s.setReceiveBufferSize(256 * 1024);
                        s.setTcpNoDelay(true);
                        socket = s;
                        peerIpAddresses.put(cleanPeerName(sender), targetIp);
                        peerIpAddresses.put(sender, targetIp);
                        Log.d(TAG, "Connected high-speed file socket to: " + targetIp + ":" + port);
                        break;
                    } catch (Exception ignored) {}
                }

                if (socket == null) {
                    Log.w(TAG, "Could not connect to any candidate IP for direct file transfer. Nearby stream will handle.");
                    return;
                }

                String msgType = offer.optString("msg_type", ChatMessageModel.TYPE_VIDEO);
                String mediaExt = offer.optString("media_ext", ".mp4");
                String content = offer.optString("content", "");
                String target = offer.optString("target", "ALL");

                File mediaDir = new File(context.getFilesDir(), "mesh_media");
                if (!mediaDir.exists()) mediaDir.mkdirs();
                File destFile = new File(mediaDir, "rec_" + msgId + mediaExt);

                try (BufferedInputStream is = new BufferedInputStream(socket.getInputStream(), 65536);
                     BufferedOutputStream fos = new BufferedOutputStream(new FileOutputStream(destFile), 65536)) {
                    byte[] buf = new byte[65536];
                    int len;
                    while ((len = is.read(buf)) != -1) {
                        fos.write(buf, 0, len);
                    }
                    fos.flush();
                }
                socket.close();

                if (destFile.length() == 0) {
                    Log.w(TAG, "NSD file transfer resulted in empty file");
                    return;
                }

                seenMessageIds.add(msgId);
                ChatMessageModel model = new ChatMessageModel(
                        msgId, sender, target, content, System.currentTimeMillis(),
                        ChatMessageModel.STATUS_DELIVERED, msgType, destFile.getAbsolutePath(),
                        ChatMessageModel.ROUTE_BLE, 0
                );
                db.insertOrUpdateMessage(model);

                mainHandler.post(() -> {
                    for (MeshEventListener l : listeners) {
                        l.onMessageReceived(model);
                    }
                });
                Log.d(TAG, "NSD file received and saved: " + destFile.getAbsolutePath() + " (" + destFile.length() + " bytes)");
            } catch (Exception e) {
                Log.e(TAG, "Failed receiving NSD file offer: " + e.getMessage());
            }
        });
    }

    private synchronized void checkAndCompleteFileTransfer(long payloadId) {
        JSONObject header = incomingFileHeaders.get(payloadId);
        Payload payload = incomingFilePayloads.get(payloadId);
        if (header == null || payload == null) return;
        if (!completedFilePayloadIds.contains(payloadId)) {
            Log.d(TAG, "Payload " + payloadId + " still transferring, waiting for completion");
            return;
        }

        try {
            Payload.File payloadFile = payload.asFile();
            if (payloadFile == null) return;

            String msgId = header.getString("msg_id");
            if (seenMessageIds.contains(msgId)) {
                incomingFileHeaders.remove(payloadId);
                incomingFilePayloads.remove(payloadId);
                completedFilePayloadIds.remove(payloadId);
                return;
            }

            String sender = header.getString("sender");
            if (isSelfNode("", sender)) {
                incomingFileHeaders.remove(payloadId);
                incomingFilePayloads.remove(payloadId);
                completedFilePayloadIds.remove(payloadId);
                return;
            }

            String target = header.optString("target", "ALL");
            String content = header.optString("content", "");
            String msgType = header.optString("msg_type", ChatMessageModel.TYPE_VIDEO);
            String mediaExt = header.optString("media_ext", ".mp4");
            long timestamp = header.optLong("timestamp", System.currentTimeMillis());

            File mediaDir = new File(context.getFilesDir(), "mesh_media");
            if (!mediaDir.exists()) mediaDir.mkdirs();
            File destFile = new File(mediaDir, "rec_" + msgId + mediaExt);

            boolean copied = false;

            // 1. Try reading via ParcelFileDescriptor (Primary for Google Nearby on Scoped Storage)
            try {
                ParcelFileDescriptor pfd = payloadFile.asParcelFileDescriptor();
                if (pfd != null) {
                    try (FileInputStream fis = new FileInputStream(pfd.getFileDescriptor());
                         FileOutputStream fos = new FileOutputStream(destFile)) {
                        byte[] buf = new byte[32768];
                        int len;
                        while ((len = fis.read(buf)) != -1) {
                            fos.write(buf, 0, len);
                        }
                        fos.flush();
                        copied = destFile.length() > 0;
                    }
                }
            } catch (Exception e) {
                Log.w(TAG, "Could not copy via ParcelFileDescriptor: " + e.getMessage());
            }

            // 2. Try reading via asUri() if ParcelFileDescriptor wasn't available or empty
            if (!copied) {
                try {
                    android.net.Uri uri = payloadFile.asUri();
                    if (uri != null) {
                        try (InputStream is = context.getContentResolver().openInputStream(uri);
                             FileOutputStream fos = new FileOutputStream(destFile)) {
                            if (is != null) {
                                byte[] buf = new byte[32768];
                                int len;
                                while ((len = is.read(buf)) != -1) {
                                    fos.write(buf, 0, len);
                                }
                                fos.flush();
                                copied = destFile.length() > 0;
                            }
                        }
                    }
                } catch (Throwable t) {
                    Log.w(TAG, "Could not copy via asUri: " + t.getMessage());
                }
            }

            // 3. Try reading via asJavaFile() if available
            if (!copied) {
                try {
                    File sourceFile = payloadFile.asJavaFile();
                    if (sourceFile != null && sourceFile.exists()) {
                        copyFile(sourceFile, destFile);
                        copied = destFile.length() > 0;
                    }
                } catch (Exception e) {
                    Log.w(TAG, "Could not copy via asJavaFile: " + e.getMessage());
                }
            }

            if (!copied || destFile.length() == 0) {
                Log.e(TAG, "Failed to copy payload " + payloadId + " from any source");
                return;
            }

            seenMessageIds.add(msgId);
            incomingFileHeaders.remove(payloadId);
            incomingFilePayloads.remove(payloadId);
            completedFilePayloadIds.remove(payloadId);

            ChatMessageModel model = new ChatMessageModel(
                    msgId, sender, target, content, timestamp,
                    ChatMessageModel.STATUS_DELIVERED, msgType, destFile.getAbsolutePath(),
                    ChatMessageModel.ROUTE_BLE, 0
            );
            db.insertOrUpdateMessage(model);

            mainHandler.post(() -> {
                for (MeshEventListener l : listeners) {
                    l.onMessageReceived(model);
                }
            });
            Log.d(TAG, "Successfully completed file transfer (" + msgType + ") to " + destFile.getAbsolutePath() + " (" + destFile.length() + " bytes)");
        } catch (Exception e) {
            Log.e(TAG, "Failed completing file transfer: " + e.getMessage());
        }
    }

    private void copyFile(File src, File dst) throws Exception {
        try (FileInputStream in = new FileInputStream(src);
             FileOutputStream out = new FileOutputStream(dst)) {
            byte[] buf = new byte[32768];
            int len;
            while ((len = in.read(buf)) != -1) {
                out.write(buf, 0, len);
            }
            out.flush();
        }
    }

    public void broadcastSOS(double lat, double lng, float accuracy, String description) {
        String eventId = "SOS_" + System.currentTimeMillis();
        seenMessageIds.add(eventId);

        LocalSosModel sos = new LocalSosModel();
        sos.eventId = eventId;
        sos.originDeviceId = myNodeId;
        sos.userName = myDisplayName;
        sos.type = "EMERGENCY";
        sos.severity = "CRITICAL";
        sos.description = description;
        sos.latitude = lat;
        sos.longitude = lng;
        sos.accuracy = accuracy;
        sos.status = "ACTIVE";
        sos.source = "LOCAL";
        sos.hopCount = 0;
        sos.createdAt = System.currentTimeMillis();
        sos.synced = false;

        db.insertOrUpdateSOS(sos);

        try {
            JSONObject obj = new JSONObject();
            obj.put("pkt_type", "SOS");
            obj.put("event_id", eventId);
            obj.put("origin_dev", myNodeId);
            obj.put("user_name", myDisplayName);
            obj.put("type", "EMERGENCY");
            obj.put("severity", "CRITICAL");
            obj.put("description", description);
            obj.put("latitude", lat);
            obj.put("longitude", lng);
            obj.put("accuracy", accuracy);
            obj.put("created_at", sos.createdAt);
            obj.put("hop_count", 0);

            String jsonStr = obj.toString();
            byte[] bytes = jsonStr.getBytes(StandardCharsets.UTF_8);
            Payload payload = Payload.fromBytes(bytes);

            for (String ep : connectedPeers.keySet()) {
                if (!ep.startsWith("NSD_")) {
                    connectionsClient.sendPayload(ep, payload);
                }
            }
            broadcastToNsdPeers(jsonStr);

        } catch (Exception e) {
            Log.e(TAG, "Failed to broadcast SOS: " + e.getMessage());
        }
    }

    private void relayPacketToPeers(String packetJson, String excludeEndpoint) {
        byte[] bytes = packetJson.getBytes(StandardCharsets.UTF_8);
        Payload payload = Payload.fromBytes(bytes);

        for (String ep : connectedPeers.keySet()) {
            if (!ep.equals(excludeEndpoint)) {
                if (!ep.startsWith("NSD_")) {
                    connectionsClient.sendPayload(ep, payload);
                }
            }
        }
        broadcastToNsdPeers(packetJson);
    }

    private void sendHelloPacket(String endpointId) {
        try {
            SharedPreferences prefs = context.getSharedPreferences("meshlink_prefs", Context.MODE_PRIVATE);
            JSONObject obj = new JSONObject();
            obj.put("pkt_type", "HELLO");
            obj.put("node_id", myNodeId);
            obj.put("name", myDisplayName);
            obj.put("pub", cryptoManager.getMyPublicKeyBase64());
            obj.put("avatar", prefs.getString("user_emoji", ""));
            obj.put("avatar_pic", prefs.getString("user_profile_pic_base64", ""));
            obj.put("bio", prefs.getString("user_bio", "Mesh Citizen"));

            byte[] bytes = obj.toString().getBytes(StandardCharsets.UTF_8);
            connectionsClient.sendPayload(endpointId, Payload.fromBytes(bytes));
            Log.d(TAG, "Sent HELLO handshake packet to " + endpointId);
        } catch (Exception e) {
            Log.e(TAG, "Failed to send HELLO packet: " + e.getMessage());
        }
    }

    private final Map<String, String> peerAvatars = new ConcurrentHashMap<>();

    public void reloadProfile() {
        SharedPreferences prefs = context.getSharedPreferences("meshlink_prefs", Context.MODE_PRIVATE);
        this.myDisplayName = prefs.getString("user_name", "Anonymous");
        String myPic = prefs.getString("user_profile_pic_base64", "");
        if (myPic != null && !myPic.isEmpty()) {
            savePeerAvatar(myDisplayName, myPic);
            savePeerAvatar(myNodeId, myPic);
        }
    }

    public void savePeerAvatar(String peerKey, String avatarBase64) {
        if (peerKey == null || peerKey.trim().isEmpty() || avatarBase64 == null || avatarBase64.isEmpty()) return;
        String trimmed = peerKey.trim();
        String clean = cleanPeerName(trimmed);
        String lower = trimmed.toLowerCase(java.util.Locale.ROOT);
        String cleanLower = clean.toLowerCase(java.util.Locale.ROOT);

        peerAvatars.put(trimmed, avatarBase64);
        peerAvatars.put(clean, avatarBase64);
        peerAvatars.put(lower, avatarBase64);
        peerAvatars.put(cleanLower, avatarBase64);

        SharedPreferences prefs = context.getSharedPreferences("meshlink_avatars", Context.MODE_PRIVATE);
        prefs.edit()
                .putString(trimmed, avatarBase64)
                .putString(clean, avatarBase64)
                .putString(lower, avatarBase64)
                .putString(cleanLower, avatarBase64)
                .apply();
    }

    public String getPeerAvatarBase64(String peerKey) {
        if (peerKey == null || peerKey.trim().isEmpty()) return null;
        String trimmed = peerKey.trim();
        String clean = cleanPeerName(trimmed);
        String lower = trimmed.toLowerCase(java.util.Locale.ROOT);
        String cleanLower = clean.toLowerCase(java.util.Locale.ROOT);

        if (peerAvatars.containsKey(trimmed)) return peerAvatars.get(trimmed);
        if (peerAvatars.containsKey(clean)) return peerAvatars.get(clean);
        if (peerAvatars.containsKey(lower)) return peerAvatars.get(lower);
        if (peerAvatars.containsKey(cleanLower)) return peerAvatars.get(cleanLower);

        SharedPreferences prefs = context.getSharedPreferences("meshlink_avatars", Context.MODE_PRIVATE);
        String saved = prefs.getString(trimmed, null);
        if (saved == null) saved = prefs.getString(clean, null);
        if (saved == null) saved = prefs.getString(lower, null);
        if (saved == null) saved = prefs.getString(cleanLower, null);

        if (saved != null) {
            peerAvatars.put(trimmed, saved);
            peerAvatars.put(clean, saved);
            return saved;
        }

        // Fallback for self
        if (clean.equalsIgnoreCase(cleanPeerName(myDisplayName)) || trimmed.equalsIgnoreCase(myNodeId)) {
            SharedPreferences myPrefs = context.getSharedPreferences("meshlink_prefs", Context.MODE_PRIVATE);
            String myPic = myPrefs.getString("user_profile_pic_base64", "");
            if (!myPic.isEmpty()) return myPic;
        }

        return null;
    }

    public android.graphics.Bitmap getPeerAvatarBitmap(String peerKey) {
        String b64 = getPeerAvatarBase64(peerKey);
        if (b64 != null && !b64.isEmpty()) {
            return com.example.meshlink.data.ImageUtils.base64ToBitmap(b64);
        }
        return null;
    }

    public void broadcastAvatarUpdate(String avatarBase64) {
        if (avatarBase64 == null) avatarBase64 = "";
        SharedPreferences prefs = context.getSharedPreferences("meshlink_prefs", Context.MODE_PRIVATE);
        prefs.edit().putString("user_profile_pic_base64", avatarBase64).apply();

        if (!avatarBase64.isEmpty()) {
            savePeerAvatar(myDisplayName, avatarBase64);
            savePeerAvatar(myNodeId, avatarBase64);
        }

        try {
            JSONObject obj = new JSONObject();
            obj.put("pkt_type", "PROFILE_UPDATE");
            obj.put("node_id", myNodeId);
            obj.put("name", myDisplayName);
            obj.put("avatar_pic", avatarBase64);

            byte[] bytes = obj.toString().getBytes(StandardCharsets.UTF_8);
            Payload payload = Payload.fromBytes(bytes);

            for (String endpointId : connectedPeers.keySet()) {
                if (!endpointId.startsWith("NSD_")) {
                    try {
                        connectionsClient.sendPayload(endpointId, payload);
                    } catch (Exception ignored) {}
                }
            }
            broadcastToNsdPeers(obj.toString());
        } catch (Exception ignored) {}
    }

    public Map<String, String> getConnectedPeers() {
        return new HashMap<>(connectedPeers);
    }

    public int getConnectedPeerCount() {
        Set<String> uniquePeers = new HashSet<>(connectedPeers.values());
        return uniquePeers.size();
    }

    public String getPeerIp(String peer) {
        if (peer == null || peer.isEmpty()) return null;
        String clean = cleanPeerName(peer);
        if (peerIpAddresses.containsKey(clean)) return peerIpAddresses.get(clean);
        if (peerIpAddresses.containsKey(peer)) return peerIpAddresses.get(peer);
        for (Socket s : nsdPeerSockets.values()) {
            if (s != null && s.getInetAddress() != null && !isLocalAddress(s.getInetAddress())) {
                return s.getInetAddress().getHostAddress();
            }
        }
        return null;
    }

    public String getMyDisplayName() {
        return myDisplayName;
    }

    public String getMyNodeId() {
        return myNodeId;
    }

    public static List<String> getLocalIpCandidates() {
        List<String> wifiIps = new ArrayList<>();
        List<String> hotspotIps = new ArrayList<>();
        List<String> directIps = new ArrayList<>();
        List<String> otherIps = new ArrayList<>();

        try {
            List<NetworkInterface> interfaces = Collections.list(NetworkInterface.getNetworkInterfaces());
            for (NetworkInterface intf : interfaces) {
                if (!intf.isUp() || intf.isLoopback()) continue;
                String name = intf.getName().toLowerCase();
                for (InetAddress addr : Collections.list(intf.getInetAddresses())) {
                    if (addr instanceof Inet4Address && !addr.isLoopbackAddress()) {
                        String ip = addr.getHostAddress();
                        if (ip == null || ip.startsWith("127.")) continue;
                        if (name.contains("wlan") && !name.contains("p2p") && !name.contains("swlan") && !name.contains("ap")) {
                            if (!wifiIps.contains(ip)) wifiIps.add(ip);
                        } else if (name.contains("ap") || name.contains("swlan") || name.contains("softap")) {
                            if (!hotspotIps.contains(ip)) hotspotIps.add(ip);
                        } else if (name.contains("p2p")) {
                            if (!directIps.contains(ip)) directIps.add(ip);
                        } else if (!name.contains("usb") && !name.contains("rndis") && !name.contains("dummy")) {
                            if (!otherIps.contains(ip)) otherIps.add(ip);
                        }
                    }
                }
            }
        } catch (Exception ignored) {}

        List<String> all = new ArrayList<>();
        all.addAll(wifiIps);
        all.addAll(hotspotIps);
        all.addAll(directIps);
        all.addAll(otherIps);
        if (all.isEmpty()) {
            all.add("192.168.49.1");
        }
        return all;
    }

    public static List<String> getSubnetBroadcastAddresses() {
        List<String> list = new ArrayList<>();
        list.add("255.255.255.255");
        list.add("192.168.49.255");
        list.add("192.168.43.255");
        list.add("192.168.1.255");
        list.add("192.168.0.255");
        list.add("192.168.29.255");
        list.add("192.168.31.255");
        list.add("192.168.137.255");

        try {
            List<NetworkInterface> interfaces = Collections.list(NetworkInterface.getNetworkInterfaces());
            for (NetworkInterface intf : interfaces) {
                if (!intf.isUp() || intf.isLoopback()) continue;
                for (InterfaceAddress addr : intf.getInterfaceAddresses()) {
                    InetAddress bcast = addr.getBroadcast();
                    if (bcast != null && bcast.getHostAddress() != null) {
                        String bIp = bcast.getHostAddress();
                        if (!list.contains(bIp)) list.add(bIp);
                    }
                }
            }
        } catch (Exception ignored) {}
        return list;
    }

    public static String getLocalIpAddress() {
        List<String> cands = getLocalIpCandidates();
        return cands.isEmpty() ? "192.168.49.1" : cands.get(0);
    }

    public static boolean isLocalAddress(InetAddress addr) {
        if (addr == null || addr.isLoopbackAddress()) return true;
        try {
            if (NetworkInterface.getByInetAddress(addr) != null) return true;
            List<NetworkInterface> interfaces = Collections.list(NetworkInterface.getNetworkInterfaces());
            for (NetworkInterface intf : interfaces) {
                for (InetAddress a : Collections.list(intf.getInetAddresses())) {
                    if (a.getHostAddress() != null && a.getHostAddress().equals(addr.getHostAddress())) {
                        return true;
                    }
                }
            }
        } catch (Exception ignored) {}
        return false;
    }

    public boolean isSelfNode(String peerId, String peerName) {
        String cleanMine = cleanPeerName(myDisplayName);
        if (peerId != null && !peerId.isEmpty()) {
            String cleanP = cleanPeerName(peerId);
            if (cleanP.equalsIgnoreCase(cleanMine)) return true;
            if (myNodeId != null && (peerId.equals(myNodeId) || cleanP.equalsIgnoreCase(myNodeId))) return true;
        }
        if (peerName != null && !peerName.isEmpty()) {
            String cleanP = cleanPeerName(peerName);
            if (cleanP.equalsIgnoreCase(cleanMine)) return true;
            if (myNodeId != null && (peerName.equals(myNodeId) || cleanP.equalsIgnoreCase(myNodeId))) return true;
        }
        return false;
    }

    public void sendCallOffer(String targetPeerId, String callId, String callType, String localIp) {
        try {
            JSONObject obj = new JSONObject();
            obj.put("pkt_type", "CALL_OFFER");
            obj.put("call_id", callId);
            obj.put("caller_name", myDisplayName);
            obj.put("caller_id", myNodeId);
            obj.put("target_peer_id", targetPeerId);
            obj.put("target_peer_name", cleanPeerName(targetPeerId));
            obj.put("call_type", callType);
            obj.put("caller_ip", (localIp != null && !localIp.isEmpty()) ? localIp : getLocalIpAddress());
            obj.put("candidate_ips", new JSONArray(getLocalIpCandidates()));
            obj.put("hop_count", 0);
            String jsonStr = obj.toString();
            byte[] bytes = jsonStr.getBytes(StandardCharsets.UTF_8);
            Payload payload = Payload.fromBytes(bytes);
            for (String ep : connectedPeers.keySet()) {
                if (!ep.startsWith("NSD_")) {
                    connectionsClient.sendPayload(ep, payload);
                }
            }
            broadcastToNsdPeers(jsonStr);
            Log.d(TAG, "Sent CALL_OFFER: " + callId + " (" + callType + ") towards " + targetPeerId);
        } catch (Exception e) {
            Log.e(TAG, "Failed to send call offer: " + e.getMessage());
        }
    }

    public void sendCallAccept(String targetPeerId, String callId, String localIp) {
        try {
            JSONObject obj = new JSONObject();
            obj.put("pkt_type", "CALL_ACCEPT");
            obj.put("call_id", callId);
            obj.put("peer_id", myNodeId);
            obj.put("peer_name", myDisplayName);
            obj.put("target_peer_id", targetPeerId);
            obj.put("target_peer_name", cleanPeerName(targetPeerId));
            obj.put("acceptor_ip", (localIp != null && !localIp.isEmpty()) ? localIp : getLocalIpAddress());
            obj.put("candidate_ips", new JSONArray(getLocalIpCandidates()));
            obj.put("hop_count", 0);
            String jsonStr = obj.toString();
            byte[] bytes = jsonStr.getBytes(StandardCharsets.UTF_8);
            Payload payload = Payload.fromBytes(bytes);
            for (String ep : connectedPeers.keySet()) {
                if (!ep.startsWith("NSD_")) {
                    connectionsClient.sendPayload(ep, payload);
                }
            }
            broadcastToNsdPeers(jsonStr);
            Log.d(TAG, "Sent CALL_ACCEPT: " + callId + " towards " + targetPeerId);
        } catch (Exception e) {
            Log.e(TAG, "Failed to send call accept: " + e.getMessage());
        }
    }

    public void sendCallAccept(String targetPeerId, String callId) {
        sendCallAccept(targetPeerId, callId, getLocalIpAddress());
    }

    public void sendCallReject(String targetPeerId, String callId) {
        sendCallReject(targetPeerId, callId, "DECLINED");
    }

    public void sendCallReject(String targetPeerId, String callId, String reason) {
        try {
            JSONObject obj = new JSONObject();
            obj.put("pkt_type", "CALL_REJECT");
            obj.put("call_id", callId);
            obj.put("peer_id", myNodeId);
            obj.put("peer_name", myDisplayName);
            obj.put("target_peer_id", targetPeerId);
            obj.put("target_peer_name", cleanPeerName(targetPeerId));
            obj.put("reason", reason != null ? reason : "DECLINED");
            obj.put("hop_count", 0);
            String jsonStr = obj.toString();
            byte[] bytes = jsonStr.getBytes(StandardCharsets.UTF_8);
            Payload payload = Payload.fromBytes(bytes);
            for (String ep : connectedPeers.keySet()) {
                if (!ep.startsWith("NSD_")) {
                    connectionsClient.sendPayload(ep, payload);
                }
            }
            broadcastToNsdPeers(jsonStr);
            Log.d(TAG, "Sent CALL_REJECT: " + callId + " (reason=" + reason + ")");
        } catch (Exception e) {
            Log.e(TAG, "Failed to send call reject: " + e.getMessage());
        }
    }

    public void sendCallEnd(String targetPeerId, String callId) {
        try {
            JSONObject obj = new JSONObject();
            obj.put("pkt_type", "CALL_END");
            obj.put("call_id", callId);
            obj.put("peer_id", myNodeId);
            obj.put("peer_name", myDisplayName);
            obj.put("target_peer_id", targetPeerId);
            obj.put("target_peer_name", cleanPeerName(targetPeerId));
            obj.put("hop_count", 0);
            String jsonStr = obj.toString();
            byte[] bytes = jsonStr.getBytes(StandardCharsets.UTF_8);
            Payload payload = Payload.fromBytes(bytes);
            for (String ep : connectedPeers.keySet()) {
                if (!ep.startsWith("NSD_")) {
                    connectionsClient.sendPayload(ep, payload);
                }
            }
            broadcastToNsdPeers(jsonStr);
            Log.d(TAG, "Sent CALL_END: " + callId);
        } catch (Exception e) {
            Log.e(TAG, "Failed to send call end: " + e.getMessage());
        }
    }
}
