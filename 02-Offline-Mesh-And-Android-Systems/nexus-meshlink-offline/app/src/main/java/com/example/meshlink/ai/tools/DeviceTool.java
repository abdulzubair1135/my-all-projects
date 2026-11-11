package com.example.meshlink.ai.tools;

import android.content.Context;

import com.example.meshlink.ai.model.DeviceCapabilityDetector;

public class DeviceTool {

    public static ToolResult getDeviceDiagnostics(Context context) {
        DeviceCapabilityDetector.DeviceProfile profile = DeviceCapabilityDetector.detect(context);

        StringBuilder sb = new StringBuilder();
        sb.append("📱 **DEVICE HARDWARE & AI DIAGNOSTICS:**\n\n");
        sb.append("• **Total RAM:** `").append(profile.ramTotalGb).append(" GB` (Available: `")
                .append(profile.availableRamBytes / (1024 * 1024)).append(" MB`)\n");
        sb.append("• **CPU Configuration:** `").append(profile.cpuCores).append(" Cores` (`")
                .append(profile.cpuArchitecture).append("`)\n");
        sb.append("• **Free Storage:** `").append(profile.storageAvailableMb).append(" MB`\n");
        sb.append("• **Battery Health:** `").append(profile.batteryPct).append("%` ")
                .append(profile.isCharging ? "⚡ (Charging)" : "🔋 (On Battery)").append("\n");
        sb.append("• **Android System:** `Android ").append(profile.androidVersion).append("` (API ")
                .append(profile.androidSdk).append(")\n");
        sb.append("• **Hardware Tier:** `").append(profile.recommendedTier).append("`\n");
        sb.append("• **Recommended AI Model:** `").append(profile.recommendedModelName).append("`\n\n");
        sb.append("💡 *Aap Settings me jakar model download ya battery saver mode configure kar sakte hain.*");

        return ToolResult.text(sb.toString()).addChip("AI Settings");
    }
}
