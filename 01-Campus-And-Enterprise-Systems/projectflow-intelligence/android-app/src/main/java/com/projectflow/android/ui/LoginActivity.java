package com.projectflow.android.ui;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import com.projectflow.android.R;
import com.projectflow.android.data.remote.ApiClient;
import com.projectflow.android.data.remote.ApiService;
import com.projectflow.android.data.remote.model.DtoModels.*;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

import java.util.HashMap;
import java.util.Map;

public class LoginActivity extends AppCompatActivity {

    private EditText etEmail;
    private EditText etPassword;
    private EditText etName;
    private EditText etWorkspace;
    private View layoutNameField;
    private View layoutWorkspaceField;
    private View layoutRememberRow;

    private TextView tabSignIn;
    private TextView tabSignUp;
    private TextView tvAuthTitle;
    private TextView tvAuthSubtitle;
    private TextView btnSignIn;
    private TextView tvSignUp;
    private TextView tvForgotPassword;
    private ImageView ivTogglePassword;
    private boolean isPasswordVisible = false;
    private ProgressBar progressBar;
    private TextView tvError;
    private CheckBox cbRememberMe;

    private boolean isSignUpMode = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        StatusBarUtils.applyLightStatusBar(this);
        setContentView(R.layout.activity_login);

        etEmail = findViewById(R.id.emailEditText);
        etPassword = findViewById(R.id.passwordEditText);
        ivTogglePassword = findViewById(R.id.ivTogglePassword);
        etName = findViewById(R.id.etName);
        etWorkspace = findViewById(R.id.etWorkspace);
        layoutNameField = findViewById(R.id.layoutNameField);
        layoutWorkspaceField = findViewById(R.id.layoutWorkspaceField);
        layoutRememberRow = findViewById(R.id.layoutRememberRow);

        tabSignIn = findViewById(R.id.tabSignIn);
        tabSignUp = findViewById(R.id.tabSignUp);
        tvAuthTitle = findViewById(R.id.tvAuthTitle);
        tvAuthSubtitle = findViewById(R.id.tvAuthSubtitle);
        btnSignIn = findViewById(R.id.btnSignIn);
        tvSignUp = findViewById(R.id.tvSignUp);
        tvForgotPassword = findViewById(R.id.tvForgotPassword);
        progressBar = findViewById(R.id.progressBar);
        tvError = findViewById(R.id.tvError);
        cbRememberMe = findViewById(R.id.cbRememberMe);

        tabSignIn.setOnClickListener(v -> setMode(false));
        tabSignUp.setOnClickListener(v -> setMode(true));
        tvSignUp.setOnClickListener(v -> setMode(!isSignUpMode));
        if (tvForgotPassword != null) {
            tvForgotPassword.setOnClickListener(v -> showForgotPasswordDialog());
        }

        if (ivTogglePassword != null) {
            ivTogglePassword.setOnClickListener(v -> {
                isPasswordVisible = !isPasswordVisible;
                togglePasswordVisibility(etPassword, ivTogglePassword, isPasswordVisible);
            });
        }


        btnSignIn.setOnClickListener(v -> {
            String email = etEmail.getText() != null ? etEmail.getText().toString().trim() : "";
            String password = etPassword.getText() != null ? etPassword.getText().toString().trim() : "";


            if (isSignUpMode) {
                String name = etName.getText() != null ? etName.getText().toString().trim() : "";
                if (name.isEmpty()) {
                    etName.setError("Full name is required");
                    etName.requestFocus();
                    return;
                }
            }

            if (email.isEmpty()) {
                etEmail.setError("Email is required");
                etEmail.requestFocus();
                return;
            }

            if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
                etEmail.setError("Please enter a valid email address");
                etEmail.requestFocus();
                return;
            }

            if (password.isEmpty()) {
                etPassword.setError("Password is required");
                etPassword.requestFocus();
                return;
            }

            if (password.length() < 6) {
                etPassword.setError("Password must be at least 6 characters");
                etPassword.requestFocus();
                return;
            }

            performAuth(email, password);
        });
    }

    private void setMode(boolean signUp) {
        isSignUpMode = signUp;
        if (signUp) {
            tabSignIn.setBackgroundResource(android.R.color.transparent);
            tabSignIn.setTextColor(ContextCompat.getColor(this, R.color.text_secondary));

            tabSignUp.setBackgroundResource(R.drawable.bg_chip_selected);
            tabSignUp.setTextColor(ContextCompat.getColor(this, R.color.white));

            layoutNameField.setVisibility(View.VISIBLE);
            layoutWorkspaceField.setVisibility(View.VISIBLE);
            layoutRememberRow.setVisibility(View.GONE);

            tvAuthTitle.setText("Join ProjectFlow");
            tvAuthSubtitle.setText("Create your workspace & lead with intelligence");
            btnSignIn.setText("Create Account");
            tvSignUp.setText("Already have an account? Sign In");
        } else {
            tabSignIn.setBackgroundResource(R.drawable.bg_chip_selected);
            tabSignIn.setTextColor(ContextCompat.getColor(this, R.color.white));

            tabSignUp.setBackgroundResource(android.R.color.transparent);
            tabSignUp.setTextColor(ContextCompat.getColor(this, R.color.text_secondary));

            layoutNameField.setVisibility(View.GONE);
            layoutWorkspaceField.setVisibility(View.GONE);
            layoutRememberRow.setVisibility(View.VISIBLE);

            tvAuthTitle.setText(R.string.welcome_back);
            tvAuthSubtitle.setText("Sign in to your intelligent workspace");
            btnSignIn.setText(R.string.sign_in);
            tvSignUp.setText(R.string.dont_have_account);
        }
    }

    private void performAuth(String email, String password) {
        progressBar.setVisibility(View.VISIBLE);
        btnSignIn.setEnabled(false);
        tvError.setVisibility(View.GONE);

        ApiService api = ApiClient.getService(this);
        Map<String, String> body = new HashMap<>();
        body.put("email", email);
        body.put("password", password);

        Call<AuthResponse> authCall;
        if (isSignUpMode) {
            String name = etName.getText() != null ? etName.getText().toString().trim() : "";
            String workspace = etWorkspace.getText() != null ? etWorkspace.getText().toString().trim() : "";
            if (!name.isEmpty()) body.put("fullName", name);
            if (!workspace.isEmpty()) body.put("workspaceName", workspace);
            authCall = api.signup(body);
        } else {
            authCall = api.login(body);
        }

        authCall.enqueue(new Callback<AuthResponse>() {
            @Override
            public void onResponse(Call<AuthResponse> call, Response<AuthResponse> response) {
                progressBar.setVisibility(View.GONE);
                btnSignIn.setEnabled(true);

                if (response.isSuccessful() && response.body() != null && response.body().token != null) {
                    String userEmail = response.body().user != null ? response.body().user.email : email;
                    String userName = response.body().user != null ? response.body().user.fullName : null;
                    String userRole = response.body().user != null ? response.body().user.role : "MEMBER";
                    saveSessionAndNavigate(response.body().token, userEmail, userName, userRole);
                } else {
                    String errorMsg = "Invalid email or password. Please try again.";
                    try {
                        if (response.errorBody() != null) {
                            String errJson = response.errorBody().string();
                            org.json.JSONObject obj = new org.json.JSONObject(errJson);
                            if (obj.has("error")) {
                                errorMsg = obj.getString("error");
                            }
                        }
                    } catch (Exception ignored) {}
                    tvError.setText(errorMsg);
                    tvError.setVisibility(View.VISIBLE);
                    Toast.makeText(LoginActivity.this, errorMsg, Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<AuthResponse> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                btnSignIn.setEnabled(true);
                String errorMsg = "Unable to connect to server. Please check your network.";
                tvError.setText(errorMsg);
                tvError.setVisibility(View.VISIBLE);
                Toast.makeText(LoginActivity.this, errorMsg, Toast.LENGTH_LONG).show();
            }
        });
    }

    private void saveSessionAndNavigate(String token, String email, String fullName, String role) {
        String displayName = (fullName != null && !fullName.isEmpty()) 
                ? fullName 
                : ((etName.getText() != null && !etName.getText().toString().trim().isEmpty())
                    ? etName.getText().toString().trim()
                    : (email.split("@")[0]));

        if (token != null && token.contains(".")) {
            try {
                String[] parts = token.split("\\.");
                if (parts.length >= 2) {
                    byte[] decoded = android.util.Base64.decode(parts[1], android.util.Base64.URL_SAFE | android.util.Base64.NO_WRAP | android.util.Base64.DEFAULT);
                    String payload = new String(decoded, java.nio.charset.StandardCharsets.UTF_8);
                    org.json.JSONObject obj = new org.json.JSONObject(payload);
                    if (obj.has("role")) role = obj.getString("role");
                }
            } catch (Exception ignored) {}
        }

        SharedPreferences prefs = getSharedPreferences("projectflow_prefs", Context.MODE_PRIVATE);
        prefs.edit()
                .putString("auth_token", token)
                .putString("user_email", email)
                .putString("user_name", displayName)
                .putString("user_display_name", displayName)
                .putString("user_role", role)
                .putBoolean("remember_me", cbRememberMe.isChecked())
                .apply();

        // Register FCM Push Notification Token with backend
        String fcmToken = prefs.getString("fcm_token", null);
        if (fcmToken != null && !fcmToken.isEmpty()) {
            Map<String, String> fcmBody = new HashMap<>();
            fcmBody.put("fcmToken", fcmToken);
            fcmBody.put("email", email);
            ApiClient.getService(this).registerFcmToken(fcmBody).enqueue(new Callback<Map<String, Object>>() {
                @Override
                public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                    android.util.Log.d("ProjectFlowAuth", "FCM token synced to server");
                }
                @Override
                public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                    android.util.Log.w("ProjectFlowAuth", "FCM token sync postponed: " + t.getMessage());
                }
            });
        }

        String msg = isSignUpMode ? "Welcome to ProjectFlow, " + displayName + "!" : "Signed in as " + displayName;
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
        startActivity(new Intent(LoginActivity.this, MainActivity.class));
        finish();
    }

    private void showForgotPasswordDialog() {
        View dialogView = getLayoutInflater().inflate(R.layout.dialog_forgot_password, null);
        androidx.appcompat.app.AlertDialog dialog = new androidx.appcompat.app.AlertDialog.Builder(this)
                .setView(dialogView)
                .setCancelable(true)
                .create();

        if (dialog.getWindow() != null) {
            dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
        }

        View layoutStep1 = dialogView.findViewById(R.id.layoutStep1Email);
        View layoutStep2 = dialogView.findViewById(R.id.layoutStep2Reset);
        EditText etForgotEmail = dialogView.findViewById(R.id.etForgotEmail);
        EditText etForgotOtp = dialogView.findViewById(R.id.etForgotOtp);
        EditText etForgotNewPassword = dialogView.findViewById(R.id.etForgotNewPassword);
        ImageView ivToggleForgotOtp = dialogView.findViewById(R.id.ivToggleForgotOtp);
        ImageView ivToggleForgotNewPassword = dialogView.findViewById(R.id.ivToggleForgotNewPassword);
        TextView tvForgotNotice = dialogView.findViewById(R.id.tvForgotNotice);
        TextView tvForgotError = dialogView.findViewById(R.id.tvForgotError);
        ProgressBar progressBarForgot = dialogView.findViewById(R.id.progressBarForgot);
        View btnCancelStep1 = dialogView.findViewById(R.id.btnCancelStep1);
        View btnSendOtp = dialogView.findViewById(R.id.btnSendOtp);
        View btnCancelStep2 = dialogView.findViewById(R.id.btnCancelStep2);
        View btnSubmitReset = dialogView.findViewById(R.id.btnSubmitReset);

        final boolean[] isOtpVisible = {true};
        if (ivToggleForgotOtp != null) {
            ivToggleForgotOtp.setOnClickListener(v -> {
                isOtpVisible[0] = !isOtpVisible[0];
                togglePasswordVisibility(etForgotOtp, ivToggleForgotOtp, isOtpVisible[0]);
            });
        }

        final boolean[] isNewPassVisible = {false};
        if (ivToggleForgotNewPassword != null) {
            ivToggleForgotNewPassword.setOnClickListener(v -> {
                isNewPassVisible[0] = !isNewPassVisible[0];
                togglePasswordVisibility(etForgotNewPassword, ivToggleForgotNewPassword, isNewPassVisible[0]);
            });
        }

        String currentEmail = etEmail.getText() != null ? etEmail.getText().toString().trim() : "";
        if (!currentEmail.isEmpty()) {
            etForgotEmail.setText(currentEmail);
        }


        btnCancelStep1.setOnClickListener(v -> dialog.dismiss());
        btnCancelStep2.setOnClickListener(v -> dialog.dismiss());

        btnSendOtp.setOnClickListener(v -> {
            String email = etForgotEmail.getText() != null ? etForgotEmail.getText().toString().trim() : "";
            if (email.isEmpty()) {
                etForgotEmail.setError("Email is required");
                etForgotEmail.requestFocus();
                return;
            }
            if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
                etForgotEmail.setError("Please enter a valid email address");
                etForgotEmail.requestFocus();
                return;
            }

            progressBarForgot.setVisibility(View.VISIBLE);
            tvForgotError.setVisibility(View.GONE);
            btnSendOtp.setEnabled(false);

            ApiService api = ApiClient.getService(this);
            Map<String, String> body = new HashMap<>();
            body.put("email", email);

            api.forgotPassword(body).enqueue(new Callback<Map<String, Object>>() {
                @Override
                public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                    progressBarForgot.setVisibility(View.GONE);
                    btnSendOtp.setEnabled(true);

                    if (response.isSuccessful() && response.body() != null) {
                        layoutStep1.setVisibility(View.GONE);
                        layoutStep2.setVisibility(View.VISIBLE);
                        tvForgotNotice.setText("Verification code sent! (OTP: 1234)");
                        etForgotOtp.setText("1234");
                    } else {
                        String errMsg = "Email address not found. Please sign up first.";
                        try {
                            if (response.errorBody() != null) {
                                org.json.JSONObject errObj = new org.json.JSONObject(response.errorBody().string());
                                if (errObj.has("error")) errMsg = errObj.getString("error");
                            }
                        } catch (Exception ignored) {}
                        tvForgotError.setText(errMsg);
                        tvForgotError.setVisibility(View.VISIBLE);
                    }
                }

                @Override
                public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                    progressBarForgot.setVisibility(View.GONE);
                    btnSendOtp.setEnabled(true);
                    tvForgotError.setText("Network error: Unable to reach authentication server.");
                    tvForgotError.setVisibility(View.VISIBLE);
                }
            });
        });

        btnSubmitReset.setOnClickListener(v -> {
            String email = etForgotEmail.getText() != null ? etForgotEmail.getText().toString().trim() : "";
            String otp = etForgotOtp.getText() != null ? etForgotOtp.getText().toString().trim() : "";
            String newPassword = etForgotNewPassword.getText() != null ? etForgotNewPassword.getText().toString().trim() : "";

            if (otp.isEmpty()) {
                etForgotOtp.setError("OTP code is required (1234)");
                etForgotOtp.requestFocus();
                return;
            }
            if (newPassword.isEmpty()) {
                etForgotNewPassword.setError("New password is required");
                etForgotNewPassword.requestFocus();
                return;
            }
            if (newPassword.length() < 6) {
                etForgotNewPassword.setError("Password must be at least 6 characters");
                etForgotNewPassword.requestFocus();
                return;
            }

            progressBarForgot.setVisibility(View.VISIBLE);
            tvForgotError.setVisibility(View.GONE);
            btnSubmitReset.setEnabled(false);

            ApiService api = ApiClient.getService(this);
            Map<String, String> body = new HashMap<>();
            body.put("email", email);
            body.put("otp", otp);
            body.put("newPassword", newPassword);

            api.resetPassword(body).enqueue(new Callback<Map<String, Object>>() {
                @Override
                public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                    progressBarForgot.setVisibility(View.GONE);
                    btnSubmitReset.setEnabled(true);

                    if (response.isSuccessful() && response.body() != null) {
                        dialog.dismiss();
                        Toast.makeText(LoginActivity.this, "Password reset successfully! Please log in.", Toast.LENGTH_LONG).show();
                        etEmail.setText(email);
                        etPassword.setText(newPassword);
                        etPassword.requestFocus();
                    } else {
                        String errMsg = "Password reset failed. Invalid OTP or request.";
                        try {
                            if (response.errorBody() != null) {
                                org.json.JSONObject errObj = new org.json.JSONObject(response.errorBody().string());
                                if (errObj.has("error")) errMsg = errObj.getString("error");
                            }
                        } catch (Exception ignored) {}
                        tvForgotError.setText(errMsg);
                        tvForgotError.setVisibility(View.VISIBLE);
                    }
                }

                @Override
                public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                    progressBarForgot.setVisibility(View.GONE);
                    btnSubmitReset.setEnabled(true);
                    tvForgotError.setText("Network error: Unable to reach authentication server.");
                    tvForgotError.setVisibility(View.VISIBLE);
                }
            });
        });

        dialog.show();
    }

    private void togglePasswordVisibility(EditText editText, ImageView toggleView, boolean isVisible) {
        if (editText == null || toggleView == null) return;
        if (isVisible) {
            editText.setTransformationMethod(android.text.method.HideReturnsTransformationMethod.getInstance());
            toggleView.setImageResource(R.drawable.ic_eye);
            toggleView.setColorFilter(ContextCompat.getColor(this, R.color.primary_earth));
        } else {
            editText.setTransformationMethod(android.text.method.PasswordTransformationMethod.getInstance());
            toggleView.setImageResource(R.drawable.ic_eye_off);
            toggleView.setColorFilter(ContextCompat.getColor(this, R.color.text_muted));
        }
        if (editText.getText() != null) {
            editText.setSelection(editText.getText().length());
        }
    }
}


