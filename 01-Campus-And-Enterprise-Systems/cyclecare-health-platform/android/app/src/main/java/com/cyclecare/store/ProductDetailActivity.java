package com.cyclecare.store;

import android.content.Intent;
import android.graphics.Paint;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.models.Product;
import com.cyclecare.utils.ImageLoader;
import com.google.gson.Gson;

import java.util.HashMap;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ProductDetailActivity extends AppCompatActivity {

    public static final String EXTRA_PRODUCT_ID = "product_id";
    public static final String EXTRA_PRODUCT_NAME = "product_name";
    public static final String EXTRA_PRODUCT_PRICE = "product_price";
    public static final String EXTRA_PRODUCT_IMAGE = "product_image";
    public static final String EXTRA_PRODUCT_DESC = "product_desc";

    private ImageView ivProductHero;
    private TextView tvBadgeStatus, tvBrand, tvCategory, tvTitle;
    private TextView tvStock, tvPrice, tvMrp, tvDiscountTag;
    private TextView tvQuantity, tvDescription, tvSku;
    private Button btnQtyMinus, btnQtyPlus, btnAddToCart, btnBuyNow;
    private ImageButton btnBack;

    private String productId;
    private int quantity = 1;
    private Product currentProduct;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_product_detail);

        initViews();
        handleIntentData(getIntent());

        btnBack.setOnClickListener(v -> finish());
        btnQtyMinus.setOnClickListener(v -> {
            if (quantity > 1) {
                quantity--;
                tvQuantity.setText(String.valueOf(quantity));
            }
        });
        btnQtyPlus.setOnClickListener(v -> {
            quantity++;
            tvQuantity.setText(String.valueOf(quantity));
        });

        btnAddToCart.setOnClickListener(v -> addToCart());
        btnBuyNow.setOnClickListener(v -> buyNow());
        ImageButton btnCart = findViewById(R.id.btn_cart);
        if (btnCart != null) {
            btnCart.setOnClickListener(v -> {
                Intent cartIntent = new Intent(ProductDetailActivity.this, CartActivity.class);
                startActivity(cartIntent);
            });
        }
        View cardPartnerCare = findViewById(R.id.card_partner_care);
        if (cardPartnerCare != null) {
            cardPartnerCare.setOnClickListener(v -> {
                Intent chatIntent = new Intent(ProductDetailActivity.this, com.cyclecare.chat.CircleChatActivity.class);
                chatIntent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_CONTACT_NAME, "Husband / Partner");
                chatIntent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_RELATIONSHIP, "Partner");
                startActivity(chatIntent);
                Toast.makeText(ProductDetailActivity.this, "Opening Circle Care Chat to share item...", Toast.LENGTH_SHORT).show();
            });
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleIntentData(intent);
    }

    private void initViews() {
        btnBack = findViewById(R.id.btn_back);
        ivProductHero = findViewById(R.id.iv_product_hero);
        tvBadgeStatus = findViewById(R.id.tv_badge_status);
        tvBrand = findViewById(R.id.tv_brand);
        tvCategory = findViewById(R.id.tv_category);
        tvTitle = findViewById(R.id.tv_title);
        tvStock = findViewById(R.id.tv_stock);
        tvPrice = findViewById(R.id.tv_price);
        tvMrp = findViewById(R.id.tv_mrp);
        tvDiscountTag = findViewById(R.id.tv_discount_tag);
        tvQuantity = findViewById(R.id.tv_quantity);
        tvDescription = findViewById(R.id.tv_description);
        tvSku = findViewById(R.id.tv_sku);
        btnQtyMinus = findViewById(R.id.btn_qty_minus);
        btnQtyPlus = findViewById(R.id.btn_qty_plus);
        btnAddToCart = findViewById(R.id.btn_add_to_cart);
        btnBuyNow = findViewById(R.id.btn_buy_now);

        // Strike through original MRP
        tvMrp.setPaintFlags(tvMrp.getPaintFlags() | Paint.STRIKE_THRU_TEXT_FLAG);
    }

    private void handleIntentData(Intent intent) {
        if (intent == null) return;

        // Check for deep link URI: cyclecare://product/{id} or https://...
        Uri data = intent.getData();
        if (data != null) {
            String pathSegment = data.getLastPathSegment();
            if (pathSegment != null && !pathSegment.isEmpty()) {
                productId = pathSegment;
            }
        }

        // Fallback or explicit extra
        if (productId == null || productId.isEmpty()) {
            productId = intent.getStringExtra(EXTRA_PRODUCT_ID);
        }

        // Check for immediate preview extras
        String extraName = intent.getStringExtra(EXTRA_PRODUCT_NAME);
        String extraPrice = intent.getStringExtra(EXTRA_PRODUCT_PRICE);
        String extraImage = intent.getStringExtra(EXTRA_PRODUCT_IMAGE);
        String extraDesc = intent.getStringExtra(EXTRA_PRODUCT_DESC);

        if (extraName != null) {
            tvTitle.setText(extraName);
        }
        if (extraPrice != null) {
            tvPrice.setText("₹ " + extraPrice);
            tvMrp.setText("₹ " + (Double.parseDouble(extraPrice) + 50));
        }
        if (extraDesc != null) {
            tvDescription.setText(extraDesc);
        }
        if (extraImage != null && !extraImage.isEmpty()) {
            ImageLoader.getInstance().loadImage(extraImage, ivProductHero, R.drawable.ic_nav_store_3d);
        }

        if (productId != null && !productId.isEmpty()) {
            fetchProductDetails(productId);
        }
    }

    private void fetchProductDetails(String id) {
        ApiClient.getApiService(this).getProductDetails(id).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    Object productObj = body.get("product");
                    if (productObj != null) {
                        Gson gson = new Gson();
                        String json = gson.toJson(productObj);
                        currentProduct = gson.fromJson(json, Product.class);
                        updateUI(currentProduct);
                    }
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                // If API failed, keep extra fields displayed
            }
        });
    }

    private void updateUI(Product p) {
        if (p == null) return;

        tvTitle.setText(p.getName());
        tvBrand.setText(p.getBrand());
        tvCategory.setText(p.getCategory());
        tvDescription.setText(p.getDescription());
        tvSku.setText("SKU: " + p.getSku());

        double activePrice = p.getActivePrice();
        tvPrice.setText("₹ " + (int) activePrice);

        if (p.getDiscountPrice() != null && p.getDiscountPrice() > 0 && p.getDiscountPrice() < p.getPrice()) {
            tvMrp.setVisibility(View.VISIBLE);
            tvMrp.setText("₹ " + (int) p.getPrice());
            int pct = (int) Math.round(((p.getPrice() - p.getDiscountPrice()) / p.getPrice()) * 100);
            tvDiscountTag.setVisibility(View.VISIBLE);
            tvDiscountTag.setText(pct + "% OFF");
        } else {
            tvMrp.setVisibility(View.GONE);
            tvDiscountTag.setVisibility(View.GONE);
        }

        if (p.getStock() > 0) {
            tvStock.setText("In Stock (" + p.getStock() + ")");
            tvStock.setTextColor(getResources().getColor(R.color.colorMintGreenDark));
            btnAddToCart.setEnabled(true);
            btnBuyNow.setEnabled(true);
        } else {
            tvStock.setText("Out of Stock");
            tvStock.setTextColor(0xFFDC2626);
            btnAddToCart.setEnabled(false);
            btnBuyNow.setText("Notify When Available");
        }

        if (p.getImageUrl() != null && !p.getImageUrl().isEmpty()) {
            ImageLoader.getInstance().loadImage(p.getImageUrl(), ivProductHero, R.drawable.ic_nav_store_3d);
        }
    }

    private void addToCart() {
        String name = currentProduct != null ? currentProduct.getName() : tvTitle.getText().toString();
        Toast.makeText(this, "Added " + quantity + "x " + name + " to Care Kit Cart!", Toast.LENGTH_SHORT).show();

        if (productId != null) {
            Map<String, Object> cartItem = new HashMap<>();
            cartItem.put("product_id", productId);
            cartItem.put("quantity", quantity);
            ApiClient.getApiService(ProductDetailActivity.this).addToCart(cartItem).enqueue(new Callback<Map<String, Object>>() {
                @Override
                public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {}
                @Override
                public void onFailure(Call<Map<String, Object>> call, Throwable t) {}
            });
        }

        Intent cartIntent = new Intent(this, CartActivity.class);
        startActivity(cartIntent);
    }

    private void buyNow() {
        double price = 199.0;
        if (currentProduct != null) {
            price = currentProduct.getDiscountPrice() > 0 ? currentProduct.getDiscountPrice() : currentProduct.getPrice();
        }

        Intent checkoutIntent = new Intent(this, CheckoutActivity.class);
        checkoutIntent.putExtra(CheckoutActivity.EXTRA_BUY_NOW_PRODUCT_ID, productId);
        checkoutIntent.putExtra(CheckoutActivity.EXTRA_BUY_NOW_PRODUCT_NAME, currentProduct != null ? currentProduct.getName() : tvTitle.getText().toString());
        checkoutIntent.putExtra(CheckoutActivity.EXTRA_BUY_NOW_PRICE, price);
        checkoutIntent.putExtra(CheckoutActivity.EXTRA_BUY_NOW_QTY, quantity);
        checkoutIntent.putExtra(CheckoutActivity.EXTRA_BUY_NOW_IMAGE, currentProduct != null ? currentProduct.getImageUrl() : "");
        startActivity(checkoutIntent);
    }
}
