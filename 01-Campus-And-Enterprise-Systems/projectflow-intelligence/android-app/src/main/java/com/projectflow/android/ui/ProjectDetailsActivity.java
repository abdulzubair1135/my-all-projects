package com.projectflow.android.ui;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.projectflow.android.R;
import com.projectflow.android.data.local.AppDatabase;
import com.projectflow.android.data.repository.ProjectFlowRepository;
import com.projectflow.android.ui.adapter.RiskAdapter;
import com.projectflow.android.ui.adapter.TaskAdapter;

public class ProjectDetailsActivity extends AppCompatActivity {

    private TextView tvProjectCode, tvProjectStatus, tvProjectName, tvProjectDesc, tvTargetDate, tvProgressPercent;
    private ProgressBar pbProjectProgress;
    private RecyclerView rvProjectTasks, rvProjectRisks;
    private TextView tvEmptyTasks, tvEmptyRisks, btnAddTask;
    private TaskAdapter taskAdapter;
    private RiskAdapter riskAdapter;
    private ProjectFlowRepository repository;
    private String projectId = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        StatusBarUtils.applyLightStatusBar(this);
        setContentView(R.layout.activity_project_details);

        repository = new ProjectFlowRepository(this);

        tvProjectCode = findViewById(R.id.tvProjectCode);
        tvProjectStatus = findViewById(R.id.tvProjectStatus);
        tvProjectName = findViewById(R.id.tvProjectName);
        tvProjectDesc = findViewById(R.id.tvProjectDesc);
        tvTargetDate = findViewById(R.id.tvTargetDate);
        tvProgressPercent = findViewById(R.id.tvProgressPercent);
        pbProjectProgress = findViewById(R.id.pbProjectProgress);

        rvProjectTasks = findViewById(R.id.rvProjectTasks);
        rvProjectRisks = findViewById(R.id.rvProjectRisks);
        tvEmptyTasks = findViewById(R.id.tvEmptyTasks);
        tvEmptyRisks = findViewById(R.id.tvEmptyRisks);
        btnAddTask = findViewById(R.id.btnAddTask);

        projectId = getIntent().getStringExtra("project_id");
        if (projectId == null) projectId = "10000000-0000-0000-0000-000000000001";

        String name = getIntent().getStringExtra("project_name");
        String code = getIntent().getStringExtra("project_code");
        String desc = getIntent().getStringExtra("project_desc");
        String target = getIntent().getStringExtra("project_target");
        String status = getIntent().getStringExtra("project_status");
        String assignee = getIntent().getStringExtra("project_assignee_name");
        String team = getIntent().getStringExtra("project_team_name");

        tvProjectName.setText(name != null ? name : "ProjectFlow Core Platform");
        tvProjectCode.setText(code != null ? code : "PRJ");
        tvProjectDesc.setText(desc != null ? desc : "Full-stack project management and intelligence engine.");
        
        String assignmentInfo = "";
        if (assignee != null && !assignee.isEmpty()) assignmentInfo = " • 👤 " + assignee;
        else if (team != null && !team.isEmpty()) assignmentInfo = " • 👥 " + team;
        tvTargetDate.setText("Target: " + (target != null ? target : "Ongoing") + assignmentInfo);
        tvProjectStatus.setText(status != null ? status : "IN_PROGRESS");

        TextView tvProjectTeamBadge = findViewById(R.id.tvProjectTeamBadge);
        TextView tvProjectAssigneeBadge = findViewById(R.id.tvProjectAssigneeBadge);
        TextView tvProjectMembersList = findViewById(R.id.tvProjectMembersList);

        if (tvProjectTeamBadge != null) {
            if (team != null && !team.isEmpty()) {
                tvProjectTeamBadge.setText("👥 Team: " + team);
                tvProjectTeamBadge.setVisibility(View.VISIBLE);
            } else {
                tvProjectTeamBadge.setVisibility(View.GONE);
            }
        }

        if (tvProjectAssigneeBadge != null) {
            if (assignee != null && !assignee.isEmpty()) {
                tvProjectAssigneeBadge.setText("👤 Lead: " + assignee);
                tvProjectAssigneeBadge.setVisibility(View.VISIBLE);
            } else {
                tvProjectAssigneeBadge.setVisibility(View.GONE);
            }
        }

        if (tvProjectMembersList != null) {
            if (assignee != null && !assignee.isEmpty()) {
                tvProjectMembersList.setText("Members: " + assignee);
            } else if (team != null && !team.isEmpty()) {
                tvProjectMembersList.setText("Members: " + team + " Members");
            } else {
                tvProjectMembersList.setText("Members: Open for assignment");
            }
        }

        taskAdapter = new TaskAdapter(task -> {
            Intent intent = new Intent(ProjectDetailsActivity.this, TaskDetailsActivity.class);
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
        rvProjectTasks.setLayoutManager(new LinearLayoutManager(this));
        rvProjectTasks.setAdapter(taskAdapter);

        riskAdapter = new RiskAdapter();
        rvProjectRisks.setLayoutManager(new LinearLayoutManager(this));
        rvProjectRisks.setAdapter(riskAdapter);

        View btnBack = findViewById(R.id.btnBackProjectDetails);
        if (btnBack != null) {
            btnBack.setOnClickListener(v -> finish());
        }

        btnAddTask.setOnClickListener(v -> {
            Intent intent = new Intent(ProjectDetailsActivity.this, CreateTaskActivity.class);
            intent.putExtra("project_id", projectId);
            startActivity(intent);
        });

        // Observe Tasks via repository so it triggers network sync and live updates
        repository.getTasks(projectId).observe(this, tasks -> {
            if (tasks != null && !tasks.isEmpty()) {
                tvEmptyTasks.setVisibility(View.GONE);
                rvProjectTasks.setVisibility(View.VISIBLE);
                taskAdapter.setTasks(tasks);

                int done = 0;
                java.util.Set<String> contributors = new java.util.LinkedHashSet<>();
                if (assignee != null && !assignee.isEmpty()) contributors.add(assignee);
                for (var t : tasks) {
                    if ("DONE".equalsIgnoreCase(t.statusCategory)) done++;
                    if (t.assigneeName != null && !t.assigneeName.isEmpty()) {
                        contributors.add(t.assigneeName);
                    }
                }
                int prog = Math.round((done * 100f) / tasks.size());
                pbProjectProgress.setProgress(prog);
                tvProgressPercent.setText(prog + "% Complete");

                if (tvProjectMembersList != null && !contributors.isEmpty()) {
                    StringBuilder sb = new StringBuilder();
                    for (String c : contributors) {
                        if (sb.length() > 0) sb.append(", ");
                        sb.append(c);
                    }
                    tvProjectMembersList.setText("Active Contributors: " + sb.toString());
                }
            } else {
                rvProjectTasks.setVisibility(View.GONE);
                tvEmptyTasks.setVisibility(View.VISIBLE);
            }
        });

        // Observe Risks
        repository.getRisks(projectId).observe(this, risks -> {
            if (risks != null && !risks.isEmpty()) {
                tvEmptyRisks.setVisibility(View.GONE);
                rvProjectRisks.setVisibility(View.VISIBLE);
                riskAdapter.setRisks(risks);
            } else {
                rvProjectRisks.setVisibility(View.GONE);
                tvEmptyRisks.setVisibility(View.VISIBLE);
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (repository != null) {
            repository.refreshTasks(projectId);
            repository.refreshAllTasks();
        }
    }
}
