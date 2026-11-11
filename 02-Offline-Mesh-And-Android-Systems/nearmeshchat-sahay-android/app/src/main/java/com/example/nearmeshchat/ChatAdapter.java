package com.example.nearmeshchat;

import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class ChatAdapter extends RecyclerView.Adapter<ChatAdapter.ChatViewHolder> {

    private final List<ChatMessageModel> messages;
    private final String myId;
    private final SimpleDateFormat timeFormat = new SimpleDateFormat("hh:mm a", Locale.getDefault());

    public ChatAdapter(List<ChatMessageModel> messages, String myId) {
        this.messages = messages;
        this.myId = myId;
    }

    @NonNull
    @Override
    public ChatViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_chat_bubble, parent, false);
        return new ChatViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ChatViewHolder holder, int position) {
        ChatMessageModel msg = messages.get(position);
        holder.tvText.setText(msg.content);

        String timeStr = timeFormat.format(new Date(msg.timestamp));
        boolean isMe = msg.sender.equals(myId);

        if (isMe) {
            holder.tvSender.setText("You (Local Node)");
            holder.tvInitial.setText("Y");
            holder.tvMeta.setText(timeStr + " • Direct Node");
            holder.tvTag.setText("Verified");
            holder.tvTag.setTextColor(Color.parseColor("#16A34A"));
            holder.tvTag.setBackgroundColor(Color.parseColor("#F0FDF4"));

            holder.tvEyeStatus.setVisibility(View.VISIBLE);
            if ("PENDING".equals(msg.status)) {
                holder.tvEyeStatus.setText("⏳ Outbox");
            } else if ("DELIVERED".equals(msg.status)) {
                holder.tvEyeStatus.setText("✓ Relayed");
            } else {
                holder.tvEyeStatus.setText("✓✓ Synced");
            }
        } else {
            String senderName = msg.sender;
            if (senderName.length() > 10) {
                senderName = "Peer-" + senderName.substring(0, 6);
            }
            holder.tvSender.setText(senderName);
            holder.tvInitial.setText(senderName.substring(0, 1).toUpperCase());
            holder.tvMeta.setText(timeStr + " • 1.2 km nearby");

            if (msg.content.toLowerCase().contains("water") || msg.content.toLowerCase().contains("flood")) {
                holder.tvTag.setText("Flood");
                holder.tvTag.setTextColor(Color.parseColor("#2563EB"));
                holder.tvTag.setBackgroundColor(Color.parseColor("#EFF6FF"));
            } else if (msg.content.toLowerCase().contains("medic") || msg.content.toLowerCase().contains("doctor")) {
                holder.tvTag.setText("Medical Help");
                holder.tvTag.setTextColor(Color.parseColor("#DC2626"));
                holder.tvTag.setBackgroundColor(Color.parseColor("#FEF2F2"));
            } else if (msg.content.toLowerCase().contains("shelter") || msg.content.toLowerCase().contains("camp")) {
                holder.tvTag.setText("Shelter");
                holder.tvTag.setTextColor(Color.parseColor("#D97706"));
                holder.tvTag.setBackgroundColor(Color.parseColor("#FFFBEB"));
            } else {
                holder.tvTag.setText("Community");
                holder.tvTag.setTextColor(Color.parseColor("#4B5563"));
                holder.tvTag.setBackgroundColor(Color.parseColor("#F3F4F6"));
            }

            holder.tvEyeStatus.setVisibility(View.GONE);
        }

        holder.tvLikes.setText(" " + ((position * 7 + 3) % 24));
    }

    @Override
    public int getItemCount() {
        return messages.size();
    }

    public static class ChatViewHolder extends RecyclerView.ViewHolder {
        LinearLayout container, bubble;
        TextView tvText, tvTime, tvEyeStatus, tvInitial, tvSender, tvMeta, tvTag, tvLikes;

        public ChatViewHolder(@NonNull View itemView) {
            super(itemView);
            container = itemView.findViewById(R.id.layoutBubbleContainer);
            bubble = itemView.findViewById(R.id.bubbleCard);
            tvText = itemView.findViewById(R.id.tvBubbleText);
            tvTime = itemView.findViewById(R.id.tvBubbleTime);
            tvEyeStatus = itemView.findViewById(R.id.tvEyeStatus);
            tvInitial = itemView.findViewById(R.id.tvBubbleAvatarInitial);
            tvSender = itemView.findViewById(R.id.tvBubbleSender);
            tvMeta = itemView.findViewById(R.id.tvBubbleMeta);
            tvTag = itemView.findViewById(R.id.tvBubbleTag);
            tvLikes = itemView.findViewById(R.id.tvBubbleLikes);
        }
    }
}
