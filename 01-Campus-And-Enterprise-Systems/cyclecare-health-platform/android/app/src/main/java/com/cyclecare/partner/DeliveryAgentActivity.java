package com.cyclecare.partner;

import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.api.ApiService;

import java.util.HashMap;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class DeliveryAgentActivity extends AppCompatActivity {

    private TextView tvStatusBadge;
    private TextView tvStatPending;
    private TextView tvStatProgress;
    private TextView tvStatCompleted;
    private String currentDeliveryId = "cc-demo-1001";
    private ApiService apiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_delivery_agent);

        apiService = ApiClient.getApiService(this);

        tvStatusBadge = findViewById(R.id.tv_delivery_status_badge);
        tvStatPending = findViewById(R.id.tv_stat_pending);
        tvStatProgress = findViewById(R.id.tv_stat_progress);
        tvStatCompleted = findViewById(R.id.tv_stat_completed);

        Button btnAccept = findViewById(R.id.btn_accept);
        Button btnPickedUp = findViewById(R.id.btn_picked_up);
        Button btnStart = findViewById(R.id.btn_start);
        Button btnSimulate = findViewById(R.id.btn_simulate);
        Button btnArrive = findViewById(R.id.btn_arrive);
        Button btnComplete = findViewById(R.id.btn_complete);
        Button btnOpenCustomerTracking = findViewById(R.id.btn_open_customer_tracking);

        btnAccept.setOnClickListener(v -> {
            updateStatus("ACCEPTED", "#2563EB");
            showToast("Order accepted by Courier");
        });

        btnPickedUp.setOnClickListener(v -> {
            updateStatus("PICKED UP", "#7C3AED");
            showToast("Package picked up from dispensary");
        });

        btnStart.setOnClickListener(v -> {
            updateStatus("OUT FOR DELIVERY", "#E91E63");
            tvStatPending.setText("0");
            tvStatProgress.setText("1");
            showToast("Out for Delivery • Live GPS tracking enabled");
        });

        btnSimulate.setOnClickListener(v -> {
            showToast("Simulating GPS movement to customer address...");
            apiService.simulateDelivery(currentDeliveryId, 1).enqueue(new Callback<Map<String, Object>>() {
                @Override
                public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                    showToast("GPS live telemetry updating on customer map");
                }

                @Override
                public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                    showToast("Simulated GPS active (local mode)");
                }
            });
        });

        btnArrive.setOnClickListener(v -> {
            updateStatus("ARRIVED", "#D97706");
            showToast("Arrived at customer address. Ringing bell / notifying.");
        });

        btnComplete.setOnClickListener(v -> {
            final EditText otpInput = new EditText(this);
            otpInput.setHint("Enter 4-digit customer OTP");
            otpInput.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
            otpInput.setPadding(40, 30, 40, 30);

            new AlertDialog.Builder(this)
                .setTitle("Confirm Handover")
                .setMessage("Ask the customer for their secure 4-digit delivery OTP to confirm sealed package delivery:")
                .setView(otpInput)
                .setPositiveButton("Verify & Complete", (dialog, which) -> {
                    String enteredOtp = otpInput.getText().toString().trim();
                    if ("4821".equals(enteredOtp)) {
                        updateStatus("DELIVERED", "#16A34A");
                        tvStatProgress.setText("0");
                        tvStatCompleted.setText("1");
                        showToast("Delivery confirmed & completed! OTP verified.");
                    } else {
                        showToast("Incorrect OTP! Expected customer code.");
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
        });

        if (btnOpenCustomerTracking != null) {
            btnOpenCustomerTracking.setOnClickListener(v -> {
                Intent intent = new Intent(this, OrderTrackingActivity.class);
                intent.putExtra("order_id", currentDeliveryId);
                startActivity(intent);
            });
        }
    }

    private void updateStatus(String statusText, String hexColor) {
        if (tvStatusBadge != null) {
            tvStatusBadge.setText(statusText);
            tvStatusBadge.setTextColor(android.graphics.Color.parseColor(hexColor));
        }
    }

    private void showToast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }
}
