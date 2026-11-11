package com.example.meshlink.ai.tools;

import android.content.Context;

import com.example.meshlink.mesh.MeshCoordinator;

public class MeshTool {

    private final Context context;

    public MeshTool(Context context) {
        this.context = context.getApplicationContext();
    }

    public ToolResult getMeshStatus() {
        try {
            MeshCoordinator coordinator = MeshCoordinator.getInstance(context);
            int peerCount = coordinator != null ? coordinator.getConnectedPeerCount() : 0;
            String myId = coordinator != null ? coordinator.getMyNodeId() : "Unknown";

            StringBuilder sb = new StringBuilder();
            sb.append("🌐 **NEXUS MESHLINK DIAGNOSTICS:**\n\n");
            sb.append("• **My Node ID:** `").append(myId).append("`\n");
            sb.append("• **Nearby Nodes Discovered:** `").append(peerCount).append(" device(s)`\n");
            sb.append("• **Transport Layers:** BLE 5.0 (Advertising + Scanning) & Wi-Fi Direct P2P\n");
            sb.append("• **Multi-hop Relay Status:** Active (TTL: 5 hops)\n");
            sb.append("• **Network State:** ").append(peerCount > 0 ? "🟢 Online Mesh (P2P Cluster)" : "🟡 Scanning for nearby peers").append("\n\n");

            if (peerCount == 0) {
                sb.append("💡 *Tip: Agar pass me koi device nahi mil raha hai, to Top Header me 'Refresh Mesh' pill tap karein.*");
            } else {
                sb.append("💡 *Aap kisi bhi connected peer ko bina internet ke text, voice call ya video call kar sakte hain!*");
            }

            return ToolResult.text(sb.toString()).addChip("Refresh Mesh");
        } catch (Exception e) {
            return ToolResult.text("Mesh status check failed: " + e.getMessage());
        }
    }
}
