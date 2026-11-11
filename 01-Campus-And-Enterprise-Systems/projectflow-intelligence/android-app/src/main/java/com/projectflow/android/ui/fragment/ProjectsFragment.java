package com.projectflow.android.ui.fragment;

import android.app.AlertDialog;
import android.content.Intent;
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
import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.projectflow.android.R;
import com.projectflow.android.data.local.AppDatabase;
import com.projectflow.android.data.local.ProjectEntity;
import com.projectflow.android.data.local.WorkspaceEntity;
import com.projectflow.android.data.repository.ProjectFlowRepository;
import com.projectflow.android.ui.ProjectDetailsActivity;
import com.projectflow.android.ui.adapter.ProjectAdapter;

import java.util.ArrayList;
import java.util.List;

public class ProjectsFragment extends Fragment {

    private ProjectFlowRepository repository;
    private ProjectAdapter adapter;
    private RecyclerView rvProjects;
    private FloatingActionButton fabAdd;
    private EditText etSearchProjects;
    private TextView chipAll, chipActive, chipCompleted, chipOnHold;

    private final List<ProjectEntity> allProjects = new ArrayList<>();
    private final java.util.Set<String> userSquads = new java.util.HashSet<>();
    private String selectedStatus = "ALL";
    private String searchQuery = "";

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_projects, container, false);
        rvProjects = v.findViewById(R.id.rvProjects);
        fabAdd = v.findViewById(R.id.fabAddProject);
        etSearchProjects = v.findViewById(R.id.etSearchProjects);
        chipAll = v.findViewById(R.id.chipAll);
        chipActive = v.findViewById(R.id.chipActive);
        chipCompleted = v.findViewById(R.id.chipCompleted);
        chipOnHold = v.findViewById(R.id.chipOnHold);
        return v;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        repository = new ProjectFlowRepository(requireContext());

        android.content.SharedPreferences prefs = requireContext().getSharedPreferences("projectflow_prefs", android.content.Context.MODE_PRIVATE);
        String currentEmail = prefs.getString("user_email", "").trim().toLowerCase();
        if (currentEmail.contains("abdulzubair221") || currentEmail.contains("admin") || currentEmail.contains("vipra")) {
            userSquads.add("core engineering");
            userSquads.add("engineering");
        }
        if (currentEmail.contains("boyunder") || currentEmail.contains("puneet") || currentEmail.contains("design")) {
            userSquads.add("ui/ux design group");
            userSquads.add("design-group");
        }

        adapter = new ProjectAdapter(project -> {
            Intent intent = new Intent(requireContext(), ProjectDetailsActivity.class);
            intent.putExtra("project_id", project.id);
            intent.putExtra("project_name", project.name);
            intent.putExtra("project_code", project.code);
            intent.putExtra("project_desc", project.description);
            intent.putExtra("project_target", project.targetDate);
            intent.putExtra("project_status", project.status);
            intent.putExtra("project_assignee_name", project.assigneeName);
            intent.putExtra("project_assignee_email", project.assigneeEmail);
            intent.putExtra("project_team_name", project.teamName);
            startActivity(intent);
        });

        rvProjects.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvProjects.setAdapter(adapter);

        repository.fetchChatGroups(new ProjectFlowRepository.DataCallback<List<com.projectflow.android.data.remote.model.DtoModels.ChatGroupDto>>() {
            @Override
            public void onData(List<com.projectflow.android.data.remote.model.DtoModels.ChatGroupDto> groups) {
                if (groups != null && isAdded()) {
                    for (var g : groups) {
                        if (g.name != null && g.members != null) {
                            for (String m : g.members) {
                                if (m != null && m.trim().equalsIgnoreCase(currentEmail)) {
                                    userSquads.add(g.name.trim().toLowerCase());
                                    if (g.channel != null) userSquads.add(g.channel.trim().toLowerCase());
                                }
                            }
                        }
                    }
                    if (getActivity() != null) getActivity().runOnUiThread(() -> applyFilter());
                }
            }

            @Override
            public void onError(String message) {}
        });

        etSearchProjects.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {
                searchQuery = (s != null) ? s.toString().trim().toLowerCase() : "";
                applyFilter();
            }
            @Override public void afterTextChanged(Editable s) {}
        });

        chipAll.setOnClickListener(v -> selectStatus("ALL", chipAll));
        chipActive.setOnClickListener(v -> selectStatus("IN_PROGRESS", chipActive));
        chipCompleted.setOnClickListener(v -> selectStatus("COMPLETED", chipCompleted));
        chipOnHold.setOnClickListener(v -> selectStatus("ON_HOLD", chipOnHold));

        repository.getProjects().observe(getViewLifecycleOwner(), list -> {
            allProjects.clear();
            if (list != null) allProjects.addAll(list);
            applyFilter();
        });

        repository.getAllTasks().observe(getViewLifecycleOwner(), taskList -> {
            if (adapter != null) {
                adapter.setTasks(taskList);
            }
        });

        fabAdd.setOnClickListener(v -> showCreateProjectDialog());
    }

    private void selectStatus(String status, TextView selectedChip) {
        selectedStatus = status;
        TextView[] chips = {chipAll, chipActive, chipCompleted, chipOnHold};
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

    private void applyFilter() {
        if (!isAdded()) return;
        android.content.SharedPreferences prefs = requireContext().getSharedPreferences("projectflow_prefs", android.content.Context.MODE_PRIVATE);
        String currentEmail = prefs.getString("user_email", "").trim().toLowerCase();

        List<ProjectEntity> filtered = new ArrayList<>();
        for (ProjectEntity p : allProjects) {
            boolean matchesStatus = "ALL".equals(selectedStatus) || selectedStatus.equalsIgnoreCase(p.status);
            boolean matchesSearch = searchQuery.isEmpty() ||
                    (p.name != null && p.name.toLowerCase().contains(searchQuery)) ||
                    (p.code != null && p.code.toLowerCase().contains(searchQuery)) ||
                    (p.description != null && p.description.toLowerCase().contains(searchQuery));

            if (!matchesStatus || !matchesSearch) {
                continue;
            }

            // Strict assignment filter:
            // 1. If assigned to a specific person:
            if (p.assigneeEmail != null && !p.assigneeEmail.trim().isEmpty()) {
                if (!p.assigneeEmail.trim().equalsIgnoreCase(currentEmail)) {
                    continue; // Belongs to another individual!
                }
            }

            // 2. If assigned to a squad:
            if (p.teamName != null && !p.teamName.trim().isEmpty()) {
                String teamLower = p.teamName.trim().toLowerCase();
                if (!userSquads.contains(teamLower)) {
                    continue; // Belongs to another squad!
                }
            }

            // 3. User directive: "demo data nahi chahiye ... sirf user ko wahi task or project dike jo user ko diya gaya hai"
            boolean hasUserAssignee = (p.assigneeEmail != null && !p.assigneeEmail.trim().isEmpty());
            boolean hasSquadAssignee = (p.teamName != null && !p.teamName.trim().isEmpty());
            if (!hasUserAssignee && !hasSquadAssignee) {
                continue; // Exclude unassigned demo projects
            }

            filtered.add(p);
        }
        if (adapter != null) {
            adapter.setProjects(filtered);
        }
    }

    private void showCreateProjectDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(requireContext());
        builder.setTitle("New Project");

        LinearLayout layout = new LinearLayout(requireContext());
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(48, 24, 48, 24);

        final EditText etName = new EditText(requireContext());
        etName.setHint("Project Name");
        layout.addView(etName);

        final EditText etCode = new EditText(requireContext());
        etCode.setHint("Project Code (e.g. PRJ)");
        layout.addView(etCode);

        final EditText etDesc = new EditText(requireContext());
        etDesc.setHint("Description");
        layout.addView(etDesc);

        builder.setView(layout);

        builder.setPositiveButton("Create", (dialog, which) -> {
            String name = etName.getText().toString().trim();
            String code = etCode.getText().toString().trim();
            String desc = etDesc.getText().toString().trim();
            if (name.isEmpty()) return;

            new Thread(() -> {
                android.content.SharedPreferences prefs = requireContext().getSharedPreferences("projectflow_prefs", android.content.Context.MODE_PRIVATE);
                String currentEmail = prefs.getString("user_email", "").trim();
                String currentName = prefs.getString("user_name", "Team Member").trim();
                List<WorkspaceEntity> wsList = AppDatabase.getInstance(requireContext()).workspaceDao().getAllSync();
                String wsId = (wsList != null && !wsList.isEmpty()) ? wsList.get(0).id : "00000000-0000-0000-0000-000000000001";
                repository.createProject(wsId, name, code, desc, null, currentName, currentEmail, null, null,
                        () -> requireActivity().runOnUiThread(() -> {
                            Toast.makeText(requireContext(), "Project Created", Toast.LENGTH_SHORT).show();
                            repository.refreshProjects();
                        }),
                        () -> requireActivity().runOnUiThread(() -> Toast.makeText(requireContext(), "Failed creating project", Toast.LENGTH_SHORT).show())
                );
            }).start();
        });

        builder.setNegativeButton("Cancel", (dialog, which) -> dialog.cancel());
        builder.show();
    }
}
