package com.projectflow.android.ui;

import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.widget.CheckBox;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import com.projectflow.android.R;
import com.projectflow.android.data.local.AppDatabase;
import com.projectflow.android.data.local.TaskEntity;

public class TaskDetailsActivity extends AppCompatActivity {

    private String taskId = "";
    private String taskProjectId = "";
    private String taskTitle = "";
    private String taskDesc = "";
    private String taskPriority = "";
    private String taskDue = "";

    private TextView tvStatus;
    private TextView tvProgressPercent;
    private ProgressBar pbTaskProgress;
    private CheckBox cbSubtask1, cbSubtask2, cbSubtask3, cbSubtask4;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        StatusBarUtils.applyLightStatusBar(this);
        setContentView(R.layout.activity_task_details);

        ImageView btnBack = findViewById(R.id.btnBack);
        TextView tvTitle = findViewById(R.id.tvDetailTitle);
        TextView tvDesc = findViewById(R.id.tvDetailDesc);
        TextView tvPriorityBadge = findViewById(R.id.tvDetailPriorityBadge);
        TextView tvDueDate = findViewById(R.id.tvDetailDueDate);
        TextView tvProject = findViewById(R.id.tvDetailProject);
        tvStatus = findViewById(R.id.tvDetailStatus);
        tvProgressPercent = findViewById(R.id.tvProgressPercent);
        pbTaskProgress = findViewById(R.id.pbTaskProgress);

        cbSubtask1 = findViewById(R.id.cbSubtask1);
        cbSubtask2 = findViewById(R.id.cbSubtask2);
        cbSubtask3 = findViewById(R.id.cbSubtask3);
        cbSubtask4 = findViewById(R.id.cbSubtask4);

        View btnSetInProgress = findViewById(R.id.btnSetInProgress);
        View btnSetDone = findViewById(R.id.btnSetDone);

        btnBack.setOnClickListener(v -> finish());

        taskId = getIntent().getStringExtra("task_id");
        taskProjectId = getIntent().getStringExtra("task_project_id");
        taskTitle = getIntent().getStringExtra("task_title");
        taskDesc = getIntent().getStringExtra("task_desc");
        taskPriority = getIntent().getStringExtra("task_priority");
        taskDue = getIntent().getStringExtra("task_due");
        if (taskDue == null) taskDue = getIntent().getStringExtra("task_due_date");
        String currentStatus = getIntent().getStringExtra("task_status");

        if (taskTitle != null && !taskTitle.isEmpty()) tvTitle.setText(taskTitle);
        if (taskDesc != null && !taskDesc.isEmpty()) tvDesc.setText(taskDesc);

        if (taskPriority != null && !taskPriority.isEmpty()) {
            tvPriorityBadge.setText(taskPriority.toUpperCase() + " PRIORITY");
            if (taskPriority.toUpperCase().contains("HIGH") || taskPriority.toUpperCase().contains("CRIT")) {
                tvPriorityBadge.setTextColor(Color.parseColor("#E05D52"));
            } else if (taskPriority.toUpperCase().contains("MED")) {
                tvPriorityBadge.setTextColor(ContextCompat.getColor(this, R.color.chart_progress));
            } else {
                tvPriorityBadge.setTextColor(ContextCompat.getColor(this, R.color.chart_done));
            }
        }

        if (taskDue != null && !taskDue.isEmpty()) {
            tvDueDate.setText(taskDue.contains("T") ? taskDue.split("T")[0] : taskDue);
        }

        String assignee = getIntent().getStringExtra("task_assignee_name");
        String email = getIntent().getStringExtra("task_assignee_email");
        String team = getIntent().getStringExtra("task_team_name");
        String basePrj = (taskProjectId != null && !taskProjectId.isEmpty()) ? "PRJ-" + taskProjectId : "PF-CORE";
        if (assignee != null && !assignee.isEmpty()) {
            tvProject.setText(basePrj + " • 👤 " + assignee);
        } else if (team != null && !team.isEmpty()) {
            tvProject.setText(basePrj + " • 👥 " + team);
        } else {
            tvProject.setText(basePrj);
        }

        TextView tvDetailAssignee = findViewById(R.id.tvDetailAssignee);
        TextView tvDetailAssigneeSub = findViewById(R.id.tvDetailAssigneeSub);
        if (tvDetailAssignee != null) {
            if (assignee != null && !assignee.isEmpty()) {
                tvDetailAssignee.setText(assignee);
                if (tvDetailAssigneeSub != null) {
                    tvDetailAssigneeSub.setText(email != null && !email.isEmpty() ? email : (team != null ? "Squad: " + team : "Core Member"));
                }
            } else if (team != null && !team.isEmpty()) {
                tvDetailAssignee.setText("Squad: " + team);
                if (tvDetailAssigneeSub != null) {
                    tvDetailAssigneeSub.setText("Whole Squad Assignment");
                }
            } else {
                tvDetailAssignee.setText("Unassigned");
                if (tvDetailAssigneeSub != null) {
                    tvDetailAssigneeSub.setText("Open for assignment");
                }
            }
        }

        int initialProgress = getIntent().getIntExtra("task_progress", 0);
        if (currentStatus != null && "DONE".equalsIgnoreCase(currentStatus)) {
            initialProgress = 100;
        }
        if (initialProgress >= 25) cbSubtask1.setChecked(true);
        if (initialProgress >= 50) cbSubtask2.setChecked(true);
        if (initialProgress >= 75) cbSubtask3.setChecked(true);
        if (initialProgress >= 100) cbSubtask4.setChecked(true);
        pbTaskProgress.setProgress(initialProgress);
        tvProgressPercent.setText(initialProgress + "%");

        if (currentStatus != null && !currentStatus.isEmpty()) {
            updateStatusBadge(currentStatus);
        } else if (initialProgress == 100) {
            updateStatusBadge("DONE");
        } else if (initialProgress > 0) {
            updateStatusBadge("IN_PROGRESS");
        } else {
            updateStatusBadge("TODO");
        }

        // Subtasks listener to dynamically adjust progress & persist
        View.OnClickListener subtaskListener = v -> recalculateProgressAndSave();
        cbSubtask1.setOnClickListener(subtaskListener);
        cbSubtask2.setOnClickListener(subtaskListener);
        cbSubtask3.setOnClickListener(subtaskListener);
        cbSubtask4.setOnClickListener(subtaskListener);

        btnSetInProgress.setOnClickListener(v -> updateTaskStatus("IN_PROGRESS"));
        btnSetDone.setOnClickListener(v -> {
            cbSubtask1.setChecked(true);
            cbSubtask2.setChecked(true);
            cbSubtask3.setChecked(true);
            cbSubtask4.setChecked(true);
            recalculateProgressAndSave();
        });
    }

    private void recalculateProgressAndSave() {
        int count = 0;
        if (cbSubtask1.isChecked()) count++;
        if (cbSubtask2.isChecked()) count++;
        if (cbSubtask3.isChecked()) count++;
        if (cbSubtask4.isChecked()) count++;

        int percent = (int) ((count / 4.0f) * 100);
        pbTaskProgress.setProgress(percent);
        tvProgressPercent.setText(percent + "%");

        String newStatus;
        if (percent == 100) {
            newStatus = "DONE";
        } else if (percent > 0) {
            newStatus = "IN_PROGRESS";
        } else {
            newStatus = "TODO";
        }
        updateTaskStatus(newStatus);
    }

    private void updateStatusBadge(String status) {
        tvStatus.setText(status.replace("_", " ").toUpperCase());
        if ("DONE".equalsIgnoreCase(status)) {
            tvStatus.setTextColor(ContextCompat.getColor(this, R.color.earth_success));
            tvStatus.setCompoundDrawablesWithIntrinsicBounds(R.drawable.bg_dot_done, 0, 0, 0);
        } else {
            tvStatus.setTextColor(ContextCompat.getColor(this, R.color.chart_progress));
            tvStatus.setCompoundDrawablesWithIntrinsicBounds(R.drawable.bg_dot_progress, 0, 0, 0);
        }
    }

    private void updateTaskStatus(String newStatus) {
        updateStatusBadge(newStatus);
        new Thread(() -> {
            AppDatabase db = AppDatabase.getInstance(this);
            String pId = (taskProjectId != null && !taskProjectId.isEmpty()) ? taskProjectId : "10000000-0000-0000-0000-000000000001";
            int progress = "DONE".equalsIgnoreCase(newStatus) ? 100 : pbTaskProgress.getProgress();
            TaskEntity updated = new TaskEntity(taskId != null ? taskId : java.util.UUID.randomUUID().toString(),
                    pId, taskTitle, taskDesc, taskPriority, newStatus, progress, taskDue);
            db.taskDao().insert(updated);

            // Sync with backend API & Supabase in real-time
            if (taskId != null && !taskId.isEmpty()) {
                new com.projectflow.android.data.repository.ProjectFlowRepository(this)
                        .updateTaskStatus(taskId, newStatus, progress, null);
            }

            runOnUiThread(() -> Toast.makeText(this, "Task status updated: " + newStatus, Toast.LENGTH_SHORT).show());
        }).start();
    }
}
