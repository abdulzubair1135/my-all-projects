package com.example.meshlink.main;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;

import com.example.meshlink.R;
import com.example.meshlink.browser.BrowserFragment;
import com.example.meshlink.calls.CallsFragment;
import com.example.meshlink.chat.ChatsFragment;
import com.example.meshlink.data.ChatMessageModel;
import com.example.meshlink.data.GpsLocationProvider;
import com.example.meshlink.data.LocalSosModel;
import com.example.meshlink.mesh.MeshCoordinator;
import com.example.meshlink.mesh.WifiDirectManager;
import com.example.meshlink.setup.SetupActivity;
import com.example.meshlink.status.StatusFragment;
import com.google.android.material.tabs.TabLayout;

public class MainActivity extends AppCompatActivity implements MeshCoordinator.MeshEventListener {

    private TabLayout tabLayout;
    private TextView tvMeshStatus;
    private View dotMeshStatus;

    private MeshCoordinator meshCoordinator;
    private WifiDirectManager wifiDirectManager;
    private GpsLocationProvider gpsLocationProvider;

    private double currentLat = 23.0225;
    private double currentLng = 72.5714;
    private float currentAcc = 10f;

    private final Fragment[] fragments = new Fragment[]{
            new ChatsFragment(),
            new CallsFragment(),
            new StatusFragment(),
            new BrowserFragment(),
            new com.example.meshlink.ai.ui.NexusAiFragment()
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        SharedPreferences prefs = getSharedPreferences("meshlink_prefs", MODE_PRIVATE);
        if (!prefs.getBoolean("is_configured", false)) {
            startActivity(new Intent(this, SetupActivity.class));
            finish();
            return;
        }

        setContentView(R.layout.activity_main);

        initViews();
        initMeshEngine();
        initGps();

        // Default to first tab (Chats)
        showFragment(0);
    }

    private void initViews() {
        tabLayout = findViewById(R.id.tabLayout);
        tvMeshStatus = findViewById(R.id.tvMeshStatus);
        dotMeshStatus = findViewById(R.id.dotMeshStatus);

        tabLayout.addOnTabSelectedListener(new TabLayout.OnTabSelectedListener() {
            @Override
            public void onTabSelected(TabLayout.Tab tab) {
                showFragment(tab.getPosition());
                View fab = findViewById(R.id.fabSos);
                if (fab != null) {
                    fab.setVisibility(tab.getPosition() == 4 ? View.GONE : View.VISIBLE);
                }
            }

            @Override
            public void onTabUnselected(TabLayout.Tab tab) {}

            @Override
            public void onTabReselected(TabLayout.Tab tab) {}
        });

        // Floating SOS button
        findViewById(R.id.fabSos).setOnClickListener(v -> showSosConfirmDialog());

        // Header Settings Icon
        View btnDirectSettings = findViewById(R.id.btnHeaderDirectSettings);
        if (btnDirectSettings != null) {
            btnDirectSettings.setOnClickListener(v -> startActivity(new Intent(this, com.example.meshlink.settings.SettingsActivity.class)));
        }

        // Header QR Scanner Icon
        View btnQr = findViewById(R.id.btnHeaderQrScanner);
        if (btnQr != null) {
            btnQr.setOnClickListener(v -> startActivity(new Intent(this, com.example.meshlink.settings.QrScanActivity.class)));
        }

        // Header Profile Avatar Icon
        View flProfile = findViewById(R.id.flHeaderMyProfile);
        if (flProfile != null) {
            flProfile.setOnClickListener(v -> startActivity(new Intent(this, com.example.meshlink.settings.ProfileEditActivity.class)));
        }

        findViewById(R.id.llMeshStatusPill).setOnClickListener(v -> {
            if (tabLayout.getTabCount() > 2) {
                tabLayout.selectTab(tabLayout.getTabAt(2)); // switch to Radar tab
            }
        });

        View btnRefresh = findViewById(R.id.btnRefreshMesh);
        android.widget.ImageView ivRefreshIcon = findViewById(R.id.ivRefreshMeshIcon);
        if (btnRefresh != null) {
            btnRefresh.setOnClickListener(v -> {
                if (ivRefreshIcon != null) {
                    android.view.animation.RotateAnimation anim = new android.view.animation.RotateAnimation(
                            0f, 360f,
                            android.view.animation.Animation.RELATIVE_TO_SELF, 0.5f,
                            android.view.animation.Animation.RELATIVE_TO_SELF, 0.5f);
                    anim.setDuration(600);
                    anim.setRepeatCount(1);
                    ivRefreshIcon.startAnimation(anim);
                }

                if (meshCoordinator != null) {
                    meshCoordinator.refreshMesh();
                }
                if (wifiDirectManager != null) {
                    wifiDirectManager.discoverPeers();
                }

                if (tvMeshStatus != null) {
                    tvMeshStatus.setText("Mesh: Refreshing…");
                }
                Toast.makeText(this, "Refreshing offline mesh & scanning nearby peers...", Toast.LENGTH_SHORT).show();

                new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(this::updateMeshPill, 1200);
            });
        }
    }

    private void showFragment(int index) {
        if (index >= 0 && index < fragments.length) {
            getSupportFragmentManager().beginTransaction()
                    .replace(R.id.fragmentContainer, fragments[index])
                    .commit();
        }
    }

    private void initMeshEngine() {
        meshCoordinator = MeshCoordinator.getInstance(this);
        meshCoordinator.startMesh();

        wifiDirectManager = new WifiDirectManager(this);
        wifiDirectManager.setListener(new WifiDirectManager.WifiDirectListener() {
            @Override
            public void onPeersUpdated(java.util.List<android.net.wifi.p2p.WifiP2pDevice> peers) {}

            @Override
            public void onConnected(android.net.wifi.p2p.WifiP2pInfo info) {
                if (info.groupFormed && info.groupOwnerAddress != null) {
                    String goIp = info.groupOwnerAddress.getHostAddress();
                    if (!info.isGroupOwner && goIp != null && !goIp.isEmpty()) {
                        Log.d("MainActivity", "Wi-Fi Direct connected to GO: " + goIp + ". Connecting direct socket...");
                        meshCoordinator.connectDirectToPeer(goIp, 8988);
                    }
                }
            }

            @Override
            public void onDisconnected() {}
        });
        wifiDirectManager.start();

        com.example.meshlink.mesh.MeshForegroundService.startService(this);
    }

    private void initGps() {
        gpsLocationProvider = new GpsLocationProvider(this);
        gpsLocationProvider.startListening((lat, lng, acc) -> {
            currentLat = lat;
            currentLng = lng;
            currentAcc = acc;
        });
    }

    private void showSosConfirmDialog() {
        View dialogView = getLayoutInflater().inflate(R.layout.dialog_sos_dispatch, null);
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setView(dialogView)
                .create();
        if (dialog.getWindow() != null) {
            dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
        }

        TextView tvLocation = dialogView.findViewById(R.id.tvSosLocationPreview);
        com.google.android.material.textfield.TextInputEditText etReason = dialogView.findViewById(R.id.etSosReason);
        View btnConfirm = dialogView.findViewById(R.id.btnConfirmDispatchSos);
        View btnCancel = dialogView.findViewById(R.id.btnCancelSos);

        if (tvLocation != null) {
            tvLocation.setText(String.format(java.util.Locale.US, "GPS: %.4f° N, %.4f° E (Accuracy: ±%dm)", currentLat, currentLng, (int) currentAcc));
        }

        btnConfirm.setOnClickListener(v -> {
            String desc = (etReason != null && etReason.getText() != null && !etReason.getText().toString().trim().isEmpty())
                    ? etReason.getText().toString().trim()
                    : "Emergency assistance required!";

            meshCoordinator.broadcastSOS(currentLat, currentLng, currentAcc, desc);

            // Emergency vibration pattern
            android.os.Vibrator vib = (android.os.Vibrator) getSystemService(VIBRATOR_SERVICE);
            if (vib != null) {
                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                    vib.vibrate(android.os.VibrationEffect.createWaveform(new long[]{0, 200, 100, 200, 100, 400}, -1));
                } else {
                    vib.vibrate(500);
                }
            }

            dialog.dismiss();
            Toast.makeText(this, "EMERGENCY SOS BROADCASTED TO ALL MESH NODES!", Toast.LENGTH_LONG).show();
        });

        btnCancel.setOnClickListener(v -> dialog.dismiss());
        dialog.show();
    }

    private void updateMeshPill() {
        int count = meshCoordinator.getConnectedPeerCount();
        if (count > 0) {
            tvMeshStatus.setText("Mesh: " + count + " node" + (count > 1 ? "s" : ""));
            dotMeshStatus.setBackgroundTintList(android.content.res.ColorStateList.valueOf(android.graphics.Color.parseColor("#25D366")));
        } else {
            tvMeshStatus.setText("Mesh: Scanning…");
            dotMeshStatus.setBackgroundTintList(android.content.res.ColorStateList.valueOf(android.graphics.Color.parseColor("#0A84FF")));
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (meshCoordinator != null) {
            meshCoordinator.addListener(this);
            updateMeshPill();
        }
        updateHeaderProfile();
        checkHardwareToggles();
    }

    private void checkHardwareToggles() {
        try {
            android.location.LocationManager lm = (android.location.LocationManager) getSystemService(LOCATION_SERVICE);
            boolean isGpsEnabled = false;
            if (lm != null) {
                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.P) {
                    isGpsEnabled = lm.isLocationEnabled();
                } else {
                    isGpsEnabled = lm.isProviderEnabled(android.location.LocationManager.GPS_PROVIDER)
                            || lm.isProviderEnabled(android.location.LocationManager.NETWORK_PROVIDER);
                }
            }

            android.bluetooth.BluetoothAdapter bt = android.bluetooth.BluetoothAdapter.getDefaultAdapter();
            boolean isBtEnabled = (bt != null && bt.isEnabled());

            if (!isGpsEnabled || !isBtEnabled) {
                String missing = (!isGpsEnabled && !isBtEnabled) ? "Location (GPS) & Bluetooth" : (!isGpsEnabled ? "Location (GPS)" : "Bluetooth");
                Toast.makeText(this, "⚠️ Please turn ON " + missing + " in quick settings for fast Mesh discovery!", Toast.LENGTH_LONG).show();
            }
        } catch (Exception ignored) {}
    }

    private void updateHeaderProfile() {
        TextView tvEmoji = findViewById(R.id.tvHeaderMyEmoji);
        android.widget.ImageView ivPic = findViewById(R.id.ivHeaderMyPic);
        if (tvEmoji == null) return;

        SharedPreferences prefs = getSharedPreferences("meshlink_prefs", MODE_PRIVATE);
        String myName = prefs.getString("user_name", "User");
        String initial = (myName != null && !myName.trim().isEmpty()) ? myName.trim().substring(0, 1).toUpperCase() : "U";
        String b64 = prefs.getString("user_profile_pic_base64", "");
        if (b64.isEmpty() && meshCoordinator != null) {
            b64 = meshCoordinator.getPeerAvatarBase64(myName);
            if (b64 == null) b64 = "";
        }

        tvEmoji.setText(initial);
        if (!b64.isEmpty() && ivPic != null) {
            android.graphics.Bitmap bmp = com.example.meshlink.data.ImageUtils.base64ToBitmap(b64);
            if (bmp != null) {
                ivPic.setImageBitmap(com.example.meshlink.data.ImageUtils.getCircularBitmap(bmp));
                ivPic.setVisibility(View.VISIBLE);
                tvEmoji.setVisibility(View.GONE);
            } else {
                ivPic.setVisibility(View.GONE);
                tvEmoji.setVisibility(View.VISIBLE);
            }
        } else if (ivPic != null) {
            ivPic.setVisibility(View.GONE);
            tvEmoji.setVisibility(View.VISIBLE);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (meshCoordinator != null) {
            meshCoordinator.removeListener(this);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (gpsLocationProvider != null) {
            gpsLocationProvider.stopListening();
        }
        if (wifiDirectManager != null) {
            wifiDirectManager.stop();
        }
    }

    @Override
    public void onPeerFound(String endpointId, String peerName) {
        runOnUiThread(this::updateMeshPill);
    }

    @Override
    public void onPeerLost(String endpointId) {
        runOnUiThread(this::updateMeshPill);
    }

    @Override
    public void onPeerConnected(String endpointId, String peerName) {
        runOnUiThread(() -> {
            updateMeshPill();
            Toast.makeText(this, "Connected to node: " + peerName, Toast.LENGTH_SHORT).show();
        });
    }

    @Override
    public void onPeerDisconnected(String endpointId) {
        runOnUiThread(this::updateMeshPill);
    }

    @Override
    public void onMessageReceived(ChatMessageModel message) {
        runOnUiThread(() -> {
            Toast.makeText(this, message.sender + ": " + message.content, Toast.LENGTH_SHORT).show();
        });
    }

    @Override
    public void onIncomingCall(String callId, String callerName, String callerId, String callType, String callerIp) {
        runOnUiThread(() -> {
            android.net.Uri ringtoneUri = android.media.RingtoneManager.getDefaultUri(android.media.RingtoneManager.TYPE_RINGTONE);
            final android.media.Ringtone ringtone = android.media.RingtoneManager.getRingtone(getApplicationContext(), ringtoneUri);
            if (ringtone != null) ringtone.play();

            boolean isVideo = "video".equalsIgnoreCase(callType);
            String titleStr = isVideo ? "Incoming Video Call" : "Incoming Voice Call";

            View dialogView = getLayoutInflater().inflate(R.layout.dialog_incoming_call, null);
            AlertDialog dialog = new AlertDialog.Builder(this)
                    .setView(dialogView)
                    .setCancelable(false)
                    .create();
            if (dialog.getWindow() != null) {
                dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
            }

            TextView tvBadge = dialogView.findViewById(R.id.tvIncomingCallTypeBadge);
            TextView tvName = dialogView.findViewById(R.id.tvIncomingCallerName);
            TextView tvAvatar = dialogView.findViewById(R.id.tvIncomingCallAvatar);
            View btnAccept = dialogView.findViewById(R.id.btnAcceptCall);
            View btnDecline = dialogView.findViewById(R.id.btnDeclineCall);

            if (tvBadge != null) tvBadge.setText(isVideo ? "📹 INCOMING VIDEO CALL" : "📞 INCOMING VOICE CALL");
            if (tvName != null) tvName.setText(callerName);
            if (tvAvatar != null) tvAvatar.setText((callerName != null && !callerName.isEmpty()) ? callerName.substring(0, 1).toUpperCase() : "👤");

            btnAccept.setOnClickListener(v -> {
                if (ringtone != null && ringtone.isPlaying()) ringtone.stop();
                dialog.dismiss();
                String myLocalIp = com.example.meshlink.mesh.MeshCoordinator.getLocalIpAddress();
                meshCoordinator.sendCallAccept(callerId, callId, myLocalIp);

                Class<?> targetActivity = isVideo ? com.example.meshlink.calls.VideoCallActivity.class : com.example.meshlink.calls.VoiceCallActivity.class;
                Intent callIntent = new Intent(this, targetActivity);
                callIntent.putExtra("PEER_NAME", callerName);
                callIntent.putExtra("PEER_ID", callerId);
                callIntent.putExtra("CALL_ID", callId);
                String targetPeerIp = (callerIp != null && !callerIp.isEmpty()) ? callerIp : meshCoordinator.getPeerIp(callerId);
                callIntent.putExtra("PEER_IP", targetPeerIp);
                callIntent.putExtra("IS_INCOMING", true);
                callIntent.putExtra("CALL_STATE", "CONNECTED");
                startActivity(callIntent);
            });

            btnDecline.setOnClickListener(v -> {
                if (ringtone != null && ringtone.isPlaying()) ringtone.stop();
                dialog.dismiss();
                meshCoordinator.sendCallReject(callerId, callId);
            });

            dialog.setOnDismissListener(d -> {
                if (ringtone != null && ringtone.isPlaying()) ringtone.stop();
            });
            dialog.show();
        });
    }

    @Override
    public void onSosReceived(LocalSosModel sos) {
        runOnUiThread(() -> {
            android.net.Uri alertUri = android.media.RingtoneManager.getDefaultUri(android.media.RingtoneManager.TYPE_ALARM);
            if (alertUri == null) alertUri = android.media.RingtoneManager.getDefaultUri(android.media.RingtoneManager.TYPE_NOTIFICATION);
            final android.media.Ringtone alarm = android.media.RingtoneManager.getRingtone(getApplicationContext(), alertUri);
            if (alarm != null) alarm.play();

            View dialogView = getLayoutInflater().inflate(R.layout.dialog_incoming_sos, null);
            AlertDialog dialog = new AlertDialog.Builder(this)
                    .setView(dialogView)
                    .setCancelable(false)
                    .create();
            if (dialog.getWindow() != null) {
                dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
            }

            TextView tvSender = dialogView.findViewById(R.id.tvIncomingSosSender);
            TextView tvHops = dialogView.findViewById(R.id.tvIncomingSosHops);
            TextView tvDesc = dialogView.findViewById(R.id.tvIncomingSosDesc);
            TextView tvCoords = dialogView.findViewById(R.id.tvIncomingSosCoords);
            View btnRadar = dialogView.findViewById(R.id.btnSosViewRadar);
            View btnCall = dialogView.findViewById(R.id.btnSosCallPeer);
            View btnDismiss = dialogView.findViewById(R.id.btnSosDismiss);

            if (tvSender != null) tvSender.setText("Peer: " + (sos.userName != null ? sos.userName : "Unknown Node"));
            if (tvHops != null) tvHops.setText("Distance: " + (sos.hopCount <= 1 ? "1 Hop (Direct Mesh)" : sos.hopCount + " Hops (Relayed Mesh)"));
            if (tvDesc != null) tvDesc.setText(sos.description != null ? sos.description : "Emergency assistance required!");
            if (tvCoords != null) tvCoords.setText(String.format(java.util.Locale.US, "GPS: Lat %.4f, Lng %.4f", sos.latitude, sos.longitude));

            btnRadar.setOnClickListener(v -> {
                if (alarm != null && alarm.isPlaying()) alarm.stop();
                dialog.dismiss();
                if (tabLayout != null && tabLayout.getTabCount() > 2) {
                    tabLayout.selectTab(tabLayout.getTabAt(2));
                }
            });

            btnCall.setOnClickListener(v -> {
                if (alarm != null && alarm.isPlaying()) alarm.stop();
                dialog.dismiss();
                Intent callIntent = new Intent(this, com.example.meshlink.calls.VoiceCallActivity.class);
                callIntent.putExtra("PEER_NAME", sos.userName);
                callIntent.putExtra("PEER_ID", sos.originDeviceId);
                callIntent.putExtra("IS_INCOMING", false);
                startActivity(callIntent);
            });

            btnDismiss.setOnClickListener(v -> {
                if (alarm != null && alarm.isPlaying()) alarm.stop();
                dialog.dismiss();
            });

            dialog.show();
        });
    }
}
