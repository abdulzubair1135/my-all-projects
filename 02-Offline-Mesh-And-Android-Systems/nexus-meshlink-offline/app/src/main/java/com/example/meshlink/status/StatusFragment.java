package com.example.meshlink.status;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.meshlink.R;
import com.example.meshlink.chat.ChatActivity;
import com.example.meshlink.data.ChatMessageModel;
import com.example.meshlink.data.LocalSosModel;
import com.example.meshlink.mesh.MeshCoordinator;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class StatusFragment extends Fragment implements MeshCoordinator.MeshEventListener {

    private BleRadarView bleRadarView;
    private TextView tvPeersInRange;
    private RecyclerView rvPeersList;
    private View llPeersEmptyState;
    private PeerAdapter adapter;
    private final List<PeerItem> peerItemList = new ArrayList<>();
    private MeshCoordinator meshCoordinator;

    public static class PeerItem {
        public String endpointId;
        public String peerName;
        public int hopCount = 1;
        public String routeDetails = "Direct • 1 Hop";

        public PeerItem(String endpointId, String peerName) {
            this(endpointId, peerName, 1, "Direct • 1 Hop (Local BLE / Wi-Fi)");
        }

        public PeerItem(String endpointId, String peerName, int hopCount, String routeDetails) {
            this.endpointId = endpointId;
            this.peerName = peerName;
            this.hopCount = hopCount;
            this.routeDetails = routeDetails;
        }
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_status, container, false);

        bleRadarView = v.findViewById(R.id.bleRadarView);
        tvPeersInRange = v.findViewById(R.id.tvPeersInRange);
        rvPeersList = v.findViewById(R.id.rvPeersList);
        llPeersEmptyState = v.findViewById(R.id.llPeersEmptyState);

        rvPeersList.setLayoutManager(new LinearLayoutManager(getContext()));
        adapter = new PeerAdapter(requireContext(), peerItemList, peer -> {
            Intent intent = new Intent(requireContext(), ChatActivity.class);
            String cleanPeer = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(peer.peerName);
            intent.putExtra("PEER_ID", cleanPeer);
            intent.putExtra("DISPLAY_NAME", cleanPeer);
            intent.putExtra("MY_ID", com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(meshCoordinator.getMyDisplayName()));
            startActivity(intent);
        });
        rvPeersList.setAdapter(adapter);

        tvPeersInRange.setOnClickListener(v1 -> {
            if (meshCoordinator != null) {
                meshCoordinator.refreshMesh();
                android.widget.Toast.makeText(requireContext(), "Refreshing mesh radar & scanning...", android.widget.Toast.LENGTH_SHORT).show();
                updateRadarWithLivePeers();
            }
        });

        meshCoordinator = MeshCoordinator.getInstance(requireContext());
        updateRadarWithLivePeers();
        return v;
    }

    @Override
    public void onResume() {
        super.onResume();
        if (meshCoordinator != null) {
            meshCoordinator.addListener(this);
        }
        updateRadarWithLivePeers();
    }

    @Override
    public void onPause() {
        super.onPause();
        if (meshCoordinator != null) {
            meshCoordinator.removeListener(this);
        }
    }

    private void updateRadarWithLivePeers() {
        if (meshCoordinator == null || bleRadarView == null) return;
        Map<String, String> directPeers = meshCoordinator.getConnectedPeers();
        Map<String, Set<String>> topology = meshCoordinator.getTopologyAdjacency();
        Map<String, String> displayNames = meshCoordinator.getNodeDisplayNames();

        Map<String, PeerItem> bestPeers = new LinkedHashMap<>();
        Map<String, MeshCoordinator.RouteInfo> bestRoutes = new LinkedHashMap<>();

        // 1. Direct 1-Hop Connected Peers (Unbeatable minimal distance)
        for (Map.Entry<String, String> entry : directPeers.entrySet()) {
            String rawName = entry.getValue();
            String cleanName = MeshCoordinator.cleanPeerName(rawName);
            if (meshCoordinator.isSelfNode("", cleanName)) continue;

            String key = cleanName.toLowerCase();
            MeshCoordinator.RouteInfo r = meshCoordinator.computeRouteTo(cleanName);
            if (r == null || r.hopCount != 1) {
                r = new MeshCoordinator.RouteInfo(Arrays.asList(meshCoordinator.getMyDisplayName(), cleanName));
            }
            PeerItem item = new PeerItem(entry.getKey(), cleanName, 1, "Direct • 1 Hop (Local BLE / Wi-Fi)");
            bestPeers.put(key, item);
            bestRoutes.put(cleanName, r);
        }

        // 2. Discovered Multi-Hop Mesh Nodes (Select ONLY the single best route per unique peer)
        for (String node : topology.keySet()) {
            String resolved = displayNames.containsKey(node) ? displayNames.get(node) : node;
            String cleanName = MeshCoordinator.cleanPeerName(resolved);
            if (cleanName.startsWith("mesh@") && displayNames.containsKey(cleanName)) {
                cleanName = MeshCoordinator.cleanPeerName(displayNames.get(cleanName));
            }
            if (meshCoordinator.isSelfNode(node, cleanName)) continue;

            String key = cleanName.toLowerCase();
            // If already connected directly via 1 hop, ignore mesh redundant entries
            if (bestPeers.containsKey(key) && bestPeers.get(key).hopCount <= 1) {
                continue;
            }

            MeshCoordinator.RouteInfo r = meshCoordinator.computeRouteTo(cleanName);
            int hops = (r != null) ? r.hopCount : 2;

            // Retain the route with the fewest hops
            if (bestPeers.containsKey(key)) {
                if (hops >= bestPeers.get(key).hopCount) {
                    continue; // Existing route is already better or equal
                }
            }

            String detail;
            if (r != null && r.hopCount > 1) {
                detail = "Mesh • " + r.hopCount + " Hops (via " + (r.path.size() > 2 ? r.path.get(1) : "Relay") + ")";
            } else {
                detail = "Mesh • In Range";
            }

            PeerItem item = new PeerItem("MESH_" + node, cleanName, hops, detail);
            bestPeers.put(key, item);
            bestRoutes.put(cleanName, r);
        }

        peerItemList.clear();
        peerItemList.addAll(bestPeers.values());

        bleRadarView.setMeshTopology(meshCoordinator.getMyDisplayName(), bestRoutes, topology);
        adapter.notifyDataSetChanged();

        if (tvPeersInRange != null) {
            if (peerItemList.isEmpty()) {
                tvPeersInRange.setText("Scanning for peers…");
            } else {
                tvPeersInRange.setText(peerItemList.size() + " Peer" + (peerItemList.size() > 1 ? "s" : "") + " in Mesh Range");
            }
        }

        if (llPeersEmptyState != null) {
            llPeersEmptyState.setVisibility(peerItemList.isEmpty() ? View.VISIBLE : View.GONE);
        }
    }

    @Override
    public void onPeerFound(String endpointId, String peerName) {
        if (getActivity() != null) getActivity().runOnUiThread(this::updateRadarWithLivePeers);
    }

    @Override
    public void onPeerLost(String endpointId) {
        if (getActivity() != null) getActivity().runOnUiThread(this::updateRadarWithLivePeers);
    }

    @Override
    public void onPeerConnected(String endpointId, String peerName) {
        if (getActivity() != null) getActivity().runOnUiThread(this::updateRadarWithLivePeers);
    }

    @Override
    public void onPeerDisconnected(String endpointId) {
        if (getActivity() != null) getActivity().runOnUiThread(this::updateRadarWithLivePeers);
    }

    @Override
    public void onMessageReceived(ChatMessageModel message) {}

    @Override
    public void onSosReceived(LocalSosModel sos) {}

    @Override
    public void onTopologyUpdated() {
        if (getActivity() != null) getActivity().runOnUiThread(this::updateRadarWithLivePeers);
    }

    @Override
    public void onMeshRefreshed() {
        if (getActivity() != null) getActivity().runOnUiThread(this::updateRadarWithLivePeers);
    }

    static class PeerAdapter extends RecyclerView.Adapter<PeerAdapter.ViewHolder> {
        public interface OnPeerClick {
            void onClick(PeerItem peer);
        }

        private final Context context;
        private final List<PeerItem> list;
        private final OnPeerClick listener;

        public PeerAdapter(Context context, List<PeerItem> list, OnPeerClick listener) {
            this.context = context;
            this.list = list;
            this.listener = listener;
        }

        @NonNull
        @Override
        public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View v = LayoutInflater.from(context).inflate(R.layout.item_peer_node, parent, false);
            return new ViewHolder(v);
        }

        @Override
        public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
            PeerItem item = list.get(position);
            holder.tvPeerName.setText(item.peerName);
            holder.tvPeerAvatarLetter.setText(item.peerName.substring(0, Math.min(1, item.peerName.length())).toUpperCase());
            if (holder.tvPeerDetails != null) {
                holder.tvPeerDetails.setText(item.routeDetails);
            }

            android.graphics.Bitmap bmp = com.example.meshlink.mesh.MeshCoordinator.getInstance(context).getPeerAvatarBitmap(item.peerName);
            if (bmp == null && item.endpointId != null) {
                bmp = com.example.meshlink.mesh.MeshCoordinator.getInstance(context).getPeerAvatarBitmap(item.endpointId);
            }

            if (bmp != null && holder.ivPeerAvatarPic != null) {
                holder.ivPeerAvatarPic.setImageBitmap(com.example.meshlink.data.ImageUtils.getCircularBitmap(bmp));
                holder.ivPeerAvatarPic.setVisibility(View.VISIBLE);
            } else if (holder.ivPeerAvatarPic != null) {
                holder.ivPeerAvatarPic.setVisibility(View.GONE);
            }

            holder.btnPeerChatAction.setOnClickListener(v -> {
                if (listener != null) listener.onClick(item);
            });
        }

        @Override
        public int getItemCount() {
            return list.size();
        }

        static class ViewHolder extends RecyclerView.ViewHolder {
            TextView tvPeerAvatarLetter, tvPeerName, tvPeerDetails;
            android.widget.ImageView ivPeerAvatarPic;
            Button btnPeerChatAction;

            public ViewHolder(@NonNull View itemView) {
                super(itemView);
                tvPeerAvatarLetter = itemView.findViewById(R.id.tvPeerAvatarLetter);
                ivPeerAvatarPic = itemView.findViewById(R.id.ivPeerAvatarPic);
                tvPeerName = itemView.findViewById(R.id.tvPeerName);
                tvPeerDetails = itemView.findViewById(R.id.tvPeerDetails);
                btnPeerChatAction = itemView.findViewById(R.id.btnPeerChatAction);
            }
        }
    }
}
