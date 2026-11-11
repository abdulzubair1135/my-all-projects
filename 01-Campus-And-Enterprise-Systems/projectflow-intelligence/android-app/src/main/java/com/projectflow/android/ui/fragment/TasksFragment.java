package com.projectflow.android.ui.fragment;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.projectflow.android.R;
import com.projectflow.android.data.local.TaskEntity;
import com.projectflow.android.data.repository.ProjectFlowRepository;
import com.projectflow.android.ui.CreateTaskActivity;
import com.projectflow.android.ui.TaskDetailsActivity;
import com.projectflow.android.ui.adapter.TaskAdapter;

import java.text.SimpleDateFormat;
import java.util.*;

public class TasksFragment extends Fragment {

    private ProjectFlowRepository repository;
    private TaskAdapter adapter;
    private RecyclerView rvTasks;
    private FloatingActionButton fabAddTask;
    private EditText etSearchTasks;
    private TextView chipAllTasks, chipToday, chipOverdue, chipUpcoming;

    private final List<TaskEntity> allTasks = new ArrayList<>();
    private final java.util.Set<String> userSquads = new java.util.HashSet<>();
    private String selectedFilter = "ALL";
    private String searchQuery = "";
    private final SimpleDateFormat isoDateFormat = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_tasks, container, false);
        rvTasks = v.findViewById(R.id.rvTasks);
        fabAddTask = v.findViewById(R.id.fabAddTask);
        etSearchTasks = v.findViewById(R.id.etSearchTasks);
        chipAllTasks = v.findViewById(R.id.chipAllTasks);
        chipToday = v.findViewById(R.id.chipToday);
        chipOverdue = v.findViewById(R.id.chipOverdue);
        chipUpcoming = v.findViewById(R.id.chipUpcoming);
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

        adapter = new TaskAdapter(task -> {
            Intent intent = new Intent(requireContext(), TaskDetailsActivity.class);
            intent.putExtra("task_id", task.id);
            intent.putExtra("task_title", task.title);
            intent.putExtra("task_desc", task.description);
            intent.putExtra("task_priority", task.priority);
            intent.putExtra("task_status", task.statusCategory);
            intent.putExtra("task_due", task.dueDate);
            intent.putExtra("task_progress", task.progressPercent);
            intent.putExtra("task_project_id", task.projectId);
            intent.putExtra("task_assignee_name", task.assigneeName);
            intent.putExtra("task_assignee_email", task.assigneeEmail);
            intent.putExtra("task_team_name", task.teamName);
            startActivity(intent);
        });

        rvTasks.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvTasks.setAdapter(adapter);

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

        etSearchTasks.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {
                searchQuery = (s != null) ? s.toString().trim().toLowerCase() : "";
                applyFilter();
            }
            @Override public void afterTextChanged(Editable s) {}
        });

        chipAllTasks.setOnClickListener(v -> selectFilter("ALL", chipAllTasks));
        chipToday.setOnClickListener(v -> selectFilter("TODAY", chipToday));
        chipOverdue.setOnClickListener(v -> selectFilter("OVERDUE", chipOverdue));
        chipUpcoming.setOnClickListener(v -> selectFilter("UPCOMING", chipUpcoming));

        repository.getAllTasks().observe(getViewLifecycleOwner(), list -> {
            allTasks.clear();
            if (list != null && !list.isEmpty()) {
                allTasks.addAll(list);
            }
            applyFilter();
        });

        fabAddTask.setOnClickListener(v -> {
            startActivity(new Intent(requireContext(), CreateTaskActivity.class));
        });
    }

    private void selectFilter(String filter, TextView selectedChip) {
        selectedFilter = filter;
        TextView[] chips = {chipAllTasks, chipToday, chipOverdue, chipUpcoming};
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

        String todayIso = isoDateFormat.format(new Date());
        List<TaskEntity> filtered = new ArrayList<>();

        for (TaskEntity t : allTasks) {
            boolean matchesSearch = searchQuery.isEmpty() ||
                    (t.title != null && t.title.toLowerCase().contains(searchQuery)) ||
                    (t.description != null && t.description.toLowerCase().contains(searchQuery)) ||
                    (t.priority != null && t.priority.toLowerCase().contains(searchQuery));

            boolean matchesTab = true;
            if ("TODAY".equals(selectedFilter)) {
                matchesTab = todayIso.equals(t.dueDate);
            } else if ("OVERDUE".equals(selectedFilter)) {
                matchesTab = t.dueDate != null && t.dueDate.compareTo(todayIso) < 0 && !"DONE".equalsIgnoreCase(t.statusCategory);
            } else if ("UPCOMING".equals(selectedFilter)) {
                matchesTab = t.dueDate != null && t.dueDate.compareTo(todayIso) > 0;
            }

            if (!matchesSearch || !matchesTab) {
                continue;
            }

            // Strict assignment filter:
            // 1. If assigned to a specific person:
            if (t.assigneeEmail != null && !t.assigneeEmail.trim().isEmpty()) {
                if (!t.assigneeEmail.trim().equalsIgnoreCase(currentEmail)) {
                    continue; // Belongs to another individual!
                }
            }

            // 2. If assigned to a squad:
            if (t.teamName != null && !t.teamName.trim().isEmpty()) {
                String teamLower = t.teamName.trim().toLowerCase();
                if (!userSquads.contains(teamLower)) {
                    continue; // Belongs to another squad!
                }
            }

            // 3. User directive: "demo data nahi chahiye ... sirf user ko wahi task or project dike jo user ko diya gaya hai"
            boolean hasUserAssignee = (t.assigneeEmail != null && !t.assigneeEmail.trim().isEmpty());
            boolean hasSquadAssignee = (t.teamName != null && !t.teamName.trim().isEmpty());
            if (!hasUserAssignee && !hasSquadAssignee) {
                continue; // Exclude unassigned demo tasks
            }

            filtered.add(t);
        }

        if (adapter != null) {
            adapter.setTasks(filtered);
            if (rvTasks != null) rvTasks.scheduleLayoutAnimation();
        }
    }
}
