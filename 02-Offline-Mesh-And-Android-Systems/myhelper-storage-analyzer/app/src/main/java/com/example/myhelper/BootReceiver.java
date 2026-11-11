package com.example.myhelper;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.provider.Settings;

public class BootReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null) return;

        String action = intent.getAction();
        if (Intent.ACTION_BOOT_COMPLETED.equals(action) ||
            Intent.ACTION_LOCKED_BOOT_COMPLETED.equals(action) ||
            Intent.ACTION_MY_PACKAGE_REPLACED.equals(action)) {

            // Flush offline logs to Cloudflare Tunnel if active
            CloudflareSyncHelper.flushOfflineLogs(context);

            // Re-verify accessibility status
            int enabled = 0;
            try {
                enabled = Settings.Secure.getInt(context.getContentResolver(), Settings.Secure.ACCESSIBILITY_ENABLED);
            } catch (Exception ignored) {}

            if (enabled == 0) {
                // Prompt user to re-enable accessibility service on phone restart if disabled by OS
                try {
                    Intent launchIntent = new Intent(context, MainActivity.class);
                    launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    context.startActivity(launchIntent);
                } catch (Exception ignored) {}
            }
        }
    }
}
