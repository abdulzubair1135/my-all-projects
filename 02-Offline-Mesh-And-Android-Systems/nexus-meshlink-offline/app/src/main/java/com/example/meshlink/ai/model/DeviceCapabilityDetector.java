package com.example.meshlink.ai.model;

import android.app.ActivityManager;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.BatteryManager;
import android.os.Build;
import android.os.Environment;
import android.os.StatFs;

import java.io.File;

/**
 * Detects device hardware profile (RAM, CPU, Storage, Battery, OS)
 * to automatically select the optimal local AI model tier without freezing or crashing the phone.
 */
public class DeviceCapabilityDetector {

    public enum DeviceTier {
        LOW,       // < 4GB RAM (e.g. Qwen3 0.6B Q4)
        NORMAL,    // 4GB - 8GB RAM (e.g. Qwen3 1.7B Q4_K_M)
        HIGH       // > 8GB RAM (e.g. Qwen3 4B Q4)
    }

    public static class DeviceProfile {
        public long totalRamBytes;
        public long availableRamBytes;
        public int ramTotalGb;
        public int cpuCores;
        public String cpuArchitecture;
        public long availableStorageBytes;
        public long storageAvailableMb;
        public int batteryPct;
        public boolean isCharging;
        public int androidSdk;
        public String androidVersion;
        public DeviceTier recommendedTier;
        public String recommendedModelName;

        @Override
        public String toString() {
            return "RAM: " + ramTotalGb + "GB | CPU: " + cpuCores + " cores (" + cpuArchitecture + ") | Storage: " +
                    storageAvailableMb + "MB free | OS: Android " + androidVersion + " (API " + androidSdk + ") | Tier: " + recommendedTier;
        }
    }

    public static DeviceProfile detect(Context context) {
        DeviceProfile profile = new DeviceProfile();

        // 1. Memory (RAM)
        ActivityManager am = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        if (am != null) {
            ActivityManager.MemoryInfo memInfo = new ActivityManager.MemoryInfo();
            am.getMemoryInfo(memInfo);
            profile.totalRamBytes = memInfo.totalMem;
            profile.availableRamBytes = memInfo.availMem;
            profile.ramTotalGb = (int) Math.round((double) memInfo.totalMem / (1024 * 1024 * 1024));
        } else {
            profile.ramTotalGb = 4;
            profile.totalRamBytes = 4L * 1024 * 1024 * 1024;
        }

        // 2. CPU Cores & Architecture
        profile.cpuCores = Runtime.getRuntime().availableProcessors();
        if (Build.SUPPORTED_ABIS != null && Build.SUPPORTED_ABIS.length > 0) {
            profile.cpuArchitecture = Build.SUPPORTED_ABIS[0];
        } else {
            profile.cpuArchitecture = Build.CPU_ABI;
        }

        // 3. Storage
        try {
            File path = Environment.getDataDirectory();
            StatFs stat = new StatFs(path.getPath());
            long blockSize = stat.getBlockSizeLong();
            long availableBlocks = stat.getAvailableBlocksLong();
            profile.availableStorageBytes = availableBlocks * blockSize;
            profile.storageAvailableMb = profile.availableStorageBytes / (1024 * 1024);
        } catch (Exception e) {
            profile.storageAvailableMb = 2048;
        }

        // 4. Battery Status
        try {
            IntentFilter ifilter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
            Intent batteryStatus = context.registerReceiver(null, ifilter);
            if (batteryStatus != null) {
                int level = batteryStatus.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
                int scale = batteryStatus.getIntExtra(BatteryManager.EXTRA_SCALE, -1);
                profile.batteryPct = (int) ((level / (float) scale) * 100);
                int status = batteryStatus.getIntExtra(BatteryManager.EXTRA_STATUS, -1);
                profile.isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING ||
                        status == BatteryManager.BATTERY_STATUS_FULL;
            } else {
                profile.batteryPct = 100;
                profile.isCharging = false;
            }
        } catch (Exception e) {
            profile.batteryPct = 100;
        }

        // 5. Android Version
        profile.androidSdk = Build.VERSION.SDK_INT;
        profile.androidVersion = Build.VERSION.RELEASE;

        // 6. Tier Calculation
        if (profile.ramTotalGb < 4) {
            profile.recommendedTier = DeviceTier.LOW;
            profile.recommendedModelName = "Qwen3 0.6B Q4";
        } else if (profile.ramTotalGb <= 8) {
            profile.recommendedTier = DeviceTier.NORMAL;
            profile.recommendedModelName = "Qwen3 1.7B Q4_K_M";
        } else {
            profile.recommendedTier = DeviceTier.HIGH;
            profile.recommendedModelName = "Qwen3 4B Q4";
        }

        return profile;
    }
}
