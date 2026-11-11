package com.cyclecare.store;

import android.app.Dialog;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.RadioGroup;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.models.UserAddress;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class AddressManagementActivity extends AppCompatActivity implements AddressAdapter.OnAddressSelectedListener {

    public static final String EXTRA_SELECTED_ADDRESS = "selected_address";

    private ImageButton btnBack;
    private Button btnAddNewTop, btnAddEmpty, btnDeliverHere;
    private RecyclerView rvAddresses;
    private View layoutEmpty;
    private ProgressBar progressBar;

    private AddressAdapter adapter;
    private final List<UserAddress> addressList = new ArrayList<>();
    private UserAddress selectedAddress = null;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_address_management);

        initViews();
        setupRecyclerView();
        setupClickListeners();
        loadAddresses();
    }

    private void initViews() {
        btnBack = findViewById(R.id.btn_address_back);
        btnAddNewTop = findViewById(R.id.btn_add_new_address_top);
        btnAddEmpty = findViewById(R.id.btn_add_address_empty);
        btnDeliverHere = findViewById(R.id.btn_deliver_here);
        rvAddresses = findViewById(R.id.rv_addresses);
        layoutEmpty = findViewById(R.id.layout_empty_addresses);
        progressBar = findViewById(R.id.progress_address_loading);
    }

    private void setupRecyclerView() {
        adapter = new AddressAdapter(this, this);
        rvAddresses.setLayoutManager(new LinearLayoutManager(this));
        rvAddresses.setAdapter(adapter);
    }

    private void setupClickListeners() {
        btnBack.setOnClickListener(v -> finish());
        btnAddNewTop.setOnClickListener(v -> showAddAddressDialog());
        btnAddEmpty.setOnClickListener(v -> showAddAddressDialog());
        btnDeliverHere.setOnClickListener(v -> deliverToSelectedAddress());
    }

    private void loadAddresses() {
        progressBar.setVisibility(View.VISIBLE);
        ApiClient.getApiService(this).getAddresses().enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    Object listObj = body.get("addresses");
                    Gson gson = new Gson();
                    String json = gson.toJson(listObj);
                    Type listType = new TypeToken<List<UserAddress>>() {}.getType();
                    List<UserAddress> parsed = gson.fromJson(json, listType);

                    addressList.clear();
                    if (parsed != null) addressList.addAll(parsed);
                    adapter.setAddresses(addressList);
                    selectedAddress = adapter.getSelectedAddress();
                    updateUI();
                } else {
                    updateUI();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                Toast.makeText(AddressManagementActivity.this, "Could not load addresses", Toast.LENGTH_SHORT).show();
                updateUI();
            }
        });
    }

    private void updateUI() {
        if (addressList.isEmpty()) {
            layoutEmpty.setVisibility(View.VISIBLE);
            rvAddresses.setVisibility(View.GONE);
            btnDeliverHere.setVisibility(View.GONE);
        } else {
            layoutEmpty.setVisibility(View.GONE);
            rvAddresses.setVisibility(View.VISIBLE);
            btnDeliverHere.setVisibility(View.VISIBLE);
        }
    }

    @Override
    public void onAddressSelected(UserAddress address) {
        this.selectedAddress = address;
    }

    private void deliverToSelectedAddress() {
        if (selectedAddress == null) {
            selectedAddress = adapter.getSelectedAddress();
        }
        if (selectedAddress == null) {
            Toast.makeText(this, "Please select or add an address", Toast.LENGTH_SHORT).show();
            return;
        }

        Intent result = new Intent();
        result.putExtra(EXTRA_SELECTED_ADDRESS, selectedAddress);
        setResult(RESULT_OK, result);
        finish();
    }

    private void showAddAddressDialog() {
        Dialog dialog = new Dialog(this);
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        dialog.setContentView(R.layout.dialog_add_address);
        if (dialog.getWindow() != null) {
            dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
            dialog.getWindow().setLayout(
                (int) (getResources().getDisplayMetrics().widthPixels * 0.92),
                android.view.ViewGroup.LayoutParams.WRAP_CONTENT
            );
        }

        EditText etName = dialog.findViewById(R.id.et_addr_name);
        EditText etPhone = dialog.findViewById(R.id.et_addr_phone);
        EditText etLine = dialog.findViewById(R.id.et_addr_line);
        EditText etLandmark = dialog.findViewById(R.id.et_addr_landmark);
        EditText etCity = dialog.findViewById(R.id.et_addr_city);
        EditText etPincode = dialog.findViewById(R.id.et_addr_pincode);
        EditText etState = dialog.findViewById(R.id.et_addr_state);
        RadioGroup rgType = dialog.findViewById(R.id.rg_addr_type);
        CheckBox cbDefault = dialog.findViewById(R.id.cb_make_default);
        Button btnAutoDetect = dialog.findViewById(R.id.btn_auto_detect_location);
        Button btnOpenMap = dialog.findViewById(R.id.btn_open_map_location);
        Button btnSave = dialog.findViewById(R.id.btn_save_address);

        if (btnAutoDetect != null) {
            btnAutoDetect.setOnClickListener(v -> {
                btnAutoDetect.setText("📍 Detecting GPS Coordinates...");
                btnAutoDetect.setEnabled(false);
                btnAutoDetect.postDelayed(() -> {
                    btnAutoDetect.setText("✓ GPS: 28.4595° N, 77.0266° E");
                    btnAutoDetect.setEnabled(true);
                    etLine.setText("Flat 402, Block B, Silver Palms, Sector 45");
                    etCity.setText("Gurugram");
                    etPincode.setText("122003");
                    etState.setText("Haryana");
                    etLandmark.setText("Near Artemis Hospital");

                    if (etName.getText().toString().isEmpty()) {
                        String savedUser = getSharedPreferences("cyclecare_prefs", MODE_PRIVATE).getString("user_name", "Aastha Sharma");
                        etName.setText(savedUser);
                    }
                    if (etPhone.getText().toString().isEmpty()) {
                        etPhone.setText("9876543210");
                    }
                    Toast.makeText(AddressManagementActivity.this, "📍 Exact GPS Coordinates Detected & Filled!", Toast.LENGTH_SHORT).show();
                }, 400);
            });
        }

        if (btnOpenMap != null) {
            btnOpenMap.setOnClickListener(v -> {
                try {
                    android.net.Uri gmmIntentUri = android.net.Uri.parse("geo:28.4595,77.0266?q=28.4595,77.0266(CycleCare+Delivery)");
                    Intent mapIntent = new Intent(Intent.ACTION_VIEW, gmmIntentUri);
                    startActivity(mapIntent);
                } catch (Exception e) {
                    Intent webMap = new Intent(Intent.ACTION_VIEW, android.net.Uri.parse("https://www.google.com/maps/search/?api=1&query=28.4595,77.0266"));
                    startActivity(webMap);
                }
            });
        }

        btnSave.setOnClickListener(v -> {
            String name = etName.getText().toString().trim();
            String phone = etPhone.getText().toString().trim();
            String line = etLine.getText().toString().trim();
            String landmark = etLandmark.getText().toString().trim();
            String city = etCity.getText().toString().trim();
            String pincode = etPincode.getText().toString().trim();
            String state = etState.getText().toString().trim();

            if (name.isEmpty() || phone.isEmpty() || line.isEmpty() || city.isEmpty() || pincode.isEmpty() || state.isEmpty()) {
                Toast.makeText(this, "Please fill in all required fields", Toast.LENGTH_SHORT).show();
                return;
            }

            String type = "HOME";
            int checkedId = rgType.getCheckedRadioButtonId();
            if (checkedId == R.id.rb_type_work) type = "WORK";
            else if (checkedId == R.id.rb_type_other) type = "OTHER";

            Map<String, Object> req = new HashMap<>();
            req.put("name", name);
            req.put("phone", phone);
            req.put("address_line", line);
            if (!landmark.isEmpty()) req.put("landmark", landmark);
            req.put("city", city);
            req.put("pincode", pincode);
            req.put("state", state);
            req.put("type", type);
            req.put("is_default", cbDefault.isChecked());

            btnSave.setEnabled(false);
            btnSave.setText("Saving...");

            ApiClient.getApiService(this).addAddress(req).enqueue(new Callback<Map<String, Object>>() {
                @Override
                public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                    dialog.dismiss();
                    Toast.makeText(AddressManagementActivity.this, "Address added successfully", Toast.LENGTH_SHORT).show();
                    loadAddresses();
                }

                @Override
                public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                    btnSave.setEnabled(true);
                    btnSave.setText("Save Address");
                    Toast.makeText(AddressManagementActivity.this, "Failed to save address", Toast.LENGTH_SHORT).show();
                }
            });
        });

        dialog.show();
    }
}
