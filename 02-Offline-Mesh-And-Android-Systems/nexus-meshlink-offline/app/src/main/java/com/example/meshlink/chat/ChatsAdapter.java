package com.example.meshlink.chat;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.meshlink.R;
import com.example.meshlink.data.ContactModel;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class ChatsAdapter extends RecyclerView.Adapter<ChatsAdapter.ChatViewHolder> {

    public interface OnChatClickListener {
        void onChatClicked(ContactModel contact);
    }

    private final Context context;
    private final List<ContactModel> masterList;
    private final List<ContactModel> filteredList = new ArrayList<>();
    private final OnChatClickListener listener;
    private final SimpleDateFormat timeFormat = new SimpleDateFormat("hh:mm a", Locale.getDefault());
    private String currentFilterQuery = "";

    public ChatsAdapter(Context context, List<ContactModel> contactList, OnChatClickListener listener) {
        this.context = context;
        this.masterList = contactList;
        this.listener = listener;
        filter("");
    }

    public void filter(String query) {
        currentFilterQuery = query == null ? "" : query.trim().toLowerCase();
        filteredList.clear();
        if (currentFilterQuery.isEmpty()) {
            filteredList.addAll(masterList);
        } else {
            for (ContactModel c : masterList) {
                boolean nameMatch = c.displayName != null && c.displayName.toLowerCase().contains(currentFilterQuery);
                boolean msgMatch = c.lastMessage != null && c.lastMessage.toLowerCase().contains(currentFilterQuery);
                if (nameMatch || msgMatch) {
                    filteredList.add(c);
                }
            }
        }
        notifyDataSetChanged();
    }

    public void updateData() {
        filter(currentFilterQuery);
    }

    @NonNull
    @Override
    public ChatViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(context).inflate(R.layout.item_chat_list, parent, false);
        return new ChatViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull ChatViewHolder holder, int position) {
        ContactModel c = filteredList.get(position);
        holder.tvContactName.setText(c.displayName);
        holder.tvLastMessage.setText(c.lastMessage);
        String initial = (c.displayName != null && !c.displayName.trim().isEmpty())
                ? c.displayName.trim().substring(0, 1).toUpperCase()
                : "U";
        holder.tvAvatarEmoji.setText(initial);

        android.graphics.Bitmap peerPic = com.example.meshlink.mesh.MeshCoordinator.getInstance(context).getPeerAvatarBitmap(c.displayName);
        if (peerPic == null && c.peerId != null) {
            peerPic = com.example.meshlink.mesh.MeshCoordinator.getInstance(context).getPeerAvatarBitmap(c.peerId);
        }

        if (peerPic != null && holder.ivAvatarPic != null) {
            holder.ivAvatarPic.setImageBitmap(com.example.meshlink.data.ImageUtils.getCircularBitmap(peerPic));
            holder.ivAvatarPic.setVisibility(View.VISIBLE);
            if (holder.tvAvatarEmoji != null) holder.tvAvatarEmoji.setVisibility(View.GONE);
        } else if (holder.ivAvatarPic != null) {
            holder.ivAvatarPic.setVisibility(View.GONE);
            if (holder.tvAvatarEmoji != null) holder.tvAvatarEmoji.setVisibility(View.VISIBLE);
        }

        if (c.lastTimestamp > 0) {
            holder.tvTimestamp.setText(timeFormat.format(new Date(c.lastTimestamp)));
        } else {
            holder.tvTimestamp.setText("");
        }

        holder.dotOnline.setVisibility(c.isOnline ? View.VISIBLE : View.GONE);

        if (c.transportType != null && !c.transportType.isEmpty()) {
            holder.tvTransportBadge.setVisibility(View.VISIBLE);
            holder.tvTransportBadge.setText("WIFI_DIRECT".equals(c.transportType) ? "WiFi Direct" : "BLE Mesh");
        } else {
            holder.tvTransportBadge.setVisibility(View.GONE);
        }

        if (c.unreadCount > 0) {
            holder.tvUnreadBadge.setVisibility(View.VISIBLE);
            holder.tvUnreadBadge.setText(String.valueOf(c.unreadCount));
        } else {
            holder.tvUnreadBadge.setVisibility(View.GONE);
        }

        holder.itemView.setOnClickListener(v -> {
            if (listener != null) listener.onChatClicked(c);
        });
    }

    @Override
    public int getItemCount() {
        return filteredList.size();
    }

    static class ChatViewHolder extends RecyclerView.ViewHolder {
        TextView tvContactName, tvLastMessage, tvTimestamp, tvAvatarEmoji, tvTransportBadge, tvUnreadBadge;
        android.widget.ImageView ivAvatarPic;
        View dotOnline;

        public ChatViewHolder(@NonNull View itemView) {
            super(itemView);
            tvContactName = itemView.findViewById(R.id.tvContactName);
            tvLastMessage = itemView.findViewById(R.id.tvLastMessage);
            tvTimestamp = itemView.findViewById(R.id.tvTimestamp);
            tvAvatarEmoji = itemView.findViewById(R.id.tvAvatarEmoji);
            ivAvatarPic = itemView.findViewById(R.id.ivAvatarPic);
            tvTransportBadge = itemView.findViewById(R.id.tvTransportBadge);
            tvUnreadBadge = itemView.findViewById(R.id.tvUnreadBadge);
            dotOnline = itemView.findViewById(R.id.dotOnline);
        }
    }
}
