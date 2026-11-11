package com.projectflow.android.ui.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.projectflow.android.R;
import com.projectflow.android.data.remote.model.DtoModels.ChatMessageDto;

import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class ChatAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    public interface OnReactionClickListener {
        void onReaction(ChatMessageDto message, String emoji);
    }

    private static final int VIEW_TYPE_INCOMING = 1;
    private static final int VIEW_TYPE_OUTGOING = 2;

    private final List<ChatMessageDto> messages = new ArrayList<>();
    private final String currentUserId;
    private final String currentUserName;
    private final String currentUserEmail;
    private OnReactionClickListener reactionClickListener;

    public ChatAdapter(String currentUserId, String currentUserName, String currentUserEmail) {
        this.currentUserId = currentUserId != null ? currentUserId : "";
        this.currentUserName = currentUserName != null ? currentUserName : "";
        this.currentUserEmail = currentUserEmail != null ? currentUserEmail : "";
    }

    public ChatAdapter(String currentUserId) {
        this(currentUserId, currentUserId, "");
    }

    public void setOnReactionClickListener(OnReactionClickListener listener) {
        this.reactionClickListener = listener;
    }

    public void setMessages(List<ChatMessageDto> newMessages) {
        this.messages.clear();
        if (newMessages != null) {
            this.messages.addAll(newMessages);
        }
        notifyDataSetChanged();
    }

    public boolean setMessagesSilently(List<ChatMessageDto> newMessages) {
        if (newMessages == null) return false;
        boolean countChanged = (newMessages.size() != this.messages.size());
        if (countChanged) {
            this.messages.clear();
            this.messages.addAll(newMessages);
            notifyDataSetChanged();
            return true;
        }
        return false;
    }

    public void addMessage(ChatMessageDto message) {
        if (message != null) {
            this.messages.add(message);
            notifyItemInserted(this.messages.size() - 1);
        }
    }

    public void updateMessage(ChatMessageDto updated) {
        if (updated == null) return;
        for (int i = 0; i < messages.size(); i++) {
            if (updated.id != null && updated.id.equals(messages.get(i).id)) {
                messages.set(i, updated);
                notifyItemChanged(i);
                break;
            }
        }
    }

    private boolean isOutgoing(ChatMessageDto msg) {
        if (msg == null) return false;
        if ("You".equalsIgnoreCase(msg.senderName)) return true;
        if (currentUserName.length() > 0 && currentUserName.equalsIgnoreCase(msg.senderName)) return true;
        if (currentUserEmail.length() > 0 && currentUserEmail.equalsIgnoreCase(msg.senderEmail)) return true;
        if (currentUserId.length() > 0 && currentUserId.equalsIgnoreCase(msg.senderId)) return true;
        return false;
    }

    @Override
    public int getItemViewType(int position) {
        ChatMessageDto msg = messages.get(position);
        if (isOutgoing(msg)) {
            return VIEW_TYPE_OUTGOING;
        }
        return VIEW_TYPE_INCOMING;
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        if (viewType == VIEW_TYPE_OUTGOING) {
            View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_chat_outgoing, parent, false);
            return new OutgoingViewHolder(v);
        } else {
            View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_chat_incoming, parent, false);
            return new IncomingViewHolder(v);
        }
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        ChatMessageDto msg = messages.get(position);
        String timeStr = formatTime(msg.createdAt);
        Map<String, Integer> reactions = msg.reactions;

        int likeCount = reactions != null && reactions.containsKey("👍") ? reactions.get("👍") : 0;
        int rocketCount = reactions != null && reactions.containsKey("🚀") ? reactions.get("🚀") : 0;
        int fireCount = reactions != null && reactions.containsKey("🔥") ? reactions.get("🔥") : 0;
        int loveCount = reactions != null && reactions.containsKey("❤️") ? reactions.get("❤️") : 0;

        if (holder instanceof OutgoingViewHolder) {
            OutgoingViewHolder vh = (OutgoingViewHolder) holder;
            vh.tvContent.setText(msg.content);
            if (vh.tvHeaderTimestamp != null) vh.tvHeaderTimestamp.setText(timeStr);
            if (vh.tvTimestamp != null) vh.tvTimestamp.setText(timeStr);

            boolean isSeen = msg.seen || (msg.seenBy != null && msg.seenBy.size() > 1) || "seen".equalsIgnoreCase(msg.status);
            int seenBlueColor = android.graphics.Color.parseColor("#38BDF8"); // WhatsApp / Sky Blue
            int unseenGreyColor = androidx.core.content.ContextCompat.getColor(vh.itemView.getContext(), R.color.text_muted);
            int bubbleUnseenColor = androidx.core.content.ContextCompat.getColor(vh.itemView.getContext(), R.color.secondary_sand);

            if (vh.tvMessageTick != null) {
                if (isSeen) {
                    vh.tvMessageTick.setText("✓✓");
                    vh.tvMessageTick.setTextColor(seenBlueColor);
                } else {
                    vh.tvMessageTick.setText("✓");
                    vh.tvMessageTick.setTextColor(unseenGreyColor);
                }
            }

            if (vh.tvBubbleTick != null) {
                if (isSeen) {
                    vh.tvBubbleTick.setText("✓✓");
                    vh.tvBubbleTick.setTextColor(seenBlueColor);
                } else {
                    vh.tvBubbleTick.setText("✓");
                    vh.tvBubbleTick.setTextColor(bubbleUnseenColor);
                }
            }

            vh.btnReactLike.setText("👍 " + likeCount);
            vh.btnReactRocket.setText("🚀 " + rocketCount);
            vh.btnReactFire.setText("🔥 " + fireCount);

            bindReactionClick(vh.btnReactLike, msg, "👍");
            bindReactionClick(vh.btnReactRocket, msg, "🚀");
            bindReactionClick(vh.btnReactFire, msg, "🔥");

        } else if (holder instanceof IncomingViewHolder) {
            IncomingViewHolder vh = (IncomingViewHolder) holder;
            String sender = (msg.senderName != null && !msg.senderName.isEmpty()) ? msg.senderName : "Colleague";
            vh.tvSender.setText(sender);
            if (vh.tvAvatarInitial != null) {
                vh.tvAvatarInitial.setText(sender.substring(0, 1).toUpperCase());
            }
            if (vh.tvSenderRole != null) {
                vh.tvSenderRole.setText(msg.senderRole != null ? msg.senderRole : "MEMBER");
            }
            if (vh.tvHeaderTimestamp != null) vh.tvHeaderTimestamp.setText(timeStr);
            if (vh.tvTimestamp != null) vh.tvTimestamp.setText(timeStr);
            vh.tvContent.setText(msg.content);

            vh.btnReactLike.setText("👍 " + likeCount);
            vh.btnReactRocket.setText("🚀 " + rocketCount);
            vh.btnReactFire.setText("🔥 " + fireCount);
            if (vh.btnReactLove != null) vh.btnReactLove.setText("❤️ " + loveCount);

            bindReactionClick(vh.btnReactLike, msg, "👍");
            bindReactionClick(vh.btnReactRocket, msg, "🚀");
            bindReactionClick(vh.btnReactFire, msg, "🔥");
            if (vh.btnReactLove != null) bindReactionClick(vh.btnReactLove, msg, "❤️");
        }
    }

    private void bindReactionClick(View btn, ChatMessageDto msg, String emoji) {
        btn.setOnClickListener(v -> {
            v.animate().scaleX(1.25f).scaleY(1.25f).setDuration(120).withEndAction(() -> {
                v.animate().scaleX(1f).scaleY(1f).setDuration(120).start();
            }).start();
            if (reactionClickListener != null) {
                reactionClickListener.onReaction(msg, emoji);
            }
        });
    }

    @Override
    public int getItemCount() {
        return messages.size();
    }

    public static String formatTime(String isoString) {
        if (isoString == null || isoString.trim().isEmpty()) return "Just now";
        try {
            String trimmed = isoString.trim();
            Instant instant;
            if (trimmed.endsWith("Z")) {
                instant = Instant.parse(trimmed);
            } else if (trimmed.contains("+") || (trimmed.length() > 19 && (trimmed.charAt(19) == '-' || trimmed.charAt(19) == '+'))) {
                instant = OffsetDateTime.parse(trimmed).toInstant();
            } else {
                String clean = trimmed.replace(" ", "T");
                if (!clean.endsWith("Z")) clean = clean + "Z";
                instant = Instant.parse(clean);
            }
            ZonedDateTime localTime = instant.atZone(ZoneId.systemDefault());
            DateTimeFormatter dtf = DateTimeFormatter.ofPattern("hh:mm a", Locale.getDefault());
            return localTime.format(dtf);
        } catch (Exception e) {
            try {
                String clean = isoString.replace("T", " ").replace("Z", "");
                if (clean.length() > 19) clean = clean.substring(0, 19);
                java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
                sdf.setTimeZone(java.util.TimeZone.getTimeZone("UTC"));
                java.util.Date d = sdf.parse(clean);
                if (d != null) {
                    java.text.SimpleDateFormat out = new java.text.SimpleDateFormat("hh:mm a", Locale.getDefault());
                    return out.format(d);
                }
            } catch (Exception ignored) {}
            return "Today";
        }
    }

    static class IncomingViewHolder extends RecyclerView.ViewHolder {
        TextView tvSender, tvSenderRole, tvAvatarInitial, tvHeaderTimestamp, tvContent, tvTimestamp;
        TextView btnReactLike, btnReactRocket, btnReactFire, btnReactLove;

        IncomingViewHolder(@NonNull View itemView) {
            super(itemView);
            tvSender = itemView.findViewById(R.id.tvSenderName);
            tvSenderRole = itemView.findViewById(R.id.tvSenderRole);
            tvAvatarInitial = itemView.findViewById(R.id.tvAvatarInitial);
            tvHeaderTimestamp = itemView.findViewById(R.id.tvHeaderTimestamp);
            tvContent = itemView.findViewById(R.id.tvMessageContent);
            tvTimestamp = itemView.findViewById(R.id.tvTimestamp);
            btnReactLike = itemView.findViewById(R.id.btnReactLike);
            btnReactRocket = itemView.findViewById(R.id.btnReactRocket);
            btnReactFire = itemView.findViewById(R.id.btnReactFire);
            btnReactLove = itemView.findViewById(R.id.btnReactLove);
        }
    }

    static class OutgoingViewHolder extends RecyclerView.ViewHolder {
        TextView tvSenderName, tvSenderRole, tvHeaderTimestamp, tvContent, tvTimestamp;
        TextView tvMessageTick, tvBubbleTick;
        TextView btnReactLike, btnReactRocket, btnReactFire;

        OutgoingViewHolder(@NonNull View itemView) {
            super(itemView);
            tvSenderName = itemView.findViewById(R.id.tvSenderName);
            tvSenderRole = itemView.findViewById(R.id.tvSenderRole);
            tvHeaderTimestamp = itemView.findViewById(R.id.tvHeaderTimestamp);
            tvContent = itemView.findViewById(R.id.tvMessageContent);
            tvTimestamp = itemView.findViewById(R.id.tvTimestamp);
            tvMessageTick = itemView.findViewById(R.id.tvMessageTick);
            tvBubbleTick = itemView.findViewById(R.id.tvBubbleTick);
            btnReactLike = itemView.findViewById(R.id.btnReactLike);
            btnReactRocket = itemView.findViewById(R.id.btnReactRocket);
            btnReactFire = itemView.findViewById(R.id.btnReactFire);
        }
    }
}
