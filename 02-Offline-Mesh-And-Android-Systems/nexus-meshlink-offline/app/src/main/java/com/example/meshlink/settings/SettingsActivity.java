package com.example.meshlink.settings;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.hardware.camera2.CameraManager;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.example.meshlink.R;
import com.example.meshlink.crypto.CryptoManager;
import com.example.meshlink.data.MeshDatabase;
import com.example.meshlink.setup.SetupActivity;
import com.google.zxing.BarcodeFormat;
import com.journeyapps.barcodescanner.BarcodeEncoder;

public class SettingsActivity extends AppCompatActivity {

    private TextView tvSettingsAvatar, tvSettingsName, tvSettingsBio, tvSettingsMeshId;
    private TextView tvSirenStatus, tvStrobeStatus, tvConfigServerUrl;
    private Button btnToggleSiren, btnToggleStrobe;

    private boolean isSirenActive = false;
    private boolean isStrobeActive = false;

    private AudioTrack sirenAudioTrack;
    private Thread sirenThread;
    private Thread strobeThread;

    private ImageView ivSettingsProfilePic;

    private final androidx.activity.result.ActivityResultLauncher<String> pickImageLauncher =
            registerForActivityResult(new androidx.activity.result.contract.ActivityResultContracts.GetContent(), uri -> {
                if (uri != null) {
                    try {
                        java.io.InputStream inputStream = getContentResolver().openInputStream(uri);
                        Bitmap bitmap = android.graphics.BitmapFactory.decodeStream(inputStream);
                        if (bitmap != null) {
                            String base64 = com.example.meshlink.data.ImageUtils.bitmapToBase64(bitmap);
                            SharedPreferences prefs = getSharedPreferences("meshlink_prefs", MODE_PRIVATE);
                            prefs.edit().putString("user_profile_pic_base64", base64).apply();

                            com.example.meshlink.mesh.MeshCoordinator coord = com.example.meshlink.mesh.MeshCoordinator.getInstance(this);
                            coord.reloadProfile();
                            coord.broadcastAvatarUpdate(base64);

                            ivSettingsProfilePic.setImageBitmap(com.example.meshlink.data.ImageUtils.getCircularBitmap(bitmap));
                            ivSettingsProfilePic.setVisibility(View.VISIBLE);
                            Toast.makeText(this, "📸 Profile picture updated & synced across mesh!", Toast.LENGTH_SHORT).show();
                        }
                    } catch (Exception e) {
                        Toast.makeText(this, "Failed to load image: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                }
            });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        initViews();
        loadProfileData();
        setupSurvivalTools();
    }

    private void initViews() {
        findViewById(R.id.btnSettingsBack).setOnClickListener(v -> finish());

        tvSettingsAvatar = findViewById(R.id.tvSettingsAvatar);
        ivSettingsProfilePic = findViewById(R.id.ivSettingsProfilePic);
        tvSettingsName = findViewById(R.id.tvSettingsName);
        tvSettingsBio = findViewById(R.id.tvSettingsBio);
        tvSettingsMeshId = findViewById(R.id.tvSettingsMeshId);
        tvSirenStatus = findViewById(R.id.tvSirenStatus);
        tvStrobeStatus = findViewById(R.id.tvStrobeStatus);
        tvConfigServerUrl = findViewById(R.id.tvConfigServerUrl);

        btnToggleSiren = findViewById(R.id.btnToggleSiren);
        btnToggleStrobe = findViewById(R.id.btnToggleStrobe);

        findViewById(R.id.cardProfile).setOnClickListener(v -> startActivity(new Intent(this, ProfileEditActivity.class)));

        findViewById(R.id.btnShowQr).setOnClickListener(v -> showMyQrDialog());

        findViewById(R.id.rowServerUrl).setOnClickListener(v -> showServerUrlDialog());

        findViewById(R.id.rowViewPublicKey).setOnClickListener(v -> showPublicKeyDialog());

        View rowShare = findViewById(R.id.rowShareApp);
        if (rowShare != null) {
            rowShare.setOnClickListener(v -> shareAppApk());
        }

        findViewById(R.id.rowPanicWipe).setOnClickListener(v -> showPanicWipeConfirm());
    }

    private void shareAppApk() {
        new AlertDialog.Builder(this)
                .setTitle("📲 Share Nexus App APK")
                .setMessage("Choose how you want to send Nexus Offline Mesh Chat to a nearby device:")
                .setPositiveButton("WhatsApp / Bluetooth", (dialog, which) -> executeFileShare())
                .setNeutralButton("Wi-Fi Hotspot Link", (dialog, which) -> showLocalWifiShareDialog())
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void executeFileShare() {
        try {
            android.content.pm.ApplicationInfo appInfo = getApplicationInfo();
            java.io.File originalApk = new java.io.File(appInfo.sourceDir);

            java.io.File shareDir = new java.io.File(getCacheDir(), "shared_apk");
            if (!shareDir.exists()) shareDir.mkdirs();
            java.io.File shareApk = new java.io.File(shareDir, "Nexus_Offline_Chat.apk");

            if (!shareApk.exists() || shareApk.length() != originalApk.length()) {
                java.io.FileInputStream in = new java.io.FileInputStream(originalApk);
                java.io.FileOutputStream out = new java.io.FileOutputStream(shareApk);
                byte[] buf = new byte[16384];
                int len;
                while ((len = in.read(buf)) > 0) {
                    out.write(buf, 0, len);
                }
                in.close();
                out.close();
            }

            android.net.Uri apkUri = androidx.core.content.FileProvider.getUriForFile(
                    this,
                    getPackageName() + ".provider",
                    shareApk
            );

            Intent shareIntent = new Intent(Intent.ACTION_SEND);
            shareIntent.setType("application/vnd.android.package-archive");
            shareIntent.putExtra(Intent.EXTRA_STREAM, apkUri);
            shareIntent.putExtra(Intent.EXTRA_SUBJECT, "Nexus - Offline Mesh Chat APK");
            shareIntent.putExtra(Intent.EXTRA_TEXT, "Here is the Nexus Offline Mesh Chat APK! Install it to talk and call without Internet or SIM.");
            shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);

            startActivity(Intent.createChooser(shareIntent, "Share Nexus APK via WhatsApp, Bluetooth..."));
        } catch (Exception e) {
            Toast.makeText(this, "Could not share APK: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void showLocalWifiShareDialog() {
        String ipAddress = "192.168.49.1";
        try {
            for (java.util.Enumeration<java.net.NetworkInterface> en = java.net.NetworkInterface.getNetworkInterfaces(); en.hasMoreElements(); ) {
                java.net.NetworkInterface intf = en.nextElement();
                for (java.util.Enumeration<java.net.InetAddress> enumIpAddr = intf.getInetAddresses(); enumIpAddr.hasMoreElements(); ) {
                    java.net.InetAddress inetAddress = enumIpAddr.nextElement();
                    if (!inetAddress.isLoopbackAddress() && inetAddress instanceof java.net.Inet4Address) {
                        ipAddress = inetAddress.getHostAddress();
                        break;
                    }
                }
            }
        } catch (Exception ignored) {}

        String msg = "1. Turn ON Mobile Hotspot on this phone.\n"
                + "2. Tell the other phone to connect to your Wi-Fi Hotspot.\n"
                + "3. Open Chrome on their phone and go to:\n"
                + "   http://" + ipAddress + ":8888\n\n"
                + "The other phone can directly download and install Nexus APK!";

        new AlertDialog.Builder(this)
                .setTitle("🌐 Air-Gapped Wi-Fi Web Share")
                .setMessage(msg)
                .setPositiveButton("OK", null)
                .show();
    }

    private void loadProfileData() {
        SharedPreferences prefs = getSharedPreferences("meshlink_prefs", MODE_PRIVATE);
        CryptoManager crypto = CryptoManager.getInstance(this);

        tvSettingsName.setText(prefs.getString("user_name", "Abdul Zubair"));
        tvSettingsAvatar.setText(prefs.getString("user_emoji", "👤"));
        tvSettingsBio.setText(prefs.getString("user_bio", "Citizen / Peer Node"));
        tvSettingsMeshId.setText(crypto.getMyMeshId());

        String b64 = prefs.getString("user_profile_pic_base64", "");
        if (ivSettingsProfilePic != null) {
            if (!b64.isEmpty()) {
                Bitmap bmp = com.example.meshlink.data.ImageUtils.base64ToBitmap(b64);
                if (bmp != null) {
                    ivSettingsProfilePic.setImageBitmap(com.example.meshlink.data.ImageUtils.getCircularBitmap(bmp));
                    ivSettingsProfilePic.setVisibility(View.VISIBLE);
                } else {
                    ivSettingsProfilePic.setVisibility(View.GONE);
                }
            } else {
                ivSettingsProfilePic.setVisibility(View.GONE);
            }
        }

        tvConfigServerUrl.setText(prefs.getString("laptop_server_url", "http://192.168.137.1:8888"));
    }

    private void showMyQrDialog() {
        CryptoManager crypto = CryptoManager.getInstance(this);
        SharedPreferences prefs = getSharedPreferences("meshlink_prefs", MODE_PRIVATE);

        String localIp = com.example.meshlink.mesh.MeshCoordinator.getLocalIpAddress();
        String cleanName = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(prefs.getString("user_name", "Anonymous"));
        String payload = "meshlink://peer?id=" + crypto.getMyMeshId()
                + "&name=" + Uri.encode(cleanName)
                + "&pub=" + crypto.getMyPublicKeyBase64()
                + "&ip=" + localIp;

        try {
            BarcodeEncoder encoder = new BarcodeEncoder();
            Bitmap qrBitmap = encoder.encodeBitmap(payload, BarcodeFormat.QR_CODE, 400, 400);

            ImageView iv = new ImageView(this);
            iv.setImageBitmap(qrBitmap);
            iv.setPadding(32, 32, 32, 32);

            new AlertDialog.Builder(this)
                    .setTitle("Air-Gapped QR Identity")
                    .setMessage("Any MeshLink peer can scan this QR code to instantly verify your cryptographic identity and open an encrypted channel.")
                    .setView(iv)
                    .setPositiveButton("Close", null)
                    .setNeutralButton("SCAN QR CODE", (d, w) -> startActivity(new Intent(this, QrScanActivity.class)))
                    .show();
        } catch (Exception e) {
            Toast.makeText(this, "Failed to generate QR: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private void showServerUrlDialog() {
        SharedPreferences prefs = getSharedPreferences("meshlink_prefs", MODE_PRIVATE);
        final EditText input = new EditText(this);
        input.setText(prefs.getString("laptop_server_url", "http://192.168.137.1:8888"));

        new AlertDialog.Builder(this)
                .setTitle("Configure Laptop Server URL")
                .setMessage("Enter your laptop's Wi-Fi hotspot or local IP address and port:")
                .setView(input)
                .setPositiveButton("SAVE", (dialog, which) -> {
                    String url = input.getText().toString().trim();
                    if (!url.isEmpty()) {
                        prefs.edit().putString("laptop_server_url", url).apply();
                        tvConfigServerUrl.setText(url);
                        Toast.makeText(this, "Saved server URL", Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void showPublicKeyDialog() {
        CryptoManager crypto = CryptoManager.getInstance(this);
        String key = crypto.getMyPublicKeyBase64();

        new AlertDialog.Builder(this)
                .setTitle("Your RSA-2048 Public Key")
                .setMessage(key)
                .setPositiveButton("COPY KEY", (dialog, which) -> {
                    ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                    if (cm != null) {
                        cm.setPrimaryClip(ClipData.newPlainText("MeshLink Public Key", key));
                        Toast.makeText(this, "Public Key copied to clipboard!", Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton("Close", null)
                .show();
    }

    private void showPanicWipeConfirm() {
        View dialogView = getLayoutInflater().inflate(R.layout.dialog_confirm_danger, null);
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setView(dialogView)
                .create();
        if (dialog.getWindow() != null) {
            dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
        }

        dialogView.findViewById(R.id.btnDangerCancel).setOnClickListener(v -> dialog.dismiss());
        dialogView.findViewById(R.id.btnDangerConfirm).setOnClickListener(v -> {
            dialog.dismiss();
            MeshDatabase db = new MeshDatabase(this);
            db.clearAllData();

            getSharedPreferences("meshlink_prefs", MODE_PRIVATE).edit().clear().apply();
            getSharedPreferences("meshlink_crypto_keystore", MODE_PRIVATE).edit().clear().apply();
            getSharedPreferences("meshlink_social_graph", MODE_PRIVATE).edit().clear().apply();

            Toast.makeText(this, "Data wiped. Restarting MeshLink...", Toast.LENGTH_LONG).show();

            Intent restart = new Intent(this, SetupActivity.class);
            restart.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(restart);
            finish();
        });

        dialog.show();
    }

    private void setupSurvivalTools() {
        btnToggleSiren.setOnClickListener(v -> toggleSiren());
        btnToggleStrobe.setOnClickListener(v -> toggleStrobe());
    }

    private void toggleSiren() {
        if (!isSirenActive) {
            isSirenActive = true;
            btnToggleSiren.setText("STOP");
            tvSirenStatus.setText("Loud alarm siren emitting!");
            tvSirenStatus.setTextColor(getResources().getColor(R.color.danger_red));

            sirenThread = new Thread(() -> {
                int sampleRate = 44100;
                int minBufSize = AudioTrack.getMinBufferSize(sampleRate, AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT);
                sirenAudioTrack = new AudioTrack(AudioManager.STREAM_ALARM, sampleRate,
                        AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT, minBufSize, AudioTrack.MODE_STREAM);
                sirenAudioTrack.play();

                short[] buffer = new short[minBufSize];
                double phase = 0;
                double freq = 900;
                boolean ascending = true;

                while (isSirenActive) {
                    for (int i = 0; i < buffer.length; i++) {
                        buffer[i] = (short) (Math.sin(phase) * 32767);
                        phase += 2 * Math.PI * freq / sampleRate;
                        if (phase > 2 * Math.PI) phase -= 2 * Math.PI;

                        if (ascending) {
                            freq += 0.05;
                            if (freq > 1400) ascending = false;
                        } else {
                            freq -= 0.05;
                            if (freq < 800) ascending = true;
                        }
                    }
                    sirenAudioTrack.write(buffer, 0, buffer.length);
                }
            });
            sirenThread.start();
        } else {
            stopSiren();
        }
    }

    private void stopSiren() {
        isSirenActive = false;
        btnToggleSiren.setText("START");
        tvSirenStatus.setText("Play high-frequency audio beacon");
        tvSirenStatus.setTextColor(getResources().getColor(R.color.text_secondary));
        try {
            if (sirenAudioTrack != null) {
                sirenAudioTrack.stop();
                sirenAudioTrack.release();
            }
        } catch (Exception ignored) {}
    }

    private void toggleStrobe() {
        if (!isStrobeActive) {
            isStrobeActive = true;
            btnToggleStrobe.setText("STOP");
            tvStrobeStatus.setText("Morse SOS (... --- ...) strobe flashing!");
            tvStrobeStatus.setTextColor(getResources().getColor(R.color.warning_orange));

            strobeThread = new Thread(() -> {
                CameraManager cm = (CameraManager) getSystemService(Context.CAMERA_SERVICE);
                try {
                    String cameraId = cm != null && cm.getCameraIdList().length > 0 ? cm.getCameraIdList()[0] : null;
                    if (cameraId == null) return;

                    // Morse SOS: 3 short (150ms), 3 long (450ms), 3 short (150ms)
                    int[] pattern = {150, 100, 150, 100, 150, 300, 450, 100, 450, 100, 450, 300, 150, 100, 150, 100, 150, 800};

                    while (isStrobeActive) {
                        for (int i = 0; i < pattern.length && isStrobeActive; i++) {
                            boolean on = (i % 2 == 0);
                            cm.setTorchMode(cameraId, on);
                            Thread.sleep(pattern[i]);
                        }
                    }
                    cm.setTorchMode(cameraId, false);
                } catch (Exception ignored) {}
            });
            strobeThread.start();
        } else {
            stopStrobe();
        }
    }

    private void stopStrobe() {
        isStrobeActive = false;
        btnToggleStrobe.setText("FLASH");
        tvStrobeStatus.setText("Flash LED camera in SOS pattern");
        tvStrobeStatus.setTextColor(getResources().getColor(R.color.text_secondary));
        try {
            CameraManager cm = (CameraManager) getSystemService(Context.CAMERA_SERVICE);
            if (cm != null && cm.getCameraIdList().length > 0) {
                cm.setTorchMode(cm.getCameraIdList()[0], false);
            }
        } catch (Exception ignored) {}
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadProfileData();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        stopSiren();
        stopStrobe();
    }
}
