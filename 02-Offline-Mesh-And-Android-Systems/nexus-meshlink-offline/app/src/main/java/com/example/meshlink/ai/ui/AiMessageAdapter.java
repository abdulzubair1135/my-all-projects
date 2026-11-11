package com.example.meshlink.ai.ui;

import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.meshlink.R;
import com.example.meshlink.mesh.MeshCoordinator;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class AiMessageAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    private static final int TYPE_USER = 1;
    private static final int TYPE_BOT = 2;

    private final Context context;
    private final List<AiMessage> messages;
    private final OnChipClickListener chipClickListener;
    private final SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm", Locale.getDefault());

    public interface OnChipClickListener {
        void onChipClick(String chipText);
    }

    public AiMessageAdapter(Context context, List<AiMessage> messages, OnChipClickListener chipClickListener) {
        this.context = context;
        this.messages = messages;
        this.chipClickListener = chipClickListener;
    }

    @Override
    public int getItemViewType(int position) {
        return messages.get(position).isUser ? TYPE_USER : TYPE_BOT;
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        if (viewType == TYPE_USER) {
            View v = LayoutInflater.from(context).inflate(R.layout.item_ai_message_user, parent, false);
            return new UserViewHolder(v);
        } else {
            View v = LayoutInflater.from(context).inflate(R.layout.item_ai_message_bot, parent, false);
            return new BotViewHolder(v);
        }
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        AiMessage msg = messages.get(position);

        if (holder instanceof UserViewHolder) {
            UserViewHolder uHolder = (UserViewHolder) holder;
            uHolder.tvMessage.setText(msg.text);
            uHolder.tvTime.setText(timeFormat.format(new Date(msg.timestamp)));
        } else if (holder instanceof BotViewHolder) {
            BotViewHolder bHolder = (BotViewHolder) holder;
            bHolder.tvMessage.setText(msg.text);
            bHolder.tvTime.setText(timeFormat.format(new Date(msg.timestamp)));

            if (msg.isThinking) {
                bHolder.tvMessage.setTextColor(context.getColor(R.color.primary));
                bHolder.tvMessage.setTypeface(null, android.graphics.Typeface.ITALIC);
                bHolder.btnAction.setVisibility(View.GONE);
                bHolder.hsvChips.setVisibility(View.GONE);
                bHolder.llThoughtContainer.setVisibility(View.GONE);
                return;
            } else {
                bHolder.tvMessage.setTextColor(context.getColor(R.color.text_primary));
                bHolder.tvMessage.setTypeface(null, android.graphics.Typeface.NORMAL);
            }

            // Bind Thought Process Container (collapsible)
            if (msg.thought != null && !msg.thought.trim().isEmpty()) {
                bHolder.llThoughtContainer.setVisibility(View.VISIBLE);
                bHolder.tvThoughtContent.setText(msg.thought.trim());

                if (msg.isThoughtExpanded) {
                    bHolder.tvThoughtContent.setVisibility(View.VISIBLE);
                    bHolder.vThoughtDivider.setVisibility(View.VISIBLE);
                    bHolder.tvThoughtToggleArrow.setText("▲");
                } else {
                    bHolder.tvThoughtContent.setVisibility(View.GONE);
                    bHolder.vThoughtDivider.setVisibility(View.GONE);
                    bHolder.tvThoughtToggleArrow.setText("▼");
                }

                bHolder.llThoughtHeader.setOnClickListener(v -> {
                    msg.isThoughtExpanded = !msg.isThoughtExpanded;
                    if (msg.isThoughtExpanded) {
                        bHolder.tvThoughtContent.setVisibility(View.VISIBLE);
                        bHolder.vThoughtDivider.setVisibility(View.VISIBLE);
                        bHolder.tvThoughtToggleArrow.setText("▲");
                    } else {
                        bHolder.tvThoughtContent.setVisibility(View.GONE);
                        bHolder.vThoughtDivider.setVisibility(View.GONE);
                        bHolder.tvThoughtToggleArrow.setText("▼");
                    }
                });
            } else {
                bHolder.llThoughtContainer.setVisibility(View.GONE);
            }

            // Action Button logic
            if ("EMERGENCY_ALERT".equals(msg.actionType)) {
                bHolder.btnAction.setVisibility(View.VISIBLE);
                bHolder.btnAction.setText("🚨 Dial 112 Emergency");
                bHolder.btnAction.setOnClickListener(v -> {
                    Intent dial = new Intent(Intent.ACTION_DIAL, Uri.parse("tel:112"));
                    context.startActivity(dial);
                });
            } else if ("CALL".equals(msg.actionType)) {
                bHolder.btnAction.setVisibility(View.VISIBLE);
                bHolder.btnAction.setText("📞 Call " + (msg.actionPayload != null ? msg.actionPayload : ""));
                bHolder.btnAction.setOnClickListener(v -> {
                    Intent dial = new Intent(Intent.ACTION_DIAL, Uri.parse("tel:" + msg.actionPayload));
                    context.startActivity(dial);
                });
            } else {
                bHolder.btnAction.setVisibility(View.GONE);
            }

            // Quick Chips
            bHolder.llChips.removeAllViews();
            if (msg.chips != null && !msg.chips.isEmpty()) {
                bHolder.hsvChips.setVisibility(View.VISIBLE);
                for (String chip : msg.chips) {
                    TextView tvChip = new TextView(context);
                    tvChip.setText(chip);
                    tvChip.setTextSize(12);
                    tvChip.setTextColor(Color.parseColor("#15803D"));
                    tvChip.setBackgroundResource(R.drawable.bg_badge_blue);
                    tvChip.setPadding(24, 12, 24, 12);

                    LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                            ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                    lp.setMargins(0, 0, 16, 0);
                    tvChip.setLayoutParams(lp);

                    tvChip.setOnClickListener(v -> {
                        if (chip.contains("Call 112")) {
                            Intent dial = new Intent(Intent.ACTION_DIAL, Uri.parse("tel:112"));
                            context.startActivity(dial);
                        } else if (chip.contains("Trigger Mesh SOS")) {
                            try {
                                MeshCoordinator coord = MeshCoordinator.getInstance(context);
                                if (coord != null) {
                                    coord.broadcastSOS(23.0225, 72.5714, 10f, "AI Emergency Activated");
                                    Toast.makeText(context, "🚨 Offline Mesh SOS Beacon Broadcasted!", Toast.LENGTH_LONG).show();
                                }
                            } catch (Exception ignored) {}
                        } else if (chip.contains("AI Settings")) {
                            context.startActivity(new Intent(context, NexusAiSettingsActivity.class));
                        } else if (chipClickListener != null) {
                            chipClickListener.onChipClick(chip);
                        }
                    });

                    bHolder.llChips.addView(tvChip);
                }
            } else {
                bHolder.hsvChips.setVisibility(View.GONE);
            }
        }
    }

    @Override
    public int getItemCount() {
        return messages.size();
    }

    static class UserViewHolder extends RecyclerView.ViewHolder {
        TextView tvMessage, tvTime;
        UserViewHolder(View v) {
            super(v);
            tvMessage = v.findViewById(R.id.tvUserMessage);
            tvTime = v.findViewById(R.id.tvUserTime);
        }
    }

    static class BotViewHolder extends RecyclerView.ViewHolder {
        TextView tvHeaderLabel;
        TextView tvMessage, tvTime;
        View llThoughtContainer;
        View llThoughtHeader;
        TextView tvThoughtTitle;
        TextView tvThoughtToggleArrow;
        View vThoughtDivider;
        TextView tvThoughtContent;
        Button btnAction;
        View hsvChips;
        LinearLayout llChips;

        BotViewHolder(View v) {
            super(v);
            tvHeaderLabel = v.findViewById(R.id.tvBotHeaderLabel);
            tvMessage = v.findViewById(R.id.tvBotMessage);
            tvTime = v.findViewById(R.id.tvBotTime);
            llThoughtContainer = v.findViewById(R.id.llThoughtContainer);
            llThoughtHeader = v.findViewById(R.id.llThoughtHeader);
            tvThoughtTitle = v.findViewById(R.id.tvThoughtTitle);
            tvThoughtToggleArrow = v.findViewById(R.id.tvThoughtToggleArrow);
            vThoughtDivider = v.findViewById(R.id.vThoughtDivider);
            tvThoughtContent = v.findViewById(R.id.tvThoughtContent);
            btnAction = v.findViewById(R.id.btnBotAction);
            hsvChips = v.findViewById(R.id.hsvChips);
            llChips = v.findViewById(R.id.llChipsContainer);
        }
    }
}
