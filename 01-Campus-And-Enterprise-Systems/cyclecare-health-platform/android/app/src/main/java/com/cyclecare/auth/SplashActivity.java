package com.cyclecare.auth;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.view.animation.AccelerateDecelerateInterpolator;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.cyclecare.R;
import com.cyclecare.home.MainActivity;

public class SplashActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        FrameLayout logoContainer = findViewById(R.id.fl_logo_container);
        ImageView logo = findViewById(R.id.iv_splash_logo);
        TextView title = findViewById(R.id.tv_splash_title);
        TextView tagline = findViewById(R.id.tv_splash_tagline);
        TextView sub = findViewById(R.id.tv_splash_sub);
        View progressBar = findViewById(R.id.pb_splash);
        TextView status = findViewById(R.id.tv_splash_loading_status);

        // Initial invisible states
        logoContainer.setScaleX(0.75f);
        logoContainer.setScaleY(0.75f);
        logoContainer.setAlpha(0f);

        title.setAlpha(0f);
        title.setTranslationY(24f);

        tagline.setAlpha(0f);
        sub.setAlpha(0f);
        progressBar.setAlpha(0f);
        status.setAlpha(0f);

        // Smooth staggered entrance animations
        logoContainer.animate()
                .scaleX(1.0f)
                .scaleY(1.0f)
                .alpha(1.0f)
                .setDuration(700)
                .setInterpolator(new AccelerateDecelerateInterpolator())
                .start();

        title.animate()
                .alpha(1.0f)
                .translationY(0f)
                .setDuration(500)
                .setStartDelay(250)
                .start();

        tagline.animate()
                .alpha(1.0f)
                .setDuration(400)
                .setStartDelay(450)
                .start();

        sub.animate()
                .alpha(0.85f)
                .setDuration(400)
                .setStartDelay(600)
                .start();

        progressBar.animate()
                .alpha(1.0f)
                .setDuration(300)
                .setStartDelay(750)
                .start();

        status.animate()
                .alpha(1.0f)
                .setDuration(300)
                .setStartDelay(850)
                .start();

        // Navigate cleanly to LoginActivity or MainActivity
        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            SharedPreferences prefs = getSharedPreferences("cyclecare_prefs", MODE_PRIVATE);
            String token = prefs.getString("jwt_token", null);

            Intent intent;
            if (token != null && !token.isEmpty()) {
                intent = new Intent(SplashActivity.this, MainActivity.class);
            } else {
                intent = new Intent(SplashActivity.this, LoginActivity.class);
            }
            startActivity(intent);
            overridePendingTransition(R.anim.fade_in, R.anim.fade_in);
            finish();
        }, 1600);
    }
}
