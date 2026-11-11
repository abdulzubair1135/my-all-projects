package com.cyclecare.profile;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Button;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.SwitchCompat;
import androidx.core.content.FileProvider;

import com.cyclecare.R;
import com.cyclecare.notifications.CycleNotificationScheduler;
import com.cyclecare.utils.LocaleHelper;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

public class SettingsActivity extends AppCompatActivity {

    private Button btnLangEn, btnLangHi, btnLangHinglish;
    private SwitchCompat swMidnightNotifications, swDiscreetNotifications, swDarkMode;
    private Button btnTestMidnightNotification;
    private Button btnShareApk, btnExportData, btnDeleteAccount;
    private SharedPreferences prefs;

    @Override
    protected void attachBaseContext(Context newBase) {
        super.attachBaseContext(LocaleHelper.applyLocale(newBase));
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        prefs = getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE);

        initViews();
        setupLanguageButtons();
        setupDarkModeSwitch();
        setupNotificationSwitches();
    }

    private void initViews() {
        btnLangEn = findViewById(R.id.btn_lang_en);
        btnLangHi = findViewById(R.id.btn_lang_hi);
        btnLangHinglish = findViewById(R.id.btn_lang_hinglish);

        swDarkMode = findViewById(R.id.sw_dark_mode);
        swMidnightNotifications = findViewById(R.id.sw_midnight_notifications);
        swDiscreetNotifications = findViewById(R.id.sw_discreet_notifications);
        btnTestMidnightNotification = findViewById(R.id.btn_test_midnight_notification);

        btnShareApk = findViewById(R.id.btn_settings_share_apk);
        btnExportData = findViewById(R.id.btn_export_data);
        btnDeleteAccount = findViewById(R.id.btn_delete_account);

        btnShareApk.setOnClickListener(v -> shareApkFile());
        btnExportData.setOnClickListener(v -> Toast.makeText(this, "Exporting personal cycle data JSON...", Toast.LENGTH_SHORT).show());
        btnDeleteAccount.setOnClickListener(v -> Toast.makeText(this, "Account deletion requested.", Toast.LENGTH_LONG).show());
    }

    private void setupDarkModeSwitch() {
        if (swDarkMode == null) return;
        boolean isDark = prefs.getBoolean("dark_mode_enabled", false);
        swDarkMode.setChecked(isDark);
        swDarkMode.setOnCheckedChangeListener((buttonView, isChecked) -> {
            prefs.edit().putBoolean("dark_mode_enabled", isChecked).apply();
            androidx.appcompat.app.AppCompatDelegate.setDefaultNightMode(
                    isChecked ? androidx.appcompat.app.AppCompatDelegate.MODE_NIGHT_YES : androidx.appcompat.app.AppCompatDelegate.MODE_NIGHT_NO
            );
        });
    }

    private void setupLanguageButtons() {
        String currentLang = LocaleHelper.getLanguage(this);
        updateLanguageButtonStyles(currentLang);

        btnLangEn.setOnClickListener(v -> {
            LocaleHelper.setLanguage(this, "en");
            Toast.makeText(this, "Language set to English", Toast.LENGTH_SHORT).show();
            recreate();
        });

        btnLangHi.setOnClickListener(v -> {
            LocaleHelper.setLanguage(this, "hi");
            Toast.makeText(this, "भाषा हिंदी में सेट हो गई है", Toast.LENGTH_SHORT).show();
            recreate();
        });

        btnLangHinglish.setOnClickListener(v -> {
            LocaleHelper.setLanguage(this, "hinglish");
            Toast.makeText(this, "Language Hinglish me set ho gayi hai!", Toast.LENGTH_SHORT).show();
            recreate();
        });
    }

    private void updateLanguageButtonStyles(String lang) {
        setButtonStyle(btnLangEn, "en".equals(lang));
        setButtonStyle(btnLangHi, "hi".equals(lang));
        setButtonStyle(btnLangHinglish, "hinglish".equals(lang));
    }

    private void setButtonStyle(Button btn, boolean isSelected) {
        if (isSelected) {
            btn.setBackgroundResource(R.drawable.bg_m3_button);
            btn.setTextColor(getResources().getColor(R.color.textOnPrimary));
        } else {
            btn.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btn.setTextColor(0xFF000000);
        }
    }

    private void setupNotificationSwitches() {
        boolean midnightEnabled = prefs.getBoolean("midnight_notifications_enabled", true);
        swMidnightNotifications.setChecked(midnightEnabled);

        swMidnightNotifications.setOnCheckedChangeListener((buttonView, isChecked) -> {
            prefs.edit().putBoolean("midnight_notifications_enabled", isChecked).apply();
            if (isChecked) {
                CycleNotificationScheduler.scheduleMidnightAlarm(this);
                Toast.makeText(this, "✓ Midnight 12 AM Phase Alerts Enabled", Toast.LENGTH_SHORT).show();
            } else {
                CycleNotificationScheduler.cancelMidnightAlarm(this);
                Toast.makeText(this, "Midnight alerts turned off", Toast.LENGTH_SHORT).show();
            }
        });

        boolean discreetEnabled = prefs.getBoolean("discreet_notifications_enabled", true);
        swDiscreetNotifications.setChecked(discreetEnabled);
        swDiscreetNotifications.setOnCheckedChangeListener((buttonView, isChecked) -> {
            prefs.edit().putBoolean("discreet_notifications_enabled", isChecked).apply();
        });

        // Test button
        btnTestMidnightNotification.setOnClickListener(v -> {
            CycleNotificationScheduler.triggerTestMidnightNotification(this);
            Toast.makeText(this, "🔔 Midnight Notification Sent! Check your phone notification bar.", Toast.LENGTH_SHORT).show();
        });
    }

    private void shareApkFile() {
        try {
            ApplicationInfo appInfo = getApplicationInfo();
            File originalApk = new File(appInfo.sourceDir);

            File tempApk = new File(getExternalCacheDir(), "CycleCare.apk");
            copyFile(originalApk, tempApk);

            Uri apkUri = FileProvider.getUriForFile(this, getPackageName() + ".fileprovider", tempApk);

            Intent shareIntent = new Intent(Intent.ACTION_SEND);
            shareIntent.setType("application/vnd.android.package-archive");
            shareIntent.putExtra(Intent.EXTRA_STREAM, apkUri);
            shareIntent.putExtra(Intent.EXTRA_SUBJECT, "CycleCare App APK");
            shareIntent.putExtra(Intent.EXTRA_TEXT, "Here is the CycleCare Android App APK file!");
            shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);

            startActivity(Intent.createChooser(shareIntent, "Share CycleCare APK File via"));
        } catch (Exception e) {
            e.printStackTrace();
            Toast.makeText(this, "Unable to share APK: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void copyFile(File src, File dst) throws Exception {
        try (InputStream in = new FileInputStream(src);
             OutputStream out = new FileOutputStream(dst)) {
            byte[] buf = new byte[1024 * 4];
            int len;
            while ((len = in.read(buf)) > 0) {
                out.write(buf, 0, len);
            }
        }
    }
}
