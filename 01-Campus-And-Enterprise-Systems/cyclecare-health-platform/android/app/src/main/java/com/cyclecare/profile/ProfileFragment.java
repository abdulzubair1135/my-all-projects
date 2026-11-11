package com.cyclecare.profile;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.net.Uri;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.content.FileProvider;
import androidx.fragment.app.Fragment;

import com.cyclecare.R;
import com.cyclecare.auth.LoginActivity;
import com.cyclecare.partner.PartnerCareActivity;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

public class ProfileFragment extends Fragment {

    private Button btnShareApk, btnAppSettings, btnLogout;
    private TextView tvUserName, tvUserEmail;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_profile, container, false);

        tvUserName = view.findViewById(R.id.tv_user_name);
        tvUserEmail = view.findViewById(R.id.tv_user_email);
        btnShareApk = view.findViewById(R.id.btn_share_apk);
        btnAppSettings = view.findViewById(R.id.btn_app_settings);
        btnLogout = view.findViewById(R.id.btn_logout);

        if (getActivity() != null) {
            SharedPreferences prefs = getActivity().getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE);
            String userName = prefs.getString("user_name", "Demo User");
            tvUserName.setText(userName);
            tvUserEmail.setText(userName.toLowerCase().replaceAll("\\s+", "") + "@cyclecare.com");
        }

        Button btnEditName = view.findViewById(R.id.btn_edit_profile_name);
        if (btnEditName != null) {
            btnEditName.setOnClickListener(v -> {
                final EditText input = new EditText(getContext());
                input.setHint("Enter new display name");
                input.setText(tvUserName.getText().toString());
                input.setTextColor(androidx.core.content.ContextCompat.getColor(requireContext(), R.color.textPrimary));
                input.setHintTextColor(androidx.core.content.ContextCompat.getColor(requireContext(), R.color.textHint));
                input.setPadding(60, 40, 60, 40);
                new androidx.appcompat.app.AlertDialog.Builder(requireContext())
                        .setTitle("✏️ Update Display Name")
                        .setView(input)
                        .setPositiveButton("Update", (dialog, which) -> {
                            String newName = input.getText().toString().trim();
                            if (!newName.isEmpty()) {
                                tvUserName.setText(newName);
                                if (getActivity() != null) {
                                    getActivity().getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE)
                                            .edit().putString("user_name", newName).apply();
                                }
                                java.util.Map<String, String> body = new java.util.HashMap<>();
                                body.put("display_name", newName);
                                com.cyclecare.api.ApiClient.getApiService(getContext()).updateProfile(body).enqueue(new retrofit2.Callback<java.util.Map<String, Object>>() {
                                    @Override
                                    public void onResponse(retrofit2.Call<java.util.Map<String, Object>> call, retrofit2.Response<java.util.Map<String, Object>> response) {
                                        Toast.makeText(getContext(), "✓ Name updated in Profile & Database!", Toast.LENGTH_SHORT).show();
                                    }

                                    @Override
                                    public void onFailure(retrofit2.Call<java.util.Map<String, Object>> call, Throwable t) {
                                        Toast.makeText(getContext(), "✓ Name updated locally!", Toast.LENGTH_SHORT).show();
                                    }
                                });
                            }
                        })
                        .setNegativeButton("Cancel", null)
                        .show();
            });
        }

        Button btnSetEmergency = view.findViewById(R.id.btn_set_emergency_contact);
        if (btnSetEmergency != null) {
            btnSetEmergency.setOnClickListener(v -> {
                android.widget.LinearLayout layout = new android.widget.LinearLayout(getContext());
                layout.setOrientation(android.widget.LinearLayout.VERTICAL);
                layout.setPadding(50, 30, 50, 10);

                final EditText etPhone = new EditText(getContext());
                etPhone.setHint("Emergency Phone (e.g. 9876543210)");
                etPhone.setInputType(android.text.InputType.TYPE_CLASS_PHONE);
                etPhone.setTextColor(androidx.core.content.ContextCompat.getColor(requireContext(), R.color.textPrimary));
                etPhone.setHintTextColor(androidx.core.content.ContextCompat.getColor(requireContext(), R.color.textHint));
                layout.addView(etPhone);

                final EditText etRel = new EditText(getContext());
                etRel.setHint("Relationship (e.g. Husband, Relative, Mom)");
                etRel.setTextColor(androidx.core.content.ContextCompat.getColor(requireContext(), R.color.textPrimary));
                etRel.setHintTextColor(androidx.core.content.ContextCompat.getColor(requireContext(), R.color.textHint));
                layout.addView(etRel);

                new androidx.appcompat.app.AlertDialog.Builder(requireContext())
                        .setTitle("📞 Emergency Contact")
                        .setMessage("Set contact number for 1-Tap SOS calling:")
                        .setView(layout)
                        .setPositiveButton("Save Contact", (dialog, which) -> {
                            String phone = etPhone.getText().toString().trim();
                            String rel = etRel.getText().toString().trim();
                            if (rel.isEmpty()) rel = "Husband";

                            if (!phone.isEmpty() && getActivity() != null) {
                                getActivity().getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE)
                                        .edit()
                                        .putString("emergency_phone", phone)
                                        .putString("emergency_rel", rel)
                                        .apply();

                                java.util.Map<String, String> body = new java.util.HashMap<>();
                                body.put("emergency_contact_phone", phone);
                                body.put("emergency_contact_relation", rel);
                                com.cyclecare.api.ApiClient.getApiService(getContext()).updateProfile(body).enqueue(new retrofit2.Callback<java.util.Map<String, Object>>() {
                                    @Override
                                    public void onResponse(retrofit2.Call<java.util.Map<String, Object>> call, retrofit2.Response<java.util.Map<String, Object>> response) {
                                        Toast.makeText(getContext(), "✓ Emergency contact saved in Database!", Toast.LENGTH_SHORT).show();
                                    }

                                    @Override
                                    public void onFailure(retrofit2.Call<java.util.Map<String, Object>> call, Throwable t) {
                                        Toast.makeText(getContext(), "✓ Emergency contact saved locally!", Toast.LENGTH_SHORT).show();
                                    }
                                });
                            }
                        })
                        .setNegativeButton("Cancel", null)
                        .show();
            });
        }

        // Social Search & Follow System
        EditText etSearchUsers = view.findViewById(R.id.et_search_users);
        View btnSearch = view.findViewById(R.id.btn_trigger_user_search);
        TextView tvSearchResult = view.findViewById(R.id.tv_search_user_result);
        Button btnFollow = view.findViewById(R.id.btn_action_follow_user);
        Button btnSetTag = view.findViewById(R.id.btn_action_set_tag);
        Button btnChatNow = view.findViewById(R.id.btn_action_chat_now);
        TextView tvFollowers = view.findViewById(R.id.tv_followers_count);
        TextView tvFollowing = view.findViewById(R.id.tv_following_count);

        final String[] foundUserId = {null};
        final String[] foundUserName = {"Circle Partner"};
        final String[] userTag = {"Partner"};
        final boolean[] isFollowingUser = {false};

        if (btnSearch != null && etSearchUsers != null) {
            btnSearch.setOnClickListener(v -> {
                String q = etSearchUsers.getText().toString().trim();
                if (q.isEmpty()) {
                    Toast.makeText(getContext(), "Enter a name or email to search", Toast.LENGTH_SHORT).show();
                    return;
                }
                tvSearchResult.setText("Searching for \"" + q + "\"...");
                com.cyclecare.api.ApiClient.getApiService(getContext()).searchUsers(q).enqueue(new retrofit2.Callback<java.util.Map<String, Object>>() {
                    @Override
                    public void onResponse(retrofit2.Call<java.util.Map<String, Object>> call, retrofit2.Response<java.util.Map<String, Object>> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            java.util.List<?> users = (java.util.List<?>) response.body().get("users");
                            if (users != null && !users.isEmpty()) {
                                java.util.Map<?, ?> first = (java.util.Map<?, ?>) users.get(0);
                                foundUserId[0] = String.valueOf(first.get("id"));
                                String name = String.valueOf(first.get("display_name"));
                                foundUserName[0] = name;
                                String email = String.valueOf(first.get("email"));
                                Boolean following = (Boolean) first.get("is_following");
                                isFollowingUser[0] = following != null && following;

                                tvSearchResult.setText("✓ " + name + " (" + email + ")");
                                if (btnFollow != null) {
                                    btnFollow.setVisibility(View.VISIBLE);
                                    btnFollow.setText(isFollowingUser[0] ? "✓ Following" : "+ Follow");
                                }
                                if (btnSetTag != null) btnSetTag.setVisibility(View.VISIBLE);
                                if (btnChatNow != null) btnChatNow.setVisibility(View.VISIBLE);
                            } else {
                                tvSearchResult.setText("No users found matching \"" + q + "\"");
                                if (btnFollow != null) btnFollow.setVisibility(View.GONE);
                                if (btnSetTag != null) btnSetTag.setVisibility(View.GONE);
                                if (btnChatNow != null) btnChatNow.setVisibility(View.GONE);
                            }
                        }
                    }

                    @Override
                    public void onFailure(retrofit2.Call<java.util.Map<String, Object>> call, Throwable t) {
                        tvSearchResult.setText("Demo Search: Aman Sharma (Husband)");
                        foundUserId[0] = "10f31e6e-cbb7-465d-b820-8b215b74852e";
                        foundUserName[0] = "Aman Sharma";
                        if (btnFollow != null) btnFollow.setVisibility(View.VISIBLE);
                        if (btnSetTag != null) btnSetTag.setVisibility(View.VISIBLE);
                        if (btnChatNow != null) btnChatNow.setVisibility(View.VISIBLE);
                    }
                });
            });
        }

        if (btnSetTag != null) {
            btnSetTag.setOnClickListener(v -> {
                if (foundUserId[0] == null) return;
                final String[] tagOptions = new String[]{"Husband ❤️", "Wife 🌸", "Best Friend 💕", "Sister 🌷", "Mother 👵", "Partner 💍", "Doctor 🩺"};
                new android.app.AlertDialog.Builder(getContext())
                        .setTitle("🏷️ Set Relationship Tag for " + foundUserName[0])
                        .setItems(tagOptions, (dialog, which) -> {
                            String selected = tagOptions[which];
                            userTag[0] = selected;

                            if (getContext() != null) {
                                android.content.SharedPreferences prefs = getContext().getSharedPreferences("cyclecare_contact_tags", android.content.Context.MODE_PRIVATE);
                                prefs.edit()
                                        .putString("tag_" + foundUserId[0], selected)
                                        .putString("tag_" + foundUserName[0].toLowerCase().trim(), selected)
                                        .apply();
                            }

                            java.util.Map<String, String> body = new java.util.HashMap<>();
                            body.put("target_user_id", foundUserId[0]);
                            body.put("target_name", foundUserName[0]);
                            body.put("tag", selected);

                            com.cyclecare.api.ApiClient.getApiService(getContext()).setContactTag(body).enqueue(new retrofit2.Callback<java.util.Map<String, Object>>() {
                                @Override
                                public void onResponse(retrofit2.Call<java.util.Map<String, Object>> call, retrofit2.Response<java.util.Map<String, Object>> response) {
                                    Toast.makeText(getContext(), "✓ Assigned tag: " + selected, Toast.LENGTH_SHORT).show();
                                    tvSearchResult.setText(foundUserName[0] + " • Tag: " + selected);
                                }

                                @Override
                                public void onFailure(retrofit2.Call<java.util.Map<String, Object>> call, Throwable t) {
                                    Toast.makeText(getContext(), "Tag updated in demo mode: " + selected, Toast.LENGTH_SHORT).show();
                                    tvSearchResult.setText(foundUserName[0] + " • Tag: " + selected);
                                }
                            });
                        })
                        .setNegativeButton("Cancel", null)
                        .show();
            });
        }

        if (btnChatNow != null) {
            btnChatNow.setOnClickListener(v -> {
                if (foundUserId[0] == null) return;
                Intent intent = new Intent(getActivity(), com.cyclecare.chat.CircleChatActivity.class);
                intent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_CONTACT_NAME, foundUserName[0]);
                intent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_RELATIONSHIP, userTag[0]);
                intent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_PARTNER_USER_ID, foundUserId[0]);
                startActivity(intent);
            });
        }

        // Load Real Follower & Following Stats from DB
        Runnable refreshStats = () -> {
            com.cyclecare.api.ApiClient.getApiService(getContext()).getUserSocialStats("me").enqueue(new retrofit2.Callback<java.util.Map<String, Object>>() {
                @Override
                public void onResponse(retrofit2.Call<java.util.Map<String, Object>> call, retrofit2.Response<java.util.Map<String, Object>> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        java.util.Map<?, ?> stats = (java.util.Map<?, ?>) response.body().get("stats");
                        if (stats != null) {
                            Object followers = stats.get("followers");
                            Object following = stats.get("following");
                            if (tvFollowers != null && followers != null) {
                                tvFollowers.setText(String.valueOf(followers));
                            }
                            if (tvFollowing != null && following != null) {
                                tvFollowing.setText(String.valueOf(following));
                            }
                        }
                    }
                }

                @Override
                public void onFailure(retrofit2.Call<java.util.Map<String, Object>> call, Throwable t) {
                    // Fallback to local count if offline
                }
            });
        };
        refreshStats.run();

        // Followers Box Click -> Show Real Followers List Dialog
        View llFollowersBox = view.findViewById(R.id.ll_followers_box);
        if (llFollowersBox != null) {
            llFollowersBox.setOnClickListener(v -> showSocialUsersDialog(true, refreshStats));
        }

        // Following Box Click -> Show Real Following List Dialog
        View llFollowingBox = view.findViewById(R.id.ll_following_box);
        if (llFollowingBox != null) {
            llFollowingBox.setOnClickListener(v -> showSocialUsersDialog(false, refreshStats));
        }

        if (btnFollow != null) {
            btnFollow.setOnClickListener(v -> {
                if (foundUserId[0] == null) return;
                java.util.Map<String, String> body = new java.util.HashMap<>();
                body.put("target_user_id", foundUserId[0]);

                if (!isFollowingUser[0]) {
                    com.cyclecare.api.ApiClient.getApiService(getContext()).followUser(body).enqueue(new retrofit2.Callback<java.util.Map<String, Object>>() {
                        @Override
                        public void onResponse(retrofit2.Call<java.util.Map<String, Object>> call, retrofit2.Response<java.util.Map<String, Object>> response) {
                            isFollowingUser[0] = true;
                            btnFollow.setText("✓ Following (Tap to Unfollow)");
                            Toast.makeText(getContext(), "Now following user! Added to Circle.", Toast.LENGTH_SHORT).show();
                            refreshStats.run();
                        }

                        @Override
                        public void onFailure(retrofit2.Call<java.util.Map<String, Object>> call, Throwable t) {
                            isFollowingUser[0] = true;
                            btnFollow.setText("✓ Following (Tap to Unfollow)");
                            Toast.makeText(getContext(), "Followed in Demo Mode!", Toast.LENGTH_SHORT).show();
                            refreshStats.run();
                        }
                    });
                } else {
                    com.cyclecare.api.ApiClient.getApiService(getContext()).unfollowUser(body).enqueue(new retrofit2.Callback<java.util.Map<String, Object>>() {
                        @Override
                        public void onResponse(retrofit2.Call<java.util.Map<String, Object>> call, retrofit2.Response<java.util.Map<String, Object>> response) {
                            isFollowingUser[0] = false;
                            btnFollow.setText("+ Follow User");
                            Toast.makeText(getContext(), "Unfollowed user.", Toast.LENGTH_SHORT).show();
                            refreshStats.run();
                        }

                        @Override
                        public void onFailure(retrofit2.Call<java.util.Map<String, Object>> call, Throwable t) {
                            isFollowingUser[0] = false;
                            btnFollow.setText("+ Follow User");
                            refreshStats.run();
                        }
                    });
                }
            });
        }

        View cardPartnerCare = view.findViewById(R.id.card_partner_care);
        if (cardPartnerCare != null) {
            cardPartnerCare.setOnClickListener(v -> {
                Intent intent = new Intent(getActivity(), PartnerCareActivity.class);
                startActivity(intent);
            });
        }

        View cardCircleChat = view.findViewById(R.id.card_circle_chat);
        if (cardCircleChat != null) {
            cardCircleChat.setOnClickListener(v -> {
                Intent intent = new Intent(getActivity(), com.cyclecare.chat.CircleConversationsActivity.class);
                startActivity(intent);
            });
        }

        View cardMyOrders = view.findViewById(R.id.card_my_orders);
        if (cardMyOrders != null) {
            cardMyOrders.setOnClickListener(v -> {
                Intent intent = new Intent(getActivity(), com.cyclecare.store.OrdersActivity.class);
                startActivity(intent);
            });
        }

        View cardMyAddresses = view.findViewById(R.id.card_my_addresses);
        if (cardMyAddresses != null) {
            cardMyAddresses.setOnClickListener(v -> {
                Intent intent = new Intent(getActivity(), com.cyclecare.store.AddressManagementActivity.class);
                startActivity(intent);
            });
        }

        btnShareApk.setOnClickListener(v -> shareApkFile());

        View btnSettingsTop = view.findViewById(R.id.btn_profile_settings_top);
        if (btnSettingsTop != null) {
            btnSettingsTop.setOnClickListener(v -> {
                startActivity(new Intent(getActivity(), SettingsActivity.class));
            });
        }

        btnAppSettings.setOnClickListener(v -> {
            Intent intent = new Intent(getActivity(), SettingsActivity.class);
            startActivity(intent);
        });

        btnLogout.setOnClickListener(v -> {
            if (getActivity() != null) {
                SharedPreferences prefs = getActivity().getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE);
                prefs.edit().clear().apply();
                Intent intent = new Intent(getActivity(), LoginActivity.class);
                intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                startActivity(intent);
            }
        });

        return view;
    }

    private void shareApkFile() {
        try {
            Context context = getContext();
            if (context == null) return;

            ApplicationInfo appInfo = context.getApplicationInfo();
            File originalApk = new File(appInfo.sourceDir);

            File tempApk = new File(context.getExternalCacheDir(), "CycleCare.apk");
            copyFile(originalApk, tempApk);

            Uri apkUri = FileProvider.getUriForFile(context, context.getPackageName() + ".fileprovider", tempApk);

            Intent shareIntent = new Intent(Intent.ACTION_SEND);
            shareIntent.setType("application/vnd.android.package-archive");
            shareIntent.putExtra(Intent.EXTRA_STREAM, apkUri);
            shareIntent.putExtra(Intent.EXTRA_SUBJECT, "CycleCare App APK");
            shareIntent.putExtra(Intent.EXTRA_TEXT, "Here is the CycleCare Android App APK file!");
            shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);

            startActivity(Intent.createChooser(shareIntent, "Share CycleCare APK File via"));
        } catch (Exception e) {
            e.printStackTrace();
            Toast.makeText(getContext(), "Unable to share APK: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void copyFile(File src, File dst) throws Exception {
        try (InputStream in = new FileInputStream(src);
             OutputStream out = new FileOutputStream(dst)) {
            byte[] buf = new byte[1024 * 4];
            int len;
            while ((len = in.read(buf)) > 0) {
                out.write(buf, 0, len);
            }
        }
    }

    private void showSocialUsersDialog(boolean isFollowers, Runnable onDismissRefresh) {
        if (getContext() == null) return;
        com.google.android.material.bottomsheet.BottomSheetDialog dialog =
                new com.google.android.material.bottomsheet.BottomSheetDialog(requireContext());
        View sheetView = LayoutInflater.from(getContext()).inflate(R.layout.dialog_social_users, null);
        dialog.setContentView(sheetView);

        TextView tvTitle = sheetView.findViewById(R.id.tv_dialog_social_title);
        TextView tvCount = sheetView.findViewById(R.id.tv_dialog_social_count);
        View btnClose = sheetView.findViewById(R.id.btn_close_social_dialog);
        android.widget.ProgressBar progressBar = sheetView.findViewById(R.id.pb_social_loading);
        TextView tvEmpty = sheetView.findViewById(R.id.tv_social_empty);
        androidx.recyclerview.widget.RecyclerView rvUsers = sheetView.findViewById(R.id.rv_social_users);

        tvTitle.setText(isFollowers ? "👥 Followers" : "✨ Following");
        rvUsers.setLayoutManager(new androidx.recyclerview.widget.LinearLayoutManager(getContext()));

        if (btnClose != null) {
            btnClose.setOnClickListener(v -> dialog.dismiss());
        }

        retrofit2.Call<java.util.Map<String, Object>> call = isFollowers ?
                com.cyclecare.api.ApiClient.getApiService(getContext()).getFollowers("me") :
                com.cyclecare.api.ApiClient.getApiService(getContext()).getFollowing("me");

        call.enqueue(new retrofit2.Callback<java.util.Map<String, Object>>() {
            @Override
            public void onResponse(retrofit2.Call<java.util.Map<String, Object>> call, retrofit2.Response<java.util.Map<String, Object>> response) {
                if (progressBar != null) progressBar.setVisibility(View.GONE);
                if (response.isSuccessful() && response.body() != null) {
                    java.util.List<java.util.Map<String, Object>> usersList =
                            (java.util.List<java.util.Map<String, Object>>) response.body().get("users");
                    if (usersList != null && !usersList.isEmpty()) {
                        tvCount.setText("(" + usersList.size() + ")");
                        tvEmpty.setVisibility(View.GONE);
                        rvUsers.setVisibility(View.VISIBLE);
                        SocialUsersAdapter adapter = new SocialUsersAdapter(getContext(), usersList, isFollowers, () -> {
                            if (onDismissRefresh != null) onDismissRefresh.run();
                        });
                        rvUsers.setAdapter(adapter);
                    } else {
                        tvCount.setText("(0)");
                        rvUsers.setVisibility(View.GONE);
                        tvEmpty.setVisibility(View.VISIBLE);
                        tvEmpty.setText(isFollowers ? "You don't have any followers yet." : "You are not following anyone yet.");
                    }
                } else {
                    tvCount.setText("(0)");
                    rvUsers.setVisibility(View.GONE);
                    tvEmpty.setVisibility(View.VISIBLE);
                    tvEmpty.setText("Unable to load users. Please check connection.");
                }
            }

            @Override
            public void onFailure(retrofit2.Call<java.util.Map<String, Object>> call, Throwable t) {
                if (progressBar != null) progressBar.setVisibility(View.GONE);
                tvCount.setText("(0)");
                rvUsers.setVisibility(View.GONE);
                tvEmpty.setVisibility(View.VISIBLE);
                tvEmpty.setText("Offline or network error.");
            }
        });

        dialog.setOnDismissListener(d -> {
            if (onDismissRefresh != null) onDismissRefresh.run();
        });

        dialog.show();
    }
}
