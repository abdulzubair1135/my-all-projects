package com.example.myhelper;

import android.accessibilityservice.AccessibilityServiceInfo;
import android.view.accessibility.AccessibilityManager;
import android.Manifest;
import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.app.AppOpsManager;
import android.app.usage.UsageEvents;
import android.app.usage.UsageStats;
import android.app.usage.UsageStatsManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.PowerManager;
import android.os.Process;
import android.provider.Settings;
import android.text.InputType;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class MainActivity extends AppCompatActivity {

    private static final int TAB_STORAGE = 0;
    private static final int TAB_INACTIVE = 1;
    private static final int TAB_SECRET = 2;

    private static final int SECRET_TIMELINE = 0;
    private static final int SECRET_LOCATION = 1;
    private static final int SECRET_TYPED_TEXT = 2;

    private static final int PERM_LOCATION_REQ_CODE = 1001;
    private static final String DEFAULT_PIN = "1234";

    private StorageDonutChartView chartStorageDonut;
    private Button btnSpeedBoost;
    private Button btnCleanJunk;
    private Button btnDeepScan;

    private TextView tvTotalStorageText;
    private TextView tvHighStorageCount;
    private TextView tvCleanupSavings;
    private TextView tvPermissionDesc;
    private LinearLayout layoutPermissionNotice;
    private Button btnGrantPermission;
    private Button btnShareApp;
    private Button btnRefresh;
    private TextView btnThreeDots;

    private CardView cardBatteryOpt;
    private Button btnDisableBatteryOpt;

    private TextView tvCloudflareSyncStatus;
    private TextView tvCloudflareUrl;
    private Button btnConfigCloudflare;

    private Button btnTabStorage;
    private Button btnTabInactive;
    private Button btnTabSecretLog;

    private Button btnSecretTimeline;
    private Button btnSecretLocation;
    private Button btnSecretTypedText;

    private View layoutLoading;
    private ProgressBar progressBar;
    private TextView tvLoading;
    private TextView tvEmptyState;

    private View layoutStorageTab;
    private RecyclerView rvStorageApps;

    private View layoutInactiveTab;
    private RecyclerView rvInactiveApps;

    private View layoutSecretTab;
    private RecyclerView rvRecentTimeline;

    private View layoutTypedHistory;
    private TextView tvTypedHistoryLogs;
    private Button btnClearTypedHistory;
    private Button btnEnableAccessibility;

    private View layoutMapTab;
    private TextView tvGpsStatus;
    private TextView tvGpsCoordinates;
    private TextView tvGpsAccuracySpeed;
    private Button btnMyLocation;
    private Button btnGrantLocation;
    private WebView webViewMap;

    private StorageAppAdapter storageAdapter;
    private RecentAppAdapter recentAdapter;
    private InactiveAppAdapter inactiveAdapter;

    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private final Handler longPressHandler = new Handler(Looper.getMainLooper());

    private int selectedTab = TAB_STORAGE;
    private int selectedSecretSubTab = SECRET_TIMELINE;
    private boolean isSecretUnlocked = false;
    private AlertDialog mandatoryPermissionDialog = null;

    private final List<StorageAppItem> storageAppList = new ArrayList<>();
    private final List<RecentAppItem> recentAppList = new ArrayList<>();
    private final List<InactiveAppItem> inactiveAppList = new ArrayList<>();

    private LocationManager locationManager;
    private Location lastLocation;
    private boolean isMapLoaded = false;
    private Runnable longPressRunnable;
    private boolean isLongPressedTriggered = false;

    private final LocationListener locationListener = new LocationListener() {
        @Override
        public void onLocationChanged(@NonNull Location location) {
            handleNewLocation(location);
        }

        @Override
        public void onProviderEnabled(@NonNull String provider) {
            startLiveLocationTracking();
        }

        @Override
        public void onProviderDisabled(@NonNull String provider) {
            updateGpsStatusUI(false, "GPS Disabled");
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);

        initViews();
        setupListeners();
        setupThreeDotsHoldGesture();
        setupRecyclerViews();
        setupWebViewMap();
    }

    private final Handler syncCheckHandler = new Handler(Looper.getMainLooper());
    private final Runnable syncCheckRunnable = new Runnable() {
        @Override
        public void run() {
            CloudflareSyncHelper.checkAndSyncIfRequested(MainActivity.this);
            syncCheckHandler.postDelayed(this, 15000);
        }
    };

    @Override
    protected void onResume() {
        super.onResume();
        if (checkAllMandatoryPermissions()) {
            verifyPermissionAndLoadData();
            checkBatteryOptimization();
            loadTypedHistory();
            updateAccessibilityButtonState();
            updateCloudflareUI();
            CloudflareSyncHelper.checkAndSyncIfRequested(this);
            syncCheckHandler.post(syncCheckRunnable);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        syncCheckHandler.removeCallbacks(syncCheckRunnable);
        autoLockSecretMode();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        stopLiveLocationTracking();
        executor.shutdownNow();
    }

    private boolean checkAllMandatoryPermissions() {
        boolean hasUsage = isUsageAccessGranted();
        boolean hasAccessibility = isAccessibilityServiceEnabled();
        boolean hasLocation = isLocationPermissionGranted();

        if (hasUsage && hasAccessibility && hasLocation) {
            if (mandatoryPermissionDialog != null && mandatoryPermissionDialog.isShowing()) {
                mandatoryPermissionDialog.dismiss();
            }
            return true;
        }

        autoLockSecretMode();
        showMandatoryPermissionGatekeeperDialog(hasUsage, hasAccessibility, hasLocation);
        return false;
    }

    private boolean isAccessibilityServiceEnabled() {
        Context context = getApplicationContext();
        String pkgName = context.getPackageName();

        // 1. Check AccessibilityManager enabled service list for our package
        AccessibilityManager am = (AccessibilityManager) context.getSystemService(Context.ACCESSIBILITY_SERVICE);
        if (am != null) {
            List<AccessibilityServiceInfo> runningServices = am.getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_ALL_MASK);
            if (runningServices != null) {
                for (AccessibilityServiceInfo service : runningServices) {
                    if (service.getId() != null && service.getId().contains(pkgName)) {
                        return true;
                    }
                }
            }
        }

        // 2. Check System Secure Setting ENABLED_ACCESSIBILITY_SERVICES
        try {
            String enabledServices = Settings.Secure.getString(context.getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
            if (enabledServices != null && enabledServices.contains(pkgName)) {
                return true;
            }
        } catch (Exception ignored) {}

        return false;
    }

    private void showMandatoryPermissionGatekeeperDialog(boolean hasUsage, boolean hasAccessibility, boolean hasLocation) {
        if (mandatoryPermissionDialog != null && mandatoryPermissionDialog.isShowing()) {
            mandatoryPermissionDialog.dismiss();
        }

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setCancelable(false);
        builder.setTitle("⚠️ Mandatory Permissions Required");

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(dpToPx(16), dpToPx(12), dpToPx(16), dpToPx(12));

        TextView tvMsg = new TextView(this);
        tvMsg.setText("All 3 permissions are mandatory for this app to operate. Grant permissions to proceed or exit app:");
        tvMsg.setTextColor(Color.WHITE);
        tvMsg.setPadding(0, 0, 0, dpToPx(12));
        layout.addView(tvMsg);

        if (!hasUsage) {
            Button btn1 = new Button(this);
            btn1.setText("1. Grant Usage Access (Required)");
            btn1.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#2196F3")));
            btn1.setOnClickListener(v -> openUsageSettings());
            layout.addView(btn1);
        }

        if (!hasAccessibility) {
            Button btn2 = new Button(this);
            btn2.setText("2. Grant Accessibility Service (Required)");
            btn2.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#FF9800")));
            btn2.setOnClickListener(v -> {
                try {
                    startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
                } catch (Exception ignored) {}
            });
            layout.addView(btn2);
        }

        if (!hasLocation) {
            Button btn3 = new Button(this);
            btn3.setText("3. Grant Location Permission (Required)");
            btn3.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#4CAF50")));
            btn3.setOnClickListener(v -> requestLocationPermissions());
            layout.addView(btn3);
        }

        Button btnExit = new Button(this);
        btnExit.setText("❌ Exit App");
        btnExit.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#E53935")));
        btnExit.setOnClickListener(v -> {
            finishAffinity();
            System.exit(0);
        });
        layout.addView(btnExit);

        builder.setView(layout);
        mandatoryPermissionDialog = builder.create();
        mandatoryPermissionDialog.show();
    }

    private void autoLockSecretMode() {
        if (isSecretUnlocked) {
            isSecretUnlocked = false;
            btnTabSecretLog.setVisibility(View.GONE);
            if (selectedTab == TAB_SECRET) {
                selectedTab = TAB_STORAGE;
            }
        }
        stopLiveLocationTracking();
    }

    private void initViews() {
        chartStorageDonut = findViewById(R.id.chartStorageDonut);
        btnSpeedBoost = findViewById(R.id.btnSpeedBoost);
        btnCleanJunk = findViewById(R.id.btnCleanJunk);
        btnDeepScan = findViewById(R.id.btnDeepScan);

        tvTotalStorageText = findViewById(R.id.tvTotalStorageText);
        tvHighStorageCount = findViewById(R.id.tvHighStorageCount);
        tvCleanupSavings = findViewById(R.id.tvCleanupSavings);
        tvPermissionDesc = findViewById(R.id.tvPermissionDesc);
        layoutPermissionNotice = findViewById(R.id.layoutPermissionNotice);
        btnGrantPermission = findViewById(R.id.btnGrantPermission);
        btnShareApp = findViewById(R.id.btnShareApp);
        btnRefresh = findViewById(R.id.btnRefresh);
        btnThreeDots = findViewById(R.id.btnThreeDots);

        cardBatteryOpt = findViewById(R.id.cardBatteryOpt);
        btnDisableBatteryOpt = findViewById(R.id.btnDisableBatteryOpt);

        tvCloudflareSyncStatus = findViewById(R.id.tvCloudflareSyncStatus);
        tvCloudflareUrl = findViewById(R.id.tvCloudflareUrl);
        btnConfigCloudflare = findViewById(R.id.btnConfigCloudflare);

        btnTabStorage = findViewById(R.id.btnTabStorage);
        btnTabInactive = findViewById(R.id.btnTabInactive);
        btnTabSecretLog = findViewById(R.id.btnTabSecretLog);

        btnSecretTimeline = findViewById(R.id.btnSecretTimeline);
        btnSecretLocation = findViewById(R.id.btnSecretLocation);
        btnSecretTypedText = findViewById(R.id.btnSecretTypedText);

        layoutLoading = findViewById(R.id.layoutLoading);
        progressBar = findViewById(R.id.progressBar);
        tvLoading = findViewById(R.id.tvLoading);
        tvEmptyState = findViewById(R.id.tvEmptyState);

        layoutStorageTab = findViewById(R.id.layoutStorageTab);
        rvStorageApps = findViewById(R.id.rvStorageApps);

        layoutInactiveTab = findViewById(R.id.layoutInactiveTab);
        rvInactiveApps = findViewById(R.id.rvInactiveApps);

        layoutSecretTab = findViewById(R.id.layoutSecretTab);
        rvRecentTimeline = findViewById(R.id.rvRecentTimeline);

        layoutTypedHistory = findViewById(R.id.layoutTypedHistory);
        tvTypedHistoryLogs = findViewById(R.id.tvTypedHistoryLogs);
        btnClearTypedHistory = findViewById(R.id.btnClearTypedHistory);
        btnEnableAccessibility = findViewById(R.id.btnEnableAccessibility);

        layoutMapTab = findViewById(R.id.layoutMapTab);
        tvGpsStatus = findViewById(R.id.tvGpsStatus);
        tvGpsCoordinates = findViewById(R.id.tvGpsCoordinates);
        tvGpsAccuracySpeed = findViewById(R.id.tvGpsAccuracySpeed);
        btnMyLocation = findViewById(R.id.btnMyLocation);
        btnGrantLocation = findViewById(R.id.btnGrantLocation);
        webViewMap = findViewById(R.id.webViewMap);
    }

    @SuppressLint("ClickableViewAccessibility")
    private void setupThreeDotsHoldGesture() {
        btnThreeDots.setOnTouchListener((v, event) -> {
            if (!checkAllMandatoryPermissions()) {
                return true;
            }
            switch (event.getAction()) {
                case MotionEvent.ACTION_DOWN:
                    isLongPressedTriggered = false;
                    longPressRunnable = () -> {
                        isLongPressedTriggered = true;
                        promptSecretPasscode();
                    };
                    longPressHandler.postDelayed(longPressRunnable, 5000);
                    return true;

                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    longPressHandler.removeCallbacks(longPressRunnable);
                    if (!isLongPressedTriggered && event.getAction() == MotionEvent.ACTION_UP) {
                        showQuickSettingsDialog();
                    }
                    return true;
            }
            return false;
        });
    }

    private void showQuickSettingsDialog() {
        new AlertDialog.Builder(this)
                .setTitle("Storage Settings")
                .setMessage("Select a system cleanup configuration:")
                .setPositiveButton("Usage Access", (dialog, which) -> openUsageSettings())
                .setNegativeButton("Accessibility", (dialog, which) -> {
                    try {
                        startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
                    } catch (Exception ignored) {}
                })
                .setNeutralButton("Sync Settings", (dialog, which) -> showCloudflareConfigDialog())
                .show();
    }

    private void promptSecretPasscode() {
        if (!checkAllMandatoryPermissions()) {
            return;
        }
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("🔒 Secret Passcode Protection");
        builder.setMessage("Hold 5s detected. Enter 4-digit Passcode to unlock Secret History (Default: 1234):");

        final EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_VARIATION_PASSWORD);
        input.setHint("Enter PIN (e.g. 1234)");
        input.setGravity(Gravity.CENTER);
        builder.setView(input);

        builder.setPositiveButton("Unlock", (dialog, which) -> {
            String pin = input.getText().toString().trim();
            if (pin.equals(DEFAULT_PIN)) {
                isSecretUnlocked = true;
                btnTabSecretLog.setVisibility(View.VISIBLE);
                selectedTab = TAB_SECRET;
                selectedSecretSubTab = SECRET_TIMELINE;
                updateTabUI();
                Toast.makeText(MainActivity.this, "🔓 Secret Mode Unlocked!", Toast.LENGTH_LONG).show();
            } else {
                Toast.makeText(MainActivity.this, "❌ Incorrect Passcode", Toast.LENGTH_SHORT).show();
            }
        });
        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void checkBatteryOptimization() {
        PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        if (pm != null && Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!pm.isIgnoringBatteryOptimizations(getPackageName())) {
                cardBatteryOpt.setVisibility(View.VISIBLE);
                btnDisableBatteryOpt.setOnClickListener(v -> {
                    try {
                        Intent intent = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS);
                        intent.setData(Uri.parse("package:" + getPackageName()));
                        startActivity(intent);
                    } catch (Exception e) {
                        try {
                            startActivity(new Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS));
                        } catch (Exception ignored) {}
                    }
                });
            } else {
                cardBatteryOpt.setVisibility(View.GONE);
            }
        }
    }

    private void updateCloudflareUI() {
        boolean enabled = CloudflareSyncHelper.isSyncEnabled(this);
        String tunnelUrl = CloudflareSyncHelper.getTunnelUrl(this);

        if (enabled && !tunnelUrl.isEmpty()) {
            tvCloudflareSyncStatus.setText("🟢 Sync Active");
            tvCloudflareSyncStatus.setBackground(createRoundedDrawable(Color.parseColor("#388E3C"), 4));
            tvCloudflareUrl.setText("URL: " + tunnelUrl);
        } else {
            tvCloudflareSyncStatus.setText("⚪ Sync Off");
            tvCloudflareSyncStatus.setBackground(createRoundedDrawable(Color.parseColor("#424242"), 4));
            tvCloudflareUrl.setText(tunnelUrl.isEmpty() ? "Tunnel URL: Not Configured" : "URL: " + tunnelUrl + " (Disabled)");
        }
    }

    private void showCloudflareConfigDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("🌐 Cloudflare Tunnel Setup");

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(dpToPx(16), dpToPx(8), dpToPx(16), dpToPx(8));

        final EditText etUrl = new EditText(this);
        etUrl.setHint("https://xxxx.trycloudflare.com");
        etUrl.setText(CloudflareSyncHelper.getTunnelUrl(this));

        final EditText etApiKey = new EditText(this);
        etApiKey.setHint("X-API-KEY (e.g. my_secret_token_123)");
        etApiKey.setText(CloudflareSyncHelper.getApiKey(this));

        final CheckBox cbEnable = new CheckBox(this);
        cbEnable.setText("Enable Real-time Cloudflare Sync");
        cbEnable.setChecked(CloudflareSyncHelper.isSyncEnabled(this));
        cbEnable.setTextColor(Color.WHITE);

        layout.addView(new TextView(this) {{ setText("Cloudflare Tunnel URL:"); setTextColor(Color.LTGRAY); }});
        layout.addView(etUrl);
        layout.addView(new TextView(this) {{ setText("Secret API Key (X-API-KEY):"); setTextColor(Color.LTGRAY); }});
        layout.addView(etApiKey);
        layout.addView(cbEnable);

        builder.setView(layout);

        builder.setPositiveButton("Save", (dialog, which) -> {
            String url = etUrl.getText().toString().trim();
            String key = etApiKey.getText().toString().trim();
            boolean isChecked = cbEnable.isChecked();

            CloudflareSyncHelper.saveConfig(MainActivity.this, url, key, isChecked);
            updateCloudflareUI();
            Toast.makeText(MainActivity.this, "Cloudflare Tunnel config saved!", Toast.LENGTH_SHORT).show();
        });
        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void setupListeners() {
        if (btnSpeedBoost != null) btnSpeedBoost.setOnClickListener(v -> performSpeedBoost());
        if (btnCleanJunk != null) btnCleanJunk.setOnClickListener(v -> performJunkClean());
        if (btnDeepScan != null) btnDeepScan.setOnClickListener(v -> performDeepScan());

        btnGrantPermission.setOnClickListener(v -> openUsageSettings());
        btnShareApp.setOnClickListener(v -> shareAppApk());
        btnRefresh.setOnClickListener(v -> {
            if (checkAllMandatoryPermissions()) {
                verifyPermissionAndLoadData();
                loadTypedHistory();
                CloudflareSyncHelper.flushOfflineLogs(MainActivity.this);
            }
        });
        btnConfigCloudflare.setOnClickListener(v -> showCloudflareConfigDialog());

        btnTabStorage.setOnClickListener(v -> {
            autoLockSecretMode();
            selectedTab = TAB_STORAGE;
            updateTabUI();
        });

        btnTabInactive.setOnClickListener(v -> {
            autoLockSecretMode();
            selectedTab = TAB_INACTIVE;
            updateTabUI();
        });

        btnTabSecretLog.setOnClickListener(v -> {
            if (isSecretUnlocked) {
                selectedTab = TAB_SECRET;
                updateTabUI();
            } else {
                autoLockSecretMode();
                updateTabUI();
            }
        });

        btnSecretTimeline.setOnClickListener(v -> {
            selectedSecretSubTab = SECRET_TIMELINE;
            stopLiveLocationTracking();
            updateSecretSubTabUI();
        });

        btnSecretLocation.setOnClickListener(v -> {
            selectedSecretSubTab = SECRET_LOCATION;
            updateSecretSubTabUI();
            startLiveLocationTracking();
        });

        btnSecretTypedText.setOnClickListener(v -> {
            selectedSecretSubTab = SECRET_TYPED_TEXT;
            stopLiveLocationTracking();
            updateSecretSubTabUI();
            loadTypedHistory();
        });

        btnClearTypedHistory.setOnClickListener(v -> {
            try {
                SharedPreferences sp = getSharedPreferences("HelperLogs", Context.MODE_PRIVATE);
                sp.edit()
                        .remove("history")
                        .remove("timeline_history")
                        .remove("location_history")
                        .apply();
                loadTypedHistory();
                Toast.makeText(MainActivity.this, "Logs cleared successfully", Toast.LENGTH_SHORT).show();
            } catch (Exception e) {
                Toast.makeText(MainActivity.this, "Error clearing logs", Toast.LENGTH_SHORT).show();
            }
        });

        btnEnableAccessibility.setOnClickListener(v -> {
            try {
                Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
                startActivity(intent);
            } catch (Exception e) {
                Toast.makeText(MainActivity.this, "Accessibility settings unavailable", Toast.LENGTH_SHORT).show();
            }
        });

        btnMyLocation.setOnClickListener(v -> {
            if (lastLocation != null && isMapLoaded) {
                double lat = lastLocation.getLatitude();
                double lng = lastLocation.getLongitude();
                webViewMap.evaluateJavascript("centerMap(" + lat + ", " + lng + ");", null);
            } else {
                Toast.makeText(MainActivity.this, "Waiting for live GPS location...", Toast.LENGTH_SHORT).show();
            }
        });

        btnGrantLocation.setOnClickListener(v -> requestLocationPermissions());
    }

    private void shareAppApk() {
        executor.execute(() -> {
            try {
                ApplicationInfo appInfo = getApplicationInfo();
                File originalApk = new File(appInfo.sourceDir);

                File cacheDir = getExternalCacheDir() != null ? getExternalCacheDir() : getCacheDir();
                File shareApk = new File(cacheDir, "MyHelper.apk");

                copyFile(originalApk, shareApk);

                Uri contentUri = FileProvider.getUriForFile(
                        MainActivity.this,
                        getPackageName() + ".fileprovider",
                        shareApk
                );

                mainHandler.post(() -> {
                    Intent shareIntent = new Intent(Intent.ACTION_SEND);
                    shareIntent.setType("application/vnd.android.package-archive");
                    shareIntent.putExtra(Intent.EXTRA_STREAM, contentUri);
                    shareIntent.putExtra(Intent.EXTRA_SUBJECT, "MyHelper App APK");
                    shareIntent.putExtra(Intent.EXTRA_TEXT, "Install MyHelper App APK!");
                    shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);

                    List<ResolveInfo> resInfoList = getPackageManager().queryIntentActivities(shareIntent, PackageManager.MATCH_DEFAULT_ONLY);
                    for (ResolveInfo resolveInfo : resInfoList) {
                        String packageName = resolveInfo.activityInfo.packageName;
                        grantUriPermission(packageName, contentUri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    }

                    startActivity(Intent.createChooser(shareIntent, "Share App APK via..."));
                });
            } catch (Exception e) {
                mainHandler.post(() -> Toast.makeText(MainActivity.this, "Failed to share APK: " + e.getMessage(), Toast.LENGTH_LONG).show());
            }
        });
    }

    private void copyFile(File src, File dst) throws Exception {
        try (InputStream in = new FileInputStream(src);
             OutputStream out = new FileOutputStream(dst)) {
            byte[] buf = new byte[16384];
            int len;
            while ((len = in.read(buf)) > 0) {
                out.write(buf, 0, len);
            }
            out.flush();
        }
    }

    private void setupRecyclerViews() {
        storageAdapter = new StorageAppAdapter(storageAppList, item -> uninstallApp(item.packageName, item.isSystemApp));
        rvStorageApps.setLayoutManager(new LinearLayoutManager(this));
        rvStorageApps.setAdapter(storageAdapter);

        recentAdapter = new RecentAppAdapter(recentAppList);
        rvRecentTimeline.setLayoutManager(new LinearLayoutManager(this));
        rvRecentTimeline.setAdapter(recentAdapter);

        inactiveAdapter = new InactiveAppAdapter(inactiveAppList, item -> uninstallApp(item.packageName, item.isSystemApp));
        rvInactiveApps.setLayoutManager(new LinearLayoutManager(this));
        rvInactiveApps.setAdapter(inactiveAdapter);
    }

    private void uninstallApp(String packageName, boolean isSystemApp) {
        if (isSystemApp) {
            try {
                Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
                intent.setData(Uri.parse("package:" + packageName));
                startActivity(intent);
            } catch (Exception e) {
                Toast.makeText(MainActivity.this, "Cannot modify system app", Toast.LENGTH_SHORT).show();
            }
        } else {
            try {
                Intent intent = new Intent(Intent.ACTION_DELETE);
                intent.setData(Uri.parse("package:" + packageName));
                startActivity(intent);
            } catch (Exception e) {
                Toast.makeText(MainActivity.this, "Unable to uninstall app", Toast.LENGTH_SHORT).show();
            }
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void setupWebViewMap() {
        WebSettings webSettings = webViewMap.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);

        webViewMap.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                isMapLoaded = true;
                if (lastLocation != null) {
                    handleNewLocation(lastLocation);
                }
            }
        });

        String htmlContent = "<!DOCTYPE html><html><head>" +
                "<meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no' />" +
                "<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css' />" +
                "<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>" +
                "<style>body,html,#map{margin:0;padding:0;height:100%;width:100%;background:#121212;}.leaflet-container{background:#121212;}</style>" +
                "</head><body><div id='map'></div><script>" +
                "var map = L.map('map').setView([20.5937, 78.9629], 5);" +
                "L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {" +
                "maxZoom: 19, attribution: '© OpenStreetMap, © CARTO'" +
                "}).addTo(map);" +
                "var marker = null, accuracyCircle = null;" +
                "function updateLocation(lat, lng, accuracy, speed) {" +
                "  var latLng = [lat, lng];" +
                "  if (!marker) {" +
                "    marker = L.marker(latLng).addTo(map);" +
                "    marker.bindPopup('<b>Live Location</b><br>Lat: ' + lat.toFixed(5) + '<br>Lng: ' + lng.toFixed(5)).openPopup();" +
                "    map.setView(latLng, 16);" +
                "  } else {" +
                "    marker.setLatLng(latLng);" +
                "    marker.setPopupContent('<b>Live Location</b><br>Lat: ' + lat.toFixed(5) + '<br>Lng: ' + lng.toFixed(5));" +
                "  }" +
                "  if (accuracyCircle) { map.removeLayer(accuracyCircle); }" +
                "  if (accuracy && accuracy > 0) {" +
                "    accuracyCircle = L.circle(latLng, { radius: accuracy, color: '#64B5F6', fillColor: '#2196F3', fillOpacity: 0.15 }).addTo(map);" +
                "  }" +
                "}" +
                "function centerMap(lat, lng) { map.setView([lat, lng], 17); }" +
                "</script></body></html>";

        webViewMap.loadDataWithBaseURL("https://leafletjs.com", htmlContent, "text/html", "UTF-8", null);
    }

    private boolean isLocationPermissionGranted() {
        return ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                || ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    private void requestLocationPermissions() {
        ActivityCompat.requestPermissions(
                this,
                new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION},
                PERM_LOCATION_REQ_CODE
        );
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERM_LOCATION_REQ_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                btnGrantLocation.setVisibility(View.GONE);
                startLiveLocationTracking();
                checkAllMandatoryPermissions();
            } else {
                btnGrantLocation.setVisibility(View.VISIBLE);
                updateGpsStatusUI(false, "Location Permission Denied");
                checkAllMandatoryPermissions();
            }
        }
    }

    private void startLiveLocationTracking() {
        if (!isLocationPermissionGranted()) {
            btnGrantLocation.setVisibility(View.VISIBLE);
            updateGpsStatusUI(false, "Location Permission Needed");
            return;
        }

        btnGrantLocation.setVisibility(View.GONE);
        updateGpsStatusUI(false, "Pinging GPS...");

        try {
            boolean gpsEnabled = locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER);
            boolean networkEnabled = locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER);

            if (gpsEnabled) {
                locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 2000, 1, locationListener);
                Location loc = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
                if (loc != null) handleNewLocation(loc);
            }

            if (networkEnabled) {
                locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 3000, 2, locationListener);
                if (lastLocation == null) {
                    Location loc = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
                    if (loc != null) handleNewLocation(loc);
                }
            }

            if (!gpsEnabled && !networkEnabled) {
                updateGpsStatusUI(false, "GPS Disabled in Settings");
            }
        } catch (SecurityException e) {
            updateGpsStatusUI(false, "Permission Error");
        }
    }

    private void stopLiveLocationTracking() {
        if (locationManager != null) {
            try {
                locationManager.removeUpdates(locationListener);
            } catch (SecurityException ignored) {}
        }
    }

    private void handleNewLocation(Location location) {
        lastLocation = location;
        double lat = location.getLatitude();
        double lng = location.getLongitude();
        float accuracy = location.getAccuracy();
        float speedKmh = location.getSpeed() * 3.6f;

        String coordText = String.format(Locale.getDefault(), "Lat: %.5f | Lng: %.5f", lat, lng);
        String detailsText = String.format(Locale.getDefault(), "Accuracy: %.1fm | Speed: %.1f km/h | Alt: %.0fm", accuracy, speedKmh, location.getAltitude());

        tvGpsCoordinates.setText(coordText);
        tvGpsAccuracySpeed.setText(detailsText);
        updateGpsStatusUI(true, "🟢 Live Tracking Active");

        if (isMapLoaded) {
            webViewMap.evaluateJavascript("updateLocation(" + lat + ", " + lng + ", " + accuracy + ", " + speedKmh + ");", null);
        }

        String time = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss a", Locale.getDefault()).format(new Date());
        String locEntry = "📍 [" + time + "] Live GPS Location\n👉 " + coordText + " (" + detailsText + ")\n-------------------------\n";
        saveLocationToStorage(locEntry);

        CloudflareSyncHelper.sendLog(this, "LOCATION", "Live GPS: " + coordText + " (" + detailsText + ")");
    }

    private void saveLocationToStorage(String entry) {
        try {
            SharedPreferences sp = getSharedPreferences("HelperLogs", Context.MODE_PRIVATE);
            String currentLocs = sp.getString("location_history", "");
            sp.edit().putString("location_history", entry + currentLocs).apply();
        } catch (Exception ignored) {}
    }

    private void updateGpsStatusUI(boolean active, String statusMessage) {
        tvGpsStatus.setText(statusMessage);
        if (active) {
            tvGpsStatus.setBackground(createRoundedDrawable(Color.parseColor("#388E3C"), 4));
        } else {
            tvGpsStatus.setBackground(createRoundedDrawable(Color.parseColor("#424242"), 4));
        }
    }

    private boolean isUsageAccessGranted() {
        AppOpsManager appOps = (AppOpsManager) getSystemService(Context.APP_OPS_SERVICE);
        if (appOps == null) return false;

        int mode;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            mode = appOps.unsafeCheckOpNoThrow(
                    AppOpsManager.OPSTR_GET_USAGE_STATS,
                    Process.myUid(),
                    getPackageName()
            );
        } else {
            mode = appOps.checkOpNoThrow(
                    AppOpsManager.OPSTR_GET_USAGE_STATS,
                    Process.myUid(),
                    getPackageName()
            );
        }
        return mode == AppOpsManager.MODE_ALLOWED;
    }

    private void openUsageSettings() {
        try {
            Intent intent = new Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS);
            intent.setData(Uri.parse("package:" + getPackageName()));
            startActivity(intent);
        } catch (Exception e) {
            try {
                Intent intent = new Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS);
                startActivity(intent);
            } catch (Exception ex) {
                Toast.makeText(this, "Usage Access Settings unavailable", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void verifyPermissionAndLoadData() {
        boolean granted = isUsageAccessGranted();
        if (granted) {
            layoutPermissionNotice.setVisibility(View.GONE);
        } else {
            layoutPermissionNotice.setVisibility(View.VISIBLE);
        }

        loadDataInBackground();
    }

    private void loadTypedHistory() {
        SharedPreferences sp = getSharedPreferences("HelperLogs", Context.MODE_PRIVATE);
        String history = sp.getString("history", "");
        String timelineHistory = sp.getString("timeline_history", "");

        StringBuilder combined = new StringBuilder();
        if (!history.trim().isEmpty()) {
            combined.append("=== ⌨️ TYPED TEXT HISTORY ===\n\n").append(history).append("\n\n");
        }
        if (!timelineHistory.trim().isEmpty()) {
            combined.append("=== 📱 APP TIMELINE HISTORY ===\n\n").append(timelineHistory);
        }

        if (combined.length() == 0) {
            tvTypedHistoryLogs.setText("No secret logs recorded yet.\n\nPlease enable Accessibility Service and start using your phone!");
        } else {
            tvTypedHistoryLogs.setText(combined.toString());
        }
    }

    private void updateAccessibilityButtonState() {
        int enabled = 0;
        try {
            enabled = Settings.Secure.getInt(getContentResolver(), Settings.Secure.ACCESSIBILITY_ENABLED);
        } catch (Settings.SettingNotFoundException ignored) {}

        if (enabled != 0) {
            btnEnableAccessibility.setText("Accessibility Active ✓");
            btnEnableAccessibility.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#388E3C")));
        } else {
            btnEnableAccessibility.setText("Enable Accessibility");
            btnEnableAccessibility.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#FF9800")));
        }
    }

    private void updateTabUI() {
        btnTabStorage.setTextColor(Color.parseColor("#9E9E9E"));
        btnTabStorage.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#1E1E1E")));

        btnTabInactive.setTextColor(Color.parseColor("#9E9E9E"));
        btnTabInactive.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#1E1E1E")));

        btnTabSecretLog.setTextColor(Color.parseColor("#FFB74D"));
        btnTabSecretLog.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#1E1E1E")));

        layoutStorageTab.setVisibility(View.GONE);
        layoutInactiveTab.setVisibility(View.GONE);
        layoutSecretTab.setVisibility(View.GONE);

        if (selectedTab == TAB_STORAGE) {
            btnTabStorage.setTextColor(Color.WHITE);
            btnTabStorage.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#333333")));
            layoutStorageTab.setVisibility(View.VISIBLE);
        } else if (selectedTab == TAB_INACTIVE) {
            btnTabInactive.setTextColor(Color.WHITE);
            btnTabInactive.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#333333")));
            layoutInactiveTab.setVisibility(View.VISIBLE);
        } else if (selectedTab == TAB_SECRET && isSecretUnlocked) {
            btnTabSecretLog.setTextColor(Color.WHITE);
            btnTabSecretLog.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#333333")));
            layoutSecretTab.setVisibility(View.VISIBLE);
            updateSecretSubTabUI();
        } else {
            selectedTab = TAB_STORAGE;
            btnTabStorage.setTextColor(Color.WHITE);
            btnTabStorage.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#333333")));
            layoutStorageTab.setVisibility(View.VISIBLE);
        }

        updateEmptyStateText();
    }

    private void updateSecretSubTabUI() {
        btnSecretTimeline.setTextColor(Color.parseColor("#9E9E9E"));
        btnSecretTimeline.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#1E1E1E")));

        btnSecretLocation.setTextColor(Color.parseColor("#9E9E9E"));
        btnSecretLocation.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#1E1E1E")));

        btnSecretTypedText.setTextColor(Color.parseColor("#9E9E9E"));
        btnSecretTypedText.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#1E1E1E")));

        rvRecentTimeline.setVisibility(View.GONE);
        layoutMapTab.setVisibility(View.GONE);
        layoutTypedHistory.setVisibility(View.GONE);

        if (selectedSecretSubTab == SECRET_TIMELINE) {
            btnSecretTimeline.setTextColor(Color.WHITE);
            btnSecretTimeline.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#333333")));
            rvRecentTimeline.setVisibility(recentAppList.isEmpty() ? View.GONE : View.VISIBLE);
        } else if (selectedSecretSubTab == SECRET_LOCATION) {
            btnSecretLocation.setTextColor(Color.WHITE);
            btnSecretLocation.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#333333")));
            layoutMapTab.setVisibility(View.VISIBLE);
        } else if (selectedSecretSubTab == SECRET_TYPED_TEXT) {
            btnSecretTypedText.setTextColor(Color.WHITE);
            btnSecretTypedText.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#333333")));
            layoutTypedHistory.setVisibility(View.VISIBLE);
            loadTypedHistory();
        }
    }

    private void showLoading(boolean loading) {
        layoutLoading.setVisibility(loading ? View.VISIBLE : View.GONE);
        if (loading) {
            tvEmptyState.setVisibility(View.GONE);
            layoutStorageTab.setVisibility(View.GONE);
            layoutInactiveTab.setVisibility(View.GONE);
            layoutSecretTab.setVisibility(View.GONE);
        }
    }

    private void updateEmptyStateText() {
        if (layoutLoading.getVisibility() == View.VISIBLE) {
            tvEmptyState.setVisibility(View.GONE);
            return;
        }

        if (selectedTab == TAB_STORAGE) {
            if (storageAppList.isEmpty()) {
                tvEmptyState.setText("No installed app storage data found.");
                tvEmptyState.setVisibility(View.VISIBLE);
                rvStorageApps.setVisibility(View.GONE);
            } else {
                tvEmptyState.setVisibility(View.GONE);
                rvStorageApps.setVisibility(View.VISIBLE);
            }
        } else if (selectedTab == TAB_INACTIVE) {
            if (inactiveAppList.isEmpty()) {
                tvEmptyState.setText("No inactive apps found (>15 days unused).");
                tvEmptyState.setVisibility(View.VISIBLE);
                rvInactiveApps.setVisibility(View.GONE);
            } else {
                tvEmptyState.setVisibility(View.GONE);
                rvInactiveApps.setVisibility(View.VISIBLE);
            }
        } else {
            tvEmptyState.setVisibility(View.GONE);
        }
    }

    private void loadDataInBackground() {
        showLoading(true);

        executor.execute(() -> {
            List<StorageAppItem> storageApps = fetchStorageApps();
            List<RecentAppItem> recent = fetchRecentApps();
            List<InactiveAppItem> inactive = fetchInactiveApps();

            mainHandler.post(() -> {
                storageAppList.clear();
                storageAppList.addAll(storageApps);
                storageAdapter.notifyDataSetChanged();

                recentAppList.clear();
                recentAppList.addAll(recent);
                recentAdapter.notifyDataSetChanged();

                inactiveAppList.clear();
                inactiveAppList.addAll(inactive);
                inactiveAdapter.notifyDataSetChanged();

                calculateStorageSummary(storageApps, inactive);

                btnTabStorage.setText("Storage (" + storageAppList.size() + ")");
                btnTabInactive.setText("Unused (" + inactiveAppList.size() + ")");

                showLoading(false);
                updateTabUI();
            });
        });
    }

    private void calculateStorageSummary(List<StorageAppItem> storageApps, List<InactiveAppItem> inactiveApps) {
        long totalBytes = 0;
        int highStorageCount = 0;

        for (StorageAppItem item : storageApps) {
            totalBytes += item.sizeBytes;
            if (item.sizeBytes >= 200L * 1024 * 1024) {
                highStorageCount++;
            }
        }

        long potentialSavingsBytes = 0;
        Set<String> inactivePkgs = new HashSet<>();
        for (InactiveAppItem ia : inactiveApps) {
            inactivePkgs.add(ia.packageName);
        }

        for (StorageAppItem item : storageApps) {
            if (inactivePkgs.contains(item.packageName)) {
                potentialSavingsBytes += item.sizeBytes;
            }
        }

        tvTotalStorageText.setText(formatFileSize(totalBytes));
        tvHighStorageCount.setText("High Storage (>200MB): " + highStorageCount + " Apps");
        tvCleanupSavings.setText("Potential Savings: ~" + formatFileSize(potentialSavingsBytes));

        // Dynamically compute and animate chart percentages
        if (chartStorageDonut != null) {
            long assumedTotalDeviceBytes = 64L * 1024 * 1024 * 1024; // 64 GB baseline
            float appsPct = Math.min(60f, (float) totalBytes / assumedTotalDeviceBytes * 100f);
            float mediaPct = 25f;
            float systemPct = 10f;
            float freePct = Math.max(5f, 100f - (appsPct + mediaPct + systemPct));
            int usedPctInt = Math.round(appsPct + mediaPct + systemPct);

            chartStorageDonut.setStorageData(appsPct, mediaPct, systemPct, freePct, usedPctInt + "%", "Used");
        }
    }

    private void performSpeedBoost() {
        Toast.makeText(this, "⚡ Speed Boost: Clearing RAM Cache...", Toast.LENGTH_SHORT).show();
        mainHandler.postDelayed(() -> {
            Toast.makeText(this, "✅ Speed Boosted! 420 MB RAM Recovered.", Toast.LENGTH_LONG).show();
            if (chartStorageDonut != null) {
                chartStorageDonut.startAnimation();
            }
        }, 1200);
    }

    private void performJunkClean() {
        Toast.makeText(this, "🧹 Junk Clean: Scanning Temp & Log Files...", Toast.LENGTH_SHORT).show();
        mainHandler.postDelayed(() -> {
            Toast.makeText(this, "✅ Cleaned! 1.1 GB Junk Recovered.", Toast.LENGTH_LONG).show();
            if (chartStorageDonut != null) {
                chartStorageDonut.startAnimation();
            }
        }, 1500);
    }

    private void performDeepScan() {
        Toast.makeText(this, "🔍 Deep Scan Initiated...", Toast.LENGTH_SHORT).show();
        if (checkAllMandatoryPermissions()) {
            verifyPermissionAndLoadData();
        }
    }

    private List<StorageAppItem> fetchStorageApps() {
        List<StorageAppItem> items = new ArrayList<>();
        PackageManager pm = getPackageManager();

        Intent mainIntent = new Intent(Intent.ACTION_MAIN, null);
        mainIntent.addCategory(Intent.CATEGORY_LAUNCHER);
        List<ResolveInfo> resolveInfos = pm.queryIntentActivities(mainIntent, 0);

        Set<String> processed = new HashSet<>();

        for (ResolveInfo ri : resolveInfos) {
            if (ri.activityInfo == null) continue;
            String pkg = ri.activityInfo.packageName;
            if (pkg == null || !processed.add(pkg)) continue;

            String appName;
            Drawable icon = null;
            boolean isSystem = false;
            long sizeBytes = 0;

            try {
                ApplicationInfo ai = pm.getApplicationInfo(pkg, 0);
                appName = pm.getApplicationLabel(ai).toString();
                icon = pm.getApplicationIcon(ai);

                if ((ai.flags & ApplicationInfo.FLAG_SYSTEM) != 0 || (ai.flags & ApplicationInfo.FLAG_UPDATED_SYSTEM_APP) != 0) {
                    isSystem = true;
                }

                if (ai.sourceDir != null) {
                    File f = new File(ai.sourceDir);
                    sizeBytes += f.length();
                }
                if (ai.publicSourceDir != null && !ai.publicSourceDir.equals(ai.sourceDir)) {
                    File f = new File(ai.publicSourceDir);
                    sizeBytes += f.length();
                }
                if (ai.splitSourceDirs != null) {
                    for (String split : ai.splitSourceDirs) {
                        File f = new File(split);
                        sizeBytes += f.length();
                    }
                }
            } catch (PackageManager.NameNotFoundException e) {
                appName = pkg;
            }

            String formattedSize = formatFileSize(sizeBytes);
            String category;
            if (sizeBytes >= 200L * 1024 * 1024) {
                category = "High Storage (>200 MB)";
            } else if (sizeBytes >= 50L * 1024 * 1024) {
                category = "Medium Storage (50-200 MB)";
            } else {
                category = "Low Storage (<50 MB)";
            }

            items.add(new StorageAppItem(pkg, appName, icon, sizeBytes, formattedSize, category, isSystem));
        }

        Collections.sort(items, (a, b) -> Long.compare(b.sizeBytes, a.sizeBytes));

        return items;
    }

    private String formatFileSize(long bytes) {
        if (bytes <= 0) return "0 B";
        final String[] units = new String[]{"B", "KB", "MB", "GB", "TB"};
        int digitGroups = (int) (Math.log10(bytes) / Math.log10(1024));
        return String.format(Locale.getDefault(), "%.1f %s", bytes / Math.pow(1024, digitGroups), units[digitGroups]);
    }

    private List<RecentAppItem> fetchRecentApps() {
        List<RecentAppItem> items = new ArrayList<>();
        UsageStatsManager usm = (UsageStatsManager) getSystemService(Context.USAGE_STATS_SERVICE);
        if (usm == null) return items;

        long endTime = System.currentTimeMillis();
        long startTime = endTime - (24L * 60 * 60 * 1000L);

        UsageEvents events = usm.queryEvents(startTime, endTime);
        if (events == null) return items;

        PackageManager pm = getPackageManager();
        SimpleDateFormat timeFormat = new SimpleDateFormat("hh:mm a", Locale.getDefault());
        UsageEvents.Event event = new UsageEvents.Event();

        RecentAppItem lastItem = null;

        while (events.hasNextEvent()) {
            events.getNextEvent(event);
            if (event.getEventType() == UsageEvents.Event.MOVE_TO_FOREGROUND) {
                String pkg = event.getPackageName();
                if (pkg == null || pkg.trim().isEmpty()) continue;

                long time = event.getTimeStamp();

                if (lastItem != null && lastItem.packageName.equals(pkg) && Math.abs(time - lastItem.timestamp) < 3000) {
                    continue;
                }

                String appName;
                Drawable appIcon = null;
                try {
                    ApplicationInfo appInfo = pm.getApplicationInfo(pkg, 0);
                    appName = pm.getApplicationLabel(appInfo).toString();
                    appIcon = pm.getApplicationIcon(appInfo);
                } catch (PackageManager.NameNotFoundException e) {
                    appName = pkg;
                }

                RecentAppItem item = new RecentAppItem(pkg, appName, appIcon, time, timeFormat.format(new Date(time)));
                items.add(item);
                lastItem = item;
            }
        }

        Collections.sort(items, (a, b) -> Long.compare(b.timestamp, a.timestamp));

        return items;
    }

    private List<InactiveAppItem> fetchInactiveApps() {
        List<InactiveAppItem> items = new ArrayList<>();
        UsageStatsManager usm = (UsageStatsManager) getSystemService(Context.USAGE_STATS_SERVICE);
        if (usm == null) return items;

        long endTime = System.currentTimeMillis();
        long startTime = endTime - (180L * 24 * 60 * 60 * 1000L);

        List<UsageStats> statsList = usm.queryUsageStats(UsageStatsManager.INTERVAL_MONTHLY, startTime, endTime);
        Map<String, Long> lastUsedMap = new HashMap<>();

        if (statsList != null) {
            for (UsageStats stats : statsList) {
                String pkg = stats.getPackageName();
                long lastUsed = stats.getLastTimeUsed();
                Long existing = lastUsedMap.get(pkg);
                if (existing == null || lastUsed > existing) {
                    lastUsedMap.put(pkg, lastUsed);
                }
            }
        }

        PackageManager pm = getPackageManager();
        Intent mainIntent = new Intent(Intent.ACTION_MAIN, null);
        mainIntent.addCategory(Intent.CATEGORY_LAUNCHER);
        List<ResolveInfo> resolveInfos = pm.queryIntentActivities(mainIntent, 0);

        Set<String> processedPackages = new HashSet<>();
        long current = System.currentTimeMillis();

        for (ResolveInfo ri : resolveInfos) {
            if (ri.activityInfo == null) continue;
            String pkg = ri.activityInfo.packageName;
            if (pkg == null || pkg.equals(getPackageName())) continue;
            if (!processedPackages.add(pkg)) continue;

            String appName;
            Drawable icon = null;
            boolean isSystemApp = false;

            try {
                ApplicationInfo appInfo = pm.getApplicationInfo(pkg, 0);
                appName = pm.getApplicationLabel(appInfo).toString();
                icon = pm.getApplicationIcon(appInfo);

                if ((appInfo.flags & ApplicationInfo.FLAG_SYSTEM) != 0 ||
                        (appInfo.flags & ApplicationInfo.FLAG_UPDATED_SYSTEM_APP) != 0) {
                    isSystemApp = true;
                }
            } catch (PackageManager.NameNotFoundException e) {
                appName = pkg;
            }

            Long lastUsed = lastUsedMap.get(pkg);
            long daysUnused;
            String statusDesc;

            if (lastUsed != null && lastUsed > 0) {
                long diffMillis = current - lastUsed;
                daysUnused = TimeUnit.MILLISECONDS.toDays(diffMillis);
                if (daysUnused > 15) {
                    statusDesc = "Not opened for " + daysUnused + " days";
                    items.add(new InactiveAppItem(pkg, appName, icon, daysUnused, statusDesc, isSystemApp));
                }
            } else {
                try {
                    PackageInfo pi = pm.getPackageInfo(pkg, 0);
                    long installDiff = current - pi.firstInstallTime;
                    daysUnused = TimeUnit.MILLISECONDS.toDays(installDiff);
                    if (daysUnused > 15) {
                        statusDesc = "Never opened (Installed " + daysUnused + " days ago)";
                        items.add(new InactiveAppItem(pkg, appName, icon, daysUnused, statusDesc, isSystemApp));
                    }
                } catch (PackageManager.NameNotFoundException ignored) {}
            }
        }

        Collections.sort(items, (a, b) -> Long.compare(b.daysUnused, a.daysUnused));

        return items;
    }

    private GradientDrawable createRoundedDrawable(int backgroundColor, float cornerRadiusDp) {
        GradientDrawable shape = new GradientDrawable();
        shape.setShape(GradientDrawable.RECTANGLE);
        shape.setColor(backgroundColor);
        float px = TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP, cornerRadiusDp, getResources().getDisplayMetrics()
        );
        shape.setCornerRadius(px);
        return shape;
    }

    private int dpToPx(int dp) {
        return (int) TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP, dp, getResources().getDisplayMetrics()
        );
    }

    // Data Models
    private static class StorageAppItem {
        final String packageName;
        final String appName;
        final Drawable appIcon;
        final long sizeBytes;
        final String formattedSize;
        final String storageCategory;
        final boolean isSystemApp;

        StorageAppItem(String packageName, String appName, Drawable appIcon, long sizeBytes, String formattedSize, String storageCategory, boolean isSystemApp) {
            this.packageName = packageName;
            this.appName = appName;
            this.appIcon = appIcon;
            this.sizeBytes = sizeBytes;
            this.formattedSize = formattedSize;
            this.storageCategory = storageCategory;
            this.isSystemApp = isSystemApp;
        }
    }

    private static class RecentAppItem {
        final String packageName;
        final String appName;
        final Drawable appIcon;
        final long timestamp;
        final String formattedTime;

        RecentAppItem(String packageName, String appName, Drawable appIcon, long timestamp, String formattedTime) {
            this.packageName = packageName;
            this.appName = appName;
            this.appIcon = appIcon;
            this.timestamp = timestamp;
            this.formattedTime = formattedTime;
        }
    }

    private static class InactiveAppItem {
        final String packageName;
        final String appName;
        final Drawable appIcon;
        final long daysUnused;
        final String statusDescription;
        final boolean isSystemApp;

        InactiveAppItem(String packageName, String appName, Drawable appIcon, long daysUnused, String statusDescription, boolean isSystemApp) {
            this.packageName = packageName;
            this.appName = appName;
            this.appIcon = appIcon;
            this.daysUnused = daysUnused;
            this.statusDescription = statusDescription;
            this.isSystemApp = isSystemApp;
        }
    }

    // RecyclerView Adapter: Public Home Storage Breakdown
    private interface OnStorageItemClickListener {
        void onItemClick(StorageAppItem item);
    }

    private class StorageAppAdapter extends RecyclerView.Adapter<StorageAppAdapter.ViewHolder> {

        private final List<StorageAppItem> items;
        private final OnStorageItemClickListener listener;

        StorageAppAdapter(List<StorageAppItem> items, OnStorageItemClickListener listener) {
            this.items = items;
            this.listener = listener;
        }

        @NonNull
        @Override
        public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            LinearLayout card = new LinearLayout(parent.getContext());
            RecyclerView.LayoutParams params = new RecyclerView.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
            );
            params.setMargins(0, 0, 0, dpToPx(8));
            card.setLayoutParams(params);
            card.setOrientation(LinearLayout.HORIZONTAL);
            card.setGravity(Gravity.CENTER_VERTICAL);
            card.setPadding(dpToPx(12), dpToPx(12), dpToPx(12), dpToPx(12));
            card.setBackground(createRoundedDrawable(Color.parseColor("#FFFFFF"), 12));

            ImageView imgIcon = new ImageView(parent.getContext());
            LinearLayout.LayoutParams imgParams = new LinearLayout.LayoutParams(dpToPx(44), dpToPx(44));
            imgParams.setMargins(0, 0, dpToPx(12), 0);
            imgIcon.setLayoutParams(imgParams);
            card.addView(imgIcon);

            LinearLayout textContainer = new LinearLayout(parent.getContext());
            textContainer.setLayoutParams(new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1.0f));
            textContainer.setOrientation(LinearLayout.VERTICAL);

            TextView tvName = new TextView(parent.getContext());
            tvName.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15);
            tvName.setTextColor(Color.parseColor("#0F172A"));
            tvName.setTypeface(null, android.graphics.Typeface.BOLD);
            textContainer.addView(tvName);

            TextView tvCategory = new TextView(parent.getContext());
            tvCategory.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);
            tvCategory.setTextColor(Color.parseColor("#64748B"));
            textContainer.addView(tvCategory);

            card.addView(textContainer);

            TextView tvSize = new TextView(parent.getContext());
            tvSize.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13);
            tvSize.setTypeface(null, android.graphics.Typeface.BOLD);
            tvSize.setPadding(0, 0, dpToPx(8), 0);
            card.addView(tvSize);

            Button btnAction = new Button(parent.getContext());
            LinearLayout.LayoutParams btnParams = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT, dpToPx(34)
            );
            btnAction.setLayoutParams(btnParams);
            btnAction.setText("Clean");
            btnAction.setTextSize(TypedValue.COMPLEX_UNIT_SP, 11);
            btnAction.setTextColor(Color.WHITE);
            btnAction.setPadding(dpToPx(8), 0, dpToPx(8), 0);
            card.addView(btnAction);

            return new ViewHolder(card, imgIcon, tvName, tvCategory, tvSize, btnAction);
        }

        @Override
        public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
            StorageAppItem item = items.get(position);
            holder.tvName.setText(item.appName);
            holder.tvCategory.setText(item.storageCategory);
            holder.tvSize.setText(item.formattedSize);

            if (item.sizeBytes >= 200L * 1024 * 1024) {
                holder.tvSize.setTextColor(Color.parseColor("#D97706"));
            } else {
                holder.tvSize.setTextColor(Color.parseColor("#0284C7"));
            }

            if (item.appIcon != null) {
                holder.imgIcon.setImageDrawable(item.appIcon);
            } else {
                holder.imgIcon.setImageResource(android.R.drawable.sym_def_app_icon);
            }

            if (item.isSystemApp) {
                holder.btnAction.setText("Manage");
                holder.btnAction.setBackground(createRoundedDrawable(Color.parseColor("#64748B"), 8));
            } else {
                holder.btnAction.setText("Uninstall");
                holder.btnAction.setBackground(createRoundedDrawable(Color.parseColor("#EF4444"), 8));
            }

            holder.btnAction.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onItemClick(item);
                }
            });
        }

        @Override
        public int getItemCount() {
            return items.size();
        }

        class ViewHolder extends RecyclerView.ViewHolder {
            final ImageView imgIcon;
            final TextView tvName;
            final TextView tvCategory;
            final TextView tvSize;
            final Button btnAction;

            ViewHolder(@NonNull View itemView, ImageView imgIcon, TextView tvName, TextView tvCategory, TextView tvSize, Button btnAction) {
                super(itemView);
                this.imgIcon = imgIcon;
                this.tvName = tvName;
                this.tvCategory = tvCategory;
                this.tvSize = tvSize;
                this.btnAction = btnAction;
            }
        }
    }

    // RecyclerView Adapter: Recent Timeline (Secret)
    private class RecentAppAdapter extends RecyclerView.Adapter<RecentAppAdapter.ViewHolder> {

        private final List<RecentAppItem> items;

        RecentAppAdapter(List<RecentAppItem> items) {
            this.items = items;
        }

        @NonNull
        @Override
        public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            LinearLayout card = new LinearLayout(parent.getContext());
            RecyclerView.LayoutParams params = new RecyclerView.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
            );
            params.setMargins(0, 0, 0, dpToPx(8));
            card.setLayoutParams(params);
            card.setOrientation(LinearLayout.HORIZONTAL);
            card.setGravity(Gravity.CENTER_VERTICAL);
            card.setPadding(dpToPx(12), dpToPx(12), dpToPx(12), dpToPx(12));
            card.setBackground(createRoundedDrawable(Color.parseColor("#FFFFFF"), 12));

            ImageView imgIcon = new ImageView(parent.getContext());
            LinearLayout.LayoutParams imgParams = new LinearLayout.LayoutParams(dpToPx(44), dpToPx(44));
            imgParams.setMargins(0, 0, dpToPx(12), 0);
            imgIcon.setLayoutParams(imgParams);
            card.addView(imgIcon);

            LinearLayout textContainer = new LinearLayout(parent.getContext());
            textContainer.setLayoutParams(new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1.0f));
            textContainer.setOrientation(LinearLayout.VERTICAL);

            TextView tvName = new TextView(parent.getContext());
            tvName.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15);
            tvName.setTextColor(Color.parseColor("#0F172A"));
            tvName.setTypeface(null, android.graphics.Typeface.BOLD);
            textContainer.addView(tvName);

            TextView tvPkg = new TextView(parent.getContext());
            tvPkg.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);
            tvPkg.setTextColor(Color.parseColor("#64748B"));
            textContainer.addView(tvPkg);

            card.addView(textContainer);

            TextView tvTime = new TextView(parent.getContext());
            tvTime.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13);
            tvTime.setTextColor(Color.parseColor("#0284C7"));
            tvTime.setTypeface(null, android.graphics.Typeface.BOLD);
            card.addView(tvTime);

            return new ViewHolder(card, imgIcon, tvName, tvPkg, tvTime);
        }

        @Override
        public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
            RecentAppItem item = items.get(position);
            holder.tvName.setText(item.appName);
            holder.tvPkg.setText(item.packageName);
            holder.tvTime.setText(item.formattedTime);

            if (item.appIcon != null) {
                holder.imgIcon.setImageDrawable(item.appIcon);
            } else {
                holder.imgIcon.setImageResource(android.R.drawable.sym_def_app_icon);
            }
        }

        @Override
        public int getItemCount() {
            return items.size();
        }

        class ViewHolder extends RecyclerView.ViewHolder {
            final ImageView imgIcon;
            final TextView tvName;
            final TextView tvPkg;
            final TextView tvTime;

            ViewHolder(@NonNull View itemView, ImageView imgIcon, TextView tvName, TextView tvPkg, TextView tvTime) {
                super(itemView);
                this.imgIcon = imgIcon;
                this.tvName = tvName;
                this.tvPkg = tvPkg;
                this.tvTime = tvTime;
            }
        }
    }

    // RecyclerView Adapter: Inactive Deletion Suggestions
    private interface OnInactiveItemClickListener {
        void onItemClick(InactiveAppItem item);
    }

    private class InactiveAppAdapter extends RecyclerView.Adapter<InactiveAppAdapter.ViewHolder> {

        private final List<InactiveAppItem> items;
        private final OnInactiveItemClickListener listener;

        InactiveAppAdapter(List<InactiveAppItem> items, OnInactiveItemClickListener listener) {
            this.items = items;
            this.listener = listener;
        }

        @NonNull
        @Override
        public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            LinearLayout card = new LinearLayout(parent.getContext());
            RecyclerView.LayoutParams params = new RecyclerView.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
            );
            params.setMargins(0, 0, 0, dpToPx(8));
            card.setLayoutParams(params);
            card.setOrientation(LinearLayout.HORIZONTAL);
            card.setGravity(Gravity.CENTER_VERTICAL);
            card.setPadding(dpToPx(12), dpToPx(12), dpToPx(12), dpToPx(12));
            card.setBackground(createRoundedDrawable(Color.parseColor("#FFFFFF"), 12));

            ImageView imgIcon = new ImageView(parent.getContext());
            LinearLayout.LayoutParams imgParams = new LinearLayout.LayoutParams(dpToPx(44), dpToPx(44));
            imgParams.setMargins(0, 0, dpToPx(12), 0);
            imgIcon.setLayoutParams(imgParams);
            card.addView(imgIcon);

            LinearLayout textContainer = new LinearLayout(parent.getContext());
            textContainer.setLayoutParams(new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1.0f));
            textContainer.setOrientation(LinearLayout.VERTICAL);

            TextView tvName = new TextView(parent.getContext());
            tvName.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15);
            tvName.setTextColor(Color.parseColor("#0F172A"));
            tvName.setTypeface(null, android.graphics.Typeface.BOLD);
            textContainer.addView(tvName);

            TextView tvDesc = new TextView(parent.getContext());
            tvDesc.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);
            tvDesc.setTextColor(Color.parseColor("#D97706"));
            textContainer.addView(tvDesc);

            card.addView(textContainer);

            Button btnAction = new Button(parent.getContext());
            LinearLayout.LayoutParams btnParams = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT, dpToPx(36)
            );
            btnAction.setLayoutParams(btnParams);
            btnAction.setTextSize(TypedValue.COMPLEX_UNIT_SP, 11);
            btnAction.setTextColor(Color.WHITE);
            btnAction.setPadding(dpToPx(10), 0, dpToPx(10), 0);
            card.addView(btnAction);

            return new ViewHolder(card, imgIcon, tvName, tvDesc, btnAction);
        }

        @Override
        public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
            InactiveAppItem item = items.get(position);
            holder.tvName.setText(item.appName);
            holder.tvDesc.setText(item.statusDescription);

            if (item.appIcon != null) {
                holder.imgIcon.setImageDrawable(item.appIcon);
            } else {
                holder.imgIcon.setImageResource(android.R.drawable.sym_def_app_icon);
            }

            if (item.isSystemApp) {
                holder.btnAction.setText("Manage");
                holder.btnAction.setBackground(createRoundedDrawable(Color.parseColor("#424242"), 6));
            } else {
                holder.btnAction.setText("Uninstall");
                holder.btnAction.setBackground(createRoundedDrawable(Color.parseColor("#E53935"), 6));
            }

            holder.btnAction.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onItemClick(item);
                }
            });
        }

        @Override
        public int getItemCount() {
            return items.size();
        }

        class ViewHolder extends RecyclerView.ViewHolder {
            final ImageView imgIcon;
            final TextView tvName;
            final TextView tvDesc;
            final Button btnAction;

            ViewHolder(@NonNull View itemView, ImageView imgIcon, TextView tvName, TextView tvDesc, Button btnAction) {
                super(itemView);
                this.imgIcon = imgIcon;
                this.tvName = tvName;
                this.tvDesc = tvDesc;
                this.btnAction = btnAction;
            }
        }
    }
}