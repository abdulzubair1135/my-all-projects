package com.example.meshlink.chat;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Base64;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.meshlink.R;
import com.example.meshlink.calls.VideoCallActivity;
import com.example.meshlink.calls.VoiceCallActivity;
import com.example.meshlink.data.ChatMessageModel;
import com.example.meshlink.data.LocalSosModel;
import com.example.meshlink.data.MeshDatabase;
import com.example.meshlink.mesh.MeshCoordinator;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;

public class ChatActivity extends AppCompatActivity implements MeshCoordinator.MeshEventListener {

    private String myId;
    private String peerId;
    private String displayName;

    private TextView tvChatTitle, tvChatSubtitle, tvChatAvatar;
    private ImageView ivChatAvatarPic;
    private RecyclerView rvMessages;
    private EditText etMessageInput;
    private ImageView ivSendIcon;
    private ChatAdapter adapter;
    private final List<ChatMessageModel> messageList = new ArrayList<>();

    private MeshDatabase db;
    private MeshCoordinator meshCoordinator;

    private ActivityResultLauncher<String> pickImageLauncher;
    private ActivityResultLauncher<String> pickVideoLauncher;
    private ActivityResultLauncher<Uri> takePhotoLauncher;
    private Uri cameraTempUri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat);

        peerId = getIntent().getStringExtra("PEER_ID");
        if (peerId == null) peerId = "ALL";
        if (!peerId.equals("ALL")) {
            peerId = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(peerId);
        }

        displayName = getIntent().getStringExtra("DISPLAY_NAME");
        if (displayName == null) {
            displayName = peerId.equals("ALL") ? "Public Broadcast" : peerId;
        } else if (!peerId.equals("ALL")) {
            displayName = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(displayName);
        }

        meshCoordinator = MeshCoordinator.getInstance(this);
        myId = getIntent().getStringExtra("MY_ID");
        if (myId == null) {
            myId = meshCoordinator.getMyDisplayName();
        }
        myId = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(myId);

        db = new MeshDatabase(this);

        setupMediaLaunchers();
        setupKeyboardInsetListener();
        initViews();
        setupCallButtons();
        loadMessages();
    }

    private void setupMediaLaunchers() {
        pickImageLauncher = registerForActivityResult(new ActivityResultContracts.GetContent(), uri -> {
            if (uri != null) processAndSendImage(uri);
        });

        pickVideoLauncher = registerForActivityResult(new ActivityResultContracts.GetContent(), uri -> {
            if (uri != null) processAndSendVideo(uri);
        });

        takePhotoLauncher = registerForActivityResult(new ActivityResultContracts.TakePicture(), success -> {
            if (Boolean.TRUE.equals(success) && cameraTempUri != null) {
                processAndSendImage(cameraTempUri);
            }
        });
    }

    private void setupKeyboardInsetListener() {
        View rootLayout = findViewById(R.id.rootChatLayout);
        if (rootLayout != null) {
            ViewCompat.setOnApplyWindowInsetsListener(rootLayout, (v, insets) -> {
                int imeHeight = insets.getInsets(WindowInsetsCompat.Type.ime()).bottom;
                int systemBarsHeight = insets.getInsets(WindowInsetsCompat.Type.systemBars()).bottom;
                int topBarsHeight = insets.getInsets(WindowInsetsCompat.Type.systemBars()).top;
                int bottomPadding = Math.max(imeHeight, systemBarsHeight);
                v.setPadding(0, topBarsHeight, 0, bottomPadding);

                if (rvMessages != null && adapter != null && adapter.getItemCount() > 0) {
                    rvMessages.scrollToPosition(adapter.getItemCount() - 1);
                }
                return WindowInsetsCompat.CONSUMED;
            });
        }
    }

    private void initViews() {
        findViewById(R.id.btnBack).setOnClickListener(v -> finish());

        tvChatTitle = findViewById(R.id.tvChatTitle);
        tvChatSubtitle = findViewById(R.id.tvChatSubtitle);
        tvChatAvatar = findViewById(R.id.tvChatAvatar);
        ivChatAvatarPic = findViewById(R.id.ivChatAvatarPic);
        rvMessages = findViewById(R.id.rvMessages);
        etMessageInput = findViewById(R.id.etMessageInput);
        ivSendIcon = findViewById(R.id.ivSendIcon);

        tvChatTitle.setText(displayName);
        tvChatAvatar.setText(peerId.equals("ALL") ? "ALL" : displayName.substring(0, Math.min(1, displayName.length())).toUpperCase());
        tvChatSubtitle.setText(peerId.equals("ALL") ? "Mesh Broadcast • All Nodes" : "Online • BLE Mesh");
        loadPeerAvatar();

        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setStackFromEnd(true);
        rvMessages.setLayoutManager(layoutManager);

        adapter = new ChatAdapter(this, messageList, myId);
        rvMessages.setAdapter(adapter);

        findViewById(R.id.btnSend).setOnClickListener(v -> sendMessage());

        findViewById(R.id.btnAttach).setOnClickListener(v -> showMediaAttachDialog());

        findViewById(R.id.btnCamera).setOnClickListener(v -> launchCamera());
    }

    private void showMediaAttachDialog() {
        View dialogView = getLayoutInflater().inflate(R.layout.dialog_media_attach, null);
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setView(dialogView)
                .create();
        if (dialog.getWindow() != null) {
            dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
        }

        dialogView.findViewById(R.id.btnDialogCamera).setOnClickListener(v -> {
            dialog.dismiss();
            launchCamera();
        });

        dialogView.findViewById(R.id.btnDialogGalleryPhoto).setOnClickListener(v -> {
            dialog.dismiss();
            pickImageLauncher.launch("image/*");
        });

        dialogView.findViewById(R.id.btnDialogGalleryVideo).setOnClickListener(v -> {
            dialog.dismiss();
            pickVideoLauncher.launch("video/*");
        });

        dialogView.findViewById(R.id.btnDialogCancel).setOnClickListener(v -> dialog.dismiss());

        dialog.show();
    }

    private void launchCamera() {
        try {
            File mediaDir = new File(getCacheDir(), "camera");
            if (!mediaDir.exists()) mediaDir.mkdirs();
            File photoFile = new File(mediaDir, "cam_" + System.currentTimeMillis() + ".jpg");
            cameraTempUri = androidx.core.content.FileProvider.getUriForFile(this, getPackageName() + ".provider", photoFile);
            takePhotoLauncher.launch(cameraTempUri);
        } catch (Exception e) {
            Toast.makeText(this, "Cannot open camera: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private void processAndSendImage(Uri uri) {
        if (meshCoordinator.getConnectedPeerCount() == 0) {
            Toast.makeText(this, "Connecting to peer... Photo will send automatically once connected!", Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(this, "Sending photo...", Toast.LENGTH_SHORT).show();
        }
        Executors.newSingleThreadExecutor().execute(() -> {
            try {
                InputStream is = getContentResolver().openInputStream(uri);
                Bitmap bitmap = BitmapFactory.decodeStream(is);
                if (is != null) is.close();
                if (bitmap == null) return;

                int maxDim = 1280;
                int w = bitmap.getWidth();
                int h = bitmap.getHeight();
                if (w > maxDim || h > maxDim) {
                    float scale = Math.min((float) maxDim / w, (float) maxDim / h);
                    bitmap = Bitmap.createScaledBitmap(bitmap, Math.round(w * scale), Math.round(h * scale), true);
                }

                File mediaDir = new File(getFilesDir(), "mesh_media");
                if (!mediaDir.exists()) mediaDir.mkdirs();
                File localFile = new File(mediaDir, "send_img_" + System.currentTimeMillis() + ".jpg");
                FileOutputStream fos = new FileOutputStream(localFile);
                bitmap.compress(Bitmap.CompressFormat.JPEG, 85, fos);
                fos.flush();
                fos.close();

                meshCoordinator.sendFileMessage(peerId, "Photo", ChatMessageModel.TYPE_IMAGE, localFile);

                runOnUiThread(this::loadMessages);
            } catch (Exception e) {
                runOnUiThread(() -> Toast.makeText(this, "Failed to send photo: " + e.getMessage(), Toast.LENGTH_SHORT).show());
            }
        });
    }

    private void processAndSendVideo(Uri uri) {
        if (meshCoordinator.getConnectedPeerCount() == 0) {
            Toast.makeText(this, "Connecting to peer... Video will send automatically once connected!", Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(this, "Preparing video for sending...", Toast.LENGTH_SHORT).show();
        }
        Executors.newSingleThreadExecutor().execute(() -> {
            try {
                File mediaDir = new File(getFilesDir(), "mesh_media");
                if (!mediaDir.exists()) mediaDir.mkdirs();
                File localFile = new File(mediaDir, "send_vid_" + System.currentTimeMillis() + ".mp4");

                InputStream is = getContentResolver().openInputStream(uri);
                if (is == null) return;
                FileOutputStream fos = new FileOutputStream(localFile);
                byte[] buf = new byte[32768];
                int read;
                while ((read = is.read(buf)) != -1) {
                    fos.write(buf, 0, read);
                }
                fos.flush();
                fos.close();
                is.close();

                if (localFile.length() == 0) {
                    runOnUiThread(() -> Toast.makeText(this, "Video is empty", Toast.LENGTH_SHORT).show());
                    return;
                }

                meshCoordinator.sendFileMessage(peerId, "Video", ChatMessageModel.TYPE_VIDEO, localFile);

                runOnUiThread(this::loadMessages);
            } catch (Exception e) {
                runOnUiThread(() -> Toast.makeText(this, "Failed to send video: " + e.getMessage(), Toast.LENGTH_SHORT).show());
            }
        });
    }

    private void setupCallButtons() {
        findViewById(R.id.btnVoiceCall).setOnClickListener(v -> {
            if (peerId.equals("ALL")) {
                Toast.makeText(this, "Cannot voice call broadcast channel. Pick a peer!", Toast.LENGTH_SHORT).show();
                return;
            }
            Intent callIntent = new Intent(this, VoiceCallActivity.class);
            callIntent.putExtra("PEER_NAME", displayName);
            callIntent.putExtra("PEER_ID", peerId);
            String pIp = meshCoordinator.getPeerIp(peerId);
            if (pIp != null) callIntent.putExtra("PEER_IP", pIp);
            callIntent.putExtra("IS_INCOMING", false);
            callIntent.putExtra("CALL_STATE", "CALLING");
            startActivity(callIntent);
        });

        findViewById(R.id.btnVideoCall).setOnClickListener(v -> {
            if (peerId.equals("ALL")) {
                Toast.makeText(this, "Cannot video call broadcast channel. Pick a peer!", Toast.LENGTH_SHORT).show();
                return;
            }
            Intent callIntent = new Intent(this, VideoCallActivity.class);
            callIntent.putExtra("PEER_NAME", displayName);
            callIntent.putExtra("PEER_ID", peerId);
            String pIp = meshCoordinator.getPeerIp(peerId);
            if (pIp != null) callIntent.putExtra("PEER_IP", pIp);
            callIntent.putExtra("IS_INCOMING", false);
            callIntent.putExtra("CALL_STATE", "CALLING");
            startActivity(callIntent);
        });
    }

    private void sendMessage() {
        String text = etMessageInput.getText().toString().trim();
        if (text.isEmpty()) return;

        meshCoordinator.sendChatMessage(peerId, text, ChatMessageModel.TYPE_TEXT, "");
        etMessageInput.setText("");
        loadMessages();
    }

    private void loadMessages() {
        messageList.clear();
        messageList.addAll(db.getConversation(myId, peerId));
        adapter.notifyDataSetChanged();
        if (!messageList.isEmpty()) {
            rvMessages.scrollToPosition(messageList.size() - 1);
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        meshCoordinator.addListener(this);
        loadPeerAvatar();
        loadMessages();
    }

    private void loadPeerAvatar() {
        if ("ALL".equalsIgnoreCase(peerId)) {
            if (ivChatAvatarPic != null) ivChatAvatarPic.setVisibility(View.GONE);
            if (tvChatAvatar != null) tvChatAvatar.setText("ALL");
            return;
        }
        android.graphics.Bitmap bmp = meshCoordinator.getPeerAvatarBitmap(displayName);
        if (bmp == null && peerId != null) {
            bmp = meshCoordinator.getPeerAvatarBitmap(peerId);
        }
        if (bmp != null && ivChatAvatarPic != null) {
            ivChatAvatarPic.setImageBitmap(com.example.meshlink.data.ImageUtils.getCircularBitmap(bmp));
            ivChatAvatarPic.setVisibility(View.VISIBLE);
            if (tvChatAvatar != null) tvChatAvatar.setVisibility(View.GONE);
        } else if (ivChatAvatarPic != null) {
            ivChatAvatarPic.setVisibility(View.GONE);
            if (tvChatAvatar != null) tvChatAvatar.setVisibility(View.VISIBLE);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        meshCoordinator.removeListener(this);
    }

    @Override
    public void onPeerFound(String endpointId, String peerName) {
        runOnUiThread(this::loadPeerAvatar);
    }

    @Override
    public void onPeerLost(String endpointId) {}

    @Override
    public void onPeerConnected(String endpointId, String peerName) {
        runOnUiThread(() -> {
            tvChatSubtitle.setText("Connected • BLE / WiFi");
            loadPeerAvatar();
        });
    }

    @Override
    public void onPeerDisconnected(String endpointId) {
        runOnUiThread(() -> tvChatSubtitle.setText("Waiting for peer..."));
    }

    @Override
    public void onMessageReceived(ChatMessageModel message) {
        if (message.sender.equals(peerId) || message.target.equals("ALL") || message.target.equals(peerId)) {
            runOnUiThread(() -> {
                loadMessages();
                loadPeerAvatar();
            });
        }
    }

    @Override
    public void onSosReceived(LocalSosModel sos) {}
}
