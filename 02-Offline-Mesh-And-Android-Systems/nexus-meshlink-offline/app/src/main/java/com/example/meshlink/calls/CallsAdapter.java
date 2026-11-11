package com.example.meshlink.calls;

import android.content.Context;
import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.meshlink.R;
import com.example.meshlink.data.CallModel;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class CallsAdapter extends RecyclerView.Adapter<CallsAdapter.CallViewHolder> {

    private final Context context;
    private final List<CallModel> calls;
    private final SimpleDateFormat timeFormat = new SimpleDateFormat("hh:mm a", Locale.getDefault());

    public CallsAdapter(Context context, List<CallModel> calls) {
        this.context = context;
        this.calls = calls;
    }

    @NonNull
    @Override
    public CallViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(context).inflate(R.layout.item_call_log, parent, false);
        return new CallViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull CallViewHolder holder, int position) {
        CallModel call = calls.get(position);
        holder.tvCallLogPeerName.setText(call.peerName);
        holder.tvCallLogAvatar.setText(call.peerName.substring(0, Math.min(1, call.peerName.length())).toUpperCase());

        int mins = call.durationSeconds / 60;
        int secs = call.durationSeconds % 60;
        String durStr = String.format(Locale.getDefault(), " • %02d:%02d min", mins, secs);
        holder.tvCallLogDuration.setText(durStr);

        holder.tvCallLogTransport.setText(" • " + (call.transport != null ? call.transport : "WiFi Direct"));

        if (CallModel.DIR_OUTGOING.equals(call.direction)) {
            holder.tvCallLogDirection.setText("↗ Outgoing");
            holder.tvCallLogDirection.setTextColor(context.getResources().getColor(R.color.online_green));
        } else if (CallModel.DIR_INCOMING.equals(call.direction)) {
            holder.tvCallLogDirection.setText("↙ Incoming");
            holder.tvCallLogDirection.setTextColor(context.getResources().getColor(R.color.primary));
        } else {
            holder.tvCallLogDirection.setText("✕ Missed");
            holder.tvCallLogDirection.setTextColor(context.getResources().getColor(R.color.danger_red));
        }

        if (CallModel.TYPE_VIDEO.equals(call.callType)) {
            holder.ivCallLogAction.setImageResource(android.R.drawable.ic_menu_camera);
        } else {
            holder.ivCallLogAction.setImageResource(android.R.drawable.ic_menu_call);
        }

        holder.ivCallLogAction.setOnClickListener(v -> {
            Intent intent;
            if (CallModel.TYPE_VIDEO.equals(call.callType)) {
                intent = new Intent(context, VideoCallActivity.class);
            } else {
                intent = new Intent(context, VoiceCallActivity.class);
            }
            intent.putExtra("PEER_NAME", call.peerName);
            intent.putExtra("PEER_ID", call.peerId);
            context.startActivity(intent);
        });
    }

    @Override
    public int getItemCount() {
        return calls.size();
    }

    static class CallViewHolder extends RecyclerView.ViewHolder {
        TextView tvCallLogAvatar, tvCallLogPeerName, tvCallLogDirection, tvCallLogDuration, tvCallLogTransport;
        ImageView ivCallLogAction;

        public CallViewHolder(@NonNull View itemView) {
            super(itemView);
            tvCallLogAvatar = itemView.findViewById(R.id.tvCallLogAvatar);
            tvCallLogPeerName = itemView.findViewById(R.id.tvCallLogPeerName);
            tvCallLogDirection = itemView.findViewById(R.id.tvCallLogDirection);
            tvCallLogDuration = itemView.findViewById(R.id.tvCallLogDuration);
            tvCallLogTransport = itemView.findViewById(R.id.tvCallLogTransport);
            ivCallLogAction = itemView.findViewById(R.id.ivCallLogAction);
        }
    }
}
