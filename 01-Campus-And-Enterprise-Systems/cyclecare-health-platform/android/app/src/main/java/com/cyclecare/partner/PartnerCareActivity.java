package com.cyclecare.partner;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.api.ApiService;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class PartnerCareActivity extends AppCompatActivity {

    private ApiService apiService;
    private SharedPreferences prefs;

    private TextView tvMyCycleCareId;
    private Button btnCopyId, btnShareInvite;

    // Connected views
    private LinearLayout llConnectedView;
    private TextView tvPartnerName, tvPartnerHandle;
    private TextView tvPartnerRelationshipBadge, tvPartnerPrimaryBadge;
    private Button btnSendCarePackage, btnManagePermissions, btnDisconnectPartner, btnEditRelationship;
    private LinearLayout cardSharedCycle;
    private TextView tvCycleWindowDates, tvCycleWindowTip;

    // Multi-member family sharing
    private LinearLayout llFamilyMembersSection;
    private LinearLayout llFamilyMembersList;

    // Connect input views
    private LinearLayout llConnectInputView;
    private EditText etPartnerId;
    private Button btnSearchPartner;
    private LinearLayout llSearchResult;
    private TextView tvSearchedName, tvSearchedHandle;
    private Button btnSendRequest;

    // Pending requests
    private LinearLayout llPendingRequestsSection;
    private LinearLayout llIncomingRequestsList;

    private String currentConnectionId = null;
    private String currentPartnerName = null;
    private String searchedPartnerId = null;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_partner_care);

        apiService = ApiClient.getApiService(this);
        prefs = getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE);

        initViews();
        setupListeners();
        loadOwnCycleCareId();
        loadPartnerData();
        handleIncomingDeepLink();
    }

    private void handleIncomingDeepLink() {
        Intent intent = getIntent();
        if (intent != null && intent.getData() != null) {
            android.net.Uri data = intent.getData();
            if ("cyclecare".equals(data.getScheme()) && "connect".equals(data.getHost())) {
                List<String> pathSegments = data.getPathSegments();
                if (pathSegments != null && !pathSegments.isEmpty()) {
                    String token = pathSegments.get(0);
                    Map<String, Object> body = new HashMap<>();
                    body.put("invite_token", token);
                    apiService.sendPartnerRequest(body).enqueue(new Callback<Map<String, Object>>() {
                        @Override
                        public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                            if (response.isSuccessful()) {
                                Toast.makeText(PartnerCareActivity.this, "Connected via invite link!", Toast.LENGTH_LONG).show();
                                loadPartnerData();
                            }
                        }
                        @Override
                        public void onFailure(Call<Map<String, Object>> call, Throwable t) {}
                    });
                }
            }
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadPartnerData();
    }

    private void initViews() {
        ImageButton btnBack = findViewById(R.id.btn_back);
        if (btnBack != null) {
            btnBack.setOnClickListener(v -> finish());
        }

        tvMyCycleCareId = findViewById(R.id.tv_my_cyclecare_id);
        btnCopyId = findViewById(R.id.btn_copy_id);
        btnShareInvite = findViewById(R.id.btn_share_invite);

        llConnectedView = findViewById(R.id.ll_connected_view);
        tvPartnerName = findViewById(R.id.tv_partner_name);
        tvPartnerHandle = findViewById(R.id.tv_partner_handle);
        tvPartnerRelationshipBadge = findViewById(R.id.tv_partner_relationship_badge);
        tvPartnerPrimaryBadge = findViewById(R.id.tv_partner_primary_badge);
        btnEditRelationship = findViewById(R.id.btn_edit_relationship);
        Button btnOpenCircleChat = findViewById(R.id.btn_open_circle_chat);
        if (btnOpenCircleChat != null) {
            btnOpenCircleChat.setOnClickListener(v -> {
                Intent chatIntent = new Intent(this, com.cyclecare.chat.CircleChatActivity.class);
                chatIntent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_CONNECTION_ID, currentConnectionId != null ? currentConnectionId : "demo-circle-connection");
                chatIntent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_CONTACT_NAME, currentPartnerName != null ? currentPartnerName : "Husband / Partner");
                chatIntent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_RELATIONSHIP, "Partner");
                startActivity(chatIntent);
            });
        }
        btnSendCarePackage = findViewById(R.id.btn_send_care_package);
        btnManagePermissions = findViewById(R.id.btn_manage_permissions);
        btnDisconnectPartner = findViewById(R.id.btn_disconnect_partner);
        cardSharedCycle = findViewById(R.id.card_shared_cycle);
        tvCycleWindowDates = findViewById(R.id.tv_cycle_window_dates);
        tvCycleWindowTip = findViewById(R.id.tv_cycle_window_tip);

        // Family members section
        llFamilyMembersSection = findViewById(R.id.ll_family_members_section);
        llFamilyMembersList = findViewById(R.id.ll_family_members_list);

        llConnectInputView = findViewById(R.id.ll_connect_input_view);
        etPartnerId = findViewById(R.id.et_partner_id);
        btnSearchPartner = findViewById(R.id.btn_search_partner);
        llSearchResult = findViewById(R.id.ll_search_result);
        tvSearchedName = findViewById(R.id.tv_searched_name);
        tvSearchedHandle = findViewById(R.id.tv_searched_handle);
        btnSendRequest = findViewById(R.id.btn_send_request);

        llPendingRequestsSection = findViewById(R.id.ll_pending_requests_section);
        llIncomingRequestsList = findViewById(R.id.ll_incoming_requests_list);
    }

    private void setupListeners() {
        btnCopyId.setOnClickListener(v -> copyCycleCareId());
        btnShareInvite.setOnClickListener(v -> shareInviteLink());
        btnSearchPartner.setOnClickListener(v -> searchPartner());
        btnSendRequest.setOnClickListener(v -> sendPartnerRequest());

        btnSendCarePackage.setOnClickListener(v -> {
            Intent intent = new Intent(this, CarePackageActivity.class);
            intent.putExtra("connection_id", currentConnectionId != null ? currentConnectionId : "demo_connection");
            intent.putExtra("partner_name", currentPartnerName != null ? currentPartnerName : "Partner");
            startActivity(intent);
        });

        btnManagePermissions.setOnClickListener(v -> {
            showPermissionsDialog(currentConnectionId != null ? currentConnectionId : "demo_connection");
        });

        if (btnEditRelationship != null) {
            btnEditRelationship.setOnClickListener(v -> {
                if (currentConnectionId != null) {
                    showEditRelationshipDialog(currentConnectionId, currentPartnerName);
                } else {
                    Toast.makeText(this, "No active partner connection selected", Toast.LENGTH_SHORT).show();
                }
            });
        }

        btnDisconnectPartner.setOnClickListener(v -> {
            if (currentConnectionId != null) {
                confirmDisconnect(currentConnectionId);
            } else {
                Toast.makeText(this, "Disconnected.", Toast.LENGTH_SHORT).show();
                llConnectedView.setVisibility(View.GONE);
                llConnectInputView.setVisibility(View.VISIBLE);
            }
        });
    }

    private void loadOwnCycleCareId() {
        String cyclecareId = prefs.getString("cyclecare_id", null);
        if (TextUtils.isEmpty(cyclecareId)) {
            String userName = prefs.getString("user_name", "user").toLowerCase().replaceAll("[^a-z0-9]", "");
            if (userName.length() < 3) userName = "careuser";
            cyclecareId = "@" + userName + (int) (1000 + Math.random() * 9000);
            prefs.edit().putString("cyclecare_id", cyclecareId).apply();
        }
        if (!cyclecareId.startsWith("@")) {
            cyclecareId = "@" + cyclecareId;
        }
        tvMyCycleCareId.setText(cyclecareId);
    }

    private void copyCycleCareId() {
        String id = tvMyCycleCareId.getText().toString();
        ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        ClipData clip = ClipData.newPlainText("CycleCare ID", id);
        if (clipboard != null) {
            clipboard.setPrimaryClip(clip);
            Toast.makeText(this, "CycleCare ID copied to clipboard!", Toast.LENGTH_SHORT).show();
        }
    }

    private void shareInviteLink() {
        String myId = tvMyCycleCareId.getText().toString();
        apiService.createPartnerInvite().enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                String inviteUrl = "https://cyclecare-57my.onrender.com/invite/" + myId.replace("@", "");
                if (response.isSuccessful() && response.body() != null && response.body().containsKey("invite_url")) {
                    inviteUrl = String.valueOf(response.body().get("invite_url"));
                }
                openShareSheet(myId, inviteUrl);
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                openShareSheet(myId, "https://cyclecare-57my.onrender.com/connect/" + myId.replace("@", ""));
            }
        });
    }

    private void openShareSheet(String myId, String inviteUrl) {
        String shareText = "Connect with me on CycleCare to share care, comfort, and support!\n"
                + "My CycleCare ID: " + myId + "\n"
                + "Private Invite: " + inviteUrl;

        Intent sendIntent = new Intent(Intent.ACTION_SEND);
        sendIntent.putExtra(Intent.EXTRA_TEXT, shareText);
        sendIntent.setType("text/plain");
        Intent shareIntent = Intent.createChooser(sendIntent, "Share CycleCare Invite via");
        startActivity(shareIntent);
    }

    private void searchPartner() {
        String query = etPartnerId.getText().toString().trim();
        if (TextUtils.isEmpty(query)) {
            etPartnerId.setError("Enter CycleCare ID");
            return;
        }

        btnSearchPartner.setEnabled(false);
        btnSearchPartner.setText("Searching...");

        apiService.searchPartner(query).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                btnSearchPartner.setEnabled(true);
                btnSearchPartner.setText("Search");

                if (response.isSuccessful() && response.body() != null && Boolean.TRUE.equals(response.body().get("success"))) {
                    Map<String, Object> partner = (Map<String, Object>) response.body().get("partner");
                    if (partner != null) {
                        searchedPartnerId = String.valueOf(partner.get("id"));
                        String handle = String.valueOf(partner.get("cyclecare_id"));
                        String name = String.valueOf(partner.get("display_name"));

                        llSearchResult.setVisibility(View.VISIBLE);
                        tvSearchedName.setText(name);
                        tvSearchedHandle.setText(handle);
                        return;
                    }
                }
                llSearchResult.setVisibility(View.GONE);
                Toast.makeText(PartnerCareActivity.this, "No user found with ID " + query, Toast.LENGTH_SHORT).show();
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                btnSearchPartner.setEnabled(true);
                btnSearchPartner.setText("Search");
                Toast.makeText(PartnerCareActivity.this, "Network error. Please try again.", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void sendPartnerRequest() {
        if (TextUtils.isEmpty(searchedPartnerId)) return;

        btnSendRequest.setEnabled(false);
        btnSendRequest.setText("Sending...");

        Map<String, Object> body = new HashMap<>();
        body.put("recipient_id", searchedPartnerId);

        apiService.sendPartnerRequest(body).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                btnSendRequest.setEnabled(true);
                btnSendRequest.setText("Connect");

                if (response.isSuccessful()) {
                    Toast.makeText(PartnerCareActivity.this, "Connection request sent! Awaiting response.", Toast.LENGTH_LONG).show();
                    llSearchResult.setVisibility(View.GONE);
                    etPartnerId.setText("");
                    loadPartnerData();
                } else {
                    Toast.makeText(PartnerCareActivity.this, "Could not send request. Please verify.", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                btnSendRequest.setEnabled(true);
                btnSendRequest.setText("Connect");
                Toast.makeText(PartnerCareActivity.this, "Failed to connect: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void loadPartnerData() {
        apiService.getPartnerRequests().enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    Map<String, Object> primaryPartner = (Map<String, Object>) body.get("primary_partner");
                    List<Map<String, Object>> familyMembers = (List<Map<String, Object>>) body.get("family_members");
                    List<Map<String, Object>> allActive = (List<Map<String, Object>>) body.get("all_active");
                    if (allActive == null) {
                        allActive = (List<Map<String, Object>>) body.get("active");
                    }
                    List<Map<String, Object>> incomingList = (List<Map<String, Object>>) body.get("incoming");

                    // 1. Primary Partner Resolution
                    if (primaryPartner != null) {
                        bindPrimaryPartnerCard(primaryPartner);
                    } else if (allActive != null && !allActive.isEmpty()) {
                        bindPrimaryPartnerCard(allActive.get(0));
                    } else {
                        currentConnectionId = null;
                        llConnectedView.setVisibility(View.GONE);
                    }

                    // 2. Family Members List Resolution (Multi-member family support)
                    if (familyMembers != null && !familyMembers.isEmpty()) {
                        llFamilyMembersSection.setVisibility(View.VISIBLE);
                        renderFamilyMembers(familyMembers);
                    } else {
                        llFamilyMembersSection.setVisibility(View.GONE);
                        if (llFamilyMembersList != null) {
                            llFamilyMembersList.removeAllViews();
                        }
                    }

                    // 3. Connect Input View Toggle
                    if (primaryPartner == null && (allActive == null || allActive.isEmpty())) {
                        llConnectInputView.setVisibility(View.VISIBLE);
                    } else {
                        llConnectInputView.setVisibility(View.GONE);
                    }

                    renderIncomingRequests(incomingList);
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                // Ignore transient network errors
            }
        });
    }

    private void bindPrimaryPartnerCard(Map<String, Object> partnerMap) {
        currentConnectionId = String.valueOf(partnerMap.get("id"));
        Map<String, Object> partnerInfo = (Map<String, Object>) partnerMap.get("partner_profile");
        if (partnerInfo == null) {
            partnerInfo = (Map<String, Object>) partnerMap.get("partner");
        }

        if (partnerInfo != null) {
            String name = String.valueOf(partnerInfo.get("display_name"));
            currentPartnerName = (!TextUtils.isEmpty(name) && !"null".equalsIgnoreCase(name)) ? name : "Partner";
            tvPartnerName.setText(currentPartnerName);
            String handle = String.valueOf(partnerInfo.get("cyclecare_id"));
            tvPartnerHandle.setText((!TextUtils.isEmpty(handle) && !"null".equalsIgnoreCase(handle)) ? handle : "");
        } else {
            currentPartnerName = "Partner";
            tvPartnerName.setText("Partner");
            tvPartnerHandle.setText("");
        }

        String rel = String.valueOf(partnerMap.get("resolved_relationship"));
        if (TextUtils.isEmpty(rel) || "null".equalsIgnoreCase(rel)) {
            rel = String.valueOf(partnerMap.get("relationship"));
        }
        if (tvPartnerRelationshipBadge != null) {
            tvPartnerRelationshipBadge.setText((!TextUtils.isEmpty(rel) && !"null".equalsIgnoreCase(rel)) ? rel : "Partner");
        }

        llConnectedView.setVisibility(View.VISIBLE);
        loadSharedCycle(currentConnectionId);
    }

    private void renderFamilyMembers(List<Map<String, Object>> members) {
        if (llFamilyMembersList == null) return;
        llFamilyMembersList.removeAllViews();
        LayoutInflater inflater = LayoutInflater.from(this);

        for (Map<String, Object> member : members) {
            View card = inflater.inflate(R.layout.item_family_member_card, llFamilyMembersList, false);

            TextView tvInitials = card.findViewById(R.id.tv_member_initials);
            TextView tvName = card.findViewById(R.id.tv_member_name);
            TextView tvHandle = card.findViewById(R.id.tv_member_handle);
            TextView tvBadge = card.findViewById(R.id.tv_member_relationship_badge);
            TextView tvRank = card.findViewById(R.id.tv_member_priority_rank);
            Button btnStatus = card.findViewById(R.id.btn_member_status);
            Button btnChat = card.findViewById(R.id.btn_member_chat);
            Button btnSettings = card.findViewById(R.id.btn_member_settings);

            String connId = String.valueOf(member.get("id"));
            Map<String, Object> prof = (Map<String, Object>) member.get("partner_profile");
            if (prof == null) prof = (Map<String, Object>) member.get("partner");

            String rawName = prof != null ? String.valueOf(prof.get("display_name")) : "Family Member";
            String mName = (!TextUtils.isEmpty(rawName) && !"null".equalsIgnoreCase(rawName)) ? rawName : "Family Member";
            String mHandle = prof != null ? String.valueOf(prof.get("cyclecare_id")) : "";
            String mRel = String.valueOf(member.get("resolved_relationship"));
            if (TextUtils.isEmpty(mRel) || "null".equalsIgnoreCase(mRel)) {
                mRel = String.valueOf(member.get("relationship"));
            }
            if (TextUtils.isEmpty(mRel) || "null".equalsIgnoreCase(mRel)) mRel = "Family";

            tvName.setText(mName);
            tvHandle.setText((!TextUtils.isEmpty(mHandle) && !"null".equalsIgnoreCase(mHandle)) ? mHandle : "");
            tvBadge.setText(mRel);
            tvInitials.setText(mName.length() >= 2 ? mName.substring(0, 2).toUpperCase() : mName.substring(0, 1).toUpperCase());
            tvRank.setText("Priority: " + (member.get("priority_rank") != null ? member.get("priority_rank") : "3"));

            final String fConnId = connId;
            final String fName = mName;
            final String fRel = mRel;

            btnStatus.setOnClickListener(v -> showMemberStatusDialog(fConnId, fName, fRel));

            btnChat.setOnClickListener(v -> {
                Intent chatIntent = new Intent(this, com.cyclecare.chat.CircleChatActivity.class);
                chatIntent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_CONNECTION_ID, fConnId);
                chatIntent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_CONTACT_NAME, fName);
                chatIntent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_RELATIONSHIP, fRel);
                startActivity(chatIntent);
            });

            btnSettings.setOnClickListener(v -> showPermissionsDialog(fConnId));

            llFamilyMembersList.addView(card);
        }
    }

    private void showMemberStatusDialog(String connId, String name, String relationship) {
        apiService.getMemberStatus(connId).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    Map<String, Object> cyclePhase = (Map<String, Object>) body.get("cycle_phase");
                    if (cyclePhase == null && body.get("status") instanceof Map) {
                        cyclePhase = (Map<String, Object>) ((Map<String, Object>) body.get("status")).get("cycle_phase");
                    }
                    Map<String, Object> cycleWindow = (Map<String, Object>) body.get("cycle_window");
                    if (cycleWindow == null && body.get("status") instanceof Map) {
                        cycleWindow = (Map<String, Object>) ((Map<String, Object>) body.get("status")).get("cycle_window");
                    }

                    StringBuilder sb = new StringBuilder();
                    sb.append("Relationship: ").append(relationship).append("\n\n");

                    if (cyclePhase != null && Boolean.TRUE.equals(cyclePhase.get("permitted"))) {
                        sb.append("Cycle Phase: ").append(cyclePhase.get("phase")).append("\n");
                        if (cyclePhase.get("description") != null) {
                            sb.append(cyclePhase.get("description")).append("\n");
                        }
                    } else {
                        sb.append("Cycle Phase: Private (Not Shared)\n");
                    }

                    if (cycleWindow != null && Boolean.TRUE.equals(cycleWindow.get("permitted"))) {
                        sb.append("\nEstimated Window: ").append(cycleWindow.get("estimated_start"))
                          .append(" to ").append(cycleWindow.get("estimated_end")).append("\n");
                        if (cycleWindow.get("support_tip") != null) {
                            sb.append("\nTip: ").append(cycleWindow.get("support_tip")).append("\n");
                        }
                    } else {
                        sb.append("Preparation Window: Private (Not Shared)\n");
                    }

                    sb.append("\nNote: Predictions are estimates for mutual comfort and care only, not medical diagnosis.");

                    new AlertDialog.Builder(PartnerCareActivity.this)
                            .setTitle(name + " • Sharing Status")
                            .setMessage(sb.toString())
                            .setPositiveButton("OK", null)
                            .show();
                } else {
                    Toast.makeText(PartnerCareActivity.this, "Could not fetch status: Restricted", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                Toast.makeText(PartnerCareActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void showEditRelationshipDialog(String connId, String name) {
        final String[] options = new String[] {
            "Husband", "Wife", "Boyfriend", "Girlfriend",
            "Father", "Mother", "Daughter", "Son",
            "Sister", "Brother", "Best Friend", "Family", "Other"
        };

        new AlertDialog.Builder(this)
                .setTitle("Select Relationship for " + name)
                .setItems(options, (dialog, which) -> {
                    String selected = options[which];
                    Map<String, Object> body = new HashMap<>();
                    body.put("relationship", selected);
                    apiService.updatePartnerRelationship(connId, body).enqueue(new Callback<Map<String, Object>>() {
                        @Override
                        public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                            if (response.isSuccessful() && response.body() != null) {
                                Object recipObj = response.body().get("reciprocal_relationship");
                                String msg = "Relationship updated to " + selected;
                                if (recipObj != null) {
                                    msg += " (Reciprocal: " + recipObj + ")";
                                }
                                Toast.makeText(PartnerCareActivity.this, msg, Toast.LENGTH_SHORT).show();
                                loadPartnerData();
                            } else {
                                Toast.makeText(PartnerCareActivity.this, "Failed to update relationship", Toast.LENGTH_SHORT).show();
                            }
                        }

                        @Override
                        public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                            Toast.makeText(PartnerCareActivity.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                        }
                    });
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void loadSharedCycle(String connectionId) {
        apiService.getSharedCycle(connectionId).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> cycle = (Map<String, Object>) response.body().get("shared_cycle");
                    if (cycle != null && Boolean.TRUE.equals(cycle.get("has_data"))) {
                        cardSharedCycle.setVisibility(View.VISIBLE);
                        String start = String.valueOf(cycle.get("estimated_window_start"));
                        String end = String.valueOf(cycle.get("estimated_window_end"));
                        String tip = String.valueOf(cycle.get("support_tip"));

                        tvCycleWindowDates.setText("Estimated Window: " + start + " - " + end);
                        if (!TextUtils.isEmpty(tip) && !"null".equals(tip)) {
                            tvCycleWindowTip.setText(tip);
                        }
                    } else {
                        cardSharedCycle.setVisibility(View.GONE);
                    }
                } else {
                    cardSharedCycle.setVisibility(View.GONE);
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                cardSharedCycle.setVisibility(View.GONE);
            }
        });
    }

    private void renderIncomingRequests(List<Map<String, Object>> incoming) {
        llIncomingRequestsList.removeAllViews();
        if (incoming == null || incoming.isEmpty()) {
            llPendingRequestsSection.setVisibility(View.GONE);
            return;
        }

        llPendingRequestsSection.setVisibility(View.VISIBLE);
        LayoutInflater inflater = LayoutInflater.from(this);

        for (Map<String, Object> req : incoming) {
            String reqId = String.valueOf(req.get("id"));
            Map<String, Object> p = (Map<String, Object>) req.get("partner");
            String pName = p != null ? String.valueOf(p.get("display_name")) : "Partner";
            String pHandle = p != null ? String.valueOf(p.get("cyclecare_id")) : "@user";

            View item = inflater.inflate(R.layout.view_partner_incoming_request, llIncomingRequestsList, false);
            TextView tvName = item.findViewById(R.id.tv_request_name);
            TextView tvHandle = item.findViewById(R.id.tv_request_handle);
            Button btnAccept = item.findViewById(R.id.btn_accept_request);
            Button btnDecline = item.findViewById(R.id.btn_decline_request);

            if (tvName != null) tvName.setText(pName);
            if (tvHandle != null) tvHandle.setText(pHandle);

            if (btnAccept != null) {
                btnAccept.setOnClickListener(v -> acceptRequest(reqId));
            }
            if (btnDecline != null) {
                btnDecline.setOnClickListener(v -> declineRequest(reqId));
            }

            llIncomingRequestsList.addView(item);
        }
    }

    private void acceptRequest(String requestId) {
        apiService.acceptPartnerRequest(requestId).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(PartnerCareActivity.this, "Connected! All sharing settings default to OFF for your privacy.", Toast.LENGTH_LONG).show();
                    loadPartnerData();
                } else {
                    Toast.makeText(PartnerCareActivity.this, "Could not accept request.", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                Toast.makeText(PartnerCareActivity.this, "Failed: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void declineRequest(String requestId) {
        apiService.declinePartnerRequest(requestId).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                Toast.makeText(PartnerCareActivity.this, "Request declined.", Toast.LENGTH_SHORT).show();
                loadPartnerData();
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                Toast.makeText(PartnerCareActivity.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void showPermissionsDialog(String connectionId) {
        apiService.getPartnerPermissions(connectionId).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> perms = (Map<String, Object>) response.body().get("permissions");
                    buildAndDisplayPermissionsDialog(connectionId, perms != null ? perms : new HashMap<>());
                } else {
                    Toast.makeText(PartnerCareActivity.this, "Failed to load sharing settings", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                Toast.makeText(PartnerCareActivity.this, "Network error", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void buildAndDisplayPermissionsDialog(String connectionId, Map<String, Object> currentPerms) {
        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_partner_permissions, null);
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Sharing & Privacy Controls")
                .setView(dialogView)
                .setPositiveButton("Save Settings", null)
                .setNegativeButton("Cancel", (d, w) -> d.dismiss())
                .create();

        CheckBox cbCycle = dialogView.findViewById(R.id.cb_perm_cycle);
        CheckBox cbCareKit = dialogView.findViewById(R.id.cb_perm_care_kit);
        CheckBox cbWishlist = dialogView.findViewById(R.id.cb_perm_wishlist);
        CheckBox cbSymptoms = dialogView.findViewById(R.id.cb_perm_symptoms);
        CheckBox cbShopping = dialogView.findViewById(R.id.cb_perm_shopping);
        CheckBox cbAddress = dialogView.findViewById(R.id.cb_perm_address);

        if (cbCycle != null) cbCycle.setChecked(Boolean.TRUE.equals(currentPerms.get("CYCLE_WINDOW")));
        if (cbCareKit != null) cbCareKit.setChecked(Boolean.TRUE.equals(currentPerms.get("CARE_KIT")));
        if (cbWishlist != null) cbWishlist.setChecked(Boolean.TRUE.equals(currentPerms.get("WISHLIST")));
        if (cbSymptoms != null) cbSymptoms.setChecked(Boolean.TRUE.equals(currentPerms.get("SYMPTOMS")));
        if (cbShopping != null) cbShopping.setChecked(Boolean.TRUE.equals(currentPerms.get("SHOPPING")));
        if (cbAddress != null) cbAddress.setChecked(Boolean.TRUE.equals(currentPerms.get("DELIVERY_ADDRESS")));

        dialog.show();

        dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            Map<String, Object> updatedPerms = new HashMap<>();
            if (cbCycle != null) updatedPerms.put("CYCLE_WINDOW", cbCycle.isChecked());
            if (cbCareKit != null) updatedPerms.put("CARE_KIT", cbCareKit.isChecked());
            if (cbWishlist != null) updatedPerms.put("WISHLIST", cbWishlist.isChecked());
            if (cbSymptoms != null) updatedPerms.put("SYMPTOMS", cbSymptoms.isChecked());
            if (cbShopping != null) updatedPerms.put("SHOPPING", cbShopping.isChecked());
            if (cbAddress != null) updatedPerms.put("DELIVERY_ADDRESS", cbAddress.isChecked());

            Map<String, Object> payload = new HashMap<>();
            payload.put("permissions", updatedPerms);

            apiService.updatePartnerPermissions(connectionId, payload).enqueue(new Callback<Map<String, Object>>() {
                @Override
                public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                    if (response.isSuccessful()) {
                        Toast.makeText(PartnerCareActivity.this, "Sharing settings updated instantly!", Toast.LENGTH_SHORT).show();
                        dialog.dismiss();
                        loadPartnerData();
                    } else {
                        Toast.makeText(PartnerCareActivity.this, "Failed to update settings.", Toast.LENGTH_SHORT).show();
                    }
                }

                @Override
                public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                    Toast.makeText(PartnerCareActivity.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        });
    }

    private void confirmDisconnect(String connectionId) {
        new AlertDialog.Builder(this)
                .setTitle("Disconnect Partner?")
                .setMessage("Are you sure you want to disconnect? All shared access will immediately stop, and your data will no longer be visible.")
                .setPositiveButton("Disconnect", (d, w) -> {
                    apiService.revokePartnerConnection(connectionId).enqueue(new Callback<Map<String, Object>>() {
                        @Override
                        public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                            Toast.makeText(PartnerCareActivity.this, "Disconnected successfully.", Toast.LENGTH_SHORT).show();
                            loadPartnerData();
                        }

                        @Override
                        public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                            Toast.makeText(PartnerCareActivity.this, "Error disconnecting: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                        }
                    });
                })
                .setNegativeButton("Cancel", null)
                .show();
    }
}
