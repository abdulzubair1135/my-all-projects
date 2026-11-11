package com.cyclecare.store;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.models.Order;
import com.cyclecare.partner.OrderTrackingActivity;
import com.cyclecare.utils.ImageLoader;
import com.google.gson.Gson;

import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class OrderDetailActivity extends AppCompatActivity {

    private ImageButton btnBack;
    private TextView tvTitle, tvStatusTag, tvDate, tvOtp;
    private TextView tvRecipient, tvAddressFull, tvSubtotal, tvDeliveryFee, tvTotal;
    private LinearLayout layoutItemsContainer;
    private Button btnTrackLive;

    private String orderId;
    private Order currentOrder;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_order_detail);

        initViews();
        parseIntentData();
        btnBack.setOnClickListener(v -> finish());
    }

    private void initViews() {
        btnBack = findViewById(R.id.btn_detail_back);
        tvTitle = findViewById(R.id.tv_detail_order_title);
        tvStatusTag = findViewById(R.id.tv_detail_status_tag);
        tvDate = findViewById(R.id.tv_detail_date);
        tvOtp = findViewById(R.id.tv_detail_otp);
        tvRecipient = findViewById(R.id.tv_detail_recipient);
        tvAddressFull = findViewById(R.id.tv_detail_address_full);
        tvSubtotal = findViewById(R.id.tv_detail_subtotal);
        tvDeliveryFee = findViewById(R.id.tv_detail_delivery_fee);
        tvTotal = findViewById(R.id.tv_detail_total);
        layoutItemsContainer = findViewById(R.id.layout_detail_items_container);
        btnTrackLive = findViewById(R.id.btn_detail_track_live);
    }

    private void parseIntentData() {
        Intent intent = getIntent();
        orderId = intent.getStringExtra("order_id");
        if (intent.hasExtra("order_data")) {
            currentOrder = (Order) intent.getSerializableExtra("order_data");
        }

        if (currentOrder != null) {
            bindOrderData(currentOrder);
        } else if (orderId != null) {
            fetchOrderDetails(orderId);
        }
    }

    private void fetchOrderDetails(String id) {
        ApiClient.getApiService(this).getOrderById(id).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    Object orderObj = body.get("order");
                    Gson gson = new Gson();
                    String json = gson.toJson(orderObj);
                    currentOrder = gson.fromJson(json, Order.class);
                    if (currentOrder != null) {
                        bindOrderData(currentOrder);
                    }
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                Toast.makeText(OrderDetailActivity.this, "Could not load order details", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void bindOrderData(Order order) {
        tvTitle.setText("Order #" + order.getOrderNumber());
        tvStatusTag.setText(order.getDeliveryStatus() != null ? order.getDeliveryStatus().replace("_", " ") : "PROCESSING");
        tvDate.setText(order.getCreatedAt() != null ? order.getCreatedAt().substring(0, 10) : "");
        tvOtp.setText(order.getDeliveryOtp() != null ? order.getDeliveryOtp() : "4821");

        if (order.getAddress() != null) {
            tvRecipient.setText(order.getAddress().getName() + " (" + order.getAddress().getType() + ")");
            tvAddressFull.setText(order.getAddress().getFormattedAddress());
        }

        tvSubtotal.setText("₹" + (int) order.getSubtotal());
        tvDeliveryFee.setText(order.getDeliveryFee() == 0 ? "FREE" : "₹" + (int) order.getDeliveryFee());
        tvTotal.setText("₹" + (int) order.getTotalAmount());

        btnTrackLive.setOnClickListener(v -> {
            Intent intent = new Intent(OrderDetailActivity.this, OrderTrackingActivity.class);
            intent.putExtra("order_id", order.getId());
            startActivity(intent);
        });

        // Populate items
        layoutItemsContainer.removeAllViews();
        if (order.getItems() != null) {
            LayoutInflater inflater = LayoutInflater.from(this);
            for (Order.OrderItem item : order.getItems()) {
                View itemView = inflater.inflate(R.layout.item_cart, layoutItemsContainer, false);

                ImageView ivImg = itemView.findViewById(R.id.iv_cart_item_image);
                TextView tvName = itemView.findViewById(R.id.tv_cart_item_name);
                TextView tvUnitPrice = itemView.findViewById(R.id.tv_cart_item_unit_price);
                TextView tvQty = itemView.findViewById(R.id.tv_cart_item_qty);
                TextView tvItemTotal = itemView.findViewById(R.id.tv_cart_item_total);
                View btnMinus = itemView.findViewById(R.id.btn_qty_minus);
                View btnPlus = itemView.findViewById(R.id.btn_qty_plus);
                View btnRemove = itemView.findViewById(R.id.btn_remove_item);

                btnMinus.setVisibility(View.GONE);
                btnPlus.setVisibility(View.GONE);
                btnRemove.setVisibility(View.GONE);

                tvName.setText(item.getProductNameSnapshot());
                tvUnitPrice.setText("₹" + (int) item.getUnitPrice());
                tvQty.setText("Qty: " + item.getQuantity());
                tvItemTotal.setText("₹" + (int) (item.getUnitPrice() * item.getQuantity()));

                if (item.getImageUrl() != null && !item.getImageUrl().isEmpty()) {
                    ImageLoader.getInstance().loadImage(item.getImageUrl(), ivImg, R.drawable.ic_nav_store_3d);
                }

                layoutItemsContainer.addView(itemView);
            }
        }
    }
}
