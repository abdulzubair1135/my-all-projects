package com.example.nearmeshchat;

import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.InputType;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Spinner;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONObject;

import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class LoginActivity extends AppCompatActivity {

    private EditText etMobileNumber, etFullName, etEmailAddress, etAddress, etCity;
    private Spinner spState;
    private RadioGroup rgRole;
    private RadioButton rbCitizen, rbVolunteer;
    private CheckBox cbVerify;
    private Button btnSendOtp;

    private static final String[] INDIAN_STATES = {
            "Gujarat", "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu",
            "Uttar Pradesh", "Rajasthan", "Kerala", "West Bengal", "Madhya Pradesh",
            "Punjab", "Haryana", "Bihar", "Odisha", "Assam", "Other"
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Check if user already completed onboarding
        SharedPreferences prefs = getSharedPreferences("mesh_node_info", MODE_PRIVATE);
        boolean isLoggedIn = prefs.getBoolean("is_logged_in", false);
        if (isLoggedIn && !getIntent().getBooleanExtra("force_relogin", false)) {
            startActivity(new Intent(this, MainActivity.class));
            finish();
            return;
        }

        setContentView(R.layout.activity_login);

        etMobileNumber = findViewById(R.id.etMobileNumber);
        etFullName = findViewById(R.id.etFullName);
        etEmailAddress = findViewById(R.id.etEmailAddress);
        etAddress = findViewById(R.id.etAddress);
        etCity = findViewById(R.id.etCity);
        spState = findViewById(R.id.spState);
        rgRole = findViewById(R.id.rgRole);
        rbCitizen = findViewById(R.id.rbCitizen);
        rbVolunteer = findViewById(R.id.rbVolunteer);
        cbVerify = findViewById(R.id.cbVerify);
        btnSendOtp = findViewById(R.id.btnSendOtp);

        ArrayAdapter<String> stateAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, INDIAN_STATES);
        spState.setAdapter(stateAdapter);

        // Pre-fill existing data if available
        String savedName = prefs.getString("custom_alias", "Abdul Zubair");
        String savedPhone = prefs.getString("phone", "9876543210");
        String savedEmail = prefs.getString("email", "abdulzbair221@gmail.com");
        String savedCity = prefs.getString("city", "Ahmedabad");
        String savedAddress = prefs.getString("address", "Satellite Road");

        etFullName.setText(savedName);
        etMobileNumber.setText(savedPhone);
        if (etEmailAddress != null) etEmailAddress.setText(savedEmail);
        etCity.setText(savedCity);
        etAddress.setText(savedAddress);

        findViewById(R.id.btnBack).setOnClickListener(v -> finish());

        btnSendOtp.setOnClickListener(v -> handleSendOtp());
    }

    private String getBackendUrl() {
        SharedPreferences prefs = getSharedPreferences("aapdasetu_config", MODE_PRIVATE);
        return prefs.getString("backend_url", AapdaSetuSyncManager.RENDER_BACKEND);
    }

    private void handleSendOtp() {
        String phone = etMobileNumber.getText().toString().trim();
        String name = etFullName.getText().toString().trim();
        String email = etEmailAddress != null ? etEmailAddress.getText().toString().trim() : "";
        String address = etAddress.getText().toString().trim();
        String city = etCity.getText().toString().trim();
        String state = spState.getSelectedItem().toString();
        String role = rbVolunteer.isChecked() ? "VOLUNTEER" : "CITIZEN";

        if (phone.length() < 10) {
            Toast.makeText(this, "Please enter a valid 10-digit mobile number.", Toast.LENGTH_SHORT).show();
            return;
        }

        if (name.isEmpty()) {
            Toast.makeText(this, "Please enter your full name.", Toast.LENGTH_SHORT).show();
            return;
        }

        if (email.isEmpty() || !email.contains("@")) {
            Toast.makeText(this, "Please enter a valid Gmail / Email address.", Toast.LENGTH_SHORT).show();
            return;
        }

        if (!cbVerify.isChecked()) {
            Toast.makeText(this, "Please verify your details before proceeding.", Toast.LENGTH_SHORT).show();
            return;
        }

        Toast.makeText(this, "📧 Dispatching emergency OTP to " + email + "...", Toast.LENGTH_LONG).show();

        // Dispatch OTP via Backend
        new Thread(() -> {
            try {
                OkHttpClient client = new OkHttpClient.Builder()
                        .connectTimeout(4, java.util.concurrent.TimeUnit.SECONDS)
                        .readTimeout(6, java.util.concurrent.TimeUnit.SECONDS)
                        .build();
                JSONObject json = new JSONObject();
                json.put("email", email);
                json.put("phone", phone);
                json.put("purpose", "signup");

                RequestBody body = RequestBody.create(json.toString(), MediaType.get("application/json; charset=utf-8"));
                String primaryUrl = getBackendUrl() + "/auth/send-otp";
                Request request = new Request.Builder().url(primaryUrl).post(body).build();

                Response response = null;
                try {
                    response = client.newCall(request).execute();
                } catch (Exception netErr) {
                    try {
                        String fallbackUrl = AapdaSetuSyncManager.LOCAL_BACKEND + "/auth/send-otp";
                        response = client.newCall(new Request.Builder().url(fallbackUrl).post(body).build()).execute();
                    } catch (Exception ignored) {}
                }

                String hintOtp = "123456";
                if (response != null && response.isSuccessful() && response.body() != null) {
                    JSONObject resObj = new JSONObject(response.body().string());
                    JSONObject data = resObj.optJSONObject("data");
                    if (data != null && data.has("devHint")) {
                        hintOtp = data.getString("devHint");
                    }
                }

                final String finalHint = hintOtp;
                runOnUiThread(() -> showOtpDialog(phone, email, name, address, city, state, role, finalHint));
            } catch (Exception e) {
                runOnUiThread(() -> showOtpDialog(phone, email, name, address, city, state, role, "123456"));
            }
        }).start();
    }

    private void showOtpDialog(String phone, String email, String name, String address, String city, String state, String role, String devHint) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("🔐 Enter Gmail Verification OTP");
        builder.setMessage("A 6-digit emergency verification code was dispatched to:\n" + email +
                "\n\n(Master Emergency / Demo Code: " + devHint + ")");

        final EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_CLASS_NUMBER);
        input.setHint("Enter 6-digit OTP");
        input.setText(devHint);
        builder.setView(input);

        builder.setPositiveButton("VERIFY & SIGN IN", (dialog, which) -> {
            String enteredCode = input.getText().toString().trim();
            if (enteredCode.length() >= 4) {
                verifyOtpWithBackend(phone, email, name, address, city, state, role, enteredCode);
            } else {
                Toast.makeText(this, "Please enter a valid OTP code", Toast.LENGTH_SHORT).show();
            }
        });

        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void verifyOtpWithBackend(String phone, String email, String name, String address, String city, String state, String role, String otp) {
        Toast.makeText(this, "Verifying OTP and provisioning node...", Toast.LENGTH_SHORT).show();

        new Thread(() -> {
            try {
                OkHttpClient client = new OkHttpClient();
                JSONObject json = new JSONObject();
                json.put("email", email);
                json.put("phone", phone);
                json.put("otp", otp);
                json.put("name", name);
                json.put("address", address);
                json.put("city", city);
                json.put("state", state);
                json.put("role", role);

                RequestBody body = RequestBody.create(json.toString(), MediaType.get("application/json; charset=utf-8"));
                String primaryUrl = getBackendUrl() + "/auth/verify-otp";
                Request request = new Request.Builder().url(primaryUrl).post(body).build();

                Response response = null;
                try {
                    response = client.newCall(request).execute();
                } catch (Exception netErr) {
                    try {
                        String fallbackUrl = AapdaSetuSyncManager.LOCAL_BACKEND + "/auth/verify-otp";
                        response = client.newCall(new Request.Builder().url(fallbackUrl).post(body).build()).execute();
                    } catch (Exception ignored) {}
                }

                String token = "";
                if (response != null && response.isSuccessful() && response.body() != null) {
                    JSONObject resJson = new JSONObject(response.body().string());
                    JSONObject data = resJson.optJSONObject("data");
                    if (data != null) {
                        token = data.optString("token", "");
                    }
                }

                final String finalToken = token;
                runOnUiThread(() -> completeLogin(phone, email, name, address, city, state, role, finalToken));
            } catch (Exception e) {
                runOnUiThread(() -> completeLogin(phone, email, name, address, city, state, role, ""));
            }
        }).start();
    }

    private void completeLogin(String phone, String email, String name, String address, String city, String state, String role, String token) {
        SharedPreferences prefs = getSharedPreferences("mesh_node_info", MODE_PRIVATE);
        prefs.edit()
                .putBoolean("is_logged_in", true)
                .putString("phone", phone)
                .putString("email", email)
                .putString("custom_alias", name)
                .putString("address", address)
                .putString("city", city)
                .putString("state", state)
                .putString("user_role", role)
                .putString("auth_token", token)
                .apply();

        Toast.makeText(this, "✅ Welcome to Sahay Grid, " + name + " (" + role + ")!", Toast.LENGTH_LONG).show();
        startActivity(new Intent(this, MainActivity.class));
        finish();
    }
}