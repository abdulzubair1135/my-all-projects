package com.cyclecare.chat;

import android.content.Context;
import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.cardview.widget.CardView;
import androidx.recyclerview.widget.RecyclerView;

import com.cyclecare.R;
import com.cyclecare.models.CircleContact;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class CircleConversationsAdapter extends RecyclerView.Adapter<CircleConversationsAdapter.ViewHolder> {

    public interface OnContactClickListener {
        void onContactClick(CircleContact contact);
    }

    public interface OnContactLongClickListener {
        void onContactLongClick(CircleContact contact, int position);
    }

    private final Context context;
    private final List<CircleContact> contacts;
    private final OnContactClickListener listener;
    private OnContactLongClickListener longClickListener;

    public CircleConversationsAdapter(Context context, List<CircleContact> contacts, OnContactClickListener listener) {
        this.context = context;
        this.contacts = contacts;
        this.listener = listener;
    }

    public void setOnContactLongClickListener(OnContactLongClickListener longClickListener) {
        this.longClickListener = longClickListener;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_circle_conversation, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        CircleContact contact = contacts.get(position);

        String rawName = contact.getDisplayName();
        String name = rawName != null ? rawName.replaceAll("(?i)\\s*\\((Husband|Girl|Partner|User|Male|Female)\\)", "").trim() : "Partner";
        String rel = contact.getRelationship() != null ? contact.getRelationship() : "Partner";

        String savedTag = context.getSharedPreferences("cyclecare_contact_tags", Context.MODE_PRIVATE)
                .getString("tag_" + contact.getConnectionId(), null);
        if (savedTag == null && contact.getUserId() != null) {
            savedTag = context.getSharedPreferences("cyclecare_contact_tags", Context.MODE_PRIVATE)
                    .getString("tag_" + contact.getUserId(), null);
        }
        if (savedTag == null && name != null) {
            savedTag = context.getSharedPreferences("cyclecare_contact_tags", Context.MODE_PRIVATE)
                    .getString("tag_" + name.toLowerCase().trim(), null);
        }
        if (savedTag != null) {
            rel = savedTag;
        }

        holder.tvName.setText(name);

        // Customize badge & avatar based on role/relationship
        boolean isAdmin = name.toLowerCase().contains("admin") || rel.toLowerCase().contains("admin");
        boolean isHusband = rel.toLowerCase().contains("husband");
        boolean isWife = rel.toLowerCase().contains("wife");
        boolean isDoctor = rel.toLowerCase().contains("doctor");

        if (isAdmin) {
            holder.tvBadge.setText("Admin (Help) 🛡️");
            holder.tvBadge.setTextColor(Color.parseColor("#4338CA"));
            holder.tvBadge.setBackgroundColor(Color.parseColor("#EEF2FF"));
            holder.cardAvatar.setCardBackgroundColor(Color.parseColor("#E0E7FF"));
            holder.tvAvatarLetter.setText("🛡️");
            holder.tvAvatarLetter.setTextSize(16);
        } else if (isHusband) {
            holder.tvBadge.setText(rel.contains("❤️") ? rel : rel + " ❤️");
            holder.tvBadge.setTextColor(Color.parseColor("#E91E63"));
            holder.tvBadge.setBackgroundColor(Color.parseColor("#FCE4EC"));
            holder.cardAvatar.setCardBackgroundColor(Color.parseColor("#FCE4EC"));
            holder.tvAvatarLetter.setText(name.isEmpty() ? "A" : name.substring(0, 1).toUpperCase());
            holder.tvAvatarLetter.setTextColor(Color.parseColor("#E91E63"));
            holder.tvAvatarLetter.setTextSize(20);
        } else if (isWife) {
            holder.tvBadge.setText(rel.contains("🌸") ? rel : rel + " 🌸");
            holder.tvBadge.setTextColor(Color.parseColor("#D946EF"));
            holder.tvBadge.setBackgroundColor(Color.parseColor("#FAE8FF"));
            holder.cardAvatar.setCardBackgroundColor(Color.parseColor("#FAE8FF"));
            holder.tvAvatarLetter.setText(name.isEmpty() ? "W" : name.substring(0, 1).toUpperCase());
            holder.tvAvatarLetter.setTextColor(Color.parseColor("#D946EF"));
            holder.tvAvatarLetter.setTextSize(20);
        } else if (isDoctor) {
            holder.tvBadge.setText(rel.contains("🩺") ? rel : rel + " 🩺");
            holder.tvBadge.setTextColor(Color.parseColor("#0284C7"));
            holder.tvBadge.setBackgroundColor(Color.parseColor("#E0F2FE"));
            holder.cardAvatar.setCardBackgroundColor(Color.parseColor("#E0F2FE"));
            holder.tvAvatarLetter.setText("🩺");
            holder.tvAvatarLetter.setTextSize(18);
        } else {
            holder.tvBadge.setText(rel.matches(".*[\\uD83C-\\uDBFF\\uDC00-\\uDFFF]+.*") ? rel : rel + " ✨");
            holder.tvBadge.setTextColor(Color.parseColor("#0D9488"));
            holder.tvBadge.setBackgroundColor(Color.parseColor("#CCFBF1"));
            holder.cardAvatar.setCardBackgroundColor(Color.parseColor("#F3E8FF"));
            holder.tvAvatarLetter.setText(name.isEmpty() ? "U" : name.substring(0, 1).toUpperCase());
            holder.tvAvatarLetter.setTextColor(Color.parseColor("#7C3AED"));
            holder.tvAvatarLetter.setTextSize(20);
        }

        // Snippet prefix
        String lastMsg = contact.getLastMessage();
        String type = contact.getLastMessageType();
        if ("CARE_REQUEST".equalsIgnoreCase(type)) {
            holder.tvLastMessage.setText("🌸 Care Request: " + lastMsg);
        } else if ("CARE_ITEM_SENT".equalsIgnoreCase(type)) {
            holder.tvLastMessage.setText("🎁 Care Package: " + lastMsg);
        } else {
            holder.tvLastMessage.setText(lastMsg.isEmpty() ? "Start a conversation..." : lastMsg);
        }

        // Time format
        holder.tvTime.setText(formatTime(contact.getLastMessageTime()));

        // Unread badge
        if (contact.getUnreadCount() > 0) {
            holder.tvUnreadBadge.setVisibility(View.VISIBLE);
            holder.tvUnreadBadge.setText(String.valueOf(contact.getUnreadCount()));
        } else {
            holder.tvUnreadBadge.setVisibility(View.GONE);
        }

        holder.itemView.setOnClickListener(v -> {
            if (listener != null) {
                listener.onContactClick(contact);
            }
        });

        holder.itemView.setOnLongClickListener(v -> {
            if (longClickListener != null) {
                longClickListener.onContactLongClick(contact, holder.getAdapterPosition());
                return true;
            }
            return false;
        });
    }

    @Override
    public int getItemCount() {
        return contacts != null ? contacts.size() : 0;
    }

    private String formatTime(String rawTime) {
        if (rawTime == null) return "Now";
        try {
            SimpleDateFormat parser = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault());
            Date d = parser.parse(rawTime.substring(0, Math.min(19, rawTime.length())));
            SimpleDateFormat formatter = new SimpleDateFormat("hh:mm a", Locale.getDefault());
            return d != null ? formatter.format(d) : "Now";
        } catch (Exception e) {
            return "Now";
        }
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        CardView cardAvatar;
        TextView tvAvatarLetter, tvName, tvBadge, tvLastMessage, tvTime, tvUnreadBadge;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            cardAvatar = itemView.findViewById(R.id.card_avatar);
            tvAvatarLetter = itemView.findViewById(R.id.tv_avatar_letter);
            tvName = itemView.findViewById(R.id.tv_conv_name);
            tvBadge = itemView.findViewById(R.id.tv_conv_badge);
            tvLastMessage = itemView.findViewById(R.id.tv_conv_last_message);
            tvTime = itemView.findViewById(R.id.tv_conv_time);
            tvUnreadBadge = itemView.findViewById(R.id.tv_conv_unread_badge);
        }
    }
}
