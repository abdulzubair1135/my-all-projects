package com.cyclecare.store;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.models.CartItem;
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

public class CartActivity extends AppCompatActivity implements CartAdapter.OnCartItemInteractionListener {

    private ImageButton btnBack;
    private TextView tvItemCountHeader, tvBillSubtotal, tvBillDeliveryFee, tvBillTotal, tvFooterTotal, tvDeliveryThresholdMsg;
    private View cardDeliveryThreshold, cardBottomCheckout, layoutEmptyCart, scrollCartContent;
    private Button btnProceedToCheckout, btnExploreStore;
    private ProgressBar progressBar;
    private RecyclerView rvCartItems;

    private CartAdapter adapter;
    private final List<CartItem> cartItems = new ArrayList<>();
    private double currentSubtotal = 0;
    private double currentDeliveryFee = 40;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_cart);

        initViews();
        setupRecyclerView();
        setupClickListeners();
        loadCart();
    }

    private void initViews() {
        btnBack = findViewById(R.id.btn_cart_back);
        tvItemCountHeader = findViewById(R.id.tv_cart_item_count_header);
        tvBillSubtotal = findViewById(R.id.tv_bill_subtotal);
        tvBillDeliveryFee = findViewById(R.id.tv_bill_delivery_fee);
        tvBillTotal = findViewById(R.id.tv_bill_total);
        tvFooterTotal = findViewById(R.id.tv_footer_total);
        tvDeliveryThresholdMsg = findViewById(R.id.tv_delivery_threshold_msg);
        cardDeliveryThreshold = findViewById(R.id.card_delivery_threshold);
        cardBottomCheckout = findViewById(R.id.card_bottom_checkout);
        layoutEmptyCart = findViewById(R.id.layout_empty_cart);
        scrollCartContent = findViewById(R.id.scroll_cart_content);
        btnProceedToCheckout = findViewById(R.id.btn_proceed_to_checkout);
        btnExploreStore = findViewById(R.id.btn_explore_store);
        progressBar = findViewById(R.id.progress_cart_loading);
        rvCartItems = findViewById(R.id.rv_cart_items);
    }

    private void setupRecyclerView() {
        adapter = new CartAdapter(this, this);
        rvCartItems.setLayoutManager(new LinearLayoutManager(this));
        rvCartItems.setAdapter(adapter);
    }

    private void setupClickListeners() {
        btnBack.setOnClickListener(v -> finish());
        btnExploreStore.setOnClickListener(v -> finish());
        btnProceedToCheckout.setOnClickListener(v -> proceedToCheckout());
    }

    private void loadCart() {
        progressBar.setVisibility(View.VISIBLE);
        ApiClient.getApiService(this).getCart().enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    Object itemsObj = body.get("items");
                    Gson gson = new Gson();
                    String json = gson.toJson(itemsObj);
                    Type listType = new TypeToken<List<CartItem>>() {}.getType();
                    List<CartItem> parsed = gson.fromJson(json, listType);

                    cartItems.clear();
                    if (parsed != null && !parsed.isEmpty()) {
                        cartItems.addAll(parsed);
                    } else {
                        loadLocalCartFallback();
                    }
                    adapter.setItems(cartItems);
                    updateTotalsUI();
                } else {
                    loadLocalCartFallback();
                    updateTotalsUI();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                loadLocalCartFallback();
                updateTotalsUI();
            }
        });
    }

    private void loadLocalCartFallback() {
        if (!cartItems.isEmpty()) return;
        try {
            android.content.SharedPreferences sp = getSharedPreferences("cyclecare_local_cart", MODE_PRIVATE);
            Map<String, ?> all = sp.getAll();
            for (Map.Entry<String, ?> entry : all.entrySet()) {
                if (entry.getKey().startsWith("qty_") && entry.getValue() instanceof Integer) {
                    int q = (Integer) entry.getValue();
                    if (q > 0) {
                        String pId = entry.getKey().substring(4);
                        String name = sp.getString("name_" + pId, "CycleCare Care Item");
                        float price = sp.getFloat("price_" + pId, 199.0f);
                        String img = sp.getString("img_" + pId, "");

                        CartItem item = new CartItem();
                        item.setId(pId);
                        item.setProductId(pId);
                        item.setProductName(name);
                        item.setUnitPrice(price);
                        item.setQuantity(q);
                        item.setImageUrl(img);
                        item.setItemTotal(price * q);
                        cartItems.add(item);
                    }
                }
            }
            if (adapter != null) adapter.setItems(cartItems);
        } catch (Exception ignored) {}
    }

    private void updateTotalsUI() {
        if (cartItems.isEmpty()) {
            layoutEmptyCart.setVisibility(View.VISIBLE);
            scrollCartContent.setVisibility(View.GONE);
            cardBottomCheckout.setVisibility(View.GONE);
            tvItemCountHeader.setText("0 Items");
            return;
        }

        layoutEmptyCart.setVisibility(View.GONE);
        scrollCartContent.setVisibility(View.VISIBLE);
        cardBottomCheckout.setVisibility(View.VISIBLE);

        int totalCount = 0;
        currentSubtotal = 0;
        for (CartItem item : cartItems) {
            totalCount += item.getQuantity();
            currentSubtotal += (item.getUnitPrice() * item.getQuantity());
        }

        tvItemCountHeader.setText(totalCount + (totalCount == 1 ? " Item" : " Items"));
        currentDeliveryFee = currentSubtotal >= 499 ? 0 : 40;
        double totalPayable = currentSubtotal + currentDeliveryFee;

        tvBillSubtotal.setText("₹" + (int) currentSubtotal);
        tvBillDeliveryFee.setText(currentDeliveryFee == 0 ? "FREE" : "₹" + (int) currentDeliveryFee);
        tvBillTotal.setText("₹" + (int) totalPayable);
        tvFooterTotal.setText("₹" + (int) totalPayable);

        if (currentSubtotal >= 499) {
            tvDeliveryThresholdMsg.setText("✓ You qualified for FREE Express Delivery!");
            tvDeliveryThresholdMsg.setTextColor(0xFF15803D);
        } else {
            int remaining = (int) (499 - currentSubtotal);
            tvDeliveryThresholdMsg.setText("Add ₹" + remaining + " more for FREE Express Delivery!");
            tvDeliveryThresholdMsg.setTextColor(0xFFBE185D);
        }
    }

    @Override
    public void onQuantityChanged(CartItem item, int newQuantity) {
        updateTotalsUI();
        Map<String, Object> body = new HashMap<>();
        body.put("quantity", newQuantity);
        ApiClient.getApiService(this).updateCartItem(item.getId(), body).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {}
            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {}
        });
    }

    @Override
    public void onItemRemoved(CartItem item) {
        cartItems.remove(item);
        adapter.setItems(cartItems);
        updateTotalsUI();

        ApiClient.getApiService(this).removeFromCart(item.getId()).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                Toast.makeText(CartActivity.this, "Item removed from cart", Toast.LENGTH_SHORT).show();
            }
            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {}
        });
    }

    private void proceedToCheckout() {
        if (cartItems.isEmpty()) return;
        Intent intent = new Intent(this, CheckoutActivity.class);
        intent.putExtra("subtotal", currentSubtotal);
        intent.putExtra("delivery_fee", currentDeliveryFee);
        intent.putExtra("total", currentSubtotal + currentDeliveryFee);
        intent.putExtra("cart_items", new ArrayList<>(cartItems));
        startActivity(intent);
    }
}
