package com.example.meshlink.ai.tools;

import android.content.Context;

import com.example.meshlink.ai.knowledge.OfflineKnowledgeBase;
import com.example.meshlink.mesh.MeshCoordinator;

public class EmergencyTool {

    private final Context context;

    public EmergencyTool(Context context) {
        this.context = context.getApplicationContext();
    }

    public ToolResult handleEmergency(String prompt) {
        String guidance = OfflineKnowledgeBase.query(prompt);
        if (guidance == null) {
            guidance = "🚨 **EMERGENCY ASSISTANCE DETECTED**\n\n" +
                    "Bhai ghabrao mat, pehle safe location par shift ho jao. Agar bleeding ho rahi hai to clean kapde se ghav par firm pressure banaye rakhein.\n\n" +
                    "Emergency services se connect karne ke liye niche diye gaye buttons ka use karein:";
        }

        StringBuilder response = new StringBuilder();
        response.append(guidance).append("\n\n");
        response.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
        response.append("⚠️ **IMMEDIATE EMERGENCY OPTIONS AVAILABLE:**\n");
        response.append("• **112 Direct Call**: Police / Ambulance helpline\n");
        response.append("• **Mesh SOS**: Nearby offline Nexus devices par emergency signal broadcast karein\n");
        response.append("• **Share GPS**: Live coordinates broadcast karein");

        ToolResult res = ToolResult.action(response.toString(), "EMERGENCY_ALERT", "112");
        res.addChip("📞 Call 112");
        res.addChip("🆘 Trigger Mesh SOS");
        res.addChip("📍 Share Live Location");
        return res;
    }

    public void triggerMeshSos(double lat, double lng) {
        try {
            MeshCoordinator coordinator = MeshCoordinator.getInstance(context);
            if (coordinator != null) {
                coordinator.broadcastSOS(lat, lng, 10f, "AI Emergency Mode Activated");
            }
        } catch (Exception ignored) {}
    }
}
