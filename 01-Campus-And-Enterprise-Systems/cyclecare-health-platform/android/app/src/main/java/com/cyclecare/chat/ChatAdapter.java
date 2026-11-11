package com.cyclecare.chat;

import android.content.Context;
import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.cyclecare.R;
import com.cyclecare.store.CheckoutActivity;
import com.cyclecare.models.ChatMessage;
import com.cyclecare.utils.ImageLoader;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class ChatAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    private static final int TYPE_TEXT_ME = 1;
    private static final int TYPE_TEXT_OTHER = 2;
    private static final int TYPE_CARD_ME = 3;
    private static final int TYPE_CARD_OTHER = 4;

    private final Context context;
    private final List<ChatMessage> messageList;
    private final String partnerDisplayName;
    private OnMessageLongClickListener onMessageLongClickListener;

    public interface OnMessageLongClickListener {
        void onMessageLongClick(ChatMessage message, int position);
    }

    public void setOnMessageLongClickListener(OnMessageLongClickListener listener) {
        this.onMessageLongClickListener = listener;
    }

    public ChatAdapter(Context context, List<ChatMessage> messageList, String partnerDisplayName) {
        this.context = context;
        this.messageList = messageList;
        this.partnerDisplayName = partnerDisplayName != null ? partnerDisplayName : "Partner";
    }

    @Override
    public int getItemViewType(int position) {
        ChatMessage msg = messageList.get(position);
        boolean isCard = "CARE_REQUEST".equalsIgnoreCase(msg.getMessageType()) ||
                         "CARE_ITEM_SENT".equalsIgnoreCase(msg.getMessageType()) ||
                         "EMERGENCY_SOS".equalsIgnoreCase(msg.getMessageType());

        if (msg.isMine()) {
            return isCard ? TYPE_CARD_ME : TYPE_TEXT_ME;
        } else {
            return isCard ? TYPE_CARD_OTHER : TYPE_TEXT_OTHER;
        }
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        LayoutInflater inflater = LayoutInflater.from(context);
        if (viewType == TYPE_TEXT_ME) {
            View view = inflater.inflate(R.layout.item_chat_text_me, parent, false);
            return new TextMeViewHolder(view);
        } else if (viewType == TYPE_TEXT_OTHER) {
            View view = inflater.inflate(R.layout.item_chat_text_other, parent, false);
            return new TextOtherViewHolder(view);
        } else if (viewType == TYPE_CARD_ME) {
            View view = inflater.inflate(R.layout.item_chat_card_me, parent, false);
            return new CardMeViewHolder(view);
        } else {
            View view = inflater.inflate(R.layout.item_chat_card_other, parent, false);
            return new CardOtherViewHolder(view);
        }
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        ChatMessage msg = messageList.get(position);
        String formattedTime = formatTime(msg.getCreatedAt());

        holder.itemView.setOnLongClickListener(v -> {
            if (onMessageLongClickListener != null) {
                onMessageLongClickListener.onMessageLongClick(msg, holder.getAdapterPosition());
                return true;
            }
            return false;
        });

        if (holder instanceof TextMeViewHolder) {
            TextMeViewHolder vh = (TextMeViewHolder) holder;
            vh.tvContent.setText(msg.getContent());
            vh.tvTime.setText(formattedTime);
        } else if (holder instanceof TextOtherViewHolder) {
            TextOtherViewHolder vh = (TextOtherViewHolder) holder;
            vh.tvContent.setText(msg.getContent());
            vh.tvSenderName.setText(partnerDisplayName);
            vh.tvTime.setText(formattedTime);
        } else if (holder instanceof CardMeViewHolder) {
            CardMeViewHolder vh = (CardMeViewHolder) holder;
            vh.tvTime.setText(formattedTime);
            vh.tvNote.setText(msg.getContent());
            vh.tvProductName.setText(msg.getItemName() != null ? msg.getItemName() : "Care Essential");
            vh.tvProductPrice.setText("₹ " + msg.getItemPrice());
            vh.tvProductCategory.setText(msg.getItemCategory());

            if ("CARE_REQUEST".equalsIgnoreCase(msg.getMessageType())) {
                vh.tvTypeTag.setText("🌸 Care Request Sent");
                vh.tvStatus.setText("Status: " + msg.getItemStatus() + " ✓");
            } else {
                vh.tvTypeTag.setText("🎁 Care Package Sent");
                vh.tvStatus.setText("Status: Delivered ❤️");
            }

            if (msg.getItemImage() != null && !msg.getItemImage().isEmpty()) {
                ImageLoader.getInstance().loadImage(msg.getItemImage(), vh.ivProductImg, R.drawable.ic_nav_store_3d);
            }
        } else if (holder instanceof CardOtherViewHolder) {
            CardOtherViewHolder vh = (CardOtherViewHolder) holder;
            vh.tvSenderTitle.setText(partnerDisplayName);
            vh.tvTime.setText(formattedTime);
            vh.tvNote.setText(msg.getContent());
            vh.tvProductName.setText(msg.getItemName() != null ? msg.getItemName() : "Care Essential");
            vh.tvProductPrice.setText("₹ " + msg.getItemPrice());
            vh.tvProductCategory.setText(msg.getItemCategory());

            if ("CARE_REQUEST".equalsIgnoreCase(msg.getMessageType())) {
                vh.tvTypeTag.setText("🌸 Request from " + partnerDisplayName);
                vh.btnAction.setText("Order & Send to Her ❤️");
            } else {
                vh.tvTypeTag.setText("🎁 Care Package from " + partnerDisplayName);
                vh.btnAction.setText("View Details & Accept ✓");
            }

            if (msg.getItemImage() != null && !msg.getItemImage().isEmpty()) {
                ImageLoader.getInstance().loadImage(msg.getItemImage(), vh.ivProductImg, R.drawable.ic_nav_store_3d);
            }

            // Click Action: Launch direct Checkout to order this care item immediately!
            vh.btnAction.setOnClickListener(v -> {
                Intent checkoutIntent = new Intent(context, CheckoutActivity.class);
                checkoutIntent.putExtra("product_id", "care-item-chat");
                checkoutIntent.putExtra("product_name", msg.getItemName() != null ? msg.getItemName() : "Care Essential");
                checkoutIntent.putExtra("product_price", String.valueOf(msg.getItemPrice()));
                checkoutIntent.putExtra("product_qty", 1);
                context.startActivity(checkoutIntent);
                Toast.makeText(context, "Opening instant checkout for " + msg.getItemName(), Toast.LENGTH_SHORT).show();
            });
        }
    }

    @Override
    public int getItemCount() {
        return messageList != null ? messageList.size() : 0;
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

    // ViewHolders
    static class TextMeViewHolder extends RecyclerView.ViewHolder {
        TextView tvContent, tvTime;
        public TextMeViewHolder(@NonNull View itemView) {
            super(itemView);
            tvContent = itemView.findViewById(R.id.tv_message_content);
            tvTime = itemView.findViewById(R.id.tv_message_time);
        }
    }

    static class TextOtherViewHolder extends RecyclerView.ViewHolder {
        TextView tvSenderName, tvContent, tvTime;
        public TextOtherViewHolder(@NonNull View itemView) {
            super(itemView);
            tvSenderName = itemView.findViewById(R.id.tv_sender_name);
            tvContent = itemView.findViewById(R.id.tv_message_content);
            tvTime = itemView.findViewById(R.id.tv_message_time);
        }
    }

    static class CardMeViewHolder extends RecyclerView.ViewHolder {
        TextView tvTypeTag, tvTime, tvNote, tvProductName, tvProductPrice, tvProductCategory, tvStatus;
        ImageView ivProductImg;
        public CardMeViewHolder(@NonNull View itemView) {
            super(itemView);
            tvTypeTag = itemView.findViewById(R.id.tv_card_type_tag);
            tvTime = itemView.findViewById(R.id.tv_card_time);
            tvNote = itemView.findViewById(R.id.tv_card_note);
            tvProductName = itemView.findViewById(R.id.tv_card_product_name);
            tvProductPrice = itemView.findViewById(R.id.tv_card_product_price);
            tvProductCategory = itemView.findViewById(R.id.tv_card_product_category);
            tvStatus = itemView.findViewById(R.id.tv_card_status);
            ivProductImg = itemView.findViewById(R.id.iv_card_product_img);
        }
    }

    static class CardOtherViewHolder extends RecyclerView.ViewHolder {
        TextView tvSenderTitle, tvTypeTag, tvTime, tvNote, tvProductName, tvProductPrice, tvProductCategory;
        ImageView ivProductImg;
        Button btnAction;
        public CardOtherViewHolder(@NonNull View itemView) {
            super(itemView);
            tvSenderTitle = itemView.findViewById(R.id.tv_card_sender_title);
            tvTypeTag = itemView.findViewById(R.id.tv_card_type_tag);
            tvTime = itemView.findViewById(R.id.tv_card_time);
            tvNote = itemView.findViewById(R.id.tv_card_note);
            tvProductName = itemView.findViewById(R.id.tv_card_product_name);
            tvProductPrice = itemView.findViewById(R.id.tv_card_product_price);
            tvProductCategory = itemView.findViewById(R.id.tv_card_product_category);
            ivProductImg = itemView.findViewById(R.id.iv_card_product_img);
            btnAction = itemView.findViewById(R.id.btn_card_action);
        }
    }
}
