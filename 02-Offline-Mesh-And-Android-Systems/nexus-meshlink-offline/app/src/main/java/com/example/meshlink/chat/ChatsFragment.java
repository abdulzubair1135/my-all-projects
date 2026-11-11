package com.example.meshlink.chat;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.meshlink.R;
import com.example.meshlink.data.ChatMessageModel;
import com.example.meshlink.data.ContactModel;
import com.example.meshlink.data.LocalSosModel;
import com.example.meshlink.data.MeshDatabase;
import com.example.meshlink.mesh.MeshCoordinator;
import com.example.meshlink.settings.QrScanActivity;
import com.example.meshlink.settings.SettingsActivity;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class ChatsFragment extends Fragment implements MeshCoordinator.MeshEventListener {

    private RecyclerView rvChats;
    private ChatsAdapter adapter;
    private final List<ContactModel> chatList = new ArrayList<>();
    private View llEmptyState;
    private EditText etSearchChats;
    private ImageView btnClearSearch;
    private MeshCoordinator meshCoordinator;
    private MeshDatabase db;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_chats, container, false);

        rvChats = v.findViewById(R.id.rvChats);
        llEmptyState = v.findViewById(R.id.llEmptyState);
        etSearchChats = v.findViewById(R.id.etSearchChats);
        btnClearSearch = v.findViewById(R.id.btnClearSearch);

        rvChats.setLayoutManager(new LinearLayoutManager(getContext()));

        db = new MeshDatabase(requireContext());
        meshCoordinator = MeshCoordinator.getInstance(requireContext());

        if (llEmptyState != null) {
            llEmptyState.setOnClickListener(view -> {
                if (meshCoordinator != null) {
                    meshCoordinator.refreshMesh();
                    android.widget.Toast.makeText(requireContext(), "Refreshing offline mesh & scanning...", android.widget.Toast.LENGTH_SHORT).show();
                    loadChats();
                }
            });
        }

        adapter = new ChatsAdapter(requireContext(), chatList, contact -> {
            Intent intent = new Intent(requireContext(), ChatActivity.class);
            String cleanPeer = MeshCoordinator.cleanPeerName(contact.peerId);
            intent.putExtra("PEER_ID", cleanPeer);
            intent.putExtra("DISPLAY_NAME", contact.displayName);
            intent.putExtra("MY_ID", MeshCoordinator.cleanPeerName(meshCoordinator.getMyDisplayName()));
            startActivity(intent);
        });
        rvChats.setAdapter(adapter);

        // WhatsApp-style Search Input & Clear
        if (etSearchChats != null) {
            etSearchChats.addTextChangedListener(new TextWatcher() {
                @Override
                public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

                @Override
                public void onTextChanged(CharSequence s, int start, int before, int count) {
                    String query = s != null ? s.toString() : "";
                    if (btnClearSearch != null) {
                        btnClearSearch.setVisibility(query.isEmpty() ? View.GONE : View.VISIBLE);
                    }
                    adapter.filter(query);
                }

                @Override
                public void afterTextChanged(Editable s) {}
            });
        }

        if (btnClearSearch != null) {
            btnClearSearch.setOnClickListener(view -> {
                if (etSearchChats != null) {
                    etSearchChats.setText("");
                }
            });
        }

        // Broadcast Channel click
        v.findViewById(R.id.llBroadcastChannel).setOnClickListener(view -> {
            Intent intent = new Intent(requireContext(), ChatActivity.class);
            intent.putExtra("PEER_ID", "ALL");
            intent.putExtra("DISPLAY_NAME", "Public Broadcast Channel");
            intent.putExtra("MY_ID", MeshCoordinator.cleanPeerName(meshCoordinator.getMyDisplayName()));
            startActivity(intent);
        });

        loadChats();
        return v;
    }

    @Override
    public void onResume() {
        super.onResume();
        if (meshCoordinator != null) {
            meshCoordinator.addListener(this);
        }
        loadChats();
    }

    @Override
    public void onPause() {
        super.onPause();
        if (meshCoordinator != null) {
            meshCoordinator.removeListener(this);
        }
    }

    public void loadChats() {
        if (getContext() == null) return;
        chatList.clear();

        String myName = MeshCoordinator.cleanPeerName(meshCoordinator.getMyDisplayName());

        // 1. Add chats from DB (unified & clean)
        List<ContactModel> fromDb = db.getRecentChats(myName);
        chatList.addAll(fromDb);

        // 2. Add connected peers not in DB yet, deduplicating on clean peer name
        Map<String, String> connected = meshCoordinator.getConnectedPeers();
        for (Map.Entry<String, String> entry : connected.entrySet()) {
            String peerName = MeshCoordinator.cleanPeerName(entry.getValue());
            if (peerName.equalsIgnoreCase(myName)) {
                continue;
            }

            boolean exists = false;
            for (ContactModel c : chatList) {
                if (c.peerId.equalsIgnoreCase(peerName) || c.displayName.equalsIgnoreCase(peerName)) {
                    c.isOnline = true;
                    exists = true;
                    break;
                }
            }
            String avatarLetter = peerName.substring(0, Math.min(1, peerName.length())).toUpperCase();
            if (!exists) {
                chatList.add(new ContactModel(peerName, peerName, avatarLetter, "Online now", 0, 0, true, "BLE"));
            }
        }

        adapter.updateData();
        if (llEmptyState != null) {
            llEmptyState.setVisibility(chatList.isEmpty() ? View.VISIBLE : View.GONE);
        }
    }

    @Override
    public void onPeerFound(String endpointId, String peerName) {
        if (getActivity() != null) getActivity().runOnUiThread(this::loadChats);
    }

    @Override
    public void onPeerLost(String endpointId) {
        if (getActivity() != null) getActivity().runOnUiThread(this::loadChats);
    }

    @Override
    public void onPeerConnected(String endpointId, String peerName) {
        if (getActivity() != null) getActivity().runOnUiThread(this::loadChats);
    }

    @Override
    public void onPeerDisconnected(String endpointId) {
        if (getActivity() != null) getActivity().runOnUiThread(this::loadChats);
    }

    @Override
    public void onMessageReceived(ChatMessageModel message) {
        if (getActivity() != null) getActivity().runOnUiThread(this::loadChats);
    }

    @Override
    public void onSosReceived(LocalSosModel sos) {}
}
