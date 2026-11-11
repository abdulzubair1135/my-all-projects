package com.example.myhelper;

import android.app.AppOpsManager;
import android.app.usage.UsageEvents;
import android.app.usage.UsageStats;
import android.app.usage.UsageStatsManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Process;
import android.provider.Settings;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {

    private TextView tvPermissionStatus, tvReport;
    private Button btnPermission, btnRefresh;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        tvPermissionStatus = findViewById(R.id.tvPermissionStatus);
        tvReport = findViewById(R.id.tvReport);
        btnPermission = findViewById(R.id.btnPermission);
        btnRefresh = findViewById(R.id.btnRefresh);

        btnPermission.setOnClickListener(v -> {
            Intent intent = new Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS);
            startActivity(intent);
        });

        btnRefresh.setOnClickListener(v -> runAnalysis());
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (hasUsageStatsPermission()) {
            tvPermissionStatus.setText("Status: Permission Active");
            tvPermissionStatus.setTextColor(Color.parseColor("#4CAF50"));
            btnPermission.setEnabled(false);
            btnPermission.setText("Access Granted");
            runAnalysis();
        } else {
            tvPermissionStatus.setText("Status: Usage Access Required");
            tvPermissionStatus.setTextColor(Color.parseColor("#FF5252"));
            btnPermission.setEnabled(true);
            btnPermission.setText("Grant Access");
        }
    }

    private void runAnalysis() {
        if (!hasUsageStatsPermission()) {
            tvReport.setText("Please click 'Grant Access' above and enable 'my helper' to view data.");
            return;
        }

        UsageStatsManager usm = (UsageStatsManager) getSystemService(Context.USAGE_STATS_SERVICE);
        if (usm == null) return;

        PackageManager pm = getPackageManager();
        StringBuilder report = new StringBuilder();

        // 1. DELETE SUGGESTIONS (Apps unused for > 15 days)
        report.append("🗑️ RECOMMENDED TO UNINSTALL (Unused > 15 Days):\n");
        report.append("------------------------------------------\n");

        long now = System.currentTimeMillis();
        long thirtyDaysAgo = now - (1000L * 60 * 60 * 24 * 30);
        long fifteenDaysMillis = 1000L * 60 * 60 * 24 * 15;

        List<UsageStats> statsList = usm.queryUsageStats(UsageStatsManager.INTERVAL_MONTHLY, thirtyDaysAgo, now);
        int unusedCount = 0;

        if (statsList != null) {
            for (UsageStats stat : statsList) {
                // System apps filter out karo
                if (isUserInstalledApp(stat.getPackageName(), pm)) {
                    long lastUsed = stat.getLastTimeUsed();
                    if (lastUsed > 0 && (now - lastUsed) > fifteenDaysMillis) {
                        String appLabel = getAppName(stat.getPackageName(), pm);
                        long daysUnused = (now - lastUsed) / (1000L * 60 * 60 * 24);
                        report.append("• ").append(appLabel).append(" (Last used ").append(daysUnused).append(" days ago)\n");
                        unusedCount++;
                    }
                }
            }
        }
        if (unusedCount == 0) {
            report.append("No inactive user apps found.\n");
        }

        // 2. RECENT TIMELINE (Apps opened in last 24 hours)
        report.append("\n\n🕒 RECENT APP TIMELINE (Last 24 Hours):\n");
        report.append("------------------------------------------\n");

        long oneDayAgo = now - (1000L * 60 * 60 * 24);
        UsageEvents events = usm.queryEvents(oneDayAgo, now);
        UsageEvents.Event event = new UsageEvents.Event();
        SimpleDateFormat sdf = new SimpleDateFormat("hh:mm a", Locale.getDefault());
        List<String> recentLogs = new ArrayList<>();

        while (events.hasNextEvent()) {
            events.getNextEvent(event);
            if (event.getEventType() == UsageEvents.Event.ACTIVITY_RESUMED) {
                String pkg = event.getPackageName();
                if (isUserInstalledApp(pkg, pm)) {
                    String time = sdf.format(new Date(event.getTimeStamp()));
                    String name = getAppName(pkg, pm);
                    recentLogs.add("[" + time + "]  " + name);
                }
            }
        }

        if (recentLogs.isEmpty()) {
            report.append("No recent user app launches recorded yet.\n");
        } else {
            // Show latest launches in reverse order (newest first)
            int start = Math.max(0, recentLogs.size() - 25);
            for (int i = recentLogs.size() - 1; i >= start; i--) {
                report.append("• ").append(recentLogs.get(i)).append("\n");
            }
        }

        tvReport.setText(report.toString());
    }

    private boolean isUserInstalledApp(String packageName, PackageManager pm) {
        try {
            ApplicationInfo ai = pm.getApplicationInfo(packageName, 0);
            return (ai.flags & ApplicationInfo.FLAG_SYSTEM) == 0;
        } catch (PackageManager.NameNotFoundException e) {
            return false;
        }
    }

    private String getAppName(String packageName, PackageManager pm) {
        try {
            ApplicationInfo ai = pm.getApplicationInfo(packageName, 0);
            return pm.getApplicationLabel(ai).toString();
        } catch (Exception e) {
            return packageName;
        }
    }

    private boolean hasUsageStatsPermission() {
        AppOpsManager appOps = (AppOpsManager) getSystemService(Context.APP_OPS_SERVICE);
        int mode = appOps.checkOpNoThrow(AppOpsManager.OPSTR_GET_USAGE_STATS,
                Process.myUid(), getPackageName());
        return mode == AppOpsManager.MODE_ALLOWED;
    }
}