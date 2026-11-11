package com.example.nearmeshchat;

import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;

public class ChatActivity extends AppCompatActivity {

    public static ChatActivity activeInstance;
    private String myId, peerId;
    private MeshDatabase db;
    private RecyclerView rvMessages;
    private ChatAdapter adapter;
    private List<ChatMessageModel> messageList = new ArrayList<>();
    private EditText etInput;
    private TextView tvTitle, tvPeerStatus, tvRoutingMode;
    private Button btnToggleBleMesh;

    private boolean isForcedBleMesh = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat);
        activeInstance = this;

        myId = getIntent().getStringExtra("MY_ID");
        peerId = getIntent().getStringExtra("PEER_ID");
        if (peerId == null) peerId = "ALL";

        db = new MeshDatabase(this);

        tvTitle = findViewById(R.id.tvChatTitle);
        tvTitle.setText(peerId.equals("ALL") ? "Broadcast / Emergency Net" : peerId);

        tvPeerStatus = findViewById(R.id.tvPeerStatus);
        tvRoutingMode = findViewById(R.id.tvRoutingMode);
        btnToggleBleMesh = findViewById(R.id.btnToggleBleMesh);

        findViewById(R.id.btnChatBack).setOnClickListener(v -> finish());

        rvMessages = findViewById(R.id.rvChatMessages);
        etInput = findViewById(R.id.etChatMessageInput);
        
        View btnSend = findViewById(R.id.btnChatSend);

        // Bottom Nav bar listeners
        View navHome = findViewById(R.id.chatNavHome);
        if (navHome != null) navHome.setOnClickListener(v -> finish());

        View navMap = findViewById(R.id.chatNavMap);
        if (navMap != null) navMap.setOnClickListener(v -> {
            startActivity(new android.content.Intent(this, DisasterMapActivity.class));
            finish();
        });

        View navSettings = findViewById(R.id.chatNavSettings);
        if (navSettings != null) navSettings.setOnClickListener(v -> finish());

        // Filter tabs
        TextView tabNearby = findViewById(R.id.tabNearbyUsers);
        TextView tabRescue = findViewById(R.id.tabRescueTeams);
        TextView tabGeneral = findViewById(R.id.tabGeneralChat);

        if (tabNearby != null && tabRescue != null && tabGeneral != null) {
            tabNearby.setOnClickListener(v -> {
                tabNearby.setBackgroundColor(Color.parseColor("#FEF2F2"));
                tabNearby.setTextColor(Color.parseColor("#DC2626"));
                tabRescue.setBackgroundResource(R.drawable.bg_card_rounded);
                tabRescue.setTextColor(Color.parseColor("#64748B"));
                tabGeneral.setBackgroundResource(R.drawable.bg_card_rounded);
                tabGeneral.setTextColor(Color.parseColor("#64748B"));
                Toast.makeText(this, "👥 Filtering: Nearby Users Feed", Toast.LENGTH_SHORT).show();
            });

            tabRescue.setOnClickListener(v -> {
                tabRescue.setBackgroundColor(Color.parseColor("#FEF2F2"));
                tabRescue.setTextColor(Color.parseColor("#DC2626"));
                tabNearby.setBackgroundResource(R.drawable.bg_card_rounded);
                tabNearby.setTextColor(Color.parseColor("#64748B"));
                tabGeneral.setBackgroundResource(R.drawable.bg_card_rounded);
                tabGeneral.setTextColor(Color.parseColor("#64748B"));
                Toast.makeText(this, "🦺 Filtering: Official Rescue Teams", Toast.LENGTH_SHORT).show();
            });

            tabGeneral.setOnClickListener(v -> {
                tabGeneral.setBackgroundColor(Color.parseColor("#FEF2F2"));
                tabGeneral.setTextColor(Color.parseColor("#DC2626"));
                tabNearby.setBackgroundResource(R.drawable.bg_card_rounded);
                tabNearby.setTextColor(Color.parseColor("#64748B"));
                tabRescue.setBackgroundResource(R.drawable.bg_card_rounded);
                tabRescue.setTextColor(Color.parseColor("#64748B"));
                Toast.makeText(this, "💬 Filtering: General Community Broadcast", Toast.LENGTH_SHORT).show();
            });
        }


        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setStackFromEnd(true);
        rvMessages.setLayoutManager(layoutManager);

        adapter = new ChatAdapter(messageList, myId);
        rvMessages.setAdapter(adapter);

        updateNetworkRoutingUI();

        if (btnToggleBleMesh != null) {
            btnToggleBleMesh.setOnClickListener(v -> {
                isForcedBleMesh = !isForcedBleMesh;
                updateNetworkRoutingUI();
                if (isForcedBleMesh) {
                    Toast.makeText(this, "📡 Forced Offline BLE Mesh Mode ON", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(this, "🌐 Auto Route Mode Restored", Toast.LENGTH_SHORT).show();
                }
            });
        }

        loadMessages();
        sendSeenReceipts();

        btnSend.setOnClickListener(v -> {
            String text = etInput.getText().toString().trim();
            if (!text.isEmpty()) {
                if (MainActivity.mainInstance != null) {
                    boolean isOnline = isOnline() && !isForcedBleMesh;

                    MainActivity.mainInstance.dispatchNewPrivateMessage(peerId, text);
                    etInput.setText("");
                    loadMessages();

                    if (isOnline) {
                        Toast.makeText(this, "🌐 Sent via Cloud Network", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(this, "📡 Transmitted via BLE Peer-to-Peer Mesh!", Toast.LENGTH_SHORT).show();
                    }
                } else {
                    Toast.makeText(this, "Mesh engine offline", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private boolean isOnline() {
        ConnectivityManager cm = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
        if (cm == null) return false;
        Network net = cm.getActiveNetwork();
        if (net == null) return false;
        NetworkCapabilities cap = cm.getNetworkCapabilities(net);
        return cap != null && (cap.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) || cap.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR));
    }

    private void updateNetworkRoutingUI() {
        boolean online = isOnline() && !isForcedBleMesh;
        if (tvRoutingMode != null) {
            if (online) {
                tvRoutingMode.setText("🌐 Cloud Network Active • Real-Time High Speed");
                tvRoutingMode.setTextColor(Color.parseColor("#2563EB"));
            } else {
                tvRoutingMode.setText("📡 Offline Mode: BLE Nearby Mesh Active • Zero Internet Required");
                tvRoutingMode.setTextColor(Color.parseColor("#D97706"));
            }
        }
        if (tvPeerStatus != null) {
            if (online) {
                tvPeerStatus.setText("Online • Cloud Synced");
                tvPeerStatus.setTextColor(Color.parseColor("#16A34A"));
            } else {
                tvPeerStatus.setText("Offline Mesh • BLE Nodes");
                tvPeerStatus.setTextColor(Color.parseColor("#D97706"));
            }
        }
        if (btnToggleBleMesh != null) {
            if (online) {
                btnToggleBleMesh.setText("FORCE BLE");
                btnToggleBleMesh.setBackgroundColor(Color.parseColor("#1E293B"));
            } else {
                btnToggleBleMesh.setText("AUTO ROUTE");
                btnToggleBleMesh.setBackgroundColor(Color.parseColor("#D97706"));
            }
        }
    }

    public void refreshChat() {
        runOnUiThread(() -> {
            messageList.clear();
            messageList.addAll(db.getConversation(myId, peerId));
            if (adapter != null) {
                adapter.notifyDataSetChanged();
            }
            if (!messageList.isEmpty()) {
                rvMessages.scrollToPosition(messageList.size() - 1);
            }
        });
    }

    private void loadMessages() {
        messageList.clear();
        messageList.addAll(db.getConversation(myId, peerId));
        adapter.notifyDataSetChanged();
        if (!messageList.isEmpty()) {
            rvMessages.scrollToPosition(messageList.size() - 1);
        }
    }

    private void sendSeenReceipts() {
        if (MainActivity.mainInstance != null && !peerId.equals("ALL")) {
            MainActivity.mainInstance.dispatchSeenAck(peerId);
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        updateNetworkRoutingUI();
        sendSeenReceipts();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        activeInstance = null;
    }
}
