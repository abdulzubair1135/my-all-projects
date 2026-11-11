package com.cyclecare.store;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.cyclecare.R;
import com.cyclecare.models.CartItem;
import com.cyclecare.utils.ImageLoader;

import java.util.ArrayList;
import java.util.List;

public class CartAdapter extends RecyclerView.Adapter<CartAdapter.CartViewHolder> {

    public interface OnCartItemInteractionListener {
        void onQuantityChanged(CartItem item, int newQuantity);
        void onItemRemoved(CartItem item);
    }

    private final Context context;
    private final List<CartItem> items = new ArrayList<>();
    private final OnCartItemInteractionListener listener;

    public CartAdapter(Context context, OnCartItemInteractionListener listener) {
        this.context = context;
        this.listener = listener;
    }

    public void setItems(List<CartItem> newItems) {
        this.items.clear();
        if (newItems != null) {
            this.items.addAll(newItems);
        }
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public CartViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_cart, parent, false);
        return new CartViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull CartViewHolder holder, int position) {
        CartItem item = items.get(position);

        holder.tvItemName.setText(item.getProductName());
        holder.tvUnitPrice.setText("₹" + (int) item.getUnitPrice());
        holder.tvQuantity.setText(String.valueOf(item.getQuantity()));
        holder.tvItemTotal.setText("₹" + (int) (item.getUnitPrice() * item.getQuantity()));

        if (item.getImageUrl() != null && !item.getImageUrl().trim().isEmpty()) {
            ImageLoader.getInstance().loadImage(item.getImageUrl(), holder.ivThumbnail, R.drawable.ic_nav_store_3d);
        } else {
            holder.ivThumbnail.setImageResource(R.drawable.ic_nav_store_3d);
        }

        holder.btnMinus.setOnClickListener(v -> {
            if (item.getQuantity() > 1) {
                int newQty = item.getQuantity() - 1;
                item.setQuantity(newQty);
                holder.tvQuantity.setText(String.valueOf(newQty));
                holder.tvItemTotal.setText("₹" + (int) (item.getUnitPrice() * newQty));
                if (listener != null) listener.onQuantityChanged(item, newQty);
            }
        });

        holder.btnPlus.setOnClickListener(v -> {
            int maxStock = item.getStock() > 0 ? item.getStock() : 99;
            if (item.getQuantity() < maxStock) {
                int newQty = item.getQuantity() + 1;
                item.setQuantity(newQty);
                holder.tvQuantity.setText(String.valueOf(newQty));
                holder.tvItemTotal.setText("₹" + (int) (item.getUnitPrice() * newQty));
                if (listener != null) listener.onQuantityChanged(item, newQty);
            }
        });

        holder.btnRemove.setOnClickListener(v -> {
            if (listener != null) listener.onItemRemoved(item);
        });
    }

    @Override
    public int getItemCount() {
        return items.size();
    }

    static class CartViewHolder extends RecyclerView.ViewHolder {
        ImageView ivThumbnail;
        TextView tvItemName, tvUnitPrice, tvQuantity, tvItemTotal;
        TextView btnMinus, btnPlus;
        ImageButton btnRemove;

        public CartViewHolder(@NonNull View itemView) {
            super(itemView);
            ivThumbnail = itemView.findViewById(R.id.iv_cart_item_image);
            tvItemName = itemView.findViewById(R.id.tv_cart_item_name);
            tvUnitPrice = itemView.findViewById(R.id.tv_cart_item_unit_price);
            tvQuantity = itemView.findViewById(R.id.tv_cart_item_qty);
            tvItemTotal = itemView.findViewById(R.id.tv_cart_item_total);
            btnMinus = itemView.findViewById(R.id.btn_qty_minus);
            btnPlus = itemView.findViewById(R.id.btn_qty_plus);
            btnRemove = itemView.findViewById(R.id.btn_remove_item);
        }
    }
}
