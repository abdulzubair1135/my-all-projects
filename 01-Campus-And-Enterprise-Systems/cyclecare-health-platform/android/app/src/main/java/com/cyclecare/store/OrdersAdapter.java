package com.cyclecare.store;

import android.content.Context;
import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.cyclecare.R;
import com.cyclecare.models.Order;
import com.cyclecare.partner.OrderTrackingActivity;

import java.util.ArrayList;
import java.util.List;

public class OrdersAdapter extends RecyclerView.Adapter<OrdersAdapter.OrderViewHolder> {

    private final Context context;
    private final List<Order> orders = new ArrayList<>();

    public OrdersAdapter(Context context) {
        this.context = context;
    }

    public void setOrders(List<Order> newOrders) {
        this.orders.clear();
        if (newOrders != null) {
            this.orders.addAll(newOrders);
        }
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public OrderViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_order, parent, false);
        return new OrderViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull OrderViewHolder holder, int position) {
        Order order = orders.get(position);

        holder.tvOrderNumber.setText("#" + order.getOrderNumber());
        String status = order.getDeliveryStatus();
        if ("DELIVERED".equalsIgnoreCase(status)) {
            holder.tvStatusBadge.setText("✓ DELIVERED");
            holder.tvStatusBadge.setTextColor(0xFF15803D);
            holder.tvStatusBadge.setBackgroundResource(R.drawable.bg_neu_circle_btn);
        } else if ("IN_TRANSIT".equalsIgnoreCase(status) || "OUT_FOR_DELIVERY".equalsIgnoreCase(status)) {
            holder.tvStatusBadge.setText("🚴 OUT FOR DELIVERY");
            holder.tvStatusBadge.setTextColor(0xFFD81B60);
            holder.tvStatusBadge.setBackgroundResource(R.drawable.bg_neu_circle_btn_active);
        } else {
            holder.tvStatusBadge.setText("PROCESSING");
            holder.tvStatusBadge.setTextColor(0xFFD97706);
            holder.tvStatusBadge.setBackgroundResource(R.drawable.bg_neu_circle_btn);
        }

        holder.tvDate.setText(order.getCreatedAt() != null ? order.getCreatedAt().substring(0, 10) : "Recent Order");
        int itemCount = order.getItems() != null ? order.getItems().size() : 1;
        holder.tvSummary.setText(itemCount + (itemCount == 1 ? " Care Item" : " Care Items"));
        holder.tvTotal.setText("₹" + (int) order.getTotalAmount());

        holder.btnTrack.setOnClickListener(v -> {
            Intent intent = new Intent(context, OrderTrackingActivity.class);
            intent.putExtra("order_id", order.getId());
            context.startActivity(intent);
        });

        holder.itemView.setOnClickListener(v -> {
            Intent intent = new Intent(context, OrderDetailActivity.class);
            intent.putExtra("order_id", order.getId());
            intent.putExtra("order_data", order);
            context.startActivity(intent);
        });
    }

    @Override
    public int getItemCount() {
        return orders.size();
    }

    static class OrderViewHolder extends RecyclerView.ViewHolder {
        TextView tvOrderNumber, tvStatusBadge, tvDate, tvSummary, tvTotal;
        Button btnTrack;

        public OrderViewHolder(@NonNull View itemView) {
            super(itemView);
            tvOrderNumber = itemView.findViewById(R.id.tv_order_number);
            tvStatusBadge = itemView.findViewById(R.id.tv_order_status_badge);
            tvDate = itemView.findViewById(R.id.tv_order_date);
            tvSummary = itemView.findViewById(R.id.tv_order_items_summary);
            tvTotal = itemView.findViewById(R.id.tv_order_total);
            btnTrack = itemView.findViewById(R.id.btn_track_order);
        }
    }
}
