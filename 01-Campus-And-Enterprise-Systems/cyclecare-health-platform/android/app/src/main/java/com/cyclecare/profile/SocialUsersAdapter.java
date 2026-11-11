package com.cyclecare.profile;

import android.content.Context;
import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.chat.CircleChatActivity;
import com.google.android.material.button.MaterialButton;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class SocialUsersAdapter extends RecyclerView.Adapter<SocialUsersAdapter.UserViewHolder> {

    private final Context context;
    private final List<Map<String, Object>> users;
    private final boolean isFollowersList;
    private final Runnable onDataChanged;

    public SocialUsersAdapter(Context context, List<Map<String, Object>> users, boolean isFollowersList, Runnable onDataChanged) {
        this.context = context;
        this.users = users;
        this.isFollowersList = isFollowersList;
        this.onDataChanged = onDataChanged;
    }

    @NonNull
    @Override
    public UserViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_social_user, parent, false);
        return new UserViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull UserViewHolder holder, int position) {
        Map<String, Object> u = users.get(position);
        String userId = String.valueOf(u.get("id"));
        String name = String.valueOf(u.get("display_name"));
        String email = String.valueOf(u.get("email"));
        Boolean isFollowing = (Boolean) u.get("is_following");
        Boolean isMe = (Boolean) u.get("is_me");

        holder.tvName.setText(name);
        holder.tvEmail.setText(email);
        if (name != null && !name.isEmpty()) {
            holder.tvInitial.setText(name.substring(0, 1).toUpperCase());
        } else {
            holder.tvInitial.setText("U");
        }

        if (Boolean.TRUE.equals(isMe)) {
            holder.btnAction.setVisibility(View.GONE);
            return;
        }

        holder.btnAction.setVisibility(View.VISIBLE);

        if (isFollowersList) {
            // In Followers list: if following them, give Chat option; if not, give Follow Back option
            if (Boolean.TRUE.equals(isFollowing)) {
                holder.btnAction.setText("💬 Chat");
                holder.btnAction.setStrokeColorResource(R.color.colorPrimary);
                holder.btnAction.setTextColor(context.getResources().getColor(R.color.colorPrimary));
                holder.btnAction.setOnClickListener(v -> openChat(userId, name));
            } else {
                holder.btnAction.setText("+ Follow Back");
                holder.btnAction.setStrokeColorResource(R.color.colorSecondary);
                holder.btnAction.setTextColor(context.getResources().getColor(R.color.colorSecondary));
                holder.btnAction.setOnClickListener(v -> followUser(userId, position));
            }
        } else {
            // In Following list: option to Chat or Unfollow
            holder.btnAction.setText("💬 Chat");
            holder.btnAction.setStrokeColorResource(R.color.colorPrimary);
            holder.btnAction.setTextColor(context.getResources().getColor(R.color.colorPrimary));
            holder.btnAction.setOnClickListener(v -> openChat(userId, name));
        }
    }

    private void openChat(String userId, String name) {
        Intent intent = new Intent(context, CircleChatActivity.class);
        intent.putExtra(CircleChatActivity.EXTRA_CONTACT_NAME, name);
        intent.putExtra(CircleChatActivity.EXTRA_RELATIONSHIP, "Circle Partner");
        intent.putExtra(CircleChatActivity.EXTRA_PARTNER_USER_ID, userId);
        context.startActivity(intent);
    }

    private void followUser(String targetUserId, int position) {
        Map<String, String> body = new HashMap<>();
        body.put("target_user_id", targetUserId);
        ApiClient.getApiService(context).followUser(body).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful()) {
                    users.get(position).put("is_following", true);
                    notifyItemChanged(position);
                    Toast.makeText(context, "✓ Followed back!", Toast.LENGTH_SHORT).show();
                    if (onDataChanged != null) onDataChanged.run();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                users.get(position).put("is_following", true);
                notifyItemChanged(position);
                Toast.makeText(context, "✓ Followed back!", Toast.LENGTH_SHORT).show();
                if (onDataChanged != null) onDataChanged.run();
            }
        });
    }

    @Override
    public int getItemCount() {
        return users != null ? users.size() : 0;
    }

    static class UserViewHolder extends RecyclerView.ViewHolder {
        TextView tvInitial, tvName, tvEmail;
        MaterialButton btnAction;

        UserViewHolder(@NonNull View itemView) {
            super(itemView);
            tvInitial = itemView.findViewById(R.id.tv_user_initial);
            tvName = itemView.findViewById(R.id.tv_social_display_name);
            tvEmail = itemView.findViewById(R.id.tv_social_user_email);
            btnAction = itemView.findViewById(R.id.btn_social_action);
        }
    }
}
