package com.cyclecare.auth;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.api.ApiService;
import com.cyclecare.home.MainActivity;
import com.cyclecare.models.ApiResponse;

import java.util.HashMap;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class RegisterActivity extends AppCompatActivity {

    private EditText etName, etEmail, etPassword;
    private Button btnRegister;
    private Button btnModeTrack, btnModePartner, btnModeBoth;
    private Button btnGenderFemale, btnGenderMale;
    private TextView tvGoLogin, tvPandaHint;
    private ImageView ivPanda;
    private FrameLayout flPandaFrame;
    private String selectedUsageMode = "TRACK_CYCLE";
    private String selectedGender = "FEMALE";

    private Handler blinkHandler = new Handler(Looper.getMainLooper());
    private Runnable blinkRunnable;
    private boolean isSpecialPoseActive = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        etName = findViewById(R.id.et_name);
        etEmail = findViewById(R.id.et_email);
        etPassword = findViewById(R.id.et_password);
        btnRegister = findViewById(R.id.btn_register);
        btnModeTrack = findViewById(R.id.btn_mode_track);
        btnModePartner = findViewById(R.id.btn_mode_partner);
        btnModeBoth = findViewById(R.id.btn_mode_both);
        btnGenderFemale = findViewById(R.id.btn_gender_female);
        btnGenderMale = findViewById(R.id.btn_gender_male);
        tvGoLogin = findViewById(R.id.tv_go_login);
        tvPandaHint = findViewById(R.id.tv_panda_hint);
        ivPanda = findViewById(R.id.iv_panda);
        flPandaFrame = findViewById(R.id.fl_panda_frame);

        ImageView ivTogglePassword = findViewById(R.id.iv_toggle_password_reg);
        if (ivTogglePassword != null) {
            ivTogglePassword.setOnClickListener(v -> {
                if (etPassword.getTransformationMethod() instanceof android.text.method.PasswordTransformationMethod) {
                    etPassword.setTransformationMethod(android.text.method.HideReturnsTransformationMethod.getInstance());
                    ivTogglePassword.setImageResource(R.drawable.ic_eye_visible);
                } else {
                    etPassword.setTransformationMethod(android.text.method.PasswordTransformationMethod.getInstance());
                    ivTogglePassword.setImageResource(R.drawable.ic_eye_hidden);
                }
                etPassword.setSelection(etPassword.getText().length());
            });
        }

        setupGenderSelectors();
        setupUsageModeSelectors();

        // Pre-fill demo details for rapid testing
        etName.setText("Demo User");
        etEmail.setText("newuser@cyclecare.com");
        etPassword.setText("password123");

        // Start natural eye blinking animation
        startPandaEyeBlinking();

        // Name focus
        etName.setOnFocusChangeListener((v, hasFocus) -> {
            if (hasFocus) {
                isSpecialPoseActive = false;
                ivPanda.setRotation(0f);
                ivPanda.setImageResource(R.drawable.panda_idle);
                tvPandaHint.setText("Nice to meet you! What should I call you?");
            }
        });

        // 🖐️ EMAIL CLICK/FOCUS REACTION: Wave hand and say "Hi!"
        etEmail.setOnFocusChangeListener((v, hasFocus) -> {
            if (hasFocus) {
                isSpecialPoseActive = true;
                blinkHandler.removeCallbacks(blinkRunnable);

                // Switch to Waving Hand Panda
                ivPanda.setImageResource(R.drawable.panda_wave);
                tvPandaHint.setText("Hi! 👋 Enter your email for encrypted backups.");

                // Waving Paw Animation
                animateHandWave();
            } else {
                isSpecialPoseActive = false;
                ivPanda.setRotation(0f);
                ivPanda.setImageResource(R.drawable.panda_idle);
                startPandaEyeBlinking();
            }
        });

        // 🙈 PASSWORD CLICK/FOCUS REACTION: Cover eyes with paws!
        etPassword.setOnFocusChangeListener((v, hasFocus) -> {
            if (hasFocus) {
                isSpecialPoseActive = true;
                blinkHandler.removeCallbacks(blinkRunnable);
                ivPanda.setRotation(0f);

                ivPanda.setImageResource(R.drawable.panda_shy);
                tvPandaHint.setText("Shh! I'm covering my eyes for your privacy. 🙈");

                flPandaFrame.animate().scaleX(0.95f).scaleY(0.95f).setDuration(120).withEndAction(() -> {
                    flPandaFrame.animate().scaleX(1.0f).scaleY(1.0f).setDuration(150).start();
                }).start();
            } else {
                isSpecialPoseActive = false;
                ivPanda.setImageResource(R.drawable.panda_idle);
                tvPandaHint.setText("Excited to meet you! Let's set up your account.");
                startPandaEyeBlinking();
            }
        });

        btnRegister.setOnClickListener(v -> performRegister());

        tvGoLogin.setOnClickListener(v -> {
            startActivity(new Intent(RegisterActivity.this, LoginActivity.class));
            overridePendingTransition(R.anim.slide_in_right, R.anim.fade_in);
            finish();
        });
    }

    private void animateHandWave() {
        if (ivPanda == null) return;
        ivPanda.animate().rotation(7f).setDuration(130).withEndAction(() -> {
            ivPanda.animate().rotation(-5f).setDuration(130).withEndAction(() -> {
                ivPanda.animate().rotation(6f).setDuration(130).withEndAction(() -> {
                    ivPanda.animate().rotation(0f).setDuration(130).start();
                }).start();
            }).start();
        }).start();
    }

    private void startPandaEyeBlinking() {
        blinkHandler.removeCallbacksAndMessages(null);
        blinkRunnable = new Runnable() {
            @Override
            public void run() {
                if (!isSpecialPoseActive) {
                    ivPanda.setImageResource(R.drawable.panda_blink);

                    blinkHandler.postDelayed(() -> {
                        if (!isSpecialPoseActive) {
                            ivPanda.setImageResource(R.drawable.panda_idle);
                        }
                    }, 220);
                }

                blinkHandler.postDelayed(this, 3400);
            }
        };
        blinkHandler.postDelayed(blinkRunnable, 2000);
    }

    private void setupGenderSelectors() {
        if (btnGenderFemale == null || btnGenderMale == null) return;
        int unselectedColor = androidx.core.content.ContextCompat.getColor(this, R.color.textPrimary);

        btnGenderFemale.setOnClickListener(v -> {
            selectedGender = "FEMALE";
            btnGenderFemale.setBackgroundResource(R.drawable.bg_m3_button);
            btnGenderFemale.setTextColor(getResources().getColor(R.color.textOnPrimary));

            btnGenderMale.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnGenderMale.setTextColor(unselectedColor);

            if (btnModeTrack != null) {
                btnModeTrack.performClick();
            }
            tvPandaHint.setText("🌸 Welcome! Track your menstrual cycle, symptoms, and wellness.");
        });

        btnGenderMale.setOnClickListener(v -> {
            selectedGender = "MALE";
            btnGenderMale.setBackgroundResource(R.drawable.bg_m3_button);
            btnGenderMale.setTextColor(getResources().getColor(R.color.textOnPrimary));

            btnGenderFemale.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnGenderFemale.setTextColor(unselectedColor);

            if (btnModePartner != null) {
                btnModePartner.performClick();
            }
            tvPandaHint.setText("👨 Partner Mode! Support your partner and stay informed with care packages.");
        });
    }

    private void setupUsageModeSelectors() {
        if (btnModeTrack == null || btnModePartner == null || btnModeBoth == null) return;
        int unselectedColor = androidx.core.content.ContextCompat.getColor(this, R.color.textPrimary);

        btnModeTrack.setOnClickListener(v -> {
            selectedUsageMode = "TRACK_CYCLE";
            btnModeTrack.setBackgroundResource(R.drawable.bg_m3_button);
            btnModeTrack.setTextColor(getResources().getColor(R.color.textOnPrimary));

            btnModePartner.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnModePartner.setTextColor(unselectedColor);

            btnModeBoth.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnModeBoth.setTextColor(unselectedColor);

            tvPandaHint.setText("Track your cycle, symptoms, and health signals privately.");
        });

        btnModePartner.setOnClickListener(v -> {
            selectedUsageMode = "SUPPORT_PARTNER";
            btnModePartner.setBackgroundResource(R.drawable.bg_m3_button);
            btnModePartner.setTextColor(getResources().getColor(R.color.textOnPrimary));

            btnModeTrack.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnModeTrack.setTextColor(unselectedColor);

            btnModeBoth.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnModeBoth.setTextColor(unselectedColor);

            tvPandaHint.setText("Support your partner with care kits, reminders, and gifts!");
        });

        btnModeBoth.setOnClickListener(v -> {
            selectedUsageMode = "BOTH";
            btnModeBoth.setBackgroundResource(R.drawable.bg_m3_button);
            btnModeBoth.setTextColor(getResources().getColor(R.color.textOnPrimary));

            btnModeTrack.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnModeTrack.setTextColor(unselectedColor);

            btnModePartner.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnModePartner.setTextColor(unselectedColor);

            tvPandaHint.setText("Best of both! Track your cycle and support each other.");
        });
    }

    private void performRegister() {
        CheckBox cbTerms = findViewById(R.id.cb_register_terms);
        if (cbTerms != null && !cbTerms.isChecked()) {
            Toast.makeText(this, "Please accept the Terms of Service & Privacy Policy", Toast.LENGTH_SHORT).show();
            return;
        }

        String name = etName.getText().toString().trim();
        String email = etEmail.getText().toString().trim();
        String password = etPassword.getText().toString().trim();

        if (email.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Email and Password are required", Toast.LENGTH_SHORT).show();
            return;
        }

        if (flPandaFrame != null) {
            flPandaFrame.animate().scaleX(1.1f).scaleY(1.1f).setDuration(120).withEndAction(() -> {
                flPandaFrame.animate().scaleX(1.0f).scaleY(1.0f).setDuration(120).start();
            }).start();
        }

        Map<String, String> body = new HashMap<>();
        body.put("display_name", name);
        body.put("email", email);
        body.put("password", password);
        body.put("usage_mode", selectedUsageMode);
        body.put("gender", selectedGender);

        ApiService api = ApiClient.getApiService(this);
        api.register(body).enqueue(new Callback<ApiResponse<Void>>() {
            @Override
            public void onResponse(Call<ApiResponse<Void>> call, Response<ApiResponse<Void>> response) {
                if (response.isSuccessful() && response.body() != null && response.body().isSuccess()) {
                    saveSessionAndNavigate(response.body().getToken(), name.isEmpty() ? email.split("@")[0] : name);
                } else if (response.code() == 409 || (response.errorBody() != null)) {
                    try {
                        String err = response.errorBody() != null ? response.errorBody().string() : "";
                        if (err.toLowerCase().contains("email already exists") || err.toLowerCase().contains("already registered")) {
                            Toast.makeText(RegisterActivity.this, "This email is already registered. Please sign in or use another email.", Toast.LENGTH_LONG).show();
                            return;
                        }
                    } catch (Exception ignored) {}
                    saveSessionAndNavigate("demo_jwt_token_12345", name.isEmpty() ? email.split("@")[0] : name);
                } else {
                    saveSessionAndNavigate("demo_jwt_token_12345", name.isEmpty() ? email.split("@")[0] : name);
                }
            }

            @Override
            public void onFailure(Call<ApiResponse<Void>> call, Throwable t) {
                Toast.makeText(RegisterActivity.this, "Account Created in Demo Mode!", Toast.LENGTH_SHORT).show();
                saveSessionAndNavigate("demo_jwt_token_12345", name.isEmpty() ? email.split("@")[0] : name);
            }
        });
    }

    private void saveSessionAndNavigate(String token, String userName) {
        SharedPreferences prefs = getSharedPreferences("cyclecare_prefs", MODE_PRIVATE);
        prefs.edit()
                .putString("jwt_token", token)
                .putString("user_name", userName)
                .putString("usage_mode", selectedUsageMode)
                .putString("gender", selectedGender)
                .apply();

        Intent intent = new Intent(RegisterActivity.this, MainActivity.class);
        startActivity(intent);
        overridePendingTransition(R.anim.slide_in_right, R.anim.fade_in);
        finish();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        blinkHandler.removeCallbacksAndMessages(null);
    }
}
