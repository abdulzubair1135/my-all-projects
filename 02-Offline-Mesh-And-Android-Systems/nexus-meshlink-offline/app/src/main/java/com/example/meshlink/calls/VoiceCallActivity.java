package com.example.meshlink.calls;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.AudioAttributes;
import android.media.AudioDeviceInfo;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.MediaRecorder;
import android.media.ToneGenerator;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.example.meshlink.R;
import com.example.meshlink.data.ChatMessageModel;
import com.example.meshlink.data.LocalSosModel;
import com.example.meshlink.mesh.MeshCoordinator;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.UUID;

public class VoiceCallActivity extends AppCompatActivity implements MeshCoordinator.MeshEventListener {

    private static final String TAG = "VoiceCallActivity";
    private static final int AUDIO_PORT = 50005;
    private static final int SAMPLE_RATE = 16000;
    private static final int CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO;
    private static final int AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT;
    private static final int AUDIO_FRAME_SIZE = 640; // 20ms frames @ 16kHz 16-bit mono

    private String peerName;
    private String peerId;
    private String callId;
    private volatile String peerIp = null;
    private boolean isIncoming = false;
    private volatile boolean isCallConnected = false;

    private TextView tvCallPeerName, tvCallAvatarLetter, tvCallTimer;
    private android.widget.ImageView ivCallAvatarPic;
    private TextView tvVoiceBitrate, tvVoicePing, tvVoicePackets;
    private boolean isMuted = false;
    private boolean isSpeaker = false; // Default: direct earpiece / ear pods like a real phone call!
    private android.os.PowerManager.WakeLock proximityWakeLock;

    private int hopCount = 1;
    private int secondsElapsed = 0;

    // Telemetry stats
    private final java.util.concurrent.atomic.AtomicLong bytesSentWindow = new java.util.concurrent.atomic.AtomicLong(0);
    private final java.util.concurrent.atomic.AtomicLong bytesRecvWindow = new java.util.concurrent.atomic.AtomicLong(0);
    private final java.util.concurrent.atomic.AtomicInteger pktsSentWindow = new java.util.concurrent.atomic.AtomicInteger(0);
    private final java.util.concurrent.atomic.AtomicInteger pktsRecvWindow = new java.util.concurrent.atomic.AtomicInteger(0);
    private volatile long currentRttMs = 0;

    private final Handler timerHandler = new Handler(Looper.getMainLooper());
    private final Runnable timerRunnable = new Runnable() {
        @Override
        public void run() {
            if (isCallConnected) {
                secondsElapsed++;
                int mins = secondsElapsed / 60;
                int secs = secondsElapsed % 60;
                String hopTag = hopCount > 1 ? " • Mesh (" + hopCount + " Hops)" : "";
                tvCallTimer.setText(String.format("Connected • %02d:%02d%s", mins, secs, hopTag));

                long sBytes = bytesSentWindow.getAndSet(0);
                long rBytes = bytesRecvWindow.getAndSet(0);
                int sPkts = pktsSentWindow.getAndSet(0);
                int rPkts = pktsRecvWindow.getAndSet(0);

                double totalKbPerSec = (sBytes + rBytes) / 1024.0;
                int totalPktsPerSec = sPkts + rPkts;

                if (tvVoiceBitrate != null) {
                    tvVoiceBitrate.setText(String.format(java.util.Locale.US, "⚡ %.1f KB/s", totalKbPerSec));
                }
                if (tvVoicePackets != null) {
                    tvVoicePackets.setText("📦 " + totalPktsPerSec + " pkt/s");
                }
                if (tvVoicePing != null) {
                    long latency = currentRttMs > 0 ? currentRttMs : (hopCount * 12L);
                    tvVoicePing.setText("📶 " + latency + " ms");
                }

                timerHandler.postDelayed(this, 1000);
            }
        }
    };

    private AudioRecord audioRecord;
    private AudioTrack audioTrack;
    private DatagramSocket socket;
    private Thread recordThread;
    private Thread playThread;
    private Thread beaconThread;

    private ToneGenerator ringbackToneGen;
    private final Handler ringbackHandler = new Handler(Looper.getMainLooper());
    private final Runnable ringbackRunnable = new Runnable() {
        @Override
        public void run() {
            if (!isCallConnected && !isFinishing()) {
                try {
                    if (ringbackToneGen == null) {
                        ringbackToneGen = new ToneGenerator(AudioManager.STREAM_VOICE_CALL, 70);
                    }
                    ringbackToneGen.startTone(ToneGenerator.TONE_SUP_RINGTONE, 1000);
                } catch (Exception ignored) {}
                ringbackHandler.postDelayed(this, 3000);
            }
        }
    };

    private MeshCoordinator meshCoordinator;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_voice_call);

        meshCoordinator = MeshCoordinator.getInstance(this);

        peerName = getIntent().getStringExtra("PEER_NAME");
        if (peerName == null) peerName = "Peer";
        peerId = getIntent().getStringExtra("PEER_ID");
        if (peerId == null) peerId = peerName;
        callId = getIntent().getStringExtra("CALL_ID");
        if (callId == null) callId = UUID.randomUUID().toString();

        isIncoming = getIntent().getBooleanExtra("IS_INCOMING", false);
        String callState = getIntent().getStringExtra("CALL_STATE");
        if ("CONNECTED".equalsIgnoreCase(callState)) {
            isCallConnected = true;
        }

        if (getIntent().hasExtra("PEER_IP") && getIntent().getStringExtra("PEER_IP") != null) {
            String passed = getIntent().getStringExtra("PEER_IP");
            try {
                if (!MeshCoordinator.isLocalAddress(InetAddress.getByName(passed))) {
                    peerIp = passed;
                } else {
                    peerIp = meshCoordinator.getPeerIp(peerId);
                }
            } catch (Exception e) {
                peerIp = meshCoordinator.getPeerIp(peerId);
            }
        } else {
            peerIp = meshCoordinator.getPeerIp(peerId);
        }

        hopCount = getIntent().getIntExtra("HOP_COUNT", 0);
        if (hopCount <= 0 && meshCoordinator != null) {
            MeshCoordinator.RouteInfo r = meshCoordinator.computeRouteTo(peerId);
            if (r != null) hopCount = r.hopCount;
            else hopCount = 1;
        }

        initViews();
        checkAndRequestAudioPermission();
        initAudioRouting();

        meshCoordinator.setCallActive(true, callId, peerId, "voice");

        // Start Beacon link heartbeat immediately
        startBeaconLink();

        if (isCallConnected) {
            String hopTag = hopCount > 1 ? " • Mesh (" + hopCount + " Hops)" : "";
            tvCallTimer.setText("Connected • 00:00" + hopTag);
            startCallTimer();
            startAudioP2PStream();
        } else {
            tvCallTimer.setText(hopCount > 1 ? "Calling via Mesh (" + hopCount + " Hops)..." : "Calling...");
            meshCoordinator.sendCallOffer(peerId, callId, "voice", MeshCoordinator.getLocalIpAddress());
            startRingbackTone();
        }
    }

    private void checkAndRequestAudioPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, 102);
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == 102) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                if (isCallConnected) {
                    startAudioP2PStream();
                }
            } else {
                Toast.makeText(this, "Microphone permission required for voice calls", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void initViews() {
        tvCallPeerName = findViewById(R.id.tvCallPeerName);
        tvCallAvatarLetter = findViewById(R.id.tvCallAvatarLetter);
        ivCallAvatarPic = findViewById(R.id.ivCallAvatarPic);
        tvCallTimer = findViewById(R.id.tvCallTimer);
        tvVoiceBitrate = findViewById(R.id.tvVoiceBitrate);
        tvVoicePing = findViewById(R.id.tvVoicePing);
        tvVoicePackets = findViewById(R.id.tvVoicePackets);

        tvCallPeerName.setText(peerName);
        tvCallAvatarLetter.setText(peerName.substring(0, Math.min(1, peerName.length())).toUpperCase());

        android.graphics.Bitmap peerPic = meshCoordinator != null ? meshCoordinator.getPeerAvatarBitmap(peerName) : null;
        if (peerPic != null && ivCallAvatarPic != null) {
            ivCallAvatarPic.setImageBitmap(com.example.meshlink.data.ImageUtils.getCircularBitmap(peerPic));
            ivCallAvatarPic.setVisibility(View.VISIBLE);
        }

        findViewById(R.id.btnCallBack).setOnClickListener(v -> endAndFinishCall());
        findViewById(R.id.btnCallEnd).setOnClickListener(v -> endAndFinishCall());

        findViewById(R.id.btnCallMute).setOnClickListener(v -> {
            isMuted = !isMuted;
            Toast.makeText(this, isMuted ? "Microphone Muted" : "Microphone Active", Toast.LENGTH_SHORT).show();
        });

        findViewById(R.id.btnCallSpeaker).setOnClickListener(v -> {
            isSpeaker = !isSpeaker;
            setAudioRouting(isSpeaker);
            if (isSpeaker) {
                if (proximityWakeLock != null && proximityWakeLock.isHeld()) {
                    try { proximityWakeLock.release(); } catch (Exception ignored) {}
                }
                Toast.makeText(this, "Speakerphone ON", Toast.LENGTH_SHORT).show();
            } else {
                if (proximityWakeLock != null && !proximityWakeLock.isHeld()) {
                    try { proximityWakeLock.acquire(); } catch (Exception ignored) {}
                }
                Toast.makeText(this, "Earpiece / Ear pods ON", Toast.LENGTH_SHORT).show();
            }
        });

        findViewById(R.id.btnCallSwitchVideo).setOnClickListener(v -> {
            meshCoordinator.sendCallEnd(peerId, callId);
            Intent videoIntent = new Intent(this, VideoCallActivity.class);
            videoIntent.putExtra("PEER_NAME", peerName);
            videoIntent.putExtra("PEER_ID", peerId);
            videoIntent.putExtra("PEER_IP", peerIp);
            startActivity(videoIntent);
            finish();
        });
    }

    private void initAudioRouting() {
        setAudioRouting(isSpeaker);
        try {
            android.os.PowerManager pm = (android.os.PowerManager) getSystemService(Context.POWER_SERVICE);
            if (pm != null && pm.isWakeLockLevelSupported(android.os.PowerManager.PROXIMITY_SCREEN_OFF_WAKE_LOCK)) {
                proximityWakeLock = pm.newWakeLock(android.os.PowerManager.PROXIMITY_SCREEN_OFF_WAKE_LOCK, "MeshLink:VoiceCallProximity");
                if (!isSpeaker && !proximityWakeLock.isHeld()) {
                    proximityWakeLock.acquire();
                }
            }
        } catch (Exception ignored) {}
    }

    private void setAudioRouting(boolean speaker) {
        AudioManager am = (AudioManager) getSystemService(Context.AUDIO_SERVICE);
        if (am == null) return;
        try {
            am.setMode(AudioManager.MODE_IN_COMMUNICATION);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                List<AudioDeviceInfo> devices = am.getAvailableCommunicationDevices();
                AudioDeviceInfo targetDev = null;
                if (speaker) {
                    for (AudioDeviceInfo dev : devices) {
                        if (dev.getType() == AudioDeviceInfo.TYPE_BUILTIN_SPEAKER) {
                            targetDev = dev;
                            break;
                        }
                    }
                } else {
                    // Priority: Bluetooth Headset / Ear pods > Wired Headset > Built-in Earpiece
                    for (AudioDeviceInfo dev : devices) {
                        if (dev.getType() == AudioDeviceInfo.TYPE_BLE_HEADSET ||
                            dev.getType() == AudioDeviceInfo.TYPE_BLUETOOTH_SCO ||
                            dev.getType() == AudioDeviceInfo.TYPE_WIRED_HEADSET ||
                            dev.getType() == AudioDeviceInfo.TYPE_WIRED_HEADPHONES) {
                            targetDev = dev;
                            break;
                        }
                    }
                    if (targetDev == null) {
                        for (AudioDeviceInfo dev : devices) {
                            if (dev.getType() == AudioDeviceInfo.TYPE_BUILTIN_EARPIECE) {
                                targetDev = dev;
                                break;
                            }
                        }
                    }
                }
                if (targetDev != null) {
                    am.setCommunicationDevice(targetDev);
                    Log.d(TAG, "Audio routed via setCommunicationDevice: " + targetDev.getType() + " (Speaker=" + speaker + ")");
                } else {
                    am.setSpeakerphoneOn(speaker);
                }
            } else {
                am.setSpeakerphoneOn(speaker);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error setting audio routing: " + e.getMessage());
            try { am.setSpeakerphoneOn(speaker); } catch (Exception ignored) {}
        }
    }

    private void resetAudioRouting() {
        AudioManager am = (AudioManager) getSystemService(Context.AUDIO_SERVICE);
        if (am == null) return;
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                am.clearCommunicationDevice();
            }
            am.setSpeakerphoneOn(false);
            am.setMode(AudioManager.MODE_NORMAL);
        } catch (Exception ignored) {}
    }

    private void startRingbackTone() {
        ringbackHandler.post(ringbackRunnable);
    }

    private void stopRingbackTone() {
        ringbackHandler.removeCallbacks(ringbackRunnable);
        if (ringbackToneGen != null) {
            try {
                ringbackToneGen.stopTone();
                ringbackToneGen.release();
            } catch (Exception ignored) {}
            ringbackToneGen = null;
        }
    }

    private void startCallTimer() {
        timerHandler.postDelayed(timerRunnable, 1000);
    }

    private void startBeaconLink() {
        beaconThread = new Thread(() -> {
            byte[] beaconPayload = ("BEACON:" + callId + ":" + meshCoordinator.getMyNodeId()).getBytes(StandardCharsets.UTF_8);

            DatagramSocket beaconSocket = null;
            try {
                beaconSocket = new DatagramSocket();
                beaconSocket.setBroadcast(true);
            } catch (Exception e) {
                Log.e(TAG, "Failed to create beaconSocket: " + e.getMessage());
            }

            while (!isFinishing() && beaconSocket != null && !beaconSocket.isClosed()) {
                try {
                    if (!isCallConnected || peerIp == null || peerIp.isEmpty()) {
                        List<String> broadcastTargets = MeshCoordinator.getSubnetBroadcastAddresses();
                        for (String bcastIp : broadcastTargets) {
                            try {
                                InetAddress bcastAddr = InetAddress.getByName(bcastIp);
                                DatagramPacket p = new DatagramPacket(beaconPayload, beaconPayload.length, bcastAddr, AUDIO_PORT);
                                beaconSocket.send(p);
                            } catch (Exception ignored) {}
                        }
                    }

                    if (peerIp == null || peerIp.isEmpty()) {
                        String cand = meshCoordinator.getPeerIp(peerId);
                        if (cand != null && !cand.isEmpty()) peerIp = cand;
                    }

                    if (peerIp != null && !peerIp.isEmpty()) {
                        try {
                            InetAddress pAddr = InetAddress.getByName(peerIp);
                            DatagramPacket p = new DatagramPacket(beaconPayload, beaconPayload.length, pAddr, AUDIO_PORT);
                            beaconSocket.send(p);

                            // Send Ping packet every 2s for live latency measurement
                            if (isCallConnected) {
                                byte[] pingBytes = ("PING:" + System.currentTimeMillis()).getBytes(StandardCharsets.UTF_8);
                                DatagramPacket pingPkt = new DatagramPacket(pingBytes, pingBytes.length, pAddr, AUDIO_PORT);
                                beaconSocket.send(pingPkt);
                            }
                        } catch (Exception ignored) {}
                    }

                    Thread.sleep(isCallConnected ? 2000 : 300);
                } catch (InterruptedException e) {
                    break;
                } catch (Exception ignored) {}
            }
            if (beaconSocket != null && !beaconSocket.isClosed()) {
                beaconSocket.close();
            }
        });
        beaconThread.start();
    }

    private void startAudioP2PStream() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M &&
            checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            return;
        }

        new Thread(() -> {
            try {
                int minRecordBuf = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT);
                int recordBufSize = Math.max(minRecordBuf, 1280);

                int minTrackBuf = AudioTrack.getMinBufferSize(SAMPLE_RATE, AudioFormat.CHANNEL_OUT_MONO, AUDIO_FORMAT);
                // Tight 80ms buffer size (2560 bytes) eliminates audio latency buildup while maintaining smooth playback
                int trackBufSize = Math.max(minTrackBuf * 2, 2560);

                try {
                    audioRecord = new AudioRecord(MediaRecorder.AudioSource.VOICE_COMMUNICATION,
                            SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT, recordBufSize);
                } catch (Exception ex) {
                    audioRecord = null;
                }
                if (audioRecord == null || audioRecord.getState() != AudioRecord.STATE_INITIALIZED) {
                    try {
                        audioRecord = new AudioRecord(MediaRecorder.AudioSource.MIC,
                                SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT, recordBufSize);
                    } catch (Exception ignored) {}
                }

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    try {
                        AudioAttributes attr = new AudioAttributes.Builder()
                                .setUsage(AudioAttributes.USAGE_VOICE_COMMUNICATION)
                                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                                .setFlags(AudioAttributes.FLAG_LOW_LATENCY)
                                .build();
                        AudioFormat fmt = new AudioFormat.Builder()
                                .setEncoding(AUDIO_FORMAT)
                                .setSampleRate(SAMPLE_RATE)
                                .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                                .build();
                        audioTrack = new AudioTrack(attr, fmt, trackBufSize, AudioTrack.MODE_STREAM, AudioManager.AUDIO_SESSION_ID_GENERATE);
                    } catch (Exception ignored) {}
                }
                if (audioTrack == null || audioTrack.getState() != AudioTrack.STATE_INITIALIZED) {
                    try {
                        audioTrack = new AudioTrack(AudioManager.STREAM_VOICE_CALL,
                                SAMPLE_RATE, AudioFormat.CHANNEL_OUT_MONO, AUDIO_FORMAT, trackBufSize, AudioTrack.MODE_STREAM);
                    } catch (Exception ex) {
                        audioTrack = null;
                    }
                }
                if (audioTrack == null || audioTrack.getState() != AudioTrack.STATE_INITIALIZED) {
                    try {
                        audioTrack = new AudioTrack(AudioManager.STREAM_MUSIC,
                                SAMPLE_RATE, AudioFormat.CHANNEL_OUT_MONO, AUDIO_FORMAT, trackBufSize, AudioTrack.MODE_STREAM);
                    } catch (Exception ignored) {}
                }
                if (audioTrack != null) {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                        audioTrack.setVolume(1.0f);
                    } else {
                        audioTrack.setStereoVolume(1.0f, 1.0f);
                    }
                }

                if (socket == null || socket.isClosed()) {
                    socket = new DatagramSocket(null);
                    socket.setReuseAddress(true);
                    socket.setBroadcast(true);
                    try {
                        socket.setTrafficClass(0x10); // IPTOS_LOWDELAY - Highest priority kernel IP routing
                        socket.setSendBufferSize(65536);
                        socket.setReceiveBufferSize(65536);
                    } catch (Exception ignored) {}
                    socket.bind(new InetSocketAddress(AUDIO_PORT));
                }

                if (audioRecord != null && audioRecord.getState() == AudioRecord.STATE_INITIALIZED) {
                    audioRecord.startRecording();
                }
                if (audioTrack != null && audioTrack.getState() == AudioTrack.STATE_INITIALIZED) {
                    audioTrack.play();
                }

                // Record thread - 20ms frames for real-time smooth voice flow
                recordThread = new Thread(() -> {
                    android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_URGENT_AUDIO);
                    byte[] buffer = new byte[AUDIO_FRAME_SIZE];
                    while (isCallConnected && !isFinishing()) {
                        try {
                            if (audioRecord == null || audioRecord.getState() != AudioRecord.STATE_INITIALIZED) {
                                Thread.sleep(30);
                                continue;
                            }
                            int read = audioRecord.read(buffer, 0, buffer.length);
                            if (read > 0 && !isMuted && socket != null && !socket.isClosed()) {
                                String currentTarget = peerIp;
                                if (currentTarget == null || currentTarget.isEmpty()) {
                                    currentTarget = meshCoordinator.getPeerIp(peerId);
                                    if (currentTarget != null) peerIp = currentTarget;
                                }

                                if (currentTarget != null && !currentTarget.isEmpty()) {
                                    // Direct P2P send - Zero duplicate packets for minimum latency
                                    try {
                                        InetAddress targetAddr = InetAddress.getByName(currentTarget);
                                        DatagramPacket packet = new DatagramPacket(buffer, read, targetAddr, AUDIO_PORT);
                                        socket.send(packet);
                                        bytesSentWindow.addAndGet(read);
                                        pktsSentWindow.incrementAndGet();
                                    } catch (Exception ignored) {}
                                } else {
                                    // Fallback broadcast ONLY when target peer IP has not been resolved yet
                                    List<String> bcasts = MeshCoordinator.getSubnetBroadcastAddresses();
                                    for (String bcastIp : bcasts) {
                                        try {
                                            InetAddress bcastAddr = InetAddress.getByName(bcastIp);
                                            DatagramPacket packet = new DatagramPacket(buffer, read, bcastAddr, AUDIO_PORT);
                                            socket.send(packet);
                                        } catch (Exception ignored) {}
                                    }
                                }
                            }
                        } catch (Exception ignored) {}
                    }
                });
                recordThread.start();

                // Play thread - Ultra low-latency immediate audio playback with zero packet truncation
                playThread = new Thread(() -> {
                    android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_URGENT_AUDIO);
                    byte[] inBuffer = new byte[2048];
                    DatagramPacket inPacket = new DatagramPacket(inBuffer, inBuffer.length);
                    while (isCallConnected && !isFinishing()) {
                        try {
                            if (socket == null || socket.isClosed()) break;
                            inPacket.setLength(inBuffer.length);
                            socket.receive(inPacket);
                            bytesRecvWindow.addAndGet(inPacket.getLength());
                            pktsRecvWindow.incrementAndGet();

                            // Dynamic Beacon Link: Auto-lock peer IP
                            InetAddress senderAddr = inPacket.getAddress();
                            if (senderAddr == null || senderAddr.isLoopbackAddress() || MeshCoordinator.isLocalAddress(senderAddr)) {
                                continue; // Strictly drop loopback audio from self
                            }

                            String senderIp = senderAddr.getHostAddress();
                            if (senderIp != null && !senderIp.equals(peerIp) && !senderIp.startsWith("127.")) {
                                peerIp = senderIp;
                                Log.d(TAG, "Voice Beacon Link: Auto-discovered peer IP -> " + peerIp);
                            }

                            // If packet is beacon heartbeat, skip playback
                            if (inPacket.getLength() < 100) {
                                String msg = new String(inPacket.getData(), 0, inPacket.getLength(), StandardCharsets.UTF_8);
                                if (msg.startsWith("BEACON:")) {
                                    continue;
                                } else if (msg.startsWith("PING:")) {
                                    // Send immediate PONG
                                    try {
                                        byte[] pongBytes = ("PONG:" + msg.substring(5)).getBytes(StandardCharsets.UTF_8);
                                        DatagramPacket pongPkt = new DatagramPacket(pongBytes, pongBytes.length, inPacket.getAddress(), AUDIO_PORT);
                                        socket.send(pongPkt);
                                    } catch (Exception ignored) {}
                                    continue;
                                } else if (msg.startsWith("PONG:")) {
                                    try {
                                        long sentTime = Long.parseLong(msg.substring(5));
                                        long rtt = System.currentTimeMillis() - sentTime;
                                        if (rtt >= 0 && rtt < 1000) currentRttMs = rtt;
                                    } catch (Exception ignored) {}
                                    continue;
                                }
                            }

                            if (audioTrack != null && audioTrack.getState() == AudioTrack.STATE_INITIALIZED) {
                                audioTrack.write(inPacket.getData(), 0, inPacket.getLength());
                            }
                        } catch (Exception ignored) {}
                    }
                });
                playThread.start();

            } catch (Exception e) {
                Log.e(TAG, "Voice P2P socket error: " + e.getMessage());
            }
        }).start();
    }

    private void endAndFinishCall() {
        meshCoordinator.sendCallEnd(peerId, callId);
        cleanupAndFinish("Call Ended");
    }

    private void cleanupAndFinish(String statusMessage) {
        isCallConnected = false;
        stopRingbackTone();
        timerHandler.removeCallbacks(timerRunnable);
        tvCallTimer.setText(statusMessage);

        if (beaconThread != null) {
            beaconThread.interrupt();
            beaconThread = null;
        }

        try {
            if (audioRecord != null) {
                audioRecord.stop();
                audioRecord.release();
                audioRecord = null;
            }
            if (audioTrack != null) {
                audioTrack.stop();
                audioTrack.release();
                audioTrack = null;
            }
            if (socket != null && !socket.isClosed()) {
                socket.close();
                socket = null;
            }

            com.example.meshlink.data.MeshDatabase db = new com.example.meshlink.data.MeshDatabase(this);
            com.example.meshlink.data.CallModel call = new com.example.meshlink.data.CallModel(
                    UUID.randomUUID().toString(),
                    peerName,
                    peerId,
                    com.example.meshlink.data.CallModel.TYPE_VOICE,
                    isIncoming ? com.example.meshlink.data.CallModel.DIR_INCOMING : com.example.meshlink.data.CallModel.DIR_OUTGOING,
                    secondsElapsed,
                    System.currentTimeMillis(),
                    "Offline P2P"
            );
            db.insertCallLog(call);
        } catch (Exception ignored) {}

        if (proximityWakeLock != null && proximityWakeLock.isHeld()) {
            try { proximityWakeLock.release(); } catch (Exception ignored) {}
        }
        resetAudioRouting();
        if (meshCoordinator != null) {
            meshCoordinator.setCallActive(false, null, null, null);
        }

        timerHandler.postDelayed(this::finish, 1000);
    }

    @Override
    protected void onResume() {
        super.onResume();
        meshCoordinator.addListener(this);
    }

    @Override
    protected void onPause() {
        super.onPause();
        meshCoordinator.removeListener(this);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        stopRingbackTone();
        if (proximityWakeLock != null && proximityWakeLock.isHeld()) {
            try { proximityWakeLock.release(); } catch (Exception ignored) {}
        }
        resetAudioRouting();
        if (meshCoordinator != null) {
            meshCoordinator.setCallActive(false, null, null, null);
        }
        cleanupAndFinish("Call Ended");
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
    public void onMessageReceived(ChatMessageModel message) {}

    @Override
    public void onSosReceived(LocalSosModel sos) {}

    @Override
    public void onCallAccepted(String callId, String peerId) {
        onCallAccepted(callId, peerId, "");
    }

    @Override
    public void onCallAccepted(String callId, String peerId, String acceptorIp) {
        runOnUiThread(() -> {
            stopRingbackTone();
            if (acceptorIp != null && !acceptorIp.isEmpty()) {
                peerIp = acceptorIp;
                Log.d(TAG, "Updated VoiceCall peerIp to: " + peerIp);
            } else if (peerIp == null || peerIp.isEmpty()) {
                String candidate = meshCoordinator.getPeerIp(peerId);
                if (candidate != null && !candidate.isEmpty()) {
                    peerIp = candidate;
                }
            }
            if (!isCallConnected) {
                isCallConnected = true;
                tvCallTimer.setText("Connected • 00:00");
                startCallTimer();
                startAudioP2PStream();
                Toast.makeText(this, "Call Connected", Toast.LENGTH_SHORT).show();
            }
        });
    }

    @Override
    public void onCallRejected(String callId, String peerId) {
        runOnUiThread(() -> {
            stopRingbackTone();
            Toast.makeText(this, "Call Declined by peer", Toast.LENGTH_LONG).show();
            cleanupAndFinish("Call Declined");
        });
    }

    @Override
    public void onCallEnded(String callId) {
        runOnUiThread(() -> {
            stopRingbackTone();
            Toast.makeText(this, "Call Ended by peer", Toast.LENGTH_SHORT).show();
            cleanupAndFinish("Call Ended");
        });
    }
}
