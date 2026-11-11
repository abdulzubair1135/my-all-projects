package com.projectflow.android.ui;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.media.MediaPlayer;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.widget.LinearLayout;
import android.widget.VideoView;
import androidx.appcompat.app.AppCompatActivity;
import com.projectflow.android.R;

public class SplashActivity extends AppCompatActivity {

    private static final String TAG = "SplashActivity";
    private VideoView videoViewSplash;
    private View rootSplashLayout;
    private View vSplashCover;
    private LinearLayout llFallbackLogo;
    private boolean hasNavigated = false;
    private final Handler timeoutHandler = new Handler(Looper.getMainLooper());
    private Runnable timeoutRunnable;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Enforce default Light Mode on launch
        SharedPreferences themePrefs = getSharedPreferences("projectflow_prefs", Context.MODE_PRIVATE);
        String theme = themePrefs.getString("app_theme", "light");
        if ("dark".equalsIgnoreCase(theme)) {
            androidx.appcompat.app.AppCompatDelegate.setDefaultNightMode(androidx.appcompat.app.AppCompatDelegate.MODE_NIGHT_YES);
        } else if ("system".equalsIgnoreCase(theme)) {
            androidx.appcompat.app.AppCompatDelegate.setDefaultNightMode(androidx.appcompat.app.AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM);
        } else {
            androidx.appcompat.app.AppCompatDelegate.setDefaultNightMode(androidx.appcompat.app.AppCompatDelegate.MODE_NIGHT_NO);
        }

        super.onCreate(savedInstanceState);

        // Seamless light status bar matching limestone mineral theme #F4F2E9
        Window window = getWindow();
        window.clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS);
        window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        window.setStatusBarColor(Color.parseColor("#F4F2E9"));
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            window.getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
        }

        setContentView(R.layout.activity_splash);

        videoViewSplash = findViewById(R.id.videoViewSplash);
        rootSplashLayout = findViewById(R.id.rootSplashLayout);
        vSplashCover = findViewById(R.id.vSplashCover);
        llFallbackLogo = findViewById(R.id.llFallbackLogo);

        // Tap anywhere on screen to skip/proceed immediately
        if (rootSplashLayout != null) {
            rootSplashLayout.setOnClickListener(v -> navigateNext());
        }
        if (videoViewSplash != null) {
            videoViewSplash.setOnClickListener(v -> navigateNext());
        }
        if (vSplashCover != null) {
            vSplashCover.setOnClickListener(v -> navigateNext());
        }

        // Safety fallback timeout (11.5s) in case of system media decoder hang
        timeoutRunnable = this::navigateNext;
        timeoutHandler.postDelayed(timeoutRunnable, 11500);

        playStartupVideo();
    }

    private void playStartupVideo() {
        try {
            Uri videoUri = Uri.parse("android.resource://" + getPackageName() + "/" + R.raw.splash_video);
            videoViewSplash.setVideoURI(videoUri);

            videoViewSplash.setOnPreparedListener(mp -> {
                Log.d(TAG, "Startup video prepared.");
                mp.setLooping(false);

                // Anti-flicker: hide cover view only when video rendering has physically started!
                mp.setOnInfoListener((mediaPlayer, what, extra) -> {
                    if (what == MediaPlayer.MEDIA_INFO_VIDEO_RENDERING_START) {
                        Log.d(TAG, "Video rendering started on screen -> smoothly revealing video.");
                        if (vSplashCover != null) {
                            vSplashCover.animate()
                                    .alpha(0f)
                                    .setDuration(120)
                                    .withEndAction(() -> vSplashCover.setVisibility(View.GONE))
                                    .start();
                        }
                        return true;
                    }
                    return false;
                });

                videoViewSplash.start();
            });

            videoViewSplash.setOnCompletionListener(mp -> {
                Log.d(TAG, "Startup video playback completed -> navigating.");
                navigateNext();
            });

            videoViewSplash.setOnErrorListener((mp, what, extra) -> {
                Log.w(TAG, "VideoView playback error: " + what + ", " + extra + " -> using fallback");
                showFallbackAndProceed();
                return true;
            });
        } catch (Exception e) {
            Log.e(TAG, "Failed to initialize VideoView", e);
            showFallbackAndProceed();
        }
    }

    private void showFallbackAndProceed() {
        if (vSplashCover != null) {
            vSplashCover.setVisibility(View.GONE);
        }
        if (llFallbackLogo != null) {
            llFallbackLogo.setVisibility(View.VISIBLE);
        }
        if (videoViewSplash != null) {
            videoViewSplash.setVisibility(View.GONE);
        }
        new Handler(Looper.getMainLooper()).postDelayed(this::navigateNext, 1200);
    }

    private synchronized void navigateNext() {
        if (hasNavigated) {
            return;
        }
        hasNavigated = true;
        timeoutHandler.removeCallbacksAndMessages(null);

        try {
            if (videoViewSplash != null && videoViewSplash.isPlaying()) {
                videoViewSplash.stopPlayback();
            }
        } catch (Exception ignored) {}

        SharedPreferences prefs = getSharedPreferences("projectflow_prefs", Context.MODE_PRIVATE);
        String token = prefs.getString("auth_token", null);
        boolean onboardingCompleted = prefs.getBoolean("onboarding_completed", false);

        Intent intent;
        if (token != null && !token.isEmpty()) {
            intent = new Intent(SplashActivity.this, MainActivity.class);
        } else if (!onboardingCompleted) {
            intent = new Intent(SplashActivity.this, OnboardingActivity.class);
        } else {
            intent = new Intent(SplashActivity.this, LoginActivity.class);
        }

        startActivity(intent);
        overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
        finish();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        timeoutHandler.removeCallbacksAndMessages(null);
        try {
            if (videoViewSplash != null) {
                videoViewSplash.stopPlayback();
            }
        } catch (Exception ignored) {}
    }
}
