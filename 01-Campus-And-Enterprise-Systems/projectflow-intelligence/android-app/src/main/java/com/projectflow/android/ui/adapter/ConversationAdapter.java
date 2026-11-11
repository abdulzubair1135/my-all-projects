package com.projectflow.android.ui.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;
import com.projectflow.android.R;
import com.projectflow.android.data.model.ConversationItem;

import java.util.ArrayList;
import java.util.List;

public class ConversationAdapter extends RecyclerView.Adapter<ConversationAdapter.ViewHolder> {

    public interface OnConversationClickListener {
        void onClick(ConversationItem item);
    }

    private final List<ConversationItem> items = new ArrayList<>();
    private final OnConversationClickListener listener;

    public ConversationAdapter(OnConversationClickListener listener) {
        this.listener = listener;
    }

    public void setItems(List<ConversationItem> newItems) {
        this.items.clear();
        if (newItems != null) {
            this.items.addAll(newItems);
        }
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_conversation, parent, false);
        return new ViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        ConversationItem item = items.get(position);
        holder.tvTitle.setText(item.title);
        holder.tvSnippet.setText(item.snippet != null && !item.snippet.isEmpty() ? item.snippet : "Tap to start conversation");
        holder.tvTime.setText(item.time != null ? item.time : "");

        if (item.type == ConversationItem.Type.GROUP) {
            holder.ivGroupIcon.setVisibility(View.VISIBLE);
            holder.tvInitial.setVisibility(View.GONE);
            holder.viewOnlineDot.setVisibility(View.GONE);
            holder.tvBadge.setText("Group Squad");
            holder.tvBadge.setBackgroundResource(R.drawable.bg_neu_pill);
            holder.tvBadge.setTextColor(ContextCompat.getColor(holder.itemView.getContext(), R.color.primary_earth));
        } else {
            holder.ivGroupIcon.setVisibility(View.GONE);
            holder.tvInitial.setVisibility(View.VISIBLE);
            holder.tvInitial.setText(item.initial != null ? item.initial : "U");
            holder.viewOnlineDot.setVisibility(item.online ? View.VISIBLE : View.GONE);
            holder.tvBadge.setText("1-on-1 Direct");
            holder.tvBadge.setBackgroundResource(R.drawable.bg_badge_success);
            holder.tvBadge.setTextColor(ContextCompat.getColor(holder.itemView.getContext(), R.color.earth_success));
        }

        holder.itemView.setOnClickListener(v -> {
            if (listener != null) listener.onClick(item);
        });
    }

    @Override
    public int getItemCount() {
        return items.size();
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView tvTitle, tvSnippet, tvTime, tvInitial, tvBadge;
        ImageView ivGroupIcon;
        View viewOnlineDot;

        ViewHolder(@NonNull View itemView) {
            super(itemView);
            tvTitle = itemView.findViewById(R.id.tvConversationTitle);
            tvSnippet = itemView.findViewById(R.id.tvConversationSnippet);
            tvTime = itemView.findViewById(R.id.tvConversationTime);
            tvInitial = itemView.findViewById(R.id.tvConversationInitial);
            tvBadge = itemView.findViewById(R.id.tvConversationTypeBadge);
            ivGroupIcon = itemView.findViewById(R.id.ivGroupIcon);
            viewOnlineDot = itemView.findViewById(R.id.viewOnlineDot);
        }
    }
}
