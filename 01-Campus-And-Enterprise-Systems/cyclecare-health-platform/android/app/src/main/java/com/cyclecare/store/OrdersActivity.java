package com.cyclecare.store;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.models.Order;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class OrdersActivity extends AppCompatActivity {

    private ImageButton btnBack;
    private Button chipAll, chipActive, chipDelivered, btnExplore;
    private SwipeRefreshLayout swipeRefresh;
    private RecyclerView rvOrders;
    private View layoutEmpty;
    private ProgressBar progressBar;

    private OrdersAdapter adapter;
    private final List<Order> allOrders = new ArrayList<>();
    private final List<Order> filteredOrders = new ArrayList<>();
    private String currentFilter = "ALL";

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_orders);

        initViews();
        setupRecyclerView();
        setupClickListeners();
        loadOrders();
    }

    private void initViews() {
        btnBack = findViewById(R.id.btn_orders_back);
        chipAll = findViewById(R.id.chip_filter_all);
        chipActive = findViewById(R.id.chip_filter_active);
        chipDelivered = findViewById(R.id.chip_filter_delivered);
        btnExplore = findViewById(R.id.btn_explore_store_orders);
        swipeRefresh = findViewById(R.id.swipe_refresh_orders);
        rvOrders = findViewById(R.id.rv_orders);
        layoutEmpty = findViewById(R.id.layout_empty_orders);
        progressBar = findViewById(R.id.progress_orders_loading);
    }

    private void setupRecyclerView() {
        adapter = new OrdersAdapter(this);
        rvOrders.setLayoutManager(new LinearLayoutManager(this));
        rvOrders.setAdapter(adapter);
    }

    private void setupClickListeners() {
        btnBack.setOnClickListener(v -> finish());
        btnExplore.setOnClickListener(v -> finish());
        swipeRefresh.setOnRefreshListener(this::loadOrders);

        chipAll.setOnClickListener(v -> setFilter("ALL"));
        chipActive.setOnClickListener(v -> setFilter("ACTIVE"));
        chipDelivered.setOnClickListener(v -> setFilter("DELIVERED"));
    }

    private void setFilter(String filter) {
        currentFilter = filter;
        filteredOrders.clear();

        for (Order o : allOrders) {
            String status = o.getDeliveryStatus() != null ? o.getDeliveryStatus().toUpperCase() : "PROCESSING";
            if ("ALL".equals(filter)) {
                filteredOrders.add(o);
            } else if ("ACTIVE".equals(filter)) {
                if (!"DELIVERED".equals(status) && !"CANCELLED".equals(status)) {
                    filteredOrders.add(o);
                }
            } else if ("DELIVERED".equals(filter)) {
                if ("DELIVERED".equals(status)) {
                    filteredOrders.add(o);
                }
            }
        }

        adapter.setOrders(filteredOrders);
        updateUI();
    }

    private void loadOrders() {
        progressBar.setVisibility(View.VISIBLE);
        ApiClient.getApiService(this).getUserOrders().enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);

                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    Object ordersObj = body.get("orders");
                    Gson gson = new Gson();
                    String json = gson.toJson(ordersObj);
                    Type listType = new TypeToken<List<Order>>() {}.getType();
                    List<Order> list = gson.fromJson(json, listType);

                    allOrders.clear();
                    if (list != null) allOrders.addAll(list);
                    setFilter(currentFilter);
                } else {
                    updateUI();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);
                Toast.makeText(OrdersActivity.this, "Could not load orders", Toast.LENGTH_SHORT).show();
                updateUI();
            }
        });
    }

    private void updateUI() {
        if (filteredOrders.isEmpty()) {
            layoutEmpty.setVisibility(View.VISIBLE);
            rvOrders.setVisibility(View.GONE);
        } else {
            layoutEmpty.setVisibility(View.GONE);
            rvOrders.setVisibility(View.VISIBLE);
        }
    }
}
