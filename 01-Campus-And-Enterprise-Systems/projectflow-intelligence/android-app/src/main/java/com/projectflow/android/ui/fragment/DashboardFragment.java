package com.projectflow.android.ui.fragment;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;
import com.projectflow.android.R;
import com.projectflow.android.data.local.AppDatabase;
import com.projectflow.android.data.local.ProjectEntity;
import com.projectflow.android.data.local.TaskEntity;
import com.projectflow.android.data.remote.model.DtoModels.NotificationDto;
import com.projectflow.android.data.repository.ProjectFlowRepository;
import com.projectflow.android.ui.CreateTaskActivity;
import com.projectflow.android.ui.MainActivity;
import com.projectflow.android.ui.adapter.ProjectAdapter;
import com.projectflow.android.ui.view.NeumorphicPieChartView;
import com.projectflow.android.ui.view.NeumorphicBarChartView;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

public class DashboardFragment extends Fragment {

    private TextView tvGreeting, tvUserName, tvUserRole;
    private TextView tvTotalProjects, tvTotalTasks, tvCompletedTasks, tvPendingTasks;
    private View cardTotalProjects, cardTotalTasks, cardCompletedTasks, cardPendingTasks, ivUserAvatar;
    private TextView chipDone, chipProgress, chipReview, chipTodo, tvEmptyProjects;
    private NeumorphicPieChartView pieChartView;
    private NeumorphicBarChartView barChartView;
    private RecyclerView rvRecentProjects;
    private ProjectAdapter projectAdapter;
    private SwipeRefreshLayout swipeRefresh;
    private FrameLayout btnNotificationBell;
    private TextView tvNotifBadge;
    private LinearLayout qaCreateTask, qaCalendar, qaReports, qaChat;
    private TextView btnViewAllProjects;
    private ProjectFlowRepository repository;
    private final java.util.Set<String> userSquads = new java.util.HashSet<>();
    private List<ProjectEntity> rawProjects = new ArrayList<>();
    private List<TaskEntity> rawTasks = new ArrayList<>();

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_dashboard, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        repository = new ProjectFlowRepository(requireContext());
        AppDatabase db = AppDatabase.getInstance(requireContext());

        // Header
        tvGreeting = view.findViewById(R.id.tvGreeting);
        tvUserName = view.findViewById(R.id.tvUserName);
        tvUserRole = view.findViewById(R.id.tvUserRole);
        btnNotificationBell = view.findViewById(R.id.btnNotificationBell);
        tvNotifBadge = view.findViewById(R.id.tvNotifBadge);
        ivUserAvatar = view.findViewById(R.id.ivUserAvatar);

        // Metrics
        tvTotalProjects = view.findViewById(R.id.tvTotalProjects);
        tvTotalTasks = view.findViewById(R.id.tvTotalTasks);
        tvCompletedTasks = view.findViewById(R.id.tvCompletedTasks);
        tvPendingTasks = view.findViewById(R.id.tvPendingTasks);
        cardTotalProjects = view.findViewById(R.id.cardTotalProjects);
        cardTotalTasks = view.findViewById(R.id.cardTotalTasks);
        cardCompletedTasks = view.findViewById(R.id.cardCompletedTasks);
        cardPendingTasks = view.findViewById(R.id.cardPendingTasks);

        // 3D Neumorphic Charts & Chips
        pieChartView = view.findViewById(R.id.pieChartView);
        barChartView = view.findViewById(R.id.barChartView);
        chipDone = view.findViewById(R.id.chipDone);
        chipProgress = view.findViewById(R.id.chipProgress);
        chipReview = view.findViewById(R.id.chipReview);
        chipTodo = view.findViewById(R.id.chipTodo);

        // Quick Actions
        qaCreateTask = view.findViewById(R.id.qaCreateTask);
        qaCalendar = view.findViewById(R.id.qaCalendar);
        qaReports = view.findViewById(R.id.qaReports);
        qaChat = view.findViewById(R.id.qaChat);

        // Projects List
        rvRecentProjects = view.findViewById(R.id.rvRecentProjects);
        tvEmptyProjects = view.findViewById(R.id.tvEmptyProjects);
        btnViewAllProjects = view.findViewById(R.id.btnViewAllProjects);
        swipeRefresh = view.findViewById(R.id.swipeRefresh);

        // Set dynamic time-based greeting
        int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        if (hour < 12) {
            tvGreeting.setText("Good Morning,");
        } else if (hour < 17) {
            tvGreeting.setText("Good Afternoon,");
        } else {
            tvGreeting.setText("Good Evening,");
        }

        // Set user info from SharedPreferences
        refreshUserInfo();

        // Load Squads for isolation
        SharedPreferences prefs = requireContext().getSharedPreferences("projectflow_prefs", Context.MODE_PRIVATE);
        String currentEmail = prefs.getString("user_email", "").trim().toLowerCase();
        userSquads.add("core engineering");
        userSquads.add("engineering");
        if (currentEmail.contains("abdul")) {
            userSquads.add("mobile engineering group");
        }

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
                    if (getActivity() != null) getActivity().runOnUiThread(() -> updateFilteredMetrics());
                }
            }
            @Override
            public void onError(String message) {}
        });

        // Setup Projects RecyclerView
        projectAdapter = new ProjectAdapter(project -> {
            Intent intent = new Intent(requireContext(), com.projectflow.android.ui.ProjectDetailsActivity.class);
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
        rvRecentProjects.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvRecentProjects.setAdapter(projectAdapter);

        // Wire Real LiveData Observers with Isolation
        db.projectDao().getAllLive().observe(getViewLifecycleOwner(), projects -> {
            rawProjects = (projects != null) ? projects : new ArrayList<>();
            updateFilteredMetrics();
        });

        db.taskDao().getAllLive().observe(getViewLifecycleOwner(), tasks -> {
            rawTasks = (tasks != null) ? tasks : new ArrayList<>();
            if (projectAdapter != null) projectAdapter.setTasks(rawTasks);
            updateFilteredMetrics();
        });

        // Quick Actions listeners
        qaCreateTask.setOnClickListener(v -> {
            startActivity(new Intent(requireContext(), CreateTaskActivity.class));
        });

        qaCalendar.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).navigateToFragment(new CalendarFragment(), "Calendar");
            }
        });

        qaReports.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).navigateToFragment(new ReportsFragment(), "Reports");
            }
        });

        qaChat.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).navigateToFragment(new TeamFragment(), "Team & Discussions");
            }
        });

        btnViewAllProjects.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).switchTab(MainActivity.TAG_PROJECTS, "Projects");
            }
        });

        btnNotificationBell.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).navigateToFragment(new NotificationsFragment(), "Notifications");
            }
        });

        // Top Header Profile Avatar Click
        if (ivUserAvatar != null) {
            ivUserAvatar.setOnClickListener(v -> {
                if (getActivity() instanceof MainActivity) {
                    ((MainActivity) getActivity()).switchTab(MainActivity.TAG_PROFILE, "Profile & Settings");
                }
            });
        }

        // Summary Metric Cards Real Navigation
        if (cardTotalProjects != null) {
            cardTotalProjects.setOnClickListener(v -> {
                if (getActivity() instanceof MainActivity) {
                    ((MainActivity) getActivity()).switchTab(MainActivity.TAG_PROJECTS, "Projects");
                }
            });
        }

        if (cardTotalTasks != null) {
            cardTotalTasks.setOnClickListener(v -> {
                if (getActivity() instanceof MainActivity) {
                    ((MainActivity) getActivity()).switchTab(MainActivity.TAG_TASKS, "Tasks");
                }
            });
        }

        if (cardCompletedTasks != null) {
            cardCompletedTasks.setOnClickListener(v -> {
                if (getActivity() instanceof MainActivity) {
                    ((MainActivity) getActivity()).switchTab(MainActivity.TAG_TASKS, "Tasks");
                }
            });
        }

        if (cardPendingTasks != null) {
            cardPendingTasks.setOnClickListener(v -> {
                if (getActivity() instanceof MainActivity) {
                    ((MainActivity) getActivity()).switchTab(MainActivity.TAG_TASKS, "Tasks");
                }
            });
        }

        // Status Chips Click Navigation to Tasks
        View.OnClickListener openTasks = v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).switchTab(MainActivity.TAG_TASKS, "Tasks");
            }
        };
        if (chipDone != null) chipDone.setOnClickListener(openTasks);
        if (chipProgress != null) chipProgress.setOnClickListener(openTasks);
        if (chipReview != null) chipReview.setOnClickListener(openTasks);
        if (chipTodo != null) chipTodo.setOnClickListener(openTasks);

        // Chart Clicks to Open Full Reports
        if (pieChartView != null) {
            pieChartView.setOnClickListener(v -> {
                if (getActivity() instanceof MainActivity) {
                    ((MainActivity) getActivity()).navigateToFragment(new ReportsFragment(), "Reports");
                }
            });
        }
        if (barChartView != null) {
            barChartView.setOnClickListener(v -> {
                if (getActivity() instanceof MainActivity) {
                    ((MainActivity) getActivity()).navigateToFragment(new ReportsFragment(), "Reports");
                }
            });
        }

        // Load real unread notifications badge
        loadNotificationBadge();

        // Initial data sync
        repository.refreshWorkspaces();
        repository.refreshProjects();
        repository.refreshAllTasks();

        // Swipe Refresh
        swipeRefresh.setColorSchemeResources(R.color.primary_earth, R.color.muted_clay);
        swipeRefresh.setOnRefreshListener(() -> {
            repository.refreshWorkspaces();
            repository.refreshProjects();
            repository.refreshAllTasks();
            loadNotificationBadge();
            swipeRefresh.setRefreshing(false);
        });
    }

    @Override
    public void onResume() {
        super.onResume();
        refreshUserInfo();
        repository.refreshProjects();
        repository.refreshAllTasks();
        loadNotificationBadge();
    }

    private void refreshUserInfo() {
        if (!isAdded()) return;
        SharedPreferences prefs = requireContext().getSharedPreferences("projectflow_prefs", Context.MODE_PRIVATE);
        String userEmail = prefs.getString("user_email", "admin@projectflow.io");
        String defaultName = userEmail.contains("@") ? userEmail.split("@")[0] : "ProjectFlow User";
        String savedName = prefs.getString("user_name", prefs.getString("user_display_name", defaultName));
        String savedRole = prefs.getString("user_role", "MEMBER");
        tvUserName.setText(savedName);
        tvUserRole.setText(savedRole);
    }

    private void updateFilteredMetrics() {
        if (!isAdded()) return;
        SharedPreferences prefs = requireContext().getSharedPreferences("projectflow_prefs", Context.MODE_PRIVATE);
        String currentEmail = prefs.getString("user_email", "").trim().toLowerCase();

        // 1. Filter Projects for user
        List<ProjectEntity> filteredProjects = new ArrayList<>();
        for (ProjectEntity p : rawProjects) {
            boolean hasUser = (p.assigneeEmail != null && !p.assigneeEmail.trim().isEmpty());
            boolean hasSquad = (p.teamName != null && !p.teamName.trim().isEmpty());
            if (!hasUser && !hasSquad) continue; // Exclude unassigned demo data

            if (hasUser && !p.assigneeEmail.trim().equalsIgnoreCase(currentEmail)) {
                continue;
            }
            if (hasSquad && !userSquads.contains(p.teamName.trim().toLowerCase())) {
                continue;
            }
            filteredProjects.add(p);
        }

        tvTotalProjects.setText(String.valueOf(filteredProjects.size()));
        if (!filteredProjects.isEmpty()) {
            tvEmptyProjects.setVisibility(View.GONE);
            rvRecentProjects.setVisibility(View.VISIBLE);
            projectAdapter.setProjects(filteredProjects.subList(0, Math.min(filteredProjects.size(), 4)));
        } else {
            rvRecentProjects.setVisibility(View.GONE);
            tvEmptyProjects.setVisibility(View.VISIBLE);
        }

        // 2. Filter Tasks for user
        List<TaskEntity> filteredTasks = new ArrayList<>();
        int doneCount = 0;
        int inProgressCount = 0;
        int reviewCount = 0;
        int todoCount = 0;

        for (TaskEntity t : rawTasks) {
            boolean hasUser = (t.assigneeEmail != null && !t.assigneeEmail.trim().isEmpty());
            boolean hasSquad = (t.teamName != null && !t.teamName.trim().isEmpty());
            if (!hasUser && !hasSquad) continue; // Exclude unassigned demo data

            if (hasUser && !t.assigneeEmail.trim().equalsIgnoreCase(currentEmail)) {
                continue;
            }
            if (hasSquad && !userSquads.contains(t.teamName.trim().toLowerCase())) {
                continue;
            }
            filteredTasks.add(t);

            String cat = (t.statusCategory != null) ? t.statusCategory.toUpperCase() : "TODO";
            if ("DONE".equals(cat)) {
                doneCount++;
            } else if ("IN_PROGRESS".equals(cat)) {
                inProgressCount++;
            } else if ("REVIEW".equals(cat)) {
                reviewCount++;
            } else {
                todoCount++;
            }
        }

        int total = filteredTasks.size();
        int activeSum = inProgressCount + reviewCount + todoCount;
        tvTotalTasks.setText(String.valueOf(total));
        tvCompletedTasks.setText(String.valueOf(doneCount));
        tvPendingTasks.setText(String.valueOf(activeSum));

        if (chipDone != null) chipDone.setText(doneCount + " Done");
        if (chipProgress != null) chipProgress.setText(inProgressCount + " In Progress");
        if (chipReview != null) chipReview.setText(reviewCount + " Review");
        if (chipTodo != null) chipTodo.setText(todoCount + " To Do");

        if (pieChartView != null) {
            pieChartView.setTaskData(doneCount, inProgressCount, reviewCount, todoCount);
        }

        if (barChartView != null) {
            List<NeumorphicBarChartView.BarItem> barItems = new ArrayList<>();
            int max = Math.max(total, 5);
            barItems.add(new NeumorphicBarChartView.BarItem("Completed Delivery", doneCount, max, androidx.core.content.ContextCompat.getColor(requireContext(), R.color.chart_done)));
            barItems.add(new NeumorphicBarChartView.BarItem("In Active Sprint", inProgressCount, max, androidx.core.content.ContextCompat.getColor(requireContext(), R.color.chart_progress)));
            barItems.add(new NeumorphicBarChartView.BarItem("Quality & Review", reviewCount, max, androidx.core.content.ContextCompat.getColor(requireContext(), R.color.chart_review)));
            barItems.add(new NeumorphicBarChartView.BarItem("Backlog & To-Do", todoCount, max, androidx.core.content.ContextCompat.getColor(requireContext(), R.color.chart_todo)));
            barChartView.setData(barItems);
        }
    }

    private void loadNotificationBadge() {
        if (tvNotifBadge == null) return;
        repository.fetchNotifications(new ProjectFlowRepository.DataCallback<List<NotificationDto>>() {
            @Override
            public void onData(List<NotificationDto> notifs) {
                if (getActivity() != null) {
                    getActivity().runOnUiThread(() -> {
                        int unread = 0;
                        if (notifs != null) {
                            for (NotificationDto n : notifs) {
                                if (!n.read) unread++;
                            }
                        }
                        if (unread > 0) {
                            tvNotifBadge.setVisibility(View.VISIBLE);
                            tvNotifBadge.setText(unread > 9 ? "9+" : String.valueOf(unread));
                        } else {
                            tvNotifBadge.setVisibility(View.GONE);
                        }
                    });
                }
            }

            @Override
            public void onError(String message) {
                if (getActivity() != null) {
                    getActivity().runOnUiThread(() -> tvNotifBadge.setVisibility(View.GONE));
                }
            }
        });
    }
}
