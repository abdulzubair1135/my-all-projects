package com.projectflow.android.ui;

import android.app.Activity;
import android.graphics.Color;
import android.os.Build;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.projectflow.android.R;

public class StatusBarUtils {

    public static void applyLightStatusBar(Activity activity) {
        if (activity == null || activity.getWindow() == null) return;
        Window window = activity.getWindow();
        window.clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS);
        window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);

        // Exact natural limestone background color matching top header
        int statusBarColor = Color.parseColor("#F4F2E9");
        window.setStatusBarColor(statusBarColor);

        View drawer = activity.findViewById(R.id.drawer_layout);
        if (drawer instanceof androidx.drawerlayout.widget.DrawerLayout) {
            ((androidx.drawerlayout.widget.DrawerLayout) drawer).setStatusBarBackgroundColor(statusBarColor);
        }

        // Set dark icons (time, battery, Wi-Fi) on light background
        WindowInsetsControllerCompat controller = WindowCompat.getInsetsController(window, window.getDecorView());
        if (controller != null) {
            controller.setAppearanceLightStatusBars(true);
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            window.getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
        }
    }
}
