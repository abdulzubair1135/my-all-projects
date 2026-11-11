package com.cyclecare.store;

import android.content.Context;
import android.content.Intent;
import android.graphics.Paint;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.cyclecare.R;
import com.cyclecare.models.Product;
import com.cyclecare.utils.ImageLoader;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ProductAdapter extends RecyclerView.Adapter<ProductAdapter.ProductViewHolder> {

    private final Context context;
    private final List<Product> productList;
    private final Set<String> wishlistedIds = new HashSet<>();
    private OnCartUpdatedListener cartUpdatedListener;

    public interface OnCartUpdatedListener {
        void onCartUpdated();
    }

    public ProductAdapter(Context context, List<Product> productList) {
        this.context = context;
        this.productList = productList;
    }

    public void setOnCartUpdatedListener(OnCartUpdatedListener listener) {
        this.cartUpdatedListener = listener;
    }

    @NonNull
    @Override
    public ProductViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_product, parent, false);
        return new ProductViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ProductViewHolder holder, int position) {
        Product product = productList.get(position);
        holder.tvName.setText(product.getName());
        holder.tvBrand.setText("CycleCare Essentials");
        holder.tvRating.setText("4.9");
        
        int price = (int) product.getActivePrice();
        int mrp = (int) Math.round(price * 1.25); // 20-25% MRP anchor
        holder.tvPrice.setText("₹ " + price);
        holder.tvMrp.setText("₹ " + mrp);
        holder.tvMrp.setPaintFlags(holder.tvMrp.getPaintFlags() | Paint.STRIKE_THRU_TEXT_FLAG);

        holder.tvCategoryTag.setText(product.getCategory() != null ? product.getCategory() : "Essential");
        holder.tvStockStatus.setText(product.getStock() > 0 ? "In Stock" : "Restocking");

        if (product.getImageUrl() != null && !product.getImageUrl().isEmpty()) {
            ImageLoader.getInstance().loadImage(product.getImageUrl(), holder.ivProductIcon, R.drawable.ic_nav_store_3d);
        } else {
            holder.ivProductIcon.setImageResource(R.drawable.ic_nav_store_3d);
        }

        // Wishlist Toggle
        boolean isWishlisted = wishlistedIds.contains(product.getId());
        holder.btnWishlist.setImageResource(isWishlisted ? R.drawable.ic_heart_filled : R.drawable.ic_heart_outline);
        holder.btnWishlist.setOnClickListener(v -> {
            if (wishlistedIds.contains(product.getId())) {
                wishlistedIds.remove(product.getId());
                holder.btnWishlist.setImageResource(R.drawable.ic_heart_outline);
                Toast.makeText(context, "Removed from Wishlist", Toast.LENGTH_SHORT).show();
            } else {
                wishlistedIds.add(product.getId());
                holder.btnWishlist.setImageResource(R.drawable.ic_heart_filled);
                Toast.makeText(context, "Saved to Wishlist", Toast.LENGTH_SHORT).show();
            }
        });

        // Tapping product opens Product Detail page directly
        holder.itemView.setOnClickListener(v -> {
            Intent intent = new Intent(context, ProductDetailActivity.class);
            intent.putExtra(ProductDetailActivity.EXTRA_PRODUCT_ID, product.getId());
            intent.putExtra(ProductDetailActivity.EXTRA_PRODUCT_NAME, product.getName());
            intent.putExtra(ProductDetailActivity.EXTRA_PRODUCT_PRICE, String.valueOf(product.getActivePrice()));
            intent.putExtra(ProductDetailActivity.EXTRA_PRODUCT_IMAGE, product.getImageUrl());
            intent.putExtra(ProductDetailActivity.EXTRA_PRODUCT_DESC, product.getDescription());
            context.startActivity(intent);
        });

        // Quantity Stepper for Card
        final int[] itemQty = {1};
        holder.tvCardQty.setText("1");

        holder.btnCardQtyMinus.setOnClickListener(v -> {
            if (itemQty[0] > 1) {
                itemQty[0]--;
                holder.tvCardQty.setText(String.valueOf(itemQty[0]));
            }
        });

        holder.btnCardQtyPlus.setOnClickListener(v -> {
            itemQty[0]++;
            holder.tvCardQty.setText(String.valueOf(itemQty[0]));
        });

        // Add to Cart
        holder.btnAddToKit.setOnClickListener(v -> {
            int qtyToAdd = itemQty[0];
            Toast.makeText(context, "✓ " + qtyToAdd + "x " + product.getName() + " added to Cart!", Toast.LENGTH_SHORT).show();

            // Save in local SharedPreferences cart backup so cart works 100% offline & instant
            try {
                android.content.SharedPreferences sp = context.getSharedPreferences("cyclecare_local_cart", android.content.Context.MODE_PRIVATE);
                int existing = sp.getInt("qty_" + product.getId(), 0);
                sp.edit()
                    .putInt("qty_" + product.getId(), existing + qtyToAdd)
                    .putString("name_" + product.getId(), product.getName())
                    .putFloat("price_" + product.getId(), (float) product.getActivePrice())
                    .putString("img_" + product.getId(), product.getImageUrl() != null ? product.getImageUrl() : "")
                    .apply();
            } catch (Exception ignored) {}

            if (product.getId() != null) {
                java.util.Map<String, Object> cartItem = new java.util.HashMap<>();
                cartItem.put("product_id", product.getId());
                cartItem.put("quantity", qtyToAdd);
                com.cyclecare.api.ApiClient.getApiService(context).addToCart(cartItem).enqueue(new retrofit2.Callback<java.util.Map<String, Object>>() {
                    @Override
                    public void onResponse(retrofit2.Call<java.util.Map<String, Object>> call, retrofit2.Response<java.util.Map<String, Object>> response) {
                        if (cartUpdatedListener != null) {
                            cartUpdatedListener.onCartUpdated();
                        }
                    }
                    @Override
                    public void onFailure(retrofit2.Call<java.util.Map<String, Object>> call, Throwable t) {
                        if (cartUpdatedListener != null) {
                            cartUpdatedListener.onCartUpdated();
                        }
                    }
                });
            }
        });
    }

    @Override
    public int getItemCount() {
        return productList != null ? productList.size() : 0;
    }

    static class ProductViewHolder extends RecyclerView.ViewHolder {
        ImageView ivProductIcon;
        ImageButton btnWishlist;
        TextView tvBrand, tvRating, tvName, tvPrice, tvMrp, tvCategoryTag, tvStockStatus;
        TextView btnCardQtyMinus, tvCardQty, btnCardQtyPlus;
        Button btnAddToKit;

        public ProductViewHolder(@NonNull View itemView) {
            super(itemView);
            ivProductIcon = itemView.findViewById(R.id.iv_product_icon);
            btnWishlist = itemView.findViewById(R.id.btn_wishlist);
            tvBrand = itemView.findViewById(R.id.tv_product_brand);
            tvRating = itemView.findViewById(R.id.tv_rating);
            tvName = itemView.findViewById(R.id.tv_product_name);
            tvPrice = itemView.findViewById(R.id.tv_product_price);
            tvMrp = itemView.findViewById(R.id.tv_product_mrp);
            tvCategoryTag = itemView.findViewById(R.id.tv_category_tag);
            tvStockStatus = itemView.findViewById(R.id.tv_stock_status);
            btnCardQtyMinus = itemView.findViewById(R.id.btn_card_qty_minus);
            tvCardQty = itemView.findViewById(R.id.tv_card_qty);
            btnCardQtyPlus = itemView.findViewById(R.id.btn_card_qty_plus);
            btnAddToKit = itemView.findViewById(R.id.btn_add_to_kit);
        }
    }
}
