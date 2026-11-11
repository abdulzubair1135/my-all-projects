package com.example.meshlink.settings;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;

import com.example.meshlink.R;
import com.example.meshlink.crypto.CryptoManager;
import com.example.meshlink.data.ImageUtils;
import com.example.meshlink.mesh.MeshCoordinator;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

import java.io.InputStream;

public class ProfileEditActivity extends AppCompatActivity {

    private ImageView ivEditAvatarPic;
    private TextView tvEditAvatarEmoji, tvEditMeshId;
    private TextInputEditText etEditName, etEditBio;
    private MaterialButton btnSaveProfile;

    private String selectedProfilePicBase64 = "";
    private String selectedEmoji = "👤";

    // 1. Camera Launcher (Direct Photo Capture)
    private final ActivityResultLauncher<Void> cameraLauncher =
            registerForActivityResult(new ActivityResultContracts.TakePicturePreview(), bitmap -> {
                if (bitmap != null) {
                    applyNewBitmap(bitmap);
                    Toast.makeText(this, "📸 Photo captured!", Toast.LENGTH_SHORT).show();
                }
            });

    // 2. Gallery Launcher (Choose from Photos)
    private final ActivityResultLauncher<String> galleryLauncher =
            registerForActivityResult(new ActivityResultContracts.GetContent(), uri -> {
                if (uri != null) {
                    try {
                        InputStream inputStream = getContentResolver().openInputStream(uri);
                        Bitmap bitmap = BitmapFactory.decodeStream(inputStream);
                        if (bitmap != null) {
                            applyNewBitmap(bitmap);
                            Toast.makeText(this, "🖼️ Photo selected from gallery!", Toast.LENGTH_SHORT).show();
                        }
                    } catch (Exception e) {
                        Toast.makeText(this, "Failed to load image: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                }
            });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_profile_edit);

        initViews();
        loadCurrentProfile();
    }

    private void initViews() {
        findViewById(R.id.btnProfileEditBack).setOnClickListener(v -> finish());

        ivEditAvatarPic = findViewById(R.id.ivEditAvatarPic);
        tvEditAvatarEmoji = findViewById(R.id.tvEditAvatarEmoji);
        tvEditMeshId = findViewById(R.id.tvEditMeshId);
        etEditName = findViewById(R.id.etEditName);
        etEditBio = findViewById(R.id.etEditBio);
        btnSaveProfile = findViewById(R.id.btnSaveProfile);

        // Avatar container tap -> choose gallery by default
        findViewById(R.id.flEditAvatarContainer).setOnClickListener(v -> galleryLauncher.launch("image/*"));

        // Camera button
        findViewById(R.id.btnTakePhoto).setOnClickListener(v -> cameraLauncher.launch(null));

        // Gallery button
        findViewById(R.id.btnChooseGallery).setOnClickListener(v -> galleryLauncher.launch("image/*"));

        // Remove photo button
        findViewById(R.id.btnRemovePhoto).setOnClickListener(v -> {
            selectedProfilePicBase64 = "";
            ivEditAvatarPic.setVisibility(View.GONE);
            tvEditAvatarEmoji.setVisibility(View.VISIBLE);
            Toast.makeText(this, "Profile photo removed", Toast.LENGTH_SHORT).show();
        });

        // Copy Mesh ID
        View.OnClickListener copyListener = v -> {
            if (tvEditMeshId != null) {
                String id = tvEditMeshId.getText().toString();
                ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                if (cm != null) {
                    cm.setPrimaryClip(ClipData.newPlainText("Nexus Mesh ID", id));
                    Toast.makeText(this, "📋 Node ID copied to clipboard!", Toast.LENGTH_SHORT).show();
                }
            }
        };
        findViewById(R.id.cardEditMeshId).setOnClickListener(copyListener);
        findViewById(R.id.btnCopyEditMeshId).setOnClickListener(copyListener);

        setupEmojiSelectors();

        btnSaveProfile.setOnClickListener(v -> handleSave());
    }

    private void setupEmojiSelectors() {
        int[] ids = {R.id.editEmoji1, R.id.editEmoji2, R.id.editEmoji3, R.id.editEmoji4, R.id.editEmoji5};
        for (int id : ids) {
            TextView tv = findViewById(id);
            if (tv != null) {
                tv.setOnClickListener(v -> {
                    selectedEmoji = tv.getText().toString();
                    tvEditAvatarEmoji.setText(selectedEmoji);
                    if (selectedProfilePicBase64.isEmpty()) {
                        ivEditAvatarPic.setVisibility(View.GONE);
                        tvEditAvatarEmoji.setVisibility(View.VISIBLE);
                    }
                    for (int otherId : ids) {
                        TextView other = findViewById(otherId);
                        if (other != null) {
                            other.setBackgroundResource(otherId == id ? R.drawable.bg_emoji_selected : R.drawable.bg_emoji_normal);
                        }
                    }
                });
            }
        }
    }

    private void loadCurrentProfile() {
        SharedPreferences prefs = getSharedPreferences("meshlink_prefs", MODE_PRIVATE);
        CryptoManager crypto = CryptoManager.getInstance(this);

        String name = prefs.getString("user_name", "Abdul Zubair");
        String bio = prefs.getString("user_bio", "Citizen / Peer Node");
        selectedEmoji = prefs.getString("user_emoji", "👤");
        selectedProfilePicBase64 = prefs.getString("user_profile_pic_base64", "");

        etEditName.setText(name);
        etEditBio.setText(bio);
        tvEditAvatarEmoji.setText(selectedEmoji);
        tvEditMeshId.setText(crypto.getMyMeshId());

        if (!selectedProfilePicBase64.isEmpty()) {
            Bitmap bmp = ImageUtils.base64ToBitmap(selectedProfilePicBase64);
            if (bmp != null) {
                ivEditAvatarPic.setImageBitmap(ImageUtils.getCircularBitmap(bmp));
                ivEditAvatarPic.setVisibility(View.VISIBLE);
            } else {
                ivEditAvatarPic.setVisibility(View.GONE);
            }
        } else {
            ivEditAvatarPic.setVisibility(View.GONE);
        }

        // Highlight matching emoji
        int[] ids = {R.id.editEmoji1, R.id.editEmoji2, R.id.editEmoji3, R.id.editEmoji4, R.id.editEmoji5};
        for (int id : ids) {
            TextView tv = findViewById(id);
            if (tv != null) {
                boolean match = tv.getText().toString().equals(selectedEmoji);
                tv.setBackgroundResource(match ? R.drawable.bg_emoji_selected : R.drawable.bg_emoji_normal);
            }
        }
    }

    private void applyNewBitmap(Bitmap bitmap) {
        if (bitmap == null) return;
        selectedProfilePicBase64 = ImageUtils.bitmapToBase64(bitmap);
        Bitmap circ = ImageUtils.getCircularBitmap(bitmap);
        ivEditAvatarPic.setImageBitmap(circ);
        ivEditAvatarPic.setVisibility(View.VISIBLE);
    }

    private void handleSave() {
        String name = etEditName.getText() != null ? etEditName.getText().toString().trim() : "";
        String bio = etEditBio.getText() != null ? etEditBio.getText().toString().trim() : "";

        if (name.isEmpty()) {
            Toast.makeText(this, "Please enter your name or call sign", Toast.LENGTH_SHORT).show();
            return;
        }

        SharedPreferences prefs = getSharedPreferences("meshlink_prefs", MODE_PRIVATE);
        prefs.edit()
                .putString("user_name", name)
                .putString("user_bio", bio)
                .putString("user_emoji", selectedEmoji)
                .putString("user_profile_pic_base64", selectedProfilePicBase64)
                .apply();

        // Reload profile in MeshCoordinator & broadcast avatar update across mesh
        MeshCoordinator coordinator = MeshCoordinator.getInstance(this);
        coordinator.reloadProfile();
        coordinator.broadcastAvatarUpdate(selectedProfilePicBase64);

        Toast.makeText(this, "✅ Profile updated & synced across offline mesh!", Toast.LENGTH_SHORT).show();
        setResult(RESULT_OK);
        finish();
    }
}
