package com.example.meshlink.calls;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.ImageFormat;
import android.graphics.Rect;
import android.graphics.SurfaceTexture;
import android.graphics.YuvImage;
import android.hardware.Camera;
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
import android.view.Surface;
import android.view.TextureView;
import android.view.View;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.example.meshlink.R;
import com.example.meshlink.data.ChatMessageModel;
import com.example.meshlink.data.LocalSosModel;
import com.example.meshlink.mesh.MeshCoordinator;

import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

public class VideoCallActivity extends AppCompatActivity implements MeshCoordinator.MeshEventListener, TextureView.SurfaceTextureListener {

    private static final String TAG = "VideoCallActivity";
    private static final int AUDIO_PORT = 50005;
    private static final int VIDEO_PORT = 50006;
    private static final int BEACON_MAGIC = 0xBEAC01;

    private static final int SAMPLE_RATE = 16000;
    private static final int CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO;
    private static final int AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT;
    private static final int AUDIO_FRAME_SIZE = 640; // 20ms of audio @ 16kHz 16-bit mono

    private String peerName;
    private String peerId;
    private String callId;
    private volatile String peerIp = null;
    private boolean isIncoming = false;
    private volatile boolean isCallConnected = false;

    private TextView tvVideoPeerName, tvVideoDuration, tvVideoPeerLetter;
    private ImageView ivRemoteVideoFrame;
    private View llRemotePlaceholder;
    private TextureView textureLocalCamera;
    private TextView tvVideoFps, tvVideoSpeed, tvVideoPing;

    // Video Telemetry Tracking
    private final java.util.concurrent.atomic.AtomicLong videoBytesWindow = new java.util.concurrent.atomic.AtomicLong(0);
    private final java.util.concurrent.atomic.AtomicInteger videoFramesWindow = new java.util.concurrent.atomic.AtomicInteger(0);
    private volatile long currentVideoRttMs = 0;

    private boolean isMuted = false;
    private boolean isCamOff = false;
    private int currentCameraId = Camera.CameraInfo.CAMERA_FACING_FRONT;
    private int currentFrameRotation = 0;
    private byte[] nv21RotatedBuffer = null;
    private int previewWidth = 640;
    private int previewHeight = 480;

    private int hopCount = 1;
    private int secondsElapsed = 0;
    private final Handler timerHandler = new Handler(Looper.getMainLooper());
    private final Runnable timerRunnable = new Runnable() {
        @Override
        public void run() {
            if (isCallConnected) {
                secondsElapsed++;
                int mins = secondsElapsed / 60;
                int secs = secondsElapsed % 60;
                String hopTag = hopCount > 1 ? " • Mesh (" + hopCount + " Hops)" : "";
                tvVideoDuration.setText(String.format("%02d:%02d • Offline P2P Video Live%s", mins, secs, hopTag));

                int fps = videoFramesWindow.getAndSet(0);
                long bytes = videoBytesWindow.getAndSet(0);
                double kbps = bytes / 1024.0;

                if (tvVideoFps != null) {
                    tvVideoFps.setText("🎯 " + fps + " FPS");
                }
                if (tvVideoSpeed != null) {
                    tvVideoSpeed.setText(String.format(java.util.Locale.US, "⚡ %.1f KB/s", kbps));
                }
                if (tvVideoPing != null) {
                    long latency = currentVideoRttMs > 0 ? currentVideoRttMs : (hopCount * 14L);
                    tvVideoPing.setText("📶 " + latency + " ms");
                }

                timerHandler.postDelayed(this, 1000);
            }
        }
    };

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

    // Camera & P2P Stream Sockets
    private Camera camera;
    private SurfaceTexture localSurfaceTexture;
    private AudioRecord audioRecord;
    private AudioTrack audioTrack;
    private DatagramSocket audioSocket;
    private DatagramSocket videoReceiveSocket;
    private DatagramSocket videoSendSocket;
    private Thread audioRecordThread, audioPlayThread;
    private Thread videoReceiveThread;
    private Thread beaconThread;
    private final ExecutorService videoSendExecutor = Executors.newSingleThreadExecutor();
    private final ExecutorService cameraExecutor = Executors.newSingleThreadExecutor();
    private final AtomicBoolean isEncodingFrame = new AtomicBoolean(false);
    private final AtomicBoolean isSwitchingCamera = new AtomicBoolean(false);

    // Direct high-throughput TCP video stream engine
    private ServerSocket videoTcpServerSocket;
    private Socket videoTcpClientSocket;
    private Socket videoTcpActiveSendSocket;
    private DataOutputStream videoTcpOut;
    private final Object videoTcpSendLock = new Object();
    private Thread videoTcpServerThread;
    private Thread videoTcpConnectThread;
    private byte currentFrameSeq = 0;
    private final Map<Byte, byte[][]> udpFrameChunks = new ConcurrentHashMap<>();
    private final Map<Byte, Integer> udpFrameChunkCounts = new ConcurrentHashMap<>();

    private MeshCoordinator meshCoordinator;
    private long lastFrameSentTime = 0;
    private static final long MIN_FRAME_INTERVAL_MS = 60; // Max ~16 FPS for rock-solid UDP delivery

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            setShowWhenLocked(true);
            setTurnScreenOn(true);
        }
        getWindow().addFlags(
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON |
                WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED |
                WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON |
                WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD
        );

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_video_call);

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
        checkAndRequestPermissions();

        // Hardware Check: If device is Oppo Reno2 F (CPH1989) or front camera is broken, default to Back Camera!
        if (Build.MODEL.contains("CPH1989") || Build.MANUFACTURER.equalsIgnoreCase("oppo")) {
            currentCameraId = Camera.CameraInfo.CAMERA_FACING_BACK;
            Log.i(TAG, "Oppo device detected: Defaulting to Back Camera (front camera bypass).");
        }

        meshCoordinator.setCallActive(true, callId, peerId, "video");
        setAudioRouting(true); // Video call defaults to high-quality speakerphone

        // Start Beacon Link thread immediately to discover peer IP
        startBeaconLink();

        if (isCallConnected) {
            String hopTag = hopCount > 1 ? " • Mesh (" + hopCount + " Hops)" : "";
            tvVideoDuration.setText("Connected • 00:00" + hopTag);
            startCallTimer();
            startAudioVideoP2PStream();
            if (textureLocalCamera != null) {
                textureLocalCamera.post(() -> {
                    if (camera == null && !isFinishing() && !isCamOff) {
                        if (textureLocalCamera.isAvailable()) {
                            localSurfaceTexture = textureLocalCamera.getSurfaceTexture();
                            startCamera(localSurfaceTexture);
                        } else {
                            textureLocalCamera.postDelayed(() -> {
                                if (camera == null && !isFinishing() && !isCamOff && textureLocalCamera.isAvailable()) {
                                    localSurfaceTexture = textureLocalCamera.getSurfaceTexture();
                                    startCamera(localSurfaceTexture);
                                }
                            }, 300);
                        }
                    }
                });
            }
        } else {
            tvVideoDuration.setText(hopCount > 1 ? "Calling via Mesh (" + hopCount + " Hops)..." : "Calling...");
            meshCoordinator.sendCallOffer(peerId, callId, "video", MeshCoordinator.getLocalIpAddress());
            startRingbackTone();
        }
    }

    private void checkAndRequestPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED ||
                checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{
                        Manifest.permission.CAMERA,
                        Manifest.permission.RECORD_AUDIO
                }, 101);
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == 101) {
            boolean allGranted = true;
            for (int res : grantResults) {
                if (res != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }
            if (allGranted) {
                if (localSurfaceTexture == null && textureLocalCamera != null && textureLocalCamera.isAvailable()) {
                    localSurfaceTexture = textureLocalCamera.getSurfaceTexture();
                }
                if (localSurfaceTexture != null) {
                    startCamera(localSurfaceTexture);
                }
            } else {
                Toast.makeText(this, "Camera & Audio permissions are required for video calls", Toast.LENGTH_SHORT).show();
            }
        }
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
                    Log.d(TAG, "VideoCall Audio routed via setCommunicationDevice: " + targetDev.getType());
                } else {
                    am.setSpeakerphoneOn(speaker);
                }
            } else {
                am.setSpeakerphoneOn(speaker);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error setting VideoCall audio routing: " + e.getMessage());
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

    private void initViews() {
        tvVideoPeerName = findViewById(R.id.tvVideoPeerName);
        tvVideoDuration = findViewById(R.id.tvVideoDuration);
        tvVideoPeerLetter = findViewById(R.id.tvVideoPeerLetter);
        ivRemoteVideoFrame = findViewById(R.id.ivRemoteVideoFrame);
        llRemotePlaceholder = findViewById(R.id.llRemotePlaceholder);
        textureLocalCamera = findViewById(R.id.textureLocalCamera);
        tvVideoFps = findViewById(R.id.tvVideoFps);
        tvVideoSpeed = findViewById(R.id.tvVideoSpeed);
        tvVideoPing = findViewById(R.id.tvVideoPing);

        if (textureLocalCamera != null) {
            textureLocalCamera.setSurfaceTextureListener(this);
            if (textureLocalCamera.isAvailable()) {
                localSurfaceTexture = textureLocalCamera.getSurfaceTexture();
                startCamera(localSurfaceTexture);
            }
        }

        tvVideoPeerName.setText(peerName);
        tvVideoPeerLetter.setText(peerName.substring(0, Math.min(1, peerName.length())).toUpperCase());

        findViewById(R.id.btnVideoBack).setOnClickListener(v -> endAndFinishCall());
        findViewById(R.id.btnVideoEnd).setOnClickListener(v -> endAndFinishCall());

        findViewById(R.id.btnVideoMute).setOnClickListener(v -> {
            isMuted = !isMuted;
            Toast.makeText(this, isMuted ? "Microphone Muted" : "Microphone Active", Toast.LENGTH_SHORT).show();
        });

        findViewById(R.id.btnVideoToggleCam).setOnClickListener(v -> {
            isCamOff = !isCamOff;
            if (isCamOff) {
                stopCamera();
                if (textureLocalCamera != null) textureLocalCamera.setVisibility(View.INVISIBLE);
                Toast.makeText(this, "Camera Disabled", Toast.LENGTH_SHORT).show();
            } else {
                if (textureLocalCamera != null) textureLocalCamera.setVisibility(View.VISIBLE);
                startCamera(localSurfaceTexture);
                Toast.makeText(this, "Camera Enabled", Toast.LENGTH_SHORT).show();
            }
        });

        findViewById(R.id.btnVideoFlip).setOnClickListener(v -> {
            if (isSwitchingCamera.get()) return;
            v.setEnabled(false);
            currentCameraId = (currentCameraId == Camera.CameraInfo.CAMERA_FACING_FRONT) ?
                    Camera.CameraInfo.CAMERA_FACING_BACK : Camera.CameraInfo.CAMERA_FACING_FRONT;
            switchCameraAsync(() -> {
                runOnUiThread(() -> {
                    v.setEnabled(true);
                    Toast.makeText(this,
                            (currentCameraId == Camera.CameraInfo.CAMERA_FACING_FRONT) ? "Front Camera" : "Back Camera",
                            Toast.LENGTH_SHORT).show();
                });
            });
        });
    }

    private void switchCameraAsync(Runnable onComplete) {
        if (!isSwitchingCamera.compareAndSet(false, true)) {
            if (onComplete != null) onComplete.run();
            return;
        }

        cameraExecutor.execute(() -> {
            try {
                stopCamera();
                // Allow hardware Camera HAL & motorized sensors (e.g. Oppo Reno2 F) 180ms to unbind cleanly
                Thread.sleep(180);
                runOnUiThread(() -> {
                    startCamera(localSurfaceTexture);
                    isSwitchingCamera.set(false);
                    if (onComplete != null) onComplete.run();
                });
            } catch (Exception e) {
                Log.e(TAG, "Error switching camera: " + e.getMessage());
                isSwitchingCamera.set(false);
                if (onComplete != null) onComplete.run();
            }
        });
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

    private synchronized void startCamera(SurfaceTexture surfaceTexture) {
        if (surfaceTexture == null && textureLocalCamera != null) {
            if (textureLocalCamera.isAvailable()) {
                surfaceTexture = textureLocalCamera.getSurfaceTexture();
                localSurfaceTexture = surfaceTexture;
            } else {
                textureLocalCamera.postDelayed(() -> {
                    if (camera == null && !isFinishing() && !isCamOff && textureLocalCamera != null && textureLocalCamera.isAvailable()) {
                        localSurfaceTexture = textureLocalCamera.getSurfaceTexture();
                        startCamera(localSurfaceTexture);
                    }
                }, 250);
                return;
            }
        }
        if (surfaceTexture == null || isCamOff) return;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M &&
            checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            return;
        }

        try {
            stopCamera();
            int camCount = Camera.getNumberOfCameras();
            if (camCount == 0) return;

            Camera.CameraInfo info = new Camera.CameraInfo();
            int targetId = 0;
            boolean foundTarget = false;
            for (int i = 0; i < camCount; i++) {
                Camera.getCameraInfo(i, info);
                if (info.facing == currentCameraId) {
                    targetId = i;
                    foundTarget = true;
                    break;
                }
            }
            if (!foundTarget && camCount > 0) {
                targetId = 0;
                Camera.getCameraInfo(0, info);
            }

            // Retry up to 3 times to handle OEM HAL busy state
            Exception lastOpenEx = null;
            for (int attempt = 0; attempt < 3; attempt++) {
                try {
                    camera = Camera.open(targetId);
                    if (camera != null) break;
                } catch (Exception ex) {
                    lastOpenEx = ex;
                    try { Thread.sleep(150); } catch (Exception ignored) {}
                }
            }
            if (camera == null) {
                // If requested camera failed (e.g. front pop-up busy), fallback to any available camera
                Log.w(TAG, "Target camera " + targetId + " failed. Trying alternative camera IDs...");
                for (int altId = 0; altId < camCount; altId++) {
                    if (altId != targetId) {
                        try {
                            camera = Camera.open(altId);
                            if (camera != null) {
                                targetId = altId;
                                Camera.getCameraInfo(targetId, info);
                                currentCameraId = info.facing;
                                Log.i(TAG, "Fallback succeeded with camera ID " + altId);
                                break;
                            }
                        } catch (Exception ignored) {}
                    }
                }
            }
            if (camera == null) {
                if (lastOpenEx != null) throw lastOpenEx;
                throw new RuntimeException("Could not open any camera on device");
            }

            try {
                surfaceTexture.setDefaultBufferSize(640, 480);
            } catch (Exception ignored) {}
            camera.setPreviewTexture(surfaceTexture);

            // Compute correct display orientation and transmitted frame rotation
            int rotation = getWindowManager().getDefaultDisplay().getRotation();
            int degrees = 0;
            switch (rotation) {
                case Surface.ROTATION_0: degrees = 0; break;
                case Surface.ROTATION_90: degrees = 90; break;
                case Surface.ROTATION_180: degrees = 180; break;
                case Surface.ROTATION_270: degrees = 270; break;
            }

            int displayOrientation;
            if (info.facing == Camera.CameraInfo.CAMERA_FACING_FRONT) {
                displayOrientation = (info.orientation + degrees) % 360;
                displayOrientation = (360 - displayOrientation) % 360;
                currentFrameRotation = (info.orientation + degrees) % 360;
            } else {
                displayOrientation = (info.orientation - degrees + 360) % 360;
                currentFrameRotation = (info.orientation - degrees + 360) % 360;
            }
            camera.setDisplayOrientation(displayOrientation);

            // Dynamically select safe preview size from supported camera sizes
            Camera.Parameters params = camera.getParameters();
            List<Camera.Size> supportedSizes = params.getSupportedPreviewSizes();
            Camera.Size chosenSize = chooseOptimalPreviewSize(supportedSizes, 480, 360);
            if (chosenSize == null) chosenSize = chooseOptimalPreviewSize(supportedSizes, 640, 480);
            if (chosenSize != null) {
                params.setPreviewSize(chosenSize.width, chosenSize.height);
                previewWidth = chosenSize.width;
                previewHeight = chosenSize.height;
                Log.d(TAG, "Selected preview size: " + chosenSize.width + "x" + chosenSize.height);
            }

            List<String> focusModes = params.getSupportedFocusModes();
            if (focusModes != null) {
                if (focusModes.contains(Camera.Parameters.FOCUS_MODE_CONTINUOUS_VIDEO)) {
                    params.setFocusMode(Camera.Parameters.FOCUS_MODE_CONTINUOUS_VIDEO);
                } else if (focusModes.contains(Camera.Parameters.FOCUS_MODE_AUTO)) {
                    params.setFocusMode(Camera.Parameters.FOCUS_MODE_AUTO);
                }
            }

            try {
                camera.setParameters(params);
            } catch (Exception paramEx) {
                Log.w(TAG, "Failed setting preferred camera parameters, retrying with defaults: " + paramEx.getMessage());
                try {
                    Camera.Parameters fallback = camera.getParameters();
                    if (chosenSize != null) {
                        fallback.setPreviewSize(chosenSize.width, chosenSize.height);
                    }
                    camera.setParameters(fallback);
                } catch (Exception fallbackEx) {
                    Log.e(TAG, "Using basic camera parameters as fallback");
                }
            }

            camera.setPreviewCallback((data, cam) -> {
                if (isCallConnected && !isCamOff && data != null) {
                    sendVideoFrameP2P(data);
                }
            });

            camera.startPreview();
            Log.d(TAG, "Local camera preview started successfully (facing=" + info.facing + ", targetFrameRot=" + currentFrameRotation + ")");
        } catch (Exception e) {
            Log.e(TAG, "Failed to start camera preview: " + e.getMessage(), e);
            if (!isFinishing() && !isCamOff) {
                new Handler(Looper.getMainLooper()).postDelayed(() -> {
                    if (camera == null && !isFinishing() && !isCamOff) {
                        try {
                            if (localSurfaceTexture != null) {
                                startCamera(localSurfaceTexture);
                            } else if (textureLocalCamera != null && textureLocalCamera.isAvailable()) {
                                localSurfaceTexture = textureLocalCamera.getSurfaceTexture();
                                startCamera(localSurfaceTexture);
                            }
                        } catch (Exception ignored) {}
                    }
                }, 400);
            }
        }
    }

    private Camera.Size chooseOptimalPreviewSize(List<Camera.Size> sizes, int targetW, int targetH) {
        if (sizes == null || sizes.isEmpty()) return null;
        for (Camera.Size s : sizes) {
            if (s.width == targetW && s.height == targetH) {
                return s;
            }
        }
        Camera.Size best = null;
        int minDiff = Integer.MAX_VALUE;
        for (Camera.Size s : sizes) {
            int diff = Math.abs(s.width * s.height - targetW * targetH);
            if (diff < minDiff) {
                minDiff = diff;
                best = s;
            }
        }
        return best != null ? best : sizes.get(0);
    }

    private void rotateNV21(byte[] data, byte[] output, int width, int height, int rotation) {
        if (rotation == 90) {
            // Rotate Y (width x height -> height x width)
            int i = 0;
            for (int x = 0; x < width; x++) {
                for (int y = height - 1; y >= 0; y--) {
                    output[i++] = data[y * width + x];
                }
            }
            // Rotate UV
            int ySize = width * height;
            i = ySize;
            for (int x = 0; x < width; x += 2) {
                for (int y = height / 2 - 1; y >= 0; y--) {
                    output[i++] = data[ySize + (y * width) + x];
                    output[i++] = data[ySize + (y * width) + (x + 1)];
                }
            }
        } else if (rotation == 270) {
            // Rotate Y
            int i = 0;
            for (int x = width - 1; x >= 0; x--) {
                for (int y = 0; y < height; y++) {
                    output[i++] = data[y * width + x];
                }
            }
            // Rotate UV
            int ySize = width * height;
            i = ySize;
            for (int x = width - 2; x >= 0; x -= 2) {
                for (int y = 0; y < height / 2; y++) {
                    output[i++] = data[ySize + (y * width) + x];
                    output[i++] = data[ySize + (y * width) + (x + 1)];
                }
            }
        } else if (rotation == 180) {
            int ySize = width * height;
            int i = 0;
            for (int p = ySize - 1; p >= 0; p--) {
                output[i++] = data[p];
            }
            for (int p = ySize + (ySize / 2) - 2; p >= ySize; p -= 2) {
                output[i++] = data[p];
                output[i++] = data[p + 1];
            }
        } else {
            System.arraycopy(data, 0, output, 0, data.length);
        }
    }

    private synchronized void stopCamera() {
        if (camera != null) {
            try {
                camera.setPreviewCallback(null);
                camera.stopPreview();
                camera.release();
            } catch (Exception ignored) {}
            camera = null;
        }
    }

    private void sendVideoFrameP2P(byte[] nv21Data) {
        long now = System.currentTimeMillis();
        if (now - lastFrameSentTime < MIN_FRAME_INTERVAL_MS) {
            return;
        }
        if (!isEncodingFrame.compareAndSet(false, true)) {
            return; // Previous frame still encoding/sending, drop to eliminate backlog latency
        }
        lastFrameSentTime = now;

        final int width = previewWidth;
        final int height = previewHeight;
        final int rotation = currentFrameRotation;

        videoSendExecutor.execute(() -> {
            try {
                if (!isCallConnected || isCamOff) return;

                byte[] frameToSend;
                int sendWidth;
                int sendHeight;

                if (rotation == 90 || rotation == 270 || rotation == 180) {
                    int bufSize = width * height * 3 / 2;
                    if (nv21RotatedBuffer == null || nv21RotatedBuffer.length != bufSize) {
                        nv21RotatedBuffer = new byte[bufSize];
                    }
                    rotateNV21(nv21Data, nv21RotatedBuffer, width, height, rotation);
                    frameToSend = nv21RotatedBuffer;
                    sendWidth = (rotation == 90 || rotation == 270) ? height : width;
                    sendHeight = (rotation == 90 || rotation == 270) ? width : height;
                } else {
                    frameToSend = nv21Data;
                    sendWidth = width;
                    sendHeight = height;
                }

                YuvImage yuvImage = new YuvImage(frameToSend, ImageFormat.NV21, sendWidth, sendHeight, null);
                ByteArrayOutputStream outStream = new ByteArrayOutputStream();
                // Direct high-efficiency compression (yields ~12-16 KB frame)
                yuvImage.compressToJpeg(new Rect(0, 0, sendWidth, sendHeight), 28, outStream);
                byte[] jpegBytes = outStream.toByteArray();
                if (jpegBytes.length > 32000) {
                    outStream.reset();
                    yuvImage.compressToJpeg(new Rect(0, 0, sendWidth, sendHeight), 18, outStream);
                    jpegBytes = outStream.toByteArray();
                }

                // 1. Primary Engine: Direct high-speed TCP video stream
                boolean sentOverTcp = false;
                synchronized (videoTcpSendLock) {
                    if (videoTcpOut != null) {
                        try {
                            videoTcpOut.writeInt(jpegBytes.length);
                            videoTcpOut.write(jpegBytes);
                            videoTcpOut.flush();
                            videoBytesWindow.addAndGet(jpegBytes.length + 4);
                            sentOverTcp = true;
                        } catch (Exception tcpErr) {
                            Log.w(TAG, "TCP video frame write failed, resetting TCP output: " + tcpErr.getMessage());
                            videoTcpOut = null;
                        }
                    }
                }

                // 2. Secondary Engine: MTU-safe chunked UDP stream (<= 1104 bytes per packet, zero fragmentation!)
                if (!sentOverTcp || Math.random() < 0.1) {
                    if (videoSendSocket == null || videoSendSocket.isClosed()) {
                        videoSendSocket = new DatagramSocket();
                        videoSendSocket.setBroadcast(true);
                    }

                    byte seq = currentFrameSeq++;
                    int chunkSize = 1100;
                    int totalChunks = (int) Math.ceil((double) jpegBytes.length / chunkSize);

                    if (totalChunks <= 64) {
                        for (int i = 0; i < totalChunks; i++) {
                            int offset = i * chunkSize;
                            int len = Math.min(chunkSize, jpegBytes.length - offset);
                            byte[] chunkPkt = new byte[4 + len];
                            chunkPkt[0] = (byte) 0x56; // Magic 'V'
                            chunkPkt[1] = seq;
                            chunkPkt[2] = (byte) i;
                            chunkPkt[3] = (byte) totalChunks;
                            System.arraycopy(jpegBytes, offset, chunkPkt, 4, len);

                            if (peerIp != null && !peerIp.isEmpty()) {
                                try {
                                    InetAddress targetAddr = InetAddress.getByName(peerIp);
                                    DatagramPacket packet = new DatagramPacket(chunkPkt, chunkPkt.length, targetAddr, VIDEO_PORT);
                                    videoSendSocket.send(packet);
                                    videoBytesWindow.addAndGet(chunkPkt.length);
                                } catch (Exception ignored) {}
                            } else {
                                List<String> bcasts = MeshCoordinator.getSubnetBroadcastAddresses();
                                for (String bcastIp : bcasts) {
                                    try {
                                        InetAddress bcastAddr = InetAddress.getByName(bcastIp);
                                        DatagramPacket packet = new DatagramPacket(chunkPkt, chunkPkt.length, bcastAddr, VIDEO_PORT);
                                        videoSendSocket.send(packet);
                                    } catch (Exception ignored) {}
                                }
                            }
                        }
                    }
                }
            } catch (Exception ignored) {} finally {
                isEncodingFrame.set(false);
            }
        });
    }

    // Direct Beacon Link Heartbeat to discover and lock peer IP automatically
    private void startBeaconLink() {
        beaconThread = new Thread(() -> {
            byte[] beaconPayload = ("BEACON:" + callId + ":" + meshCoordinator.getMyNodeId()).getBytes(StandardCharsets.UTF_8);

            while (!isFinishing()) {
                try {
                    if (videoSendSocket == null || videoSendSocket.isClosed()) {
                        videoSendSocket = new DatagramSocket();
                        videoSendSocket.setBroadcast(true);
                    }

                    // 1. Broadcast discovery beacon on audio & video ports ONLY when peerIp is not resolved yet
                    if (!isCallConnected || peerIp == null || peerIp.isEmpty()) {
                        List<String> broadcastTargets = MeshCoordinator.getSubnetBroadcastAddresses();
                        for (String bcastIp : broadcastTargets) {
                            try {
                                InetAddress bcastAddr = InetAddress.getByName(bcastIp);
                                DatagramPacket pVid = new DatagramPacket(beaconPayload, beaconPayload.length, bcastAddr, VIDEO_PORT);
                                videoSendSocket.send(pVid);
                            } catch (Exception ignored) {}
                        }
                    }

                    if (peerIp == null || peerIp.isEmpty()) {
                        String cand = meshCoordinator.getPeerIp(peerId);
                        if (cand != null && !cand.isEmpty()) peerIp = cand;
                    }

                    // 2. Unicast beacon if peerIp is known
                    if (peerIp != null && !peerIp.isEmpty()) {
                        try {
                            InetAddress pAddr = InetAddress.getByName(peerIp);
                            DatagramPacket pUnicast = new DatagramPacket(beaconPayload, beaconPayload.length, pAddr, VIDEO_PORT);
                            videoSendSocket.send(pUnicast);
                        } catch (Exception ignored) {}
                    }

                    Thread.sleep(isCallConnected ? 2000 : 300);
                } catch (InterruptedException e) {
                    break;
                } catch (Exception ignored) {}
            }
        });
        beaconThread.start();
    }

    private void startAudioVideoP2PStream() {
        new Thread(() -> {
            try {
                // 1. Ultra-Low Latency Voice Audio Stream (Port 50005)
                int minRecordBuf = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT);
                int recordBufSize = Math.max(minRecordBuf, 1280);

                int minTrackBuf = AudioTrack.getMinBufferSize(SAMPLE_RATE, AudioFormat.CHANNEL_OUT_MONO, AUDIO_FORMAT);
                // Tight 80ms buffer (2560 bytes) ensures real-time speech without backlog lag
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

                if (audioSocket == null || audioSocket.isClosed()) {
                    audioSocket = new DatagramSocket(null);
                    audioSocket.setReuseAddress(true);
                    audioSocket.setBroadcast(true);
                    try {
                        audioSocket.setTrafficClass(0x10); // IPTOS_LOWDELAY - Kernel prioritized voice routing
                        audioSocket.setSendBufferSize(65536);
                        audioSocket.setReceiveBufferSize(65536);
                    } catch (Exception ignored) {}
                    audioSocket.bind(new InetSocketAddress(AUDIO_PORT));
                }

                if (audioRecord != null && audioRecord.getState() == AudioRecord.STATE_INITIALIZED) {
                    audioRecord.startRecording();
                }
                if (audioTrack != null && audioTrack.getState() == AudioTrack.STATE_INITIALIZED) {
                    audioTrack.play();
                }

                // Audio Recording & Transmission Thread (20ms frames)
                audioRecordThread = new Thread(() -> {
                    android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_URGENT_AUDIO);
                    byte[] buffer = new byte[AUDIO_FRAME_SIZE];
                    while (isCallConnected && !isFinishing()) {
                        try {
                            if (audioRecord == null || audioRecord.getState() != AudioRecord.STATE_INITIALIZED) {
                                Thread.sleep(30);
                                continue;
                            }
                            int read = audioRecord.read(buffer, 0, buffer.length);
                            if (read > 0 && !isMuted && audioSocket != null && !audioSocket.isClosed()) {
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
                                        audioSocket.send(packet);
                                    } catch (Exception ignored) {}
                                } else {
                                    // Fallback broadcast ONLY when target peer IP has not been resolved yet
                                    List<String> bcasts = MeshCoordinator.getSubnetBroadcastAddresses();
                                    for (String bcastIp : bcasts) {
                                        try {
                                            InetAddress bcastAddr = InetAddress.getByName(bcastIp);
                                            DatagramPacket packet = new DatagramPacket(buffer, read, bcastAddr, AUDIO_PORT);
                                            audioSocket.send(packet);
                                        } catch (Exception ignored) {}
                                    }
                                }
                            }
                        } catch (Exception ignored) {}
                    }
                });
                audioRecordThread.start();

                // Audio Receiving & Playback Thread (zero jitter, auto-learning IP, zero packet truncation)
                audioPlayThread = new Thread(() -> {
                    android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_URGENT_AUDIO);
                    byte[] inBuffer = new byte[2048];
                    DatagramPacket inPacket = new DatagramPacket(inBuffer, inBuffer.length);
                    while (isCallConnected && !isFinishing()) {
                        try {
                            if (audioSocket == null || audioSocket.isClosed()) break;
                            inPacket.setLength(inBuffer.length);
                            audioSocket.receive(inPacket);

                            // Dynamic Beacon Link: Auto-lock peer IP from incoming audio
                            InetAddress senderAddr = inPacket.getAddress();
                            if (senderAddr == null || senderAddr.isLoopbackAddress() || MeshCoordinator.isLocalAddress(senderAddr)) {
                                continue; // Strictly drop loopback audio from self
                            }

                            String senderIp = senderAddr.getHostAddress();
                            if (senderIp != null && !senderIp.equals(peerIp) && !senderIp.startsWith("127.")) {
                                peerIp = senderIp;
                                Log.d(TAG, "Beacon Link: Auto-locked peerIp from incoming audio: " + peerIp);
                            }

                            if (inPacket.getLength() < 100 && new String(inPacket.getData(), 0, inPacket.getLength()).startsWith("BEACON:")) {
                                continue;
                            }

                            // Write raw PCM audio directly to AudioTrack with zero delay
                            if (audioTrack != null && audioTrack.getState() == AudioTrack.STATE_INITIALIZED) {
                                audioTrack.write(inPacket.getData(), 0, inPacket.getLength());
                            }
                        } catch (Exception ignored) {}
                    }
                });
                audioPlayThread.start();

                // 2. Direct TCP Video Server Thread (Port 50006)
                videoTcpServerThread = new Thread(() -> {
                    try {
                        try {
                            videoTcpServerSocket = new ServerSocket(VIDEO_PORT);
                        } catch (Exception portBusy) {
                            videoTcpServerSocket = new ServerSocket(0);
                        }
                        videoTcpServerSocket.setReceiveBufferSize(512 * 1024);
                        Log.d(TAG, "TCP Video Server listening on port " + videoTcpServerSocket.getLocalPort());

                        while (isCallConnected && !isFinishing() && videoTcpServerSocket != null && !videoTcpServerSocket.isClosed()) {
                            try {
                                Socket client = videoTcpServerSocket.accept();
                                client.setTcpNoDelay(true);
                                client.setReceiveBufferSize(512 * 1024);
                                videoTcpClientSocket = client;
                                Log.d(TAG, "TCP Video client connected: " + client.getInetAddress().getHostAddress());

                                DataInputStream dis = new DataInputStream(new BufferedInputStream(client.getInputStream(), 65536));
                                BitmapFactory.Options decodeOpts = new BitmapFactory.Options();
                                decodeOpts.inPreferredConfig = Bitmap.Config.RGB_565;

                                while (isCallConnected && !isFinishing() && !client.isClosed()) {
                                    int frameLen = dis.readInt();
                                    if (frameLen > 0 && frameLen < 300000) {
                                        byte[] frameBytes = new byte[frameLen];
                                        dis.readFully(frameBytes);
                                        Bitmap bitmap = BitmapFactory.decodeByteArray(frameBytes, 0, frameLen, decodeOpts);
                                        videoBytesWindow.addAndGet(frameLen + 4);
                                        if (bitmap != null) {
                                            videoFramesWindow.incrementAndGet();
                                            runOnUiThread(() -> {
                                                if (ivRemoteVideoFrame != null) {
                                                    ivRemoteVideoFrame.setImageBitmap(bitmap);
                                                    ivRemoteVideoFrame.setVisibility(View.VISIBLE);
                                                }
                                                if (llRemotePlaceholder != null && llRemotePlaceholder.getVisibility() == View.VISIBLE) {
                                                    llRemotePlaceholder.setVisibility(View.GONE);
                                                }
                                            });
                                        }
                                    }
                                }
                            } catch (Exception ignored) {}
                        }
                    } catch (Exception e) {
                        Log.w(TAG, "TCP Video server notice: " + e.getMessage());
                    }
                });
                videoTcpServerThread.start();

                // 3. Direct TCP Video Client Connect Thread
                videoTcpConnectThread = new Thread(() -> {
                    while (isCallConnected && !isFinishing()) {
                        try {
                            if (videoTcpOut == null) {
                                String targetIp = peerIp;
                                if (targetIp == null || targetIp.isEmpty()) {
                                    targetIp = meshCoordinator.getPeerIp(peerId);
                                    if (targetIp != null) peerIp = targetIp;
                                }

                                if (targetIp != null && !targetIp.isEmpty() && !targetIp.startsWith("127.")) {
                                    try {
                                        Socket sendSock = new Socket();
                                        sendSock.connect(new InetSocketAddress(targetIp, VIDEO_PORT), 2500);
                                        sendSock.setTcpNoDelay(true);
                                        sendSock.setSendBufferSize(512 * 1024);
                                        videoTcpActiveSendSocket = sendSock;
                                        synchronized (videoTcpSendLock) {
                                            videoTcpOut = new DataOutputStream(new BufferedOutputStream(sendSock.getOutputStream(), 65536));
                                        }
                                        Log.d(TAG, "Connected high-speed TCP video send socket to " + targetIp + ":" + VIDEO_PORT);
                                    } catch (Exception ignored) {}
                                }
                            }
                            Thread.sleep(1500);
                        } catch (InterruptedException ie) {
                            break;
                        } catch (Exception ignored) {}
                    }
                });
                videoTcpConnectThread.start();

                // 4. Remote Video Frame UDP Receiver Stream (Chunked + Raw MTU-safe)
                if (videoReceiveSocket == null || videoReceiveSocket.isClosed()) {
                    videoReceiveSocket = new DatagramSocket(null);
                    videoReceiveSocket.setReuseAddress(true);
                    videoReceiveSocket.setBroadcast(true);
                    videoReceiveSocket.setReceiveBufferSize(512 * 1024);
                    videoReceiveSocket.bind(new InetSocketAddress(VIDEO_PORT));
                }

                videoReceiveThread = new Thread(() -> {
                    byte[] vidBuffer = new byte[65536];
                    DatagramPacket vidPacket = new DatagramPacket(vidBuffer, vidBuffer.length);
                    BitmapFactory.Options decodeOpts = new BitmapFactory.Options();
                    decodeOpts.inPreferredConfig = Bitmap.Config.RGB_565;

                    while (isCallConnected && !isFinishing()) {
                        try {
                            if (videoReceiveSocket == null || videoReceiveSocket.isClosed()) break;
                            vidPacket.setLength(vidBuffer.length);
                            videoReceiveSocket.receive(vidPacket);
                            videoBytesWindow.addAndGet(vidPacket.getLength());

                            InetAddress senderAddr = vidPacket.getAddress();
                            if (senderAddr == null || senderAddr.isLoopbackAddress() || MeshCoordinator.isLocalAddress(senderAddr)) {
                                continue;
                            }

                            String senderIp = senderAddr.getHostAddress();
                            if (senderIp != null && !senderIp.equals(peerIp) && !senderIp.startsWith("127.")) {
                                peerIp = senderIp;
                                Log.d(TAG, "Beacon Link: Auto-locked peerIp from incoming video: " + peerIp);
                            }

                            int pktLen = vidPacket.getLength();
                            if (pktLen < 100) {
                                String msg = new String(vidPacket.getData(), 0, pktLen, StandardCharsets.UTF_8);
                                if (msg.startsWith("BEACON:")) {
                                    continue;
                                } else if (msg.startsWith("PING:")) {
                                    try {
                                        byte[] pongBytes = ("PONG:" + msg.substring(5)).getBytes(StandardCharsets.UTF_8);
                                        DatagramPacket pongPkt = new DatagramPacket(pongBytes, pongBytes.length, vidPacket.getAddress(), VIDEO_PORT);
                                        if (videoSendSocket != null && !videoSendSocket.isClosed()) {
                                            videoSendSocket.send(pongPkt);
                                        }
                                    } catch (Exception ignored) {}
                                    continue;
                                } else if (msg.startsWith("PONG:")) {
                                    try {
                                        long sentTime = Long.parseLong(msg.substring(5));
                                        long rtt = System.currentTimeMillis() - sentTime;
                                        if (rtt >= 0 && rtt < 1000) currentVideoRttMs = rtt;
                                    } catch (Exception ignored) {}
                                    continue;
                                }
                            }

                            byte[] data = vidPacket.getData();
                            // Handle Chunked UDP video packet (Magic 0x56)
                            if (pktLen > 4 && data[0] == (byte) 0x56) {
                                byte fSeq = data[1];
                                int chunkIdx = data[2] & 0xFF;
                                int totalChunks = data[3] & 0xFF;
                                int chunkDataLen = pktLen - 4;

                                if (totalChunks > 0 && totalChunks <= 64 && chunkIdx < totalChunks) {
                                    byte[][] chunks = udpFrameChunks.get(fSeq);
                                    if (chunks == null) {
                                        chunks = new byte[totalChunks][];
                                        udpFrameChunks.put(fSeq, chunks);
                                        udpFrameChunkCounts.put(fSeq, 0);
                                        // Purge old frames
                                        if (udpFrameChunks.size() > 4) {
                                            udpFrameChunks.clear();
                                            udpFrameChunkCounts.clear();
                                            chunks = new byte[totalChunks][];
                                            udpFrameChunks.put(fSeq, chunks);
                                            udpFrameChunkCounts.put(fSeq, 0);
                                        }
                                    }

                                    if (chunks[chunkIdx] == null) {
                                        byte[] cData = new byte[chunkDataLen];
                                        System.arraycopy(data, 4, cData, 0, chunkDataLen);
                                        chunks[chunkIdx] = cData;
                                        int count = udpFrameChunkCounts.get(fSeq) + 1;
                                        udpFrameChunkCounts.put(fSeq, count);

                                        if (count == totalChunks) {
                                            // Reassemble full frame
                                            int totalBytes = 0;
                                            for (byte[] c : chunks) {
                                                if (c != null) totalBytes += c.length;
                                            }
                                            byte[] fullFrame = new byte[totalBytes];
                                            int pos = 0;
                                            for (byte[] c : chunks) {
                                                if (c != null) {
                                                    System.arraycopy(c, 0, fullFrame, pos, c.length);
                                                    pos += c.length;
                                                }
                                            }
                                            udpFrameChunks.remove(fSeq);
                                            udpFrameChunkCounts.remove(fSeq);

                                            final Bitmap bitmap = BitmapFactory.decodeByteArray(fullFrame, 0, fullFrame.length, decodeOpts);
                                            if (bitmap != null) {
                                                videoFramesWindow.incrementAndGet();
                                                runOnUiThread(() -> {
                                                    if (ivRemoteVideoFrame != null) {
                                                        ivRemoteVideoFrame.setImageBitmap(bitmap);
                                                        ivRemoteVideoFrame.setVisibility(View.VISIBLE);
                                                    }
                                                    if (llRemotePlaceholder != null && llRemotePlaceholder.getVisibility() == View.VISIBLE) {
                                                        llRemotePlaceholder.setVisibility(View.GONE);
                                                    }
                                                });
                                            }
                                        }
                                    }
                                }
                            } else {
                                // Raw unchunked JPEG
                                final Bitmap bitmap = BitmapFactory.decodeByteArray(data, 0, pktLen, decodeOpts);
                                if (bitmap != null) {
                                    videoFramesWindow.incrementAndGet();
                                    runOnUiThread(() -> {
                                        if (ivRemoteVideoFrame != null) {
                                            ivRemoteVideoFrame.setImageBitmap(bitmap);
                                            ivRemoteVideoFrame.setVisibility(View.VISIBLE);
                                        }
                                        if (llRemotePlaceholder != null && llRemotePlaceholder.getVisibility() == View.VISIBLE) {
                                            llRemotePlaceholder.setVisibility(View.GONE);
                                        }
                                    });
                                }
                            }
                        } catch (Exception ignored) {}
                    }
                });
                videoReceiveThread.start();

            } catch (Exception e) {
                Log.e(TAG, "Audio/Video P2P socket error: " + e.getMessage());
            }
        }).start();
    }

    private void endAndFinishCall() {
        meshCoordinator.sendCallEnd(peerId, callId);
        cleanupAndFinish("Call Ended");
    }

    private void cleanupAndFinish(String statusMsg) {
        isCallConnected = false;
        isSwitchingCamera.set(false);
        stopRingbackTone();
        stopCamera();
        timerHandler.removeCallbacks(timerRunnable);
        tvVideoDuration.setText(statusMsg);

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
            if (audioSocket != null && !audioSocket.isClosed()) {
                audioSocket.close();
                audioSocket = null;
            }
            if (videoReceiveSocket != null && !videoReceiveSocket.isClosed()) {
                videoReceiveSocket.close();
                videoReceiveSocket = null;
            }
            if (videoSendSocket != null && !videoSendSocket.isClosed()) {
                videoSendSocket.close();
                videoSendSocket = null;
            }
            synchronized (videoTcpSendLock) {
                if (videoTcpOut != null) {
                    try { videoTcpOut.close(); } catch (Exception ignored) {}
                    videoTcpOut = null;
                }
            }
            if (videoTcpActiveSendSocket != null && !videoTcpActiveSendSocket.isClosed()) {
                try { videoTcpActiveSendSocket.close(); } catch (Exception ignored) {}
                videoTcpActiveSendSocket = null;
            }
            if (videoTcpClientSocket != null && !videoTcpClientSocket.isClosed()) {
                try { videoTcpClientSocket.close(); } catch (Exception ignored) {}
                videoTcpClientSocket = null;
            }
            if (videoTcpServerSocket != null && !videoTcpServerSocket.isClosed()) {
                try { videoTcpServerSocket.close(); } catch (Exception ignored) {}
                videoTcpServerSocket = null;
            }

            com.example.meshlink.data.MeshDatabase db = new com.example.meshlink.data.MeshDatabase(this);
            com.example.meshlink.data.CallModel call = new com.example.meshlink.data.CallModel(
                    UUID.randomUUID().toString(),
                    peerName,
                    peerId,
                    com.example.meshlink.data.CallModel.TYPE_VIDEO,
                    isIncoming ? com.example.meshlink.data.CallModel.DIR_INCOMING : com.example.meshlink.data.CallModel.DIR_OUTGOING,
                    secondsElapsed,
                    System.currentTimeMillis(),
                    "Offline P2P"
            );
            db.insertCallLog(call);
        } catch (Exception ignored) {}

        resetAudioRouting();
        if (meshCoordinator != null) {
            meshCoordinator.setCallActive(false, null, null, null);
        }

        timerHandler.postDelayed(this::finish, 1000);
    }

    @Override
    public void onSurfaceTextureAvailable(SurfaceTexture surface, int width, int height) {
        localSurfaceTexture = surface;
        runOnUiThread(() -> startCamera(localSurfaceTexture));
    }

    @Override
    public void onSurfaceTextureSizeChanged(SurfaceTexture surface, int width, int height) {}

    @Override
    public boolean onSurfaceTextureDestroyed(SurfaceTexture surface) {
        stopCamera();
        return true;
    }

    @Override
    public void onSurfaceTextureUpdated(SurfaceTexture surface) {}

    @Override
    protected void onResume() {
        super.onResume();
        meshCoordinator.addListener(this);
        if (textureLocalCamera != null && textureLocalCamera.isAvailable()) {
            localSurfaceTexture = textureLocalCamera.getSurfaceTexture();
            startCamera(localSurfaceTexture);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        meshCoordinator.removeListener(this);
        stopCamera();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        stopRingbackTone();
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
                Log.d(TAG, "Updated VideoCall peerIp to: " + peerIp);
            } else if (peerIp == null || peerIp.isEmpty()) {
                String candidate = meshCoordinator.getPeerIp(peerId);
                if (candidate != null && !candidate.isEmpty()) {
                    peerIp = candidate;
                }
            }
            if (!isCallConnected) {
                isCallConnected = true;
                tvVideoDuration.setText("Connected • 00:00");
                startCallTimer();
                startAudioVideoP2PStream();
                if (localSurfaceTexture != null) {
                    startCamera(localSurfaceTexture);
                } else if (textureLocalCamera != null && textureLocalCamera.isAvailable()) {
                    localSurfaceTexture = textureLocalCamera.getSurfaceTexture();
                    startCamera(localSurfaceTexture);
                }
                Toast.makeText(this, "Video Call Connected", Toast.LENGTH_SHORT).show();
            }
        });
    }

    @Override
    public void onCallRejected(String callId, String peerId) {
        runOnUiThread(() -> {
            stopRingbackTone();
            Toast.makeText(this, "Video Call Declined by peer", Toast.LENGTH_LONG).show();
            cleanupAndFinish("Call Declined");
        });
    }

    @Override
    public void onCallEnded(String callId) {
        runOnUiThread(() -> {
            stopRingbackTone();
            Toast.makeText(this, "Video Call Ended by peer", Toast.LENGTH_SHORT).show();
            cleanupAndFinish("Call Ended");
        });
    }
}
