package com.cyclecare.partner;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.api.ApiService;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class CarePackageActivity extends AppCompatActivity {

    private CheckBox cbItem1, cbItem2, cbItem3;
    private EditText etCareMessage;
    private TextView tvTotalPrice;
    private Button btnCheckout;

    private ApiService apiService;
    private String connectionId;
    private String partnerName;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_care_package);

        apiService = ApiClient.getApiService(this);

        connectionId = getIntent().getStringExtra("connection_id");
        partnerName = getIntent().getStringExtra("partner_name");
        if (partnerName == null) partnerName = "Partner";

        initViews();
        calculateTotal();
    }

    private void initViews() {
        ImageButton btnBack = findViewById(R.id.btn_back);
        if (btnBack != null) {
            btnBack.setOnClickListener(v -> finish());
        }

        cbItem1 = findViewById(R.id.cb_item1);
        cbItem2 = findViewById(R.id.cb_item2);
        cbItem3 = findViewById(R.id.cb_item3);
        etCareMessage = findViewById(R.id.et_care_message);
        tvTotalPrice = findViewById(R.id.tv_total_price);
        btnCheckout = findViewById(R.id.btn_checkout_care_package);

        cbItem1.setOnCheckedChangeListener((btn, isChecked) -> calculateTotal());
        cbItem2.setOnCheckedChangeListener((btn, isChecked) -> calculateTotal());
        cbItem3.setOnCheckedChangeListener((btn, isChecked) -> calculateTotal());

        btnCheckout.setOnClickListener(v -> sendCarePackage());
    }

    private int calculateTotal() {
        int total = 0;
        if (cbItem1 != null && cbItem1.isChecked()) total += 199;
        if (cbItem2 != null && cbItem2.isChecked()) total += 169;
        if (cbItem3 != null && cbItem3.isChecked()) total += 249;

        if (tvTotalPrice != null) {
            tvTotalPrice.setText("₹ " + total);
        }
        return total;
    }

    private void sendCarePackage() {
        if (TextUtils.isEmpty(connectionId)) {
            Toast.makeText(this, "No active partner connection found.", Toast.LENGTH_SHORT).show();
            return;
        }

        int total = calculateTotal();
        if (total <= 0) {
            Toast.makeText(this, "Please select at least one care item.", Toast.LENGTH_SHORT).show();
            return;
        }

        List<Map<String, Object>> items = new ArrayList<>();
        if (cbItem1.isChecked()) {
            Map<String, Object> it = new HashMap<>();
            it.put("name", "Organic Cotton Ultra Pads");
            it.put("price", 199);
            it.put("quantity", 1);
            items.add(it);
        }
        if (cbItem2.isChecked()) {
            Map<String, Object> it = new HashMap<>();
            it.put("name", "Cramp Relief Heat Patch");
            it.put("price", 169);
            it.put("quantity", 1);
            items.add(it);
        }
        if (cbItem3.isChecked()) {
            Map<String, Object> it = new HashMap<>();
            it.put("name", "Chamomile Comfort Herbal Tea");
            it.put("price", 249);
            it.put("quantity", 1);
            items.add(it);
        }

        String note = etCareMessage.getText().toString().trim();
        if (TextUtils.isEmpty(note)) {
            note = "Take care and rest well today. I am here for you! ❤️";
        }

        btnCheckout.setEnabled(false);
        btnCheckout.setText("Processing...");

        Map<String, Object> payload = new HashMap<>();
        payload.put("items", items);
        payload.put("message", note);
        payload.put("delivery_address", "Partner Shared Delivery Address");

        apiService.createCarePackage(connectionId, payload).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                btnCheckout.setEnabled(true);
                btnCheckout.setText("Send Care Package");

                if (response.isSuccessful() || "demo_connection".equals(connectionId)) {
                    new AlertDialog.Builder(CarePackageActivity.this)
                            .setTitle("Care Package Sent! 🎁")
                            .setMessage("Your supportive care package and personal note have been dispatched to " + partnerName + "!\n\nDiscreet eco-friendly delivery has been arranged.")
                            .setPositiveButton("Wonderful", (d, w) -> {
                                d.dismiss();
                                finish();
                            })
                            .setCancelable(false)
                            .show();
                } else {
                    Toast.makeText(CarePackageActivity.this, "Could not complete order. Please verify permissions.", Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                btnCheckout.setEnabled(true);
                btnCheckout.setText("Send Care Package");
                if ("demo_connection".equals(connectionId)) {
                    new AlertDialog.Builder(CarePackageActivity.this)
                            .setTitle("Care Package Sent! 🎁")
                            .setMessage("Your supportive care package and personal note have been dispatched to " + partnerName + "!\n\nDiscreet eco-friendly delivery has been arranged.")
                            .setPositiveButton("Wonderful", (d, w) -> {
                                d.dismiss();
                                finish();
                            })
                            .setCancelable(false)
                            .show();
                } else {
                    Toast.makeText(CarePackageActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });
    }
}
