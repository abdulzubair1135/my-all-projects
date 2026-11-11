package com.example.meshlink.settings;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.example.meshlink.R;
import com.example.meshlink.calls.VideoCallActivity;
import com.example.meshlink.calls.VoiceCallActivity;
import com.example.meshlink.chat.ChatActivity;
import com.example.meshlink.mesh.MeshCoordinator;
import com.example.meshlink.social.FollowManager;
import com.google.zxing.ResultPoint;
import com.journeyapps.barcodescanner.BarcodeCallback;
import com.journeyapps.barcodescanner.BarcodeResult;
import com.journeyapps.barcodescanner.DecoratedBarcodeView;

import java.util.List;

public class QrScanActivity extends AppCompatActivity {

    private static final String TAG = "QrScanActivity";
    private DecoratedBarcodeView barcodeScanner;
    private TextView tvQrStatus;
    private boolean isTorchOn = false;
    private boolean isScanned = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_qr_scan);

        barcodeScanner = findViewById(R.id.barcodeScanner);
        tvQrStatus = findViewById(R.id.tvQrStatus);

        findViewById(R.id.btnQrBack).setOnClickListener(v -> finish());

        ImageView btnTorch = findViewById(R.id.btnToggleTorch);
        if (btnTorch != null) {
            btnTorch.setOnClickListener(v -> {
                if (barcodeScanner != null) {
                    isTorchOn = !isTorchOn;
                    if (isTorchOn) barcodeScanner.setTorchOn();
                    else barcodeScanner.setTorchOff();
                }
            });
        }

        if (barcodeScanner != null) {
            barcodeScanner.setStatusText(""); // Hide default zxing status label
            barcodeScanner.decodeContinuous(new BarcodeCallback() {
                @Override
                public void barcodeResult(BarcodeResult result) {
                    if (result != null && result.getText() != null && !isScanned) {
                        isScanned = true;
                        handleScannedData(result.getText());
                    }
                }

                @Override
                public void possibleResultPoints(List<ResultPoint> resultPoints) {}
            });
        }

        checkCameraPermission();
    }

    private void checkCameraPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.CAMERA}, 101);
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == 101 && grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            if (barcodeScanner != null) {
                barcodeScanner.resume();
            }
        } else {
            Toast.makeText(this, "Camera permission required to scan QR codes", Toast.LENGTH_SHORT).show();
            finish();
        }
    }

    private void handleScannedData(String data) {
        Log.d(TAG, "Scanned QR data: " + data);
        runOnUiThread(() -> {
            String peerId = "";
            String peerName = "Nexus Peer";
            String pubKey = "";
            String peerIp = "";

            if (data.startsWith("meshlink://peer")) {
                try {
                    Uri uri = Uri.parse(data);
                    peerId = uri.getQueryParameter("id");
                    String n = uri.getQueryParameter("name");
                    if (n != null && !n.isEmpty()) peerName = n;
                    pubKey = uri.getQueryParameter("pub");
                    peerIp = uri.getQueryParameter("ip");
                } catch (Exception e) {
                    Log.e(TAG, "Failed to parse meshlink URI: " + e.getMessage());
                }
            } else {
                peerId = data.trim();
                peerName = "Peer " + peerId.substring(0, Math.min(6, peerId.length()));
            }

            if (peerId == null || peerId.isEmpty()) {
                peerId = "Peer_" + System.currentTimeMillis();
            }

            final String fPeerId = peerId;
            final String fPeerName = MeshCoordinator.cleanPeerName(peerName);
            final String fPeerIp = (peerIp != null && !peerIp.isEmpty()) ? peerIp : "192.168.49.1";

            // 1. Follow & Save peer credentials
            FollowManager.getInstance(this).followPeer(fPeerId, fPeerName, pubKey, "👤", "Scanned via QR");

            // 2. Direct P2P connect if IP available
            if (peerIp != null && !peerIp.isEmpty()) {
                MeshCoordinator.getInstance(this).connectDirectToPeer(peerIp, 8988);
            }

            // 3. Show instant Action Dialog with sleek custom UI
            View dialogView = getLayoutInflater().inflate(R.layout.dialog_peer_action, null);
            AlertDialog dialog = new AlertDialog.Builder(this)
                    .setView(dialogView)
                    .setCancelable(false)
                    .create();
            if (dialog.getWindow() != null) {
                dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
            }

            TextView tvName = dialogView.findViewById(R.id.tvPeerName);
            TextView tvAvatar = dialogView.findViewById(R.id.tvPeerAvatar);
            TextView tvNodeId = dialogView.findViewById(R.id.tvPeerNodeId);
            TextView tvKey = dialogView.findViewById(R.id.tvPeerKeyFingerprint);
            Button btnChat = dialogView.findViewById(R.id.btnOpenChat);
            Button btnClose = dialogView.findViewById(R.id.btnClosePeerDialog);

            if (tvName != null) tvName.setText(fPeerName);
            if (tvAvatar != null) tvAvatar.setText((fPeerName != null && !fPeerName.isEmpty()) ? fPeerName.substring(0, 1).toUpperCase() : "P");
            if (tvNodeId != null) tvNodeId.setText("Node ID: " + fPeerId + (fPeerIp.length() > 0 ? " (" + fPeerIp + ")" : ""));
            if (tvKey != null) tvKey.setText("Public Key: " + (pubKey.length() > 18 ? pubKey.substring(0, 18) + "..." : pubKey));

            if (btnChat != null) {
                btnChat.setOnClickListener(v -> {
                    dialog.dismiss();
                    Intent intent = new Intent(this, ChatActivity.class);
                    intent.putExtra("PEER_ID", fPeerName);
                    intent.putExtra("DISPLAY_NAME", fPeerName);
                    intent.putExtra("MY_ID", MeshCoordinator.cleanPeerName(MeshCoordinator.getInstance(this).getMyDisplayName()));
                    startActivity(intent);
                    finish();
                });
            }

            if (btnClose != null) {
                btnClose.setOnClickListener(v -> {
                    dialog.dismiss();
                    finish();
                });
            }

            dialog.show();
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (barcodeScanner != null) {
            barcodeScanner.resume();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (barcodeScanner != null) {
            barcodeScanner.pause();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (barcodeScanner != null) {
            barcodeScanner.pause();
        }
    }
}
