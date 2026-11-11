package com.example.meshlink.setup;

import android.Manifest;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.meshlink.R;
import com.example.meshlink.main.MainActivity;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

import java.util.ArrayList;
import java.util.List;

public class SetupActivity extends AppCompatActivity {

    private TextView tvSelectedEmoji, tvMyMeshId;
    private TextInputEditText etName, etBio;
    private RadioGroup rgRole;
    private RadioButton rbCitizen, rbVolunteer;
    private MaterialButton btnContinue;
    private android.widget.ImageView ivSetupProfilePic;
    private String selectedProfilePicBase64 = "";
    private String selectedEmoji = "👤";
    private static final int PERMISSION_REQ_CODE = 1001;

    private final androidx.activity.result.ActivityResultLauncher<String> pickPhotoLauncher =
            registerForActivityResult(new androidx.activity.result.contract.ActivityResultContracts.GetContent(), uri -> {
                if (uri != null) {
                    try {
                        java.io.InputStream inputStream = getContentResolver().openInputStream(uri);
                        android.graphics.Bitmap bitmap = android.graphics.BitmapFactory.decodeStream(inputStream);
                        if (bitmap != null) {
                            selectedProfilePicBase64 = com.example.meshlink.data.ImageUtils.bitmapToBase64(bitmap);
                            if (ivSetupProfilePic != null) {
                                ivSetupProfilePic.setImageBitmap(com.example.meshlink.data.ImageUtils.getCircularBitmap(bitmap));
                                ivSetupProfilePic.setVisibility(android.view.View.VISIBLE);
                            }
                            Toast.makeText(this, "Profile photo selected!", Toast.LENGTH_SHORT).show();
                        }
                    } catch (Exception e) {
                        Toast.makeText(this, "Failed to load photo: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                }
            });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        SharedPreferences prefs = getSharedPreferences("meshlink_prefs", MODE_PRIVATE);
        boolean isConfigured = prefs.getBoolean("is_configured", false);
        if (isConfigured && !getIntent().getBooleanExtra("reconfigure", false)) {
            startActivity(new Intent(this, MainActivity.class));
            finish();
            return;
        }

        setContentView(R.layout.activity_setup);

        tvSelectedEmoji = findViewById(R.id.tvSelectedEmoji);
        ivSetupProfilePic = findViewById(R.id.ivSetupProfilePic);
        tvMyMeshId = findViewById(R.id.tvMyMeshId);
        etName = findViewById(R.id.etName);
        etBio = findViewById(R.id.etBio);
        rgRole = findViewById(R.id.rgRole);
        rbCitizen = findViewById(R.id.rbCitizen);
        rbVolunteer = findViewById(R.id.rbVolunteer);
        btnContinue = findViewById(R.id.btnContinue);

        android.view.View flAvatar = findViewById(R.id.flSetupAvatarContainer);
        if (flAvatar != null) {
            flAvatar.setOnClickListener(v -> pickPhotoLauncher.launch("image/*"));
        }
        android.view.View btnPickPhoto = findViewById(R.id.btnPickSetupPhoto);
        if (btnPickPhoto != null) {
            btnPickPhoto.setOnClickListener(v -> pickPhotoLauncher.launch("image/*"));
        }

        // Display Cryptographic Mesh ID
        com.example.meshlink.crypto.CryptoManager crypto = com.example.meshlink.crypto.CryptoManager.getInstance(this);
        if (tvMyMeshId != null) {
            tvMyMeshId.setText(crypto.getMyMeshId());
        }

        View cardMeshId = findViewById(R.id.cardMeshIdContainer);
        android.view.View.OnClickListener copyMeshIdListener = v -> {
            if (tvMyMeshId != null) {
                String id = tvMyMeshId.getText().toString();
                android.content.ClipboardManager cm = (android.content.ClipboardManager) getSystemService(android.content.Context.CLIPBOARD_SERVICE);
                if (cm != null) {
                    cm.setPrimaryClip(android.content.ClipData.newPlainText("Nexus Mesh ID", id));
                    Toast.makeText(this, "📋 Node ID copied to clipboard!", Toast.LENGTH_SHORT).show();
                }
            }
        };
        if (cardMeshId != null) cardMeshId.setOnClickListener(copyMeshIdListener);
        View btnCopy = findViewById(R.id.btnCopyMeshId);
        if (btnCopy != null) btnCopy.setOnClickListener(copyMeshIdListener);

        setupEmojiSelectors();

        String savedName = prefs.getString("user_name", "Abdul Zubair");
        String savedEmoji = prefs.getString("user_emoji", "👤");
        String savedBio = prefs.getString("user_bio", "Mesh Citizen");
        selectedEmoji = savedEmoji;
        tvSelectedEmoji.setText(selectedEmoji);
        etName.setText(savedName);
        if (etBio != null) etBio.setText(savedBio);

        // Highlight saved emoji
        int[] ids = {R.id.emoji1, R.id.emoji2, R.id.emoji3, R.id.emoji4, R.id.emoji5};
        for (int id : ids) {
            TextView tv = findViewById(id);
            if (tv != null) {
                boolean isMatch = tv.getText().toString().equals(savedEmoji);
                tv.setBackgroundResource(isMatch ? R.drawable.bg_emoji_selected : R.drawable.bg_emoji_normal);
            }
        }

        btnContinue.setOnClickListener(v -> handleContinue());

        requestNeededPermissions();
    }

    private void setupEmojiSelectors() {
        int[] ids = {R.id.emoji1, R.id.emoji2, R.id.emoji3, R.id.emoji4, R.id.emoji5};
        for (int id : ids) {
            TextView tv = findViewById(id);
            if (tv != null) {
                tv.setOnClickListener(v -> {
                    selectedEmoji = tv.getText().toString();
                    tvSelectedEmoji.setText(selectedEmoji);
                    if (ivSetupProfilePic != null) {
                        ivSetupProfilePic.setVisibility(android.view.View.GONE);
                    }
                    for (int otherId : ids) {
                        TextView otherTv = findViewById(otherId);
                        if (otherTv != null) {
                            otherTv.setBackgroundResource(otherId == id ? R.drawable.bg_emoji_selected : R.drawable.bg_emoji_normal);
                        }
                    }
                });
            }
        }
    }

    private void handleContinue() {
        String name = etName.getText() != null ? etName.getText().toString().trim() : "";
        String bio = etBio.getText() != null ? etBio.getText().toString().trim() : "Mesh Citizen";
        if (name.isEmpty()) {
            Toast.makeText(this, "Please enter your name or call sign", Toast.LENGTH_SHORT).show();
            return;
        }

        String role = (rbVolunteer != null && rbVolunteer.isChecked()) ? "VOLUNTEER" : "CITIZEN";

        com.example.meshlink.crypto.CryptoManager crypto = com.example.meshlink.crypto.CryptoManager.getInstance(this);

        SharedPreferences prefs = getSharedPreferences("meshlink_prefs", MODE_PRIVATE);
        SharedPreferences.Editor editor = prefs.edit()
                .putBoolean("is_configured", true)
                .putString("user_name", name)
                .putString("user_bio", bio)
                .putString("user_emoji", selectedEmoji)
                .putString("user_role", role)
                .putString("device_id", crypto.getMyMeshId());

        if (!selectedProfilePicBase64.isEmpty()) {
            editor.putString("user_profile_pic_base64", selectedProfilePicBase64);
        }
        editor.apply();

        com.example.meshlink.mesh.MeshCoordinator coordinator = com.example.meshlink.mesh.MeshCoordinator.getInstance(this);
        coordinator.reloadProfile();
        if (!selectedProfilePicBase64.isEmpty()) {
            coordinator.broadcastAvatarUpdate(selectedProfilePicBase64);
        }

        Toast.makeText(this, "Welcome to Nexus, " + name + "!", Toast.LENGTH_SHORT).show();
        startActivity(new Intent(this, MainActivity.class));
        finish();
    }

    private void requestNeededPermissions() {
        List<String> list = new ArrayList<>();
        list.add(Manifest.permission.ACCESS_FINE_LOCATION);
        list.add(Manifest.permission.ACCESS_COARSE_LOCATION);
        list.add(Manifest.permission.RECORD_AUDIO);
        list.add(Manifest.permission.CAMERA);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            list.add(Manifest.permission.BLUETOOTH_SCAN);
            list.add(Manifest.permission.BLUETOOTH_ADVERTISE);
            list.add(Manifest.permission.BLUETOOTH_CONNECT);
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            list.add(Manifest.permission.NEARBY_WIFI_DEVICES);
            list.add(Manifest.permission.POST_NOTIFICATIONS);
        }

        List<String> needed = new ArrayList<>();
        for (String perm : list) {
            if (ContextCompat.checkSelfPermission(this, perm) != PackageManager.PERMISSION_GRANTED) {
                needed.add(perm);
            }
        }

        if (!needed.isEmpty()) {
            ActivityCompat.requestPermissions(this, needed.toArray(new String[0]), PERMISSION_REQ_CODE);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    }
}
