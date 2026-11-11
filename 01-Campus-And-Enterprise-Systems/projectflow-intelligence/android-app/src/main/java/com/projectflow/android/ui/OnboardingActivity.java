package com.projectflow.android.ui;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import com.projectflow.android.R;

public class OnboardingActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_onboarding);

        Button btnGetStarted = findViewById(R.id.btnGetStarted);
        TextView btnSkip = findViewById(R.id.btnSkip);

        Runnable completeOnboarding = () -> {
            SharedPreferences prefs = getSharedPreferences("projectflow_prefs", Context.MODE_PRIVATE);
            prefs.edit().putBoolean("onboarding_completed", true).apply();
            startActivity(new Intent(OnboardingActivity.this, LoginActivity.class));
            finish();
        };

        btnGetStarted.setOnClickListener(v -> completeOnboarding.run());
        btnSkip.setOnClickListener(v -> completeOnboarding.run());
    }
}
