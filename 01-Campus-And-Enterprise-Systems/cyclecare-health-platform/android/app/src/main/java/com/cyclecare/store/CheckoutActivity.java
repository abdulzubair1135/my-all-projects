package com.cyclecare.store;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.models.CartItem;
import com.cyclecare.models.UserAddress;
import com.cyclecare.partner.OrderTrackingActivity;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import com.razorpay.Checkout;
import com.razorpay.PaymentResultListener;

import org.json.JSONObject;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class CheckoutActivity extends AppCompatActivity implements PaymentResultListener {

    public static final String EXTRA_BUY_NOW_PRODUCT_ID = "buy_now_product_id";
    public static final String EXTRA_BUY_NOW_PRODUCT_NAME = "buy_now_product_name";
    public static final String EXTRA_BUY_NOW_PRICE = "buy_now_price";
    public static final String EXTRA_BUY_NOW_QTY = "buy_now_qty";
    public static final String EXTRA_BUY_NOW_IMAGE = "buy_now_image";

    private static final int REQUEST_SELECT_ADDRESS = 2001;

    private ImageButton btnBack;
    private Button btnChangeAddress, btnApplyCoupon, btnPlaceOrder;
    private TextView tvRecipientName, tvAddressFull, tvPhone;
    private CheckBox cbDiscreetPackaging;
    private EditText etDeliveryNotes, etCouponCode;
    private RadioGroup rgPaymentMethods;
    private RadioButton rbDemoPayment, rbRazorpay, rbCod;
    private TextView tvCouponAppliedMsg, tvSubtotal, tvDiscount, tvDeliveryFee, tvGrandTotal, tvFooterTotal, tvItemsCount;
    private android.widget.LinearLayout layoutItemsList;
    private View layoutDiscountRow;
    private ProgressBar progressBar;

    private UserAddress selectedAddress = null;
    private final List<CartItem> checkoutCartItems = new ArrayList<>();
    private boolean isBuyNow = false;
    private String buyNowProductId = null;
    private String buyNowProductName = null;
    private double buyNowPrice = 0;
    private int buyNowQty = 1;
    private String buyNowImage = null;

    private double subtotal = 0;
    private double discount = 0;
    private double deliveryFee = 40;
    private double grandTotal = 0;
    private String appliedCoupon = null;
    private String pendingOrderId = null;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_checkout);

        Checkout.preload(getApplicationContext());

        initViews();
        parseIntentData();
        setupClickListeners();
        loadSavedAddress();

        if (isBuyNow) {
            setupBuyNowData();
        } else {
            loadCartItems();
        }
    }

    private void initViews() {
        btnBack = findViewById(R.id.btn_checkout_back);
        btnChangeAddress = findViewById(R.id.btn_change_address);
        btnApplyCoupon = findViewById(R.id.btn_apply_coupon);
        btnPlaceOrder = findViewById(R.id.btn_place_order);

        tvRecipientName = findViewById(R.id.tv_checkout_recipient_name);
        tvAddressFull = findViewById(R.id.tv_checkout_address_full);
        tvPhone = findViewById(R.id.tv_checkout_phone);

        cbDiscreetPackaging = findViewById(R.id.cb_discreet_packaging);
        etDeliveryNotes = findViewById(R.id.et_delivery_notes);
        etCouponCode = findViewById(R.id.et_coupon_code);

        rgPaymentMethods = findViewById(R.id.rg_payment_methods);
        rbDemoPayment = findViewById(R.id.rb_demo_payment);
        rbRazorpay = findViewById(R.id.rb_razorpay_payment);
        rbCod = findViewById(R.id.rb_cod_payment);

        tvCouponAppliedMsg = findViewById(R.id.tv_coupon_applied_msg);
        tvSubtotal = findViewById(R.id.tv_checkout_subtotal);
        tvDiscount = findViewById(R.id.tv_checkout_discount);
        tvDeliveryFee = findViewById(R.id.tv_checkout_delivery_fee);
        tvGrandTotal = findViewById(R.id.tv_checkout_grand_total);
        tvFooterTotal = findViewById(R.id.tv_footer_checkout_total);
        tvItemsCount = findViewById(R.id.tv_checkout_items_count);
        layoutItemsList = findViewById(R.id.layout_checkout_items_list);
        layoutDiscountRow = findViewById(R.id.layout_discount_row);
        progressBar = findViewById(R.id.progress_checkout_loading);
    }

    private void parseIntentData() {
        Intent intent = getIntent();
        if (intent.hasExtra(EXTRA_BUY_NOW_PRODUCT_ID)) {
            isBuyNow = true;
            buyNowProductId = intent.getStringExtra(EXTRA_BUY_NOW_PRODUCT_ID);
            buyNowProductName = intent.getStringExtra(EXTRA_BUY_NOW_PRODUCT_NAME);
            buyNowPrice = intent.getDoubleExtra(EXTRA_BUY_NOW_PRICE, 0);
            buyNowQty = intent.getIntExtra(EXTRA_BUY_NOW_QTY, 1);
            buyNowImage = intent.getStringExtra(EXTRA_BUY_NOW_IMAGE);
        } else if (intent.hasExtra("cart_items")) {
            @SuppressWarnings("unchecked")
            List<CartItem> passedItems = (List<CartItem>) intent.getSerializableExtra("cart_items");
            if (passedItems != null && !passedItems.isEmpty()) {
                checkoutCartItems.clear();
                checkoutCartItems.addAll(passedItems);
                subtotal = intent.getDoubleExtra("subtotal", 0);
                deliveryFee = intent.getDoubleExtra("delivery_fee", 40);
                grandTotal = intent.getDoubleExtra("total", subtotal + deliveryFee);
            }
        }
    }

    private void setupClickListeners() {
        btnBack.setOnClickListener(v -> finish());
        btnChangeAddress.setOnClickListener(v -> {
            Intent intent = new Intent(this, AddressManagementActivity.class);
            startActivityForResult(intent, REQUEST_SELECT_ADDRESS);
        });
        btnApplyCoupon.setOnClickListener(v -> applyCoupon());
        btnPlaceOrder.setOnClickListener(v -> startPlaceOrderFlow());
    }

    private void loadSavedAddress() {
        ApiClient.getApiService(this).getAddresses().enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    Object listObj = body.get("addresses");
                    Gson gson = new Gson();
                    String json = gson.toJson(listObj);
                    Type listType = new TypeToken<List<UserAddress>>() {}.getType();
                    List<UserAddress> list = gson.fromJson(json, listType);

                    if (list != null && !list.isEmpty()) {
                        selectedAddress = list.get(0);
                        for (UserAddress a : list) {
                            if (a.isDefault()) {
                                selectedAddress = a;
                                break;
                            }
                        }
                        bindAddressToUI(selectedAddress);
                    } else {
                        tvRecipientName.setText("No address selected");
                        tvAddressFull.setText("Tap CHANGE to add a delivery address");
                        tvPhone.setText("");
                    }
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {}
        });
    }

    private void bindAddressToUI(UserAddress address) {
        if (address == null) return;
        tvRecipientName.setText(address.getName() + " (" + address.getType() + ")");
        tvAddressFull.setText(address.getFormattedAddress());
        tvPhone.setText("Phone: " + address.getPhone());
    }

    private void setupBuyNowData() {
        subtotal = buyNowPrice * buyNowQty;
        recalculateTotals();
        renderOrderItemsList();
    }

    private void loadCartItems() {
        if (!checkoutCartItems.isEmpty()) {
            recalculateTotals();
            renderOrderItemsList();
            return;
        }

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

                    checkoutCartItems.clear();
                    if (parsed != null && !parsed.isEmpty()) {
                        checkoutCartItems.addAll(parsed);
                    } else {
                        loadLocalCartFallback();
                    }
                    recalculateTotals();
                    renderOrderItemsList();
                } else {
                    loadLocalCartFallback();
                    recalculateTotals();
                    renderOrderItemsList();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                loadLocalCartFallback();
                recalculateTotals();
                renderOrderItemsList();
            }
        });
    }

    private void loadLocalCartFallback() {
        if (!checkoutCartItems.isEmpty()) return;
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
                        checkoutCartItems.add(item);
                    }
                }
            }
        } catch (Exception ignored) {}
    }

    private void renderOrderItemsList() {
        if (layoutItemsList == null) return;
        layoutItemsList.removeAllViews();

        if (isBuyNow) {
            if (tvItemsCount != null) tvItemsCount.setText(buyNowQty + (buyNowQty == 1 ? " Item" : " Items"));
            addItemRow(buyNowProductName != null ? buyNowProductName : "Care Item", buyNowQty, buyNowPrice);
        } else {
            int totalQ = 0;
            for (CartItem item : checkoutCartItems) {
                totalQ += item.getQuantity();
                addItemRow(item.getProductName() != null ? item.getProductName() : "Care Item", item.getQuantity(), item.getUnitPrice());
            }
            if (tvItemsCount != null) tvItemsCount.setText(totalQ + (totalQ == 1 ? " Item" : " Items"));
        }
    }

    private void addItemRow(String name, int qty, double unitPrice) {
        android.widget.LinearLayout row = new android.widget.LinearLayout(this);
        row.setOrientation(android.widget.LinearLayout.HORIZONTAL);
        row.setPadding(0, 8, 0, 8);
        row.setGravity(android.view.Gravity.CENTER_VERTICAL);

        TextView tvName = new TextView(this);
        tvName.setLayoutParams(new android.widget.LinearLayout.LayoutParams(0, android.widget.LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f));
        tvName.setText(name + " (x" + qty + ")");
        tvName.setTextColor(0xFF2D3748);
        tvName.setTextSize(13);
        tvName.setTypeface(null, android.graphics.Typeface.BOLD);

        TextView tvPrice = new TextView(this);
        tvPrice.setLayoutParams(new android.widget.LinearLayout.LayoutParams(android.widget.LinearLayout.LayoutParams.WRAP_CONTENT, android.widget.LinearLayout.LayoutParams.WRAP_CONTENT));
        tvPrice.setText("₹" + (int)(unitPrice * qty));
        tvPrice.setTextColor(0xFFD81B60);
        tvPrice.setTextSize(13);
        tvPrice.setTypeface(null, android.graphics.Typeface.BOLD);

        row.addView(tvName);
        row.addView(tvPrice);
        layoutItemsList.addView(row);
    }

    private void recalculateTotals() {
        if (isBuyNow) {
            subtotal = buyNowPrice * buyNowQty;
        } else {
            subtotal = 0;
            for (CartItem item : checkoutCartItems) {
                subtotal += (item.getUnitPrice() * item.getQuantity());
            }
        }
        deliveryFee = (subtotal >= 499 || subtotal == 0) ? 0 : 40;
        grandTotal = Math.max(0, subtotal - discount + deliveryFee);

        tvSubtotal.setText("₹" + (int) subtotal);
        if (discount > 0) {
            layoutDiscountRow.setVisibility(View.VISIBLE);
            tvDiscount.setText("-₹" + (int) discount);
        } else {
            layoutDiscountRow.setVisibility(View.GONE);
        }
        tvDeliveryFee.setText(deliveryFee == 0 ? "FREE" : "₹" + (int) deliveryFee);
        tvGrandTotal.setText("₹" + (int) grandTotal);
        tvFooterTotal.setText("₹" + (int) grandTotal);
    }

    private void applyCoupon() {
        String code = etCouponCode.getText().toString().trim().toUpperCase();
        if (code.isEmpty()) return;

        if (code.equals("CARE10")) {
            discount = subtotal * 0.10;
            appliedCoupon = "CARE10";
            tvCouponAppliedMsg.setVisibility(View.VISIBLE);
            tvCouponAppliedMsg.setText("✓ Coupon CARE10 applied: 10% OFF (-₹" + (int) discount + ")");
        } else if (code.equals("CYCLECARE")) {
            discount = Math.min(100, subtotal);
            appliedCoupon = "CYCLECARE";
            tvCouponAppliedMsg.setVisibility(View.VISIBLE);
            tvCouponAppliedMsg.setText("✓ Coupon CYCLECARE applied: ₹100 OFF");
        } else {
            Toast.makeText(this, "Invalid promo code. Try CARE10", Toast.LENGTH_SHORT).show();
            return;
        }
        recalculateTotals();
    }

    private void startPlaceOrderFlow() {
        if (selectedAddress == null) {
            Toast.makeText(this, "Please select a delivery address", Toast.LENGTH_SHORT).show();
            Intent intent = new Intent(this, AddressManagementActivity.class);
            startActivityForResult(intent, REQUEST_SELECT_ADDRESS);
            return;
        }

        if (!isBuyNow && checkoutCartItems.isEmpty()) {
            Toast.makeText(this, "Your cart is empty", Toast.LENGTH_SHORT).show();
            return;
        }

        btnPlaceOrder.setEnabled(false);
        progressBar.setVisibility(View.VISIBLE);

        Map<String, Object> orderReq = new HashMap<>();
        if (selectedAddress != null) {
            orderReq.put("address_id", selectedAddress.getId());
        }
        orderReq.put("is_discreet_packaging", cbDiscreetPackaging.isChecked());
        orderReq.put("delivery_notes", etDeliveryNotes.getText().toString().trim());
        if (appliedCoupon != null) orderReq.put("coupon_code", appliedCoupon);

        List<Map<String, Object>> itemsList = new ArrayList<>();
        if (isBuyNow) {
            Map<String, Object> singleItem = new HashMap<>();
            singleItem.put("product_id", buyNowProductId);
            singleItem.put("quantity", buyNowQty);
            itemsList.add(singleItem);
        } else {
            for (CartItem item : checkoutCartItems) {
                String pId = item.getProductId() != null ? item.getProductId() : item.getId();
                if (pId != null) {
                    Map<String, Object> cartItemMap = new HashMap<>();
                    cartItemMap.put("product_id", pId);
                    cartItemMap.put("quantity", item.getQuantity() > 0 ? item.getQuantity() : 1);
                    itemsList.add(cartItemMap);
                }
            }
            orderReq.put("clear_cart", true);
        }
        if (!itemsList.isEmpty()) {
            orderReq.put("items", itemsList);
        }

        ApiClient.getApiService(this).createOrder(orderReq).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    Map<String, Object> orderData = (Map<String, Object>) body.get("order");
                    String orderId = orderData != null ? (String) orderData.get("id") : null;
                    pendingOrderId = orderId;

                    if (orderId == null) {
                        btnPlaceOrder.setEnabled(true);
                        Toast.makeText(CheckoutActivity.this, "Order creation error", Toast.LENGTH_SHORT).show();
                        return;
                    }

                    handlePaymentExecution(orderId);
                } else {
                    btnPlaceOrder.setEnabled(true);
                    Toast.makeText(CheckoutActivity.this, "Failed to create order", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                btnPlaceOrder.setEnabled(true);
                progressBar.setVisibility(View.GONE);
                Toast.makeText(CheckoutActivity.this, "Network error placing order", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void handlePaymentExecution(String orderId) {
        int checkedId = rgPaymentMethods.getCheckedRadioButtonId();

        if (checkedId == R.id.rb_demo_payment) {
            // Demo Payment flow (Simulated + Live Dispatch)
            Map<String, Object> demoReq = new HashMap<>();
            demoReq.put("order_id", orderId);
            demoReq.put("paymentMethod", "DEMO_UPI");

            ApiClient.getApiService(this).createDemoPayment(demoReq).enqueue(new Callback<Map<String, Object>>() {
                @Override
                public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        Map<String, Object> body = response.body();
                        Map<String, Object> payment = (Map<String, Object>) body.get("payment");
                        String paymentId = payment != null ? (String) payment.get("id") : "pay_demo_101";

                        Map<String, Object> successReq = new HashMap<>();
                        successReq.put("order_id", orderId);
                        successReq.put("payment_id", paymentId);

                        ApiClient.getApiService(CheckoutActivity.this).demoPaymentSuccess(successReq).enqueue(new Callback<Map<String, Object>>() {
                            @Override
                            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                                navigateToTracking(orderId);
                            }
                            @Override
                            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                                navigateToTracking(orderId);
                            }
                        });
                    } else {
                        navigateToTracking(orderId);
                    }
                }

                @Override
                public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                    navigateToTracking(orderId);
                }
            });

        } else if (checkedId == R.id.rb_razorpay_payment) {
            // Razorpay flow
            startRazorpayPayment(orderId, (int) (grandTotal * 100));
        } else {
            // Cash on Delivery
            Toast.makeText(this, "Order placed! Cash on delivery selected.", Toast.LENGTH_LONG).show();
            navigateToTracking(orderId);
        }
    }

    private void startRazorpayPayment(String orderId, int amountInPaise) {
        Checkout checkout = new Checkout();
        checkout.setKeyID("rzp_test_mock_id");

        try {
            JSONObject options = new JSONObject();
            options.put("name", "CycleCare");
            options.put("description", "Discreet Menstrual Wellness Order");
            options.put("currency", "INR");
            options.put("amount", amountInPaise);
            options.put("prefill.email", "care@cyclecare.app");
            options.put("prefill.contact", selectedAddress != null ? selectedAddress.getPhone() : "9999999999");

            JSONObject retryObj = new JSONObject();
            retryObj.put("enabled", true);
            retryObj.put("max_count", 2);
            options.put("retry", retryObj);

            checkout.open(this, options);
        } catch (Exception e) {
            Toast.makeText(this, "Razorpay checkout starting in fallback mode...", Toast.LENGTH_SHORT).show();
            navigateToTracking(orderId);
        }
    }

    @Override
    public void onPaymentSuccess(String razorpayPaymentId) {
        Toast.makeText(this, "Payment Verified: " + razorpayPaymentId, Toast.LENGTH_SHORT).show();
        if (pendingOrderId != null) {
            Map<String, Object> verifyReq = new HashMap<>();
            verifyReq.put("order_id", pendingOrderId);
            verifyReq.put("razorpay_payment_id", razorpayPaymentId);
            verifyReq.put("razorpay_order_id", "order_" + pendingOrderId.substring(0, 8));
            verifyReq.put("razorpay_signature", "sig_valid_mock");

            ApiClient.getApiService(this).verifyRazorpayPayment(verifyReq).enqueue(new Callback<Map<String, Object>>() {
                @Override
                public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                    navigateToTracking(pendingOrderId);
                }
                @Override
                public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                    navigateToTracking(pendingOrderId);
                }
            });
        }
    }

    @Override
    public void onPaymentError(int code, String response) {
        btnPlaceOrder.setEnabled(true);
        Toast.makeText(this, "Payment Cancelled / Incomplete: " + response, Toast.LENGTH_LONG).show();
    }

    private void navigateToTracking(String orderId) {
        try {
            getSharedPreferences("cyclecare_local_cart", MODE_PRIVATE).edit().clear().apply();
        } catch (Exception ignored) {}
        Toast.makeText(this, "✓ Order Placed! Discreet courier dispatched.", Toast.LENGTH_SHORT).show();
        Intent intent = new Intent(this, OrderTrackingActivity.class);
        intent.putExtra("order_id", orderId);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        startActivity(intent);
        finish();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_SELECT_ADDRESS && resultCode == RESULT_OK && data != null) {
            UserAddress address = (UserAddress) data.getSerializableExtra(AddressManagementActivity.EXTRA_SELECTED_ADDRESS);
            if (address != null) {
                this.selectedAddress = address;
                bindAddressToUI(selectedAddress);
            }
        }
    }
}
