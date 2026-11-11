package com.example.meshlink.calls;

import android.content.Context;
import android.content.Intent;
import android.media.AudioAttributes;
import android.media.AudioManager;
import android.media.Ringtone;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.view.View;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.example.meshlink.R;
import com.example.meshlink.data.ChatMessageModel;
import com.example.meshlink.data.LocalSosModel;
import com.example.meshlink.mesh.MeshCoordinator;

public class IncomingCallActivity extends AppCompatActivity implements MeshCoordinator.MeshEventListener {

    private String callId;
    private String callerName;
    private String callerId;
    private String callType;
    private String callerIp;

    private Ringtone ringtone;
    private Vibrator vibrator;
    private MeshCoordinator meshCoordinator;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Turn screen on and show over lock screen
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

        setContentView(R.layout.activity_incoming_call);

        meshCoordinator = MeshCoordinator.getInstance(this);

        callId = getIntent().getStringExtra("CALL_ID");
        callerName = getIntent().getStringExtra("CALLER_NAME");
        if (callerName == null) callerName = "Nexus Peer";
        callerId = getIntent().getStringExtra("CALLER_ID");
        if (callerId == null) callerId = callerName;
        callType = getIntent().getStringExtra("CALL_TYPE");
        if (callType == null) callType = "voice";
        callerIp = getIntent().getStringExtra("CALLER_IP");
        int hopCount = getIntent().getIntExtra("HOP_COUNT", 0);

        if (meshCoordinator.isCallActive()) {
            meshCoordinator.sendCallReject(callerId, callId, "BUSY");
            finish();
            return;
        }

        TextView tvCaller = findViewById(R.id.tvIncCallerName);
        TextView tvAvatar = findViewById(R.id.tvIncAvatarLetter);
        ImageView ivIncAvatarPic = findViewById(R.id.ivIncAvatarPic);
        TextView tvCallType = findViewById(R.id.tvIncCallType);
        ImageView ivAcceptIcon = findViewById(R.id.ivIncAcceptIcon);

        String cleanName = MeshCoordinator.cleanPeerName(callerName);
        tvCaller.setText(cleanName);
        tvAvatar.setText(cleanName.substring(0, Math.min(1, cleanName.length())).toUpperCase());

        android.graphics.Bitmap peerPic = meshCoordinator != null ? meshCoordinator.getPeerAvatarBitmap(cleanName) : null;
        if (peerPic == null && meshCoordinator != null && callerId != null) {
            peerPic = meshCoordinator.getPeerAvatarBitmap(callerId);
        }
        if (peerPic != null && ivIncAvatarPic != null) {
            ivIncAvatarPic.setImageBitmap(com.example.meshlink.data.ImageUtils.getCircularBitmap(peerPic));
            ivIncAvatarPic.setVisibility(View.VISIBLE);
        }

        boolean isVideo = "video".equalsIgnoreCase(callType);
        String hopLabel = hopCount > 1 ? " • Mesh (" + hopCount + " Hops)" : " • Direct";
        tvCallType.setText((isVideo ? "Incoming P2P Video Call" : "Incoming P2P Voice Call") + hopLabel);
        if (isVideo) {
            ivAcceptIcon.setImageResource(android.R.drawable.ic_menu_camera);
        } else {
            ivAcceptIcon.setImageResource(android.R.drawable.stat_sys_phone_call);
        }

        findViewById(R.id.btnIncAccept).setOnClickListener(v -> acceptCall());
        findViewById(R.id.btnIncDecline).setOnClickListener(v -> declineCall());

        startRingtoneAndVibrate();
    }

    private void startRingtoneAndVibrate() {
        try {
            Uri alert = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_RINGTONE);
            if (alert == null) alert = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
            ringtone = RingtoneManager.getRingtone(this, alert);
            if (ringtone != null) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    ringtone.setAudioAttributes(new AudioAttributes.Builder()
                            .setUsage(AudioAttributes.USAGE_NOTIFICATION_RINGTONE)
                            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                            .build());
                }
                ringtone.play();
            }

            vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
            if (vibrator != null && vibrator.hasVibrator()) {
                long[] pattern = {0, 600, 400, 600, 400};
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    vibrator.vibrate(VibrationEffect.createWaveform(pattern, 0));
                } else {
                    vibrator.vibrate(pattern, 0);
                }
            }
        } catch (Exception ignored) {}
    }

    private void stopRingtoneAndVibrate() {
        try {
            if (ringtone != null && ringtone.isPlaying()) {
                ringtone.stop();
            }
            ringtone = null;
        } catch (Exception ignored) {}

        try {
            if (vibrator != null) {
                vibrator.cancel();
            }
            vibrator = null;
        } catch (Exception ignored) {}
    }

    private void acceptCall() {
        stopRingtoneAndVibrate();

        String myLocalIp = MeshCoordinator.getLocalIpAddress();
        meshCoordinator.sendCallAccept(callerId, callId, myLocalIp);

        boolean isVideo = "video".equalsIgnoreCase(callType);
        Class<?> target = isVideo ? VideoCallActivity.class : VoiceCallActivity.class;

        Intent intent = new Intent(this, target);
        intent.putExtra("PEER_NAME", MeshCoordinator.cleanPeerName(callerName));
        intent.putExtra("PEER_ID", callerId);
        String targetPeerIp = (callerIp != null && !callerIp.isEmpty()) ? callerIp : meshCoordinator.getPeerIp(callerId);
        intent.putExtra("PEER_IP", targetPeerIp);
        intent.putExtra("IS_INCOMING", true);
        intent.putExtra("CALL_STATE", "CONNECTED");
        intent.putExtra("HOP_COUNT", getIntent().getIntExtra("HOP_COUNT", 0));
        startActivity(intent);

        finish();
    }

    private void declineCall() {
        stopRingtoneAndVibrate();
        meshCoordinator.sendCallReject(callerId, callId);
        finish();
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
        stopRingtoneAndVibrate();
    }

    @Override
    public void onCallEnded(String endedCallId) {
        if (callId != null && callId.equals(endedCallId)) {
            runOnUiThread(() -> {
                stopRingtoneAndVibrate();
                finish();
            });
        }
    }

    @Override
    public void onCallRejected(String rejectedCallId, String peerId) {
        if (callId != null && callId.equals(rejectedCallId)) {
            runOnUiThread(() -> {
                stopRingtoneAndVibrate();
                finish();
            });
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
    public void onMessageReceived(ChatMessageModel message) {}
    @Override
    public void onSosReceived(LocalSosModel sos) {}
}
