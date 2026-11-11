package com.cyclecare.chat;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.cyclecare.R;
import com.cyclecare.models.QuickCareItem;
import com.cyclecare.utils.ImageLoader;

import java.util.List;

public class CareItemSheetAdapter extends RecyclerView.Adapter<CareItemSheetAdapter.ViewHolder> {

    public interface OnCareActionListener {
        void onRequest(QuickCareItem item);
        void onSend(QuickCareItem item);
    }

    private final Context context;
    private final List<QuickCareItem> itemList;
    private final OnCareActionListener listener;

    public CareItemSheetAdapter(Context context, List<QuickCareItem> itemList, OnCareActionListener listener) {
        this.context = context;
        this.itemList = itemList;
        this.listener = listener;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_dialog_care_product, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        QuickCareItem item = itemList.get(position);
        holder.tvName.setText(item.getName());
        holder.tvDesc.setText(item.getDescription());
        holder.tvPrice.setText("₹ " + item.getPrice());

        if (item.getImageUrl() != null && !item.getImageUrl().isEmpty()) {
            ImageLoader.getInstance().loadImage(item.getImageUrl(), holder.ivImg, R.drawable.ic_nav_store_3d);
        } else {
            holder.ivImg.setImageResource(R.drawable.ic_nav_store_3d);
        }

        holder.btnRequest.setOnClickListener(v -> {
            if (listener != null) listener.onRequest(item);
        });

        holder.btnSend.setOnClickListener(v -> {
            if (listener != null) listener.onSend(item);
        });
    }

    @Override
    public int getItemCount() {
        return itemList != null ? itemList.size() : 0;
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        ImageView ivImg;
        TextView tvName, tvDesc, tvPrice;
        Button btnRequest, btnSend;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            ivImg = itemView.findViewById(R.id.iv_sheet_item_img);
            tvName = itemView.findViewById(R.id.tv_sheet_item_name);
            tvDesc = itemView.findViewById(R.id.tv_sheet_item_desc);
            tvPrice = itemView.findViewById(R.id.tv_sheet_item_price);
            btnRequest = itemView.findViewById(R.id.btn_sheet_request);
            btnSend = itemView.findViewById(R.id.btn_sheet_send);
        }
    }
}
