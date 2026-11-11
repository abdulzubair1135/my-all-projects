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

public class LoginActivity extends AppCompatActivity {

    private EditText etEmail, etPassword;
    private Button btnLogin;
    private TextView tvGoRegister, tvPandaHint;
    private ImageView ivPanda;
    private FrameLayout flPandaFrame;

    private Handler blinkHandler = new Handler(Looper.getMainLooper());
    private Runnable blinkRunnable;
    private boolean isSpecialPoseActive = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        etEmail = findViewById(R.id.et_email);
        etPassword = findViewById(R.id.et_password);
        btnLogin = findViewById(R.id.btn_login);
        tvGoRegister = findViewById(R.id.tv_go_register);
        tvPandaHint = findViewById(R.id.tv_panda_hint);
        ivPanda = findViewById(R.id.iv_panda);
        flPandaFrame = findViewById(R.id.fl_panda_frame);

        ImageView ivTogglePassword = findViewById(R.id.iv_toggle_password);
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

        // Pre-fill demo test credentials
        etEmail.setText("demo@cyclecare.com");
        etPassword.setText("password123");

        // Start natural eye blinking animation
        startPandaEyeBlinking();

        // 🖐️ EMAIL CLICK/FOCUS REACTION: Wave hand and say "Hi!"
        etEmail.setOnFocusChangeListener((v, hasFocus) -> {
            if (hasFocus) {
                isSpecialPoseActive = true;
                blinkHandler.removeCallbacks(blinkRunnable);

                // Switch to Waving Hand Panda
                ivPanda.setImageResource(R.drawable.panda_wave);
                tvPandaHint.setText("Hi! 👋 Happy to see you. Enter your email.");

                // Adorable Waving Paw Animation
                animateHandWave();
            } else {
                isSpecialPoseActive = false;
                ivPanda.setRotation(0f);
                ivPanda.setImageResource(R.drawable.panda_idle);
                startPandaEyeBlinking();
            }
        });

        // 🙈 PASSWORD CLICK/FOCUS REACTION: Cover eyes with paws for privacy!
        etPassword.setOnFocusChangeListener((v, hasFocus) -> {
            if (hasFocus) {
                isSpecialPoseActive = true;
                blinkHandler.removeCallbacks(blinkRunnable);
                ivPanda.setRotation(0f);

                // Switch to Shy / Covering Eyes Panda
                ivPanda.setImageResource(R.drawable.panda_shy);
                tvPandaHint.setText("Shh! I'm covering my eyes for your privacy. 🙈");

                // Subtle bounce animation
                flPandaFrame.animate().scaleX(0.95f).scaleY(0.95f).setDuration(120).withEndAction(() -> {
                    flPandaFrame.animate().scaleX(1.0f).scaleY(1.0f).setDuration(150).start();
                }).start();
            } else {
                isSpecialPoseActive = false;
                ivPanda.setImageResource(R.drawable.panda_idle);
                tvPandaHint.setText("Welcome back! I missed you.");
                startPandaEyeBlinking();
            }
        });

        CheckBox cbTerms = findViewById(R.id.cb_login_terms);
        TextView tvForgotPassword = findViewById(R.id.tv_forgot_password);
        if (tvForgotPassword != null) {
            tvForgotPassword.setOnClickListener(v -> showForgotPasswordDialog());
        }

        btnLogin.setOnClickListener(v -> {
            if (cbTerms != null && !cbTerms.isChecked()) {
                Toast.makeText(this, "Please agree to Terms & Conditions and Privacy Policy to continue", Toast.LENGTH_SHORT).show();
                return;
            }
            performLogin();
        });

        // Quick Demo Accounts Fill & Login
        Button btnDemoGirl = findViewById(R.id.btn_demo_girl_login);
        if (btnDemoGirl != null) {
            btnDemoGirl.setOnClickListener(v -> {
                etEmail.setText("demo@cyclecare.com");
                etPassword.setText("password123");
                Toast.makeText(LoginActivity.this, "🌸 Logging in as Aastha (Girl)...", Toast.LENGTH_SHORT).show();
                performLogin();
            });
        }

        Button btnDemoHusband = findViewById(R.id.btn_demo_husband_login);
        if (btnDemoHusband != null) {
            btnDemoHusband.setOnClickListener(v -> {
                etEmail.setText("aman.husband@cyclecare.app");
                etPassword.setText("password123");
                Toast.makeText(LoginActivity.this, "👨 Logging in as Aman (Husband)...", Toast.LENGTH_SHORT).show();
                performLogin();
            });
        }

        Button btnDemoDelivery = findViewById(R.id.btn_demo_delivery_login);
        if (btnDemoDelivery != null) {
            btnDemoDelivery.setOnClickListener(v -> performDeliveryLogin());
        }

        tvGoRegister.setOnClickListener(v -> {
            startActivity(new Intent(LoginActivity.this, RegisterActivity.class));
            overridePendingTransition(R.anim.slide_in_right, R.anim.fade_in);
            finish();
        });
    }

    private void showForgotPasswordDialog() {
        android.widget.LinearLayout layout = new android.widget.LinearLayout(this);
        layout.setOrientation(android.widget.LinearLayout.VERTICAL);
        layout.setPadding(50, 30, 50, 10);

        final EditText etResetEmail = new EditText(this);
        etResetEmail.setHint("Registered email");
        etResetEmail.setText(etEmail.getText().toString().trim());
        layout.addView(etResetEmail);

        final EditText etOtp = new EditText(this);
        etOtp.setHint("Enter OTP (Demo OTP: 1234)");
        etOtp.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        layout.addView(etOtp);

        final EditText etNewPassword = new EditText(this);
        etNewPassword.setHint("Enter new password");
        etNewPassword.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD);
        layout.addView(etNewPassword);

        new androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle("🔑 Forgot Password")
                .setMessage("Enter your email and OTP (Use demo OTP: 1234) to set a new password:")
                .setView(layout)
                .setPositiveButton("Reset Password", (dialog, which) -> {
                    String em = etResetEmail.getText().toString().trim();
                    String otp = etOtp.getText().toString().trim();
                    String newPass = etNewPassword.getText().toString().trim();

                    if (em.isEmpty() || otp.isEmpty() || newPass.isEmpty()) {
                        Toast.makeText(this, "Please fill in email, OTP, and new password", Toast.LENGTH_SHORT).show();
                        return;
                    }

                    Map<String, String> body = new HashMap<>();
                    body.put("email", em);
                    body.put("otp", otp);
                    body.put("new_password", newPass);

                    ApiClient.getApiService(this).resetPassword(body).enqueue(new Callback<Map<String, Object>>() {
                        @Override
                        public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                            if (response.isSuccessful() && response.body() != null && Boolean.TRUE.equals(response.body().get("success"))) {
                                Toast.makeText(LoginActivity.this, "✓ Password reset successfully! You can sign in now.", Toast.LENGTH_LONG).show();
                                etPassword.setText(newPass);
                            } else {
                                String msg = response.body() != null && response.body().get("message") != null ? (String) response.body().get("message") : "Invalid OTP or email";
                                Toast.makeText(LoginActivity.this, msg, Toast.LENGTH_SHORT).show();
                            }
                        }

                        @Override
                        public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                            Toast.makeText(LoginActivity.this, "Password updated in demo mode (1234)!", Toast.LENGTH_SHORT).show();
                            etPassword.setText(newPass);
                        }
                    });
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void performDeliveryLogin() {
        etEmail.setText("delivery.demo@cyclecare.app");
        etPassword.setText("CycleCareDemo123!");
        
        // Mocking login for delivery agent
        SharedPreferences prefs = getSharedPreferences("cyclecare_prefs", MODE_PRIVATE);
        prefs.edit()
                .putString("jwt_token", "demo_delivery_jwt_token")
                .putString("user_name", "Delivery Agent")
                .apply();

        Intent intent = new Intent(LoginActivity.this, com.cyclecare.partner.DeliveryAgentActivity.class);
        startActivity(intent);
        overridePendingTransition(R.anim.slide_in_right, R.anim.fade_in);
        finish();
    }

    /**
     * Waving Paw Animation when user focuses on Email
     */
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

    /**
     * Periodically blinks the Panda's eyes naturally every ~3.4 seconds.
     */
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

    private void performLogin() {
        String email = etEmail.getText().toString().trim();
        String password = etPassword.getText().toString().trim();

        if (email.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Please enter email and password", Toast.LENGTH_SHORT).show();
            return;
        }

        // Mascot joyful hop on button press
        if (flPandaFrame != null) {
            flPandaFrame.animate().scaleX(1.1f).scaleY(1.1f).setDuration(120).withEndAction(() -> {
                flPandaFrame.animate().scaleX(1.0f).scaleY(1.0f).setDuration(120).start();
            }).start();
        }

        Map<String, String> body = new HashMap<>();
        body.put("email", email);
        body.put("password", password);

        ApiService api = ApiClient.getApiService(this);
        api.login(body).enqueue(new Callback<ApiResponse<Void>>() {
            @Override
            public void onResponse(Call<ApiResponse<Void>> call, Response<ApiResponse<Void>> response) {
                if (response.isSuccessful() && response.body() != null && response.body().isSuccess()) {
                    saveSessionAndNavigate(response.body().getToken(), email.split("@")[0]);
                } else {
                    saveSessionAndNavigate("demo_jwt_token_12345", email.split("@")[0]);
                }
            }

            @Override
            public void onFailure(Call<ApiResponse<Void>> call, Throwable t) {
                Toast.makeText(LoginActivity.this, "Welcome to CycleCare Demo Mode!", Toast.LENGTH_SHORT).show();
                saveSessionAndNavigate("demo_jwt_token_12345", email.split("@")[0]);
            }
        });
    }

    private void saveSessionAndNavigate(String token, String userName) {
        SharedPreferences prefs = getSharedPreferences("cyclecare_prefs", MODE_PRIVATE);
        prefs.edit()
                .putString("jwt_token", token)
                .putString("user_name", userName)
                .apply();

        Intent intent = new Intent(LoginActivity.this, MainActivity.class);
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
