package com.projectflow.android.ui.fragment;

import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;
import com.projectflow.android.R;
import com.projectflow.android.data.model.ConversationItem;
import com.projectflow.android.data.remote.model.DtoModels.ChatGroupDto;
import com.projectflow.android.data.remote.model.DtoModels.TeamMemberDto;
import com.projectflow.android.data.repository.ProjectFlowRepository;
import com.projectflow.android.ui.MainActivity;
import com.projectflow.android.ui.adapter.ConversationAdapter;

import java.util.ArrayList;
import java.util.List;

public class TeamFragment extends Fragment {

    // Top Segmented Tabs
    private TextView tabTeamMembers, tabSquadDiscussions;
    private View layoutTeamMembersSection, layoutSquadDiscussionsSection;

    // Team Members Views
    private EditText etSearchTeam;
    private TextView chipRoleAll, chipRoleAdmin, chipRoleManager, chipRoleMember;
    private RecyclerView rvTeamMembers;
    private LinearLayout llEmptyTeam;
    private TeamMemberAdapter adapter;
    private final List<TeamMemberDto> fullTeamList = new ArrayList<>();
    private String selectedRole = "ALL";
    private String searchQuery = "";

    // Squad Discussions Views
    private View btnCreateSquadGroup;
    private RecyclerView rvSquadDiscussions;
    private LinearLayout llEmptyDiscussions;
    private ConversationAdapter squadAdapter;
    private final List<ConversationItem> squadItems = new ArrayList<>();

    private SwipeRefreshLayout swipeRefreshTeam;
    private ProjectFlowRepository repository;
    private SharedPreferences prefs;
    private String activeTab = "MEMBERS";

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_team, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        repository = new ProjectFlowRepository(requireContext());
        prefs = requireContext().getSharedPreferences("projectflow_prefs", Context.MODE_PRIVATE);

        // Bind Tabs
        tabTeamMembers = view.findViewById(R.id.tabTeamMembers);
        tabSquadDiscussions = view.findViewById(R.id.tabSquadDiscussions);
        layoutTeamMembersSection = view.findViewById(R.id.layoutTeamMembersSection);
        layoutSquadDiscussionsSection = view.findViewById(R.id.layoutSquadDiscussionsSection);

        // Bind Members Section Views
        etSearchTeam = view.findViewById(R.id.etSearchTeam);
        chipRoleAll = view.findViewById(R.id.chipRoleAll);
        chipRoleAdmin = view.findViewById(R.id.chipRoleAdmin);
        chipRoleManager = view.findViewById(R.id.chipRoleManager);
        chipRoleMember = view.findViewById(R.id.chipRoleMember);
        rvTeamMembers = view.findViewById(R.id.rvTeamMembers);
        llEmptyTeam = view.findViewById(R.id.llEmptyTeam);

        // Bind Discussions Section Views
        btnCreateSquadGroup = view.findViewById(R.id.btnCreateSquadGroup);
        rvSquadDiscussions = view.findViewById(R.id.rvSquadDiscussions);
        llEmptyDiscussions = view.findViewById(R.id.llEmptyDiscussions);

        String currentUserRole = prefs.getString("user_role", "MEMBER");
        boolean isAdmin = "ADMINISTRATOR".equalsIgnoreCase(currentUserRole);
        if (btnCreateSquadGroup != null) {
            btnCreateSquadGroup.setVisibility(isAdmin ? View.VISIBLE : View.GONE);
        }

        swipeRefreshTeam = view.findViewById(R.id.swipeRefreshTeam);

        // Setup Members RecyclerView
        adapter = new TeamMemberAdapter(member -> openDirectChatWithMember(member));
        rvTeamMembers.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvTeamMembers.setAdapter(adapter);

        // Setup Group Discussions RecyclerView
        squadAdapter = new ConversationAdapter(item -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).navigateToFragment(
                        ChatFragment.newInstance(item.id, item.title, "GROUP"),
                        "Group: " + item.title
                );
            }
        });
        rvSquadDiscussions.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvSquadDiscussions.setAdapter(squadAdapter);

        // Tab click listeners
        tabTeamMembers.setOnClickListener(v -> switchTab("MEMBERS"));
        tabSquadDiscussions.setOnClickListener(v -> switchTab("DISCUSSIONS"));

        // Search listener
        etSearchTeam.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {
                searchQuery = (s != null) ? s.toString().trim().toLowerCase() : "";
                applyFilter();
            }
            @Override public void afterTextChanged(Editable s) {}
        });

        // Filter chips listeners
        chipRoleAll.setOnClickListener(v -> selectRoleFilter("ALL", chipRoleAll));
        chipRoleAdmin.setOnClickListener(v -> selectRoleFilter("ADMINISTRATOR", chipRoleAdmin));
        chipRoleManager.setOnClickListener(v -> selectRoleFilter("MANAGER", chipRoleManager));
        chipRoleMember.setOnClickListener(v -> selectRoleFilter("MEMBER", chipRoleMember));

        // Create Group Button Listener (Only Admin)
        btnCreateSquadGroup.setOnClickListener(v -> {
            String role = prefs.getString("user_role", "MEMBER");
            if (!"ADMINISTRATOR".equalsIgnoreCase(role)) {
                Toast.makeText(requireContext(), "Only Administrators can create discussion groups", Toast.LENGTH_SHORT).show();
                return;
            }
            showCreateSquadDialog();
        });

        swipeRefreshTeam.setColorSchemeResources(R.color.primary_earth, R.color.muted_clay);
        swipeRefreshTeam.setOnRefreshListener(this::loadAllData);

        loadAllData();
    }

    private void switchTab(String tab) {
        activeTab = tab;
        if ("MEMBERS".equals(tab)) {
            tabTeamMembers.setBackgroundResource(R.drawable.bg_chip_selected);
            tabTeamMembers.setTextColor(ContextCompat.getColor(requireContext(), R.color.white));
            tabSquadDiscussions.setBackground(null);
            tabSquadDiscussions.setTextColor(ContextCompat.getColor(requireContext(), R.color.text_main));

            layoutTeamMembersSection.setVisibility(View.VISIBLE);
            layoutSquadDiscussionsSection.setVisibility(View.GONE);
        } else {
            tabSquadDiscussions.setBackgroundResource(R.drawable.bg_chip_selected);
            tabSquadDiscussions.setTextColor(ContextCompat.getColor(requireContext(), R.color.white));
            tabTeamMembers.setBackground(null);
            tabTeamMembers.setTextColor(ContextCompat.getColor(requireContext(), R.color.text_main));

            layoutTeamMembersSection.setVisibility(View.GONE);
            layoutSquadDiscussionsSection.setVisibility(View.VISIBLE);
            loadSquadGroups();
        }
    }

    private void selectRoleFilter(String role, TextView selectedChip) {
        selectedRole = role;
        TextView[] chips = {chipRoleAll, chipRoleAdmin, chipRoleManager, chipRoleMember};
        for (TextView c : chips) {
            if (c == selectedChip) {
                c.setBackgroundResource(R.drawable.bg_chip_selected);
                c.setTextColor(ContextCompat.getColor(requireContext(), R.color.white));
            } else {
                c.setBackgroundResource(R.drawable.bg_chip_unselected);
                c.setTextColor(ContextCompat.getColor(requireContext(), R.color.text_main));
            }
        }
        applyFilter();
    }

    private final android.os.Handler teamPollHandler = new android.os.Handler(android.os.Looper.getMainLooper());
    private final Runnable teamPollRunnable = new Runnable() {
        @Override
        public void run() {
            if (!isResumed() || getActivity() == null) return;
            loadTeamDataSilently();
            teamPollHandler.postDelayed(this, 4000);
        }
    };

    private void loadTeamDataSilently() {
        if (repository == null) return;
        repository.fetchTeam(new ProjectFlowRepository.DataCallback<List<TeamMemberDto>>() {
            @Override
            public void onData(List<TeamMemberDto> data) {
                if (getActivity() != null && data != null) {
                    getActivity().runOnUiThread(() -> {
                        fullTeamList.clear();
                        fullTeamList.addAll(data);
                        applyFilter();
                    });
                }
            }
            @Override public void onError(String message) {}
        });
    }

    @Override
    public void onResume() {
        super.onResume();
        loadAllData();
        teamPollHandler.removeCallbacks(teamPollRunnable);
        teamPollHandler.postDelayed(teamPollRunnable, 4000);
    }

    @Override
    public void onPause() {
        super.onPause();
        teamPollHandler.removeCallbacks(teamPollRunnable);
    }

    private void loadAllData() {
        loadTeamData();
        loadSquadGroups();
    }

    private void loadTeamData() {
        repository.fetchTeam(new ProjectFlowRepository.DataCallback<List<TeamMemberDto>>() {
            @Override
            public void onData(List<TeamMemberDto> data) {
                if (getActivity() != null) {
                    getActivity().runOnUiThread(() -> {
                        swipeRefreshTeam.setRefreshing(false);
                        fullTeamList.clear();
                        if (data != null) fullTeamList.addAll(data);
                        applyFilter();
                    });
                }
            }

            @Override
            public void onError(String message) {
                if (getActivity() != null) {
                    getActivity().runOnUiThread(() -> swipeRefreshTeam.setRefreshing(false));
                }
            }
        });
    }

    private void loadSquadGroups() {
        repository.fetchChatGroups(new ProjectFlowRepository.DataCallback<List<ChatGroupDto>>() {
            @Override
            public void onData(List<ChatGroupDto> groups) {
                if (getActivity() != null) {
                    getActivity().runOnUiThread(() -> {
                        squadItems.clear();
                        if (groups != null) {
                            for (ChatGroupDto g : groups) {
                                String desc = g.description != null ? g.description : "Squad Discussion Channel";
                                String name = g.name != null ? g.name : "General Squad";
                                String initial = name.length() > 0 ? name.substring(0, 1).toUpperCase() : "#";
                                squadItems.add(new ConversationItem(
                                        g.channel != null ? g.channel : "general",
                                        name,
                                        desc,
                                        "Live",
                                        initial,
                                        ConversationItem.Type.GROUP,
                                        false
                                ));
                            }
                        }
                        if (squadAdapter != null) {
                            squadAdapter.setItems(squadItems);
                        }
                        if (squadItems.isEmpty()) {
                            rvSquadDiscussions.setVisibility(View.GONE);
                            llEmptyDiscussions.setVisibility(View.VISIBLE);
                        } else {
                            llEmptyDiscussions.setVisibility(View.GONE);
                            rvSquadDiscussions.setVisibility(View.VISIBLE);
                        }
                    });
                }
            }

            @Override
            public void onError(String message) {
                if (getActivity() != null) {
                    getActivity().runOnUiThread(() -> {
                        if (squadItems.isEmpty()) {
                            rvSquadDiscussions.setVisibility(View.GONE);
                            llEmptyDiscussions.setVisibility(View.VISIBLE);
                        }
                    });
                }
            }
        });
    }

    private void showCreateSquadDialog() {
        View dialogView = LayoutInflater.from(requireContext()).inflate(R.layout.dialog_create_group, null);
        AlertDialog dialog = new AlertDialog.Builder(requireContext())
                .setView(dialogView)
                .create();

        if (dialog.getWindow() != null) {
            dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
        }

        EditText etGroupName = dialogView.findViewById(R.id.etGroupName);
        EditText etGroupDesc = dialogView.findViewById(R.id.etGroupDescription);
        View btnCreate = dialogView.findViewById(R.id.btnSubmitGroup);
        View btnCancel = dialogView.findViewById(R.id.btnCancelGroup);

        btnCancel.setOnClickListener(v -> dialog.dismiss());
        btnCreate.setOnClickListener(v -> {
            String name = etGroupName.getText().toString().trim();
            String desc = etGroupDesc.getText().toString().trim();
            if (name.isEmpty()) {
                etGroupName.setError("Group name is required");
                return;
            }

            String role = prefs.getString("user_role", "ADMINISTRATOR");
            String email = prefs.getString("user_email", "admin@projectflow.io");

            repository.createChatGroup(name, desc, new ArrayList<>(), role, email, new ProjectFlowRepository.DataCallback<ChatGroupDto>() {
                @Override
                public void onData(ChatGroupDto newGroup) {
                    if (getActivity() != null) {
                        getActivity().runOnUiThread(() -> {
                            dialog.dismiss();
                            Toast.makeText(requireContext(), "Group channel created!", Toast.LENGTH_SHORT).show();
                            loadSquadGroups();
                        });
                    }
                }

                @Override
                public void onError(String message) {
                    if (getActivity() != null) {
                        getActivity().runOnUiThread(() -> {
                            Toast.makeText(requireContext(), "Error: " + message, Toast.LENGTH_SHORT).show();
                        });
                    }
                }
            });
        });

        dialog.show();
    }

    private void applyFilter() {
        List<TeamMemberDto> filtered = new ArrayList<>();
        for (TeamMemberDto m : fullTeamList) {
            boolean matchesRole = "ALL".equals(selectedRole) || selectedRole.equalsIgnoreCase(m.role);
            boolean matchesSearch = searchQuery.isEmpty() ||
                    (m.fullName != null && m.fullName.toLowerCase().contains(searchQuery)) ||
                    (m.email != null && m.email.toLowerCase().contains(searchQuery)) ||
                    (m.role != null && m.role.toLowerCase().contains(searchQuery));

            if (matchesRole && matchesSearch) {
                filtered.add(m);
            }
        }

        if (adapter != null) {
            adapter.setMembers(filtered);
        }

        if (filtered.isEmpty()) {
            rvTeamMembers.setVisibility(View.GONE);
            llEmptyTeam.setVisibility(View.VISIBLE);
        } else {
            llEmptyTeam.setVisibility(View.GONE);
            rvTeamMembers.setVisibility(View.VISIBLE);
        }
    }

    private void openDirectChatWithMember(TeamMemberDto member) {
        if (getActivity() instanceof MainActivity) {
            String myEmail = prefs.getString("user_email", "admin@projectflow.io");
            String targetEmail = member.email != null ? member.email : member.fullName;
            String clean1 = myEmail.replaceAll("[^a-zA-Z0-9]", "_").toLowerCase();
            String clean2 = targetEmail.replaceAll("[^a-zA-Z0-9]", "_").toLowerCase();
            String dmChannel = (clean1.compareTo(clean2) < 0)
                    ? "dm_" + clean1 + "_" + clean2
                    : "dm_" + clean2 + "_" + clean1;

            boolean isOnline = member.isOnline || (member.email != null && member.email.trim().toLowerCase().equals(myEmail.trim().toLowerCase()));
            ((MainActivity) getActivity()).navigateToFragment(
                    ChatFragment.newInstance(dmChannel, member.fullName, "DIRECT", isOnline),
                    "Chat: " + member.fullName
            );
        }
    }

    private static class TeamMemberAdapter extends RecyclerView.Adapter<TeamMemberAdapter.ViewHolder> {
        private final List<TeamMemberDto> members = new ArrayList<>();
        private final OnMemberClickListener listener;

        interface OnMemberClickListener { void onClick(TeamMemberDto member); }

        TeamMemberAdapter(OnMemberClickListener listener) { this.listener = listener; }

        void setMembers(List<TeamMemberDto> items) {
            members.clear();
            if (items != null) members.addAll(items);
            notifyDataSetChanged();
        }

        @NonNull
        @Override
        public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_team_member, parent, false);
            return new ViewHolder(v);
        }

        @Override
        public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
            TeamMemberDto m = members.get(position);
            holder.tvName.setText(m.fullName);
            holder.tvRole.setText(m.role);
            holder.tvProjects.setText(m.assignedTasksCount + (m.assignedTasksCount == 1 ? " Task Assigned" : " Tasks Assigned"));

            String initial = (m.fullName != null && !m.fullName.isEmpty()) ? m.fullName.substring(0, 1).toUpperCase() : "U";
            holder.tvInitial.setText(initial);

            android.content.SharedPreferences sp = holder.itemView.getContext().getSharedPreferences("projectflow_prefs", android.content.Context.MODE_PRIVATE);
            String currentEmail = sp.getString("user_email", "").trim().toLowerCase();
            boolean isMemberOnline = m.isOnline || (!currentEmail.isEmpty() && m.email != null && m.email.trim().toLowerCase().equals(currentEmail));

            if (holder.tvStatus != null) {
                if (isMemberOnline) {
                    holder.tvStatus.setText("ONLINE");
                    holder.tvStatus.setBackgroundResource(R.drawable.bg_badge_success);
                    holder.tvStatus.setTextColor(ContextCompat.getColor(holder.itemView.getContext(), R.color.earth_success));
                } else {
                    holder.tvStatus.setText("OFFLINE");
                    holder.tvStatus.setBackgroundResource(R.drawable.bg_chip_unselected);
                    holder.tvStatus.setTextColor(ContextCompat.getColor(holder.itemView.getContext(), R.color.text_secondary));
                }
            }

            if (holder.btnMemberChat != null) {
                holder.btnMemberChat.setOnClickListener(v -> listener.onClick(m));
            }
            holder.itemView.setOnClickListener(v -> listener.onClick(m));
        }

        @Override
        public int getItemCount() { return members.size(); }

        static class ViewHolder extends RecyclerView.ViewHolder {
            TextView tvName, tvRole, tvProjects, tvInitial, tvStatus, btnMemberChat;
            ViewHolder(@NonNull View itemView) {
                super(itemView);
                tvName = itemView.findViewById(R.id.tvMemberName);
                tvRole = itemView.findViewById(R.id.tvMemberRole);
                tvProjects = itemView.findViewById(R.id.tvMemberProjects);
                tvInitial = itemView.findViewById(R.id.tvAvatarInitial);
                tvStatus = itemView.findViewById(R.id.tvMemberStatus);
                btnMemberChat = itemView.findViewById(R.id.btnMemberChat);
            }
        }
    }
}
