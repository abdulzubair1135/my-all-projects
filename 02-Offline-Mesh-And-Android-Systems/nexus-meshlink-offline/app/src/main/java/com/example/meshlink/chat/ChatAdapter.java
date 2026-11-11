package com.example.meshlink.chat;

import android.content.Context;
import android.content.Intent;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.meshlink.R;
import com.example.meshlink.data.ChatMessageModel;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class ChatAdapter extends RecyclerView.Adapter<ChatAdapter.MessageViewHolder> {

    private final Context context;
    private final List<ChatMessageModel> messages;
    private final String myId;
    private final SimpleDateFormat timeFormat = new SimpleDateFormat("hh:mm a", Locale.getDefault());

    public ChatAdapter(Context context, List<ChatMessageModel> messages, String myId) {
        this.context = context;
        this.messages = messages;
        this.myId = myId;
    }

    @NonNull
    @Override
    public MessageViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(context).inflate(R.layout.item_chat_bubble, parent, false);
        return new MessageViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull MessageViewHolder holder, int position) {
        ChatMessageModel msg = messages.get(position);
        boolean isMe = msg.sender.equals(myId);

        // Align bubble right for sent, left for received, or center for SOS
        LinearLayout.LayoutParams params = (LinearLayout.LayoutParams) holder.llBubbleContainer.getLayoutParams();
        boolean isSos = (msg.content != null && msg.content.contains("EMERGENCY SOS")) || "SOS".equalsIgnoreCase(msg.msgType);

        if (isSos) {
            params.gravity = Gravity.CENTER_HORIZONTAL;
            holder.llBubbleContainer.setBackgroundResource(R.drawable.bg_card_rounded);
            holder.llBubbleContainer.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#FEF2F2")));
            holder.tvBubbleText.setTextColor(Color.parseColor("#991B1B"));
            holder.tvBubbleTime.setTextColor(Color.parseColor("#DC2626"));
            holder.tvBubbleSender.setVisibility(View.VISIBLE);
            holder.tvBubbleSender.setTextColor(Color.parseColor("#EF4444"));
            holder.tvBubbleSender.setText("EMERGENCY SOS BROADCAST");
            holder.tvBubbleTicks.setVisibility(View.GONE);
            holder.tvBubbleRouting.setVisibility(View.VISIBLE);
            holder.tvBubbleRouting.setText("CRITICAL MESH ALERT");
        } else if (isMe) {
            params.gravity = Gravity.END;
            holder.llBubbleContainer.setBackgroundResource(R.drawable.bg_card_rounded);
            holder.llBubbleContainer.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#DCFCE7")));
            holder.tvBubbleText.setTextColor(Color.parseColor("#111827"));
            holder.tvBubbleTime.setTextColor(Color.parseColor("#6B7280"));
            holder.tvBubbleSender.setVisibility(View.GONE);
            holder.tvBubbleTicks.setVisibility(View.VISIBLE);
            holder.tvBubbleTicks.setTextColor(Color.parseColor("#16A34A"));
        } else {
            params.gravity = Gravity.START;
            holder.llBubbleContainer.setBackgroundResource(R.drawable.bg_card_rounded);
            holder.llBubbleContainer.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.parseColor("#FFFFFF")));
            holder.tvBubbleText.setTextColor(Color.parseColor("#111827"));
            holder.tvBubbleTime.setTextColor(Color.parseColor("#6B7280"));
            holder.tvBubbleSender.setVisibility(View.VISIBLE);
            holder.tvBubbleSender.setTextColor(Color.parseColor("#16A34A"));
            holder.tvBubbleSender.setText(msg.sender);
            holder.tvBubbleTicks.setVisibility(View.GONE);
        }
        holder.llBubbleContainer.setLayoutParams(params);

        holder.tvBubbleText.setText(msg.content);
        holder.tvBubbleTime.setText(timeFormat.format(new Date(msg.timestamp)));

        // Routing indicator badge
        if (!isSos) {
            if (msg.routingMode != null && !msg.routingMode.isEmpty()) {
                holder.tvBubbleRouting.setVisibility(View.VISIBLE);
                holder.tvBubbleRouting.setText("WIFI_DIRECT".equals(msg.routingMode) ? "WiFi" : "BLE");
            } else {
                holder.tvBubbleRouting.setVisibility(View.GONE);
            }
        }

        // Image attachment preview
        if (ChatMessageModel.TYPE_IMAGE.equals(msg.msgType) && msg.mediaPath != null && !msg.mediaPath.isEmpty()) {
            File imgFile = new File(msg.mediaPath);
            if (imgFile.exists()) {
                holder.ivBubbleImage.setVisibility(View.VISIBLE);
                holder.ivBubbleImage.setImageBitmap(BitmapFactory.decodeFile(imgFile.getAbsolutePath()));
                holder.ivBubbleImage.setOnClickListener(v -> openMediaFile(imgFile, "image/*"));
            } else {
                holder.ivBubbleImage.setVisibility(View.GONE);
            }
        } else {
            holder.ivBubbleImage.setVisibility(View.GONE);
        }

        // Video attachment preview
        if (ChatMessageModel.TYPE_VIDEO.equals(msg.msgType) && msg.mediaPath != null && !msg.mediaPath.isEmpty()) {
            File vidFile = new File(msg.mediaPath);
            if (vidFile.exists()) {
                holder.flVideoContainer.setVisibility(View.VISIBLE);
                try {
                    android.media.MediaMetadataRetriever retriever = new android.media.MediaMetadataRetriever();
                    retriever.setDataSource(vidFile.getAbsolutePath());
                    android.graphics.Bitmap thumb = retriever.getFrameAtTime();
                    if (thumb != null) {
                        holder.ivBubbleVideoThumb.setImageBitmap(thumb);
                    }
                    retriever.release();
                } catch (Exception ignored) {}

                View.OnClickListener playClick = v -> openMediaFile(vidFile, "video/*");
                holder.flVideoContainer.setOnClickListener(playClick);
                holder.btnPlayVideo.setOnClickListener(playClick);
            } else {
                holder.flVideoContainer.setVisibility(View.GONE);
            }
        } else {
            holder.flVideoContainer.setVisibility(View.GONE);
        }

        // Voice note preview
        if (ChatMessageModel.TYPE_VOICE.equals(msg.msgType)) {
            holder.llVoiceNote.setVisibility(View.VISIBLE);
        } else {
            holder.llVoiceNote.setVisibility(View.GONE);
        }
    }

    private void openMediaFile(File file, String mimeType) {
        try {
            android.net.Uri contentUri = androidx.core.content.FileProvider.getUriForFile(
                    context,
                    context.getPackageName() + ".provider",
                    file
            );
            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setDataAndType(contentUri, mimeType);
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
        } catch (Exception e) {
            android.widget.Toast.makeText(context, "Cannot open file: " + e.getMessage(), android.widget.Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    public int getItemCount() {
        return messages.size();
    }

    static class MessageViewHolder extends RecyclerView.ViewHolder {
        LinearLayout llBubbleContainer, llVoiceNote;
        FrameLayout flVideoContainer;
        TextView tvBubbleSender, tvBubbleText, tvBubbleTime, tvBubbleRouting, tvBubbleTicks;
        ImageView ivBubbleImage, ivBubbleVideoThumb, btnPlayVideo;

        public MessageViewHolder(@NonNull View itemView) {
            super(itemView);
            llBubbleContainer = itemView.findViewById(R.id.llBubbleContainer);
            llVoiceNote = itemView.findViewById(R.id.llVoiceNote);
            flVideoContainer = itemView.findViewById(R.id.flVideoContainer);
            tvBubbleSender = itemView.findViewById(R.id.tvBubbleSender);
            tvBubbleText = itemView.findViewById(R.id.tvBubbleText);
            tvBubbleTime = itemView.findViewById(R.id.tvBubbleTime);
            tvBubbleRouting = itemView.findViewById(R.id.tvBubbleRouting);
            tvBubbleTicks = itemView.findViewById(R.id.tvBubbleTicks);
            ivBubbleImage = itemView.findViewById(R.id.ivBubbleImage);
            ivBubbleVideoThumb = itemView.findViewById(R.id.ivBubbleVideoThumb);
            btnPlayVideo = itemView.findViewById(R.id.btnPlayVideo);
        }
    }
}
