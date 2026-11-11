package com.cyclecare.chat;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.DividerItemDecoration;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.api.ApiService;
import com.cyclecare.models.CircleContact;
import com.cyclecare.store.CartActivity;
import com.google.android.material.bottomsheet.BottomSheetDialog;
import com.google.android.material.floatingactionbutton.ExtendedFloatingActionButton;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class CircleConversationsActivity extends AppCompatActivity {

    private RecyclerView rvConversations;
    private CircleConversationsAdapter adapter;
    private final List<CircleContact> contactList = new ArrayList<>();
    private final List<CircleContact> filteredList = new ArrayList<>();

    private SwipeRefreshLayout swipeRefresh;
    private LinearLayout layoutEmpty;
    private EditText etSearch;
    private ExtendedFloatingActionButton fabNewChat;
    private ImageButton btnBack, btnStore, btnRefresh;

    private ApiService apiService;
    private Handler autoRefreshHandler;
    private Runnable autoRefreshRunnable;
    private final Gson gson = new Gson();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_circle_conversations);

        apiService = ApiClient.getApiService(this);
        autoRefreshHandler = new Handler(Looper.getMainLooper());

        initViews();
        setupRecyclerView();
        setupSearchFilter();
        loadContacts(true);
        startAutoRefresh();
    }

    private void initViews() {
        btnBack = findViewById(R.id.btn_conv_back);
        btnStore = findViewById(R.id.btn_conv_store);
        btnRefresh = findViewById(R.id.btn_conv_refresh);
        etSearch = findViewById(R.id.et_search_contacts);
        swipeRefresh = findViewById(R.id.swipe_refresh_conversations);
        rvConversations = findViewById(R.id.rv_conversations);
        layoutEmpty = findViewById(R.id.layout_empty_conversations);
        fabNewChat = findViewById(R.id.fab_new_chat);

        btnBack.setOnClickListener(v -> finish());
        btnStore.setOnClickListener(v -> startActivity(new Intent(this, CartActivity.class)));
        btnRefresh.setOnClickListener(v -> loadContacts(false));
        swipeRefresh.setOnRefreshListener(() -> loadContacts(false));

        fabNewChat.setOnClickListener(v -> showNewChatBottomSheet());
    }

    private void setupRecyclerView() {
        adapter = new CircleConversationsAdapter(this, filteredList, this::openChatWithContact);
        adapter.setOnContactLongClickListener((contact, position) -> {
            CharSequence[] options = new CharSequence[]{"🏷️ Change Relationship Tag", "💬 Open Chat", "🗑️ Delete Conversation"};
            new AlertDialog.Builder(this)
                    .setTitle(contact.getDisplayName())
                    .setItems(options, (dialog, which) -> {
                        if (which == 0) {
                            showChangeTagDialog(contact, position);
                        } else if (which == 1) {
                            openChatWithContact(contact);
                        } else if (which == 2) {
                            confirmDeleteConversation(contact, position);
                        }
                    })
                    .show();
        });

        LinearLayoutManager lm = new LinearLayoutManager(this);
        rvConversations.setLayoutManager(lm);
        rvConversations.addItemDecoration(new DividerItemDecoration(this, DividerItemDecoration.VERTICAL));
        rvConversations.setAdapter(adapter);
    }

    private void openChatWithContact(CircleContact contact) {
        Intent intent = new Intent(CircleConversationsActivity.this, CircleChatActivity.class);
        intent.putExtra(CircleChatActivity.EXTRA_CONNECTION_ID, contact.getConnectionId());
        intent.putExtra(CircleChatActivity.EXTRA_CONTACT_NAME, contact.getDisplayName());
        intent.putExtra(CircleChatActivity.EXTRA_RELATIONSHIP, contact.getRelationship());
        intent.putExtra(CircleChatActivity.EXTRA_PARTNER_USER_ID, contact.getUserId());
        startActivity(intent);
    }

    private void showChangeTagDialog(CircleContact contact, int position) {
        final String[] tagOptions = new String[]{
                "Husband", "Wife", "Boyfriend", "Girlfriend",
                "Father", "Mother", "Daughter", "Son",
                "Sister", "Brother", "Best Friend", "Partner", "Family", "Other"
        };
        new AlertDialog.Builder(this)
                .setTitle("Set Tag for " + contact.getDisplayName())
                .setItems(tagOptions, (d, which) -> {
                    String selected = tagOptions[which];
                    contact.setRelationship(selected);
                    adapter.notifyItemChanged(position);

                    // API update
                    Map<String, String> body = new HashMap<>();
                    if (contact.getConnectionId() != null) body.put("connection_id", contact.getConnectionId());
                    if (contact.getUserId() != null) body.put("target_user_id", contact.getUserId());
                    if (contact.getDisplayName() != null) body.put("target_name", contact.getDisplayName());
                    body.put("tag", selected);

                    apiService.setContactTag(body).enqueue(new Callback<Map<String, Object>>() {
                        @Override
                        public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                            if (response.isSuccessful() && response.body() != null) {
                                Object relObj = response.body().get("relationship");
                                Object recipObj = response.body().get("reciprocal_relationship");
                                if (relObj != null) {
                                    contact.setRelationship(String.valueOf(relObj));
                                    adapter.notifyItemChanged(position);
                                }

                                SharedPreferences prefs = getSharedPreferences("cyclecare_contact_tags", Context.MODE_PRIVATE);
                                SharedPreferences.Editor editor = prefs.edit();
                                if (contact.getConnectionId() != null) editor.putString("tag_" + contact.getConnectionId(), contact.getRelationship());
                                if (contact.getUserId() != null) editor.putString("tag_" + contact.getUserId(), contact.getRelationship());
                                editor.apply();

                                String msg = "Relationship tag set: " + contact.getRelationship();
                                if (recipObj != null) {
                                    msg += " (Reciprocal: " + recipObj + ")";
                                }
                                Toast.makeText(CircleConversationsActivity.this, msg, Toast.LENGTH_SHORT).show();
                            } else {
                                Toast.makeText(CircleConversationsActivity.this, "Relationship tag set: " + selected, Toast.LENGTH_SHORT).show();
                            }
                        }

                        @Override
                        public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                            Toast.makeText(CircleConversationsActivity.this, "Tag set locally: " + selected, Toast.LENGTH_SHORT).show();
                        }
                    });
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void confirmDeleteConversation(CircleContact contact, int position) {
        new AlertDialog.Builder(this)
                .setTitle("🗑️ Delete Conversation")
                .setMessage("Are you sure you want to remove " + contact.getDisplayName() + " and delete all chat messages?")
                .setPositiveButton("Delete", (d, w) -> {
                    if (contact.getConnectionId() != null) {
                        apiService.deleteCircleConnection(contact.getConnectionId()).enqueue(new Callback<Map<String, Object>>() {
                            @Override
                            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                                Toast.makeText(CircleConversationsActivity.this, "✓ Conversation deleted", Toast.LENGTH_SHORT).show();
                            }
                            @Override
                            public void onFailure(Call<Map<String, Object>> call, Throwable t) {}
                        });
                    }
                    if (position >= 0 && position < filteredList.size()) {
                        filteredList.remove(position);
                        adapter.notifyItemRemoved(position);
                        updateEmptyState();
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void setupSearchFilter() {
        etSearch.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                filterContacts(s.toString());
            }

            @Override
            public void afterTextChanged(Editable s) {}
        });
    }

    private void filterContacts(String query) {
        filteredList.clear();
        if (query == null || query.trim().isEmpty()) {
            filteredList.addAll(contactList);
        } else {
            String lower = query.trim().toLowerCase();
            for (CircleContact c : contactList) {
                if (c.getDisplayName().toLowerCase().contains(lower) ||
                    c.getRelationship().toLowerCase().contains(lower) ||
                    c.getLastMessage().toLowerCase().contains(lower)) {
                    filteredList.add(c);
                }
            }
        }
        adapter.notifyDataSetChanged();
        updateEmptyState();
    }

    private void loadContacts(boolean showLoading) {
        if (showLoading) swipeRefresh.setRefreshing(true);

        apiService.getCircleContacts().enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                swipeRefresh.setRefreshing(false);
                if (response.isSuccessful() && response.body() != null) {
                    Object contactsObj = response.body().get("contacts");
                    if (contactsObj != null) {
                        Type type = new TypeToken<List<CircleContact>>() {}.getType();
                        List<CircleContact> fetched = gson.fromJson(gson.toJson(contactsObj), type);
                        if (fetched != null) {
                            SharedPreferences prefs = getSharedPreferences("cyclecare_contact_tags", Context.MODE_PRIVATE);
                            for (CircleContact c : fetched) {
                                if (c.getRelationship() == null || c.getRelationship().isEmpty() || "null".equalsIgnoreCase(c.getRelationship())) {
                                    String saved = prefs.getString("tag_" + c.getConnectionId(), null);
                                    if (saved == null && c.getUserId() != null) saved = prefs.getString("tag_" + c.getUserId(), null);
                                    if (saved != null) {
                                        c.setRelationship(saved);
                                    } else {
                                        c.setRelationship("Partner");
                                    }
                                }
                            }
                            contactList.clear();
                            contactList.addAll(fetched);
                            filterContacts(etSearch.getText().toString());
                        }
                    }
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                swipeRefresh.setRefreshing(false);
            }
        });
    }

    private void updateEmptyState() {
        if (filteredList.isEmpty()) {
            layoutEmpty.setVisibility(View.VISIBLE);
            rvConversations.setVisibility(View.GONE);
        } else {
            layoutEmpty.setVisibility(View.GONE);
            rvConversations.setVisibility(View.VISIBLE);
        }
    }

    private void showNewChatBottomSheet() {
        BottomSheetDialog dialog = new BottomSheetDialog(this);
        View sheet = getLayoutInflater().inflate(R.layout.dialog_add_circle_contact, null);
        dialog.setContentView(sheet);

        EditText etQuery = sheet.findViewById(R.id.et_new_chat_query);
        Button btnFind = sheet.findViewById(R.id.btn_action_find_or_connect);
        View cardPreview = sheet.findViewById(R.id.card_found_user_preview);
        TextView tvPreviewLetter = sheet.findViewById(R.id.tv_preview_avatar_letter);
        TextView tvPreviewName = sheet.findViewById(R.id.tv_preview_user_name);
        TextView tvPreviewEmail = sheet.findViewById(R.id.tv_preview_user_email);
        TextView tvPreviewBadge = sheet.findViewById(R.id.tv_preview_tag_badge);

        final String[] selectedTag = {"Husband ❤️"};
        final Map<String, Object>[] foundUser = new Map[]{null};

        // Chip selection logic
        int[] chipIds = new int[]{
                R.id.chip_tag_husband, R.id.chip_tag_wife, R.id.chip_tag_friend,
                R.id.chip_tag_sister, R.id.chip_tag_mom, R.id.chip_tag_partner
        };
        String[] chipTags = new String[]{
                "Husband ❤️", "Wife 🌸", "Best Friend 💕", "Sister 🌷", "Mother 👵", "Partner 💍"
        };

        for (int i = 0; i < chipIds.length; i++) {
            final int idx = i;
            Button chip = sheet.findViewById(chipIds[idx]);
            if (chip != null) {
                chip.setOnClickListener(v -> {
                    selectedTag[0] = chipTags[idx];
                    tvPreviewBadge.setText(chipTags[idx]);
                    for (int j = 0; j < chipIds.length; j++) {
                        Button other = sheet.findViewById(chipIds[j]);
                        if (other != null) {
                            if (j == idx) {
                                other.setBackgroundResource(R.drawable.bg_m3_button);
                                other.setTextColor(getResources().getColor(R.color.textOnPrimary));
                            } else {
                                other.setBackgroundResource(R.drawable.bg_neu_card_raised);
                                other.setTextColor(getResources().getColor(R.color.textPrimary));
                            }
                        }
                    }
                });
            }
        }

        btnFind.setOnClickListener(v -> {
            if (foundUser[0] != null) {
                // Connect and start chat
                String targetId = String.valueOf(foundUser[0].get("id"));
                String targetName = String.valueOf(foundUser[0].get("display_name"));

                // Save to SharedPreferences
                SharedPreferences prefs = getSharedPreferences("cyclecare_contact_tags", Context.MODE_PRIVATE);
                prefs.edit()
                        .putString("tag_" + targetId, selectedTag[0])
                        .putString("tag_" + targetName.toLowerCase().trim(), selectedTag[0])
                        .apply();

                Map<String, String> body = new HashMap<>();
                body.put("target_user_id", targetId);
                body.put("target_name", targetName);
                body.put("tag", selectedTag[0]);

                apiService.setContactTag(body).enqueue(new Callback<Map<String, Object>>() {
                    @Override
                    public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {}
                    @Override
                    public void onFailure(Call<Map<String, Object>> call, Throwable t) {}
                });

                dialog.dismiss();
                Intent intent = new Intent(CircleConversationsActivity.this, CircleChatActivity.class);
                intent.putExtra(CircleChatActivity.EXTRA_CONTACT_NAME, targetName);
                intent.putExtra(CircleChatActivity.EXTRA_RELATIONSHIP, selectedTag[0]);
                intent.putExtra(CircleChatActivity.EXTRA_PARTNER_USER_ID, targetId);
                startActivity(intent);
                loadContacts(false);
                return;
            }

            String q = etQuery.getText().toString().trim();
            if (q.isEmpty()) {
                Toast.makeText(this, "Please enter a name or email", Toast.LENGTH_SHORT).show();
                return;
            }

            btnFind.setText("Searching... ⏳");
            btnFind.setEnabled(false);

            apiService.searchUsers(q).enqueue(new Callback<Map<String, Object>>() {
                @Override
                public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                    btnFind.setEnabled(true);
                    if (response.isSuccessful() && response.body() != null) {
                        List<?> users = (List<?>) response.body().get("users");
                        if (users != null && !users.isEmpty()) {
                            Map<String, Object> u = (Map<String, Object>) users.get(0);
                            foundUser[0] = u;
                            String name = String.valueOf(u.get("display_name"));
                            String email = String.valueOf(u.get("email"));

                            cardPreview.setVisibility(View.VISIBLE);
                            tvPreviewName.setText(name);
                            tvPreviewEmail.setText(email);
                            tvPreviewLetter.setText(name.isEmpty() ? "U" : name.substring(0, 1).toUpperCase());
                            tvPreviewBadge.setText(selectedTag[0]);

                            btnFind.setText("Start Chat with " + name + " 🚀");
                        } else {
                            btnFind.setText("Search & Connect 🚀");
                            Toast.makeText(CircleConversationsActivity.this, "No user found with \"" + q + "\"", Toast.LENGTH_LONG).show();
                        }
                    } else {
                        btnFind.setText("Search & Connect 🚀");
                        Toast.makeText(CircleConversationsActivity.this, "Search failed", Toast.LENGTH_SHORT).show();
                    }
                }

                @Override
                public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                    btnFind.setEnabled(true);
                    btnFind.setText("Search & Connect 🚀");
                    Toast.makeText(CircleConversationsActivity.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        });

        dialog.show();
    }

    private void startAutoRefresh() {
        autoRefreshRunnable = new Runnable() {
            @Override
            public void run() {
                loadContacts(false);
                autoRefreshHandler.postDelayed(this, 5000);
            }
        };
        autoRefreshHandler.postDelayed(autoRefreshRunnable, 5000);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (adapter != null) {
            adapter.notifyDataSetChanged();
        }
        loadContacts(false);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (autoRefreshHandler != null && autoRefreshRunnable != null) {
            autoRefreshHandler.removeCallbacks(autoRefreshRunnable);
        }
    }
}
