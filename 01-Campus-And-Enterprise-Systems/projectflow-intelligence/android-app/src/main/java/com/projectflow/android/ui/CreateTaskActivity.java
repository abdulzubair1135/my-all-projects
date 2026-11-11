package com.projectflow.android.ui;

import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Spinner;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.projectflow.android.R;
import com.projectflow.android.data.local.AppDatabase;
import com.projectflow.android.data.local.ProjectEntity;
import com.projectflow.android.data.remote.model.DtoModels.ChatGroupDto;
import com.projectflow.android.data.remote.model.DtoModels.TeamMemberDto;
import com.projectflow.android.data.repository.ProjectFlowRepository;

import java.util.ArrayList;
import java.util.List;

public class CreateTaskActivity extends AppCompatActivity {

    private final List<TeamMemberDto> memberList = new ArrayList<>();
    private final List<ChatGroupDto> groupList = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        StatusBarUtils.applyLightStatusBar(this);
        setContentView(R.layout.activity_create_task);

        View btnBack = findViewById(R.id.btnBack);
        EditText etTitle = findViewById(R.id.etTaskTitle);
        EditText etDesc = findViewById(R.id.etTaskDesc);
        EditText etDueDate = findViewById(R.id.etTaskDueDate);
        RadioGroup rgPriority = findViewById(R.id.rgPriority);
        Spinner spAssignPerson = findViewById(R.id.spAssignPerson);
        Spinner spAssignGroup = findViewById(R.id.spAssignGroup);
        View btnSubmit = findViewById(R.id.btnSubmitCreateTask);

        btnBack.setOnClickListener(v -> finish());

        // Check if pre-filled date or project passed from calendar/project screen
        String prefilledDate = getIntent().getStringExtra("default_due_date");
        if (prefilledDate != null && !prefilledDate.isEmpty()) {
            etDueDate.setText(prefilledDate);
        }

        String intentProjectId = getIntent().getStringExtra("project_id");

        etDueDate.setFocusable(false);
        etDueDate.setClickable(true);
        etDueDate.setOnClickListener(v -> {
            java.util.Calendar c = java.util.Calendar.getInstance();
            int year = c.get(java.util.Calendar.YEAR);
            int month = c.get(java.util.Calendar.MONTH);
            int day = c.get(java.util.Calendar.DAY_OF_MONTH);

            new android.app.DatePickerDialog(this, (view, y, m, d) -> {
                String formatted = String.format(java.util.Locale.US, "%04d-%02d-%02d", y, m + 1, d);
                etDueDate.setText(formatted);
            }, year, month, day).show();
        });

        ProjectFlowRepository repository = new ProjectFlowRepository(this);

        // Populate Person Dropdown
        List<String> personNames = new ArrayList<>();
        personNames.add("Unassigned");
        ArrayAdapter<String> personAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, personNames);
        spAssignPerson.setAdapter(personAdapter);

        repository.fetchTeam(new ProjectFlowRepository.DataCallback<List<TeamMemberDto>>() {
            @Override
            public void onData(List<TeamMemberDto> members) {
                runOnUiThread(() -> {
                    if (members != null) {
                        memberList.clear();
                        memberList.addAll(members);
                        for (TeamMemberDto m : members) {
                            personNames.add(m.fullName + " (" + m.role + ")");
                        }
                        personAdapter.notifyDataSetChanged();
                    }
                });
            }

            @Override
            public void onError(String message) {}
        });

        // Populate Group Dropdown
        List<String> groupNames = new ArrayList<>();
        groupNames.add("Unassigned");
        ArrayAdapter<String> groupAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, groupNames);
        spAssignGroup.setAdapter(groupAdapter);

        repository.fetchChatGroups(new ProjectFlowRepository.DataCallback<List<ChatGroupDto>>() {
            @Override
            public void onData(List<ChatGroupDto> groups) {
                runOnUiThread(() -> {
                    if (groups != null) {
                        groupList.clear();
                        groupList.addAll(groups);
                        for (ChatGroupDto g : groups) {
                            groupNames.add(g.name);
                        }
                        groupAdapter.notifyDataSetChanged();
                    }
                });
            }

            @Override
            public void onError(String message) {}
        });

        btnSubmit.setOnClickListener(v -> {
            String title = etTitle.getText().toString().trim();
            String desc = etDesc.getText().toString().trim();
            if (title.isEmpty()) {
                etTitle.setError("Task title is required");
                etTitle.requestFocus();
                return;
            }

            int selectedPriorityId = rgPriority.getCheckedRadioButtonId();
            String priority = "MEDIUM";
            if (selectedPriorityId == R.id.rbLow) priority = "LOW";
            else if (selectedPriorityId == R.id.rbHigh) priority = "HIGH";

            final String finalPriority = priority;

            int personPos = spAssignPerson.getSelectedItemPosition();
            String assigneeId = null;
            String assigneeName = null;
            String assigneeEmail = null;
            if (personPos > 0 && personPos - 1 < memberList.size()) {
                TeamMemberDto m = memberList.get(personPos - 1);
                assigneeId = m.id;
                assigneeName = m.fullName;
                assigneeEmail = m.email;
            }

            int groupPos = spAssignGroup.getSelectedItemPosition();
            String teamId = null;
            String teamName = null;
            if (groupPos > 0 && groupPos - 1 < groupList.size()) {
                ChatGroupDto g = groupList.get(groupPos - 1);
                teamId = g.id;
                teamName = g.name;
            }

            if (assigneeId == null && teamId == null) {
                android.content.SharedPreferences prefs = getSharedPreferences("projectflow_prefs", MODE_PRIVATE);
                assigneeEmail = prefs.getString("user_email", null);
                assigneeName = prefs.getString("user_name", "Team Member");
            }

            final String finalAssigneeId = assigneeId;
            final String finalAssigneeName = assigneeName;
            final String finalAssigneeEmail = assigneeEmail;
            final String finalTeamId = teamId;
            final String finalTeamName = teamName;

            new Thread(() -> {
                List<ProjectEntity> projects = AppDatabase.getInstance(this).projectDao().getAllSync();
                String projectId = (intentProjectId != null && !intentProjectId.isEmpty()) ? intentProjectId :
                        ((projects != null && !projects.isEmpty()) ? projects.get(0).id : "10000000-0000-0000-0000-000000000001");

                String dueDate = etDueDate.getText() != null ? etDueDate.getText().toString().trim() : null;
                repository.createTask(projectId, title, desc, finalPriority, dueDate, finalAssigneeId, finalAssigneeName, finalAssigneeEmail, finalTeamId, finalTeamName,
                        () -> runOnUiThread(() -> {
                            Toast.makeText(this, "Task Created Successfully", Toast.LENGTH_SHORT).show();
                            // Fire system tray notification with sound and vibration
                            com.projectflow.android.service.ProjectFlowNotificationHelper.showTaskNotification(
                                    getApplicationContext(),
                                    "New Task: " + title,
                                    "Priority: " + finalPriority + (dueDate != null && !dueDate.isEmpty() ? " • Due: " + dueDate : ""),
                                    null,
                                    finalPriority
                            );
                            finish();
                        }),
                        () -> runOnUiThread(() -> Toast.makeText(this, "Failed creating task", Toast.LENGTH_SHORT).show())
                );
            }).start();
        });
    }
}
