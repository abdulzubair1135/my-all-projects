package com.projectflow.android.ui.fragment;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
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
import com.projectflow.android.data.remote.model.DtoModels.ReportSummaryDto;
import com.projectflow.android.data.remote.model.DtoModels.TeamMemberDto;
import com.projectflow.android.data.repository.ProjectFlowRepository;

import java.util.ArrayList;
import java.util.List;

public class ReportsFragment extends Fragment {

    private TextView tvCompletionRate, tvOverdueCount;
    private View barDone, barInProgress, barTodo;
    private TextView tvLegendDone, tvLegendInProgress, tvLegendTodo;
    private RecyclerView rvProjectProgress, rvTeamWorkload;
    private SwipeRefreshLayout swipeRefreshReports;
    private ProjectFlowRepository repository;

    private ProjectProgressAdapter projectAdapter;
    private TeamWorkloadAdapter teamAdapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_reports, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        repository = new ProjectFlowRepository(requireContext());
        AppDatabase db = AppDatabase.getInstance(requireContext());

        tvCompletionRate = view.findViewById(R.id.tvCompletionRate);
        tvOverdueCount = view.findViewById(R.id.tvOverdueCount);

        barDone = view.findViewById(R.id.barDone);
        barInProgress = view.findViewById(R.id.barInProgress);
        barTodo = view.findViewById(R.id.barTodo);

        tvLegendDone = view.findViewById(R.id.tvLegendDone);
        tvLegendInProgress = view.findViewById(R.id.tvLegendInProgress);
        tvLegendTodo = view.findViewById(R.id.tvLegendTodo);

        rvProjectProgress = view.findViewById(R.id.rvProjectProgress);
        rvTeamWorkload = view.findViewById(R.id.rvTeamWorkload);
        swipeRefreshReports = view.findViewById(R.id.swipeRefreshReports);

        projectAdapter = new ProjectProgressAdapter();
        rvProjectProgress.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvProjectProgress.setAdapter(projectAdapter);

        teamAdapter = new TeamWorkloadAdapter();
        rvTeamWorkload.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvTeamWorkload.setAdapter(teamAdapter);

        // Real calculations from local tasks
        db.taskDao().getAllLive().observe(getViewLifecycleOwner(), tasks -> {
            int total = (tasks != null) ? tasks.size() : 0;
            int done = 0;
            int inProgress = 0;
            int todo = 0;
            int overdue = 0;

            if (tasks != null) {
                for (TaskEntity t : tasks) {
                    if ("DONE".equalsIgnoreCase(t.statusCategory)) {
                        done++;
                    } else if ("IN_PROGRESS".equalsIgnoreCase(t.statusCategory)) {
                        inProgress++;
                    } else {
                        todo++;
                    }
                }
            }

            int rate = total > 0 ? Math.round((done * 100f) / total) : 0;
            tvCompletionRate.setText(rate + "%");
            tvOverdueCount.setText(String.valueOf(overdue));

            tvLegendDone.setText("Done: " + done);
            tvLegendInProgress.setText("In Progress: " + inProgress);
            tvLegendTodo.setText("To Do: " + todo);

            // Update bar weights
            setBarWeight(barDone, done > 0 ? done : 0.001f);
            setBarWeight(barInProgress, inProgress > 0 ? inProgress : 0.001f);
            setBarWeight(barTodo, todo > 0 ? todo : 0.001f);
        });

        // Real project progress list
        db.projectDao().getAllLive().observe(getViewLifecycleOwner(), projects -> {
            if (projects != null) {
                projectAdapter.setProjects(projects);
            }
        });

        loadTeamWorkload();

        swipeRefreshReports.setColorSchemeResources(R.color.primary_earth, R.color.muted_clay);
        swipeRefreshReports.setOnRefreshListener(() -> {
            loadTeamWorkload();
            swipeRefreshReports.setRefreshing(false);
        });
    }

    private void setBarWeight(View v, float weight) {
        LinearLayout.LayoutParams params = (LinearLayout.LayoutParams) v.getLayoutParams();
        params.weight = weight;
        v.setLayoutParams(params);
    }

    private void loadTeamWorkload() {
        repository.fetchTeam(new ProjectFlowRepository.DataCallback<List<TeamMemberDto>>() {
            @Override
            public void onData(List<TeamMemberDto> data) {
                if (getActivity() != null) {
                    getActivity().runOnUiThread(() -> teamAdapter.setTeam(data));
                }
            }

            @Override
            public void onError(String message) {}
        });
    }

    // Adapters for Project Progress and Team Workload
    private static class ProjectProgressAdapter extends RecyclerView.Adapter<ProjectProgressAdapter.ViewHolder> {
        private final List<ProjectEntity> list = new ArrayList<>();

        void setProjects(List<ProjectEntity> projects) {
            list.clear();
            if (projects != null) list.addAll(projects);
            notifyDataSetChanged();
        }

        @NonNull
        @Override
        public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_project, parent, false);
            return new ViewHolder(v);
        }

        @Override
        public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
            ProjectEntity p = list.get(position);
            holder.tvTitle.setText(p.name);
            holder.tvMeta.setText((p.code != null ? p.code + " • " : "") + (p.status != null ? p.status : "Active"));
            int prog = "COMPLETED".equalsIgnoreCase(p.status) ? 100 : 65;
            holder.pbProgress.setProgress(prog);
            holder.tvProgress.setText(prog + "%");
        }

        @Override
        public int getItemCount() { return list.size(); }

        static class ViewHolder extends RecyclerView.ViewHolder {
            TextView tvTitle, tvMeta, tvProgress;
            ProgressBar pbProgress;
            ViewHolder(@NonNull View itemView) {
                super(itemView);
                tvTitle = itemView.findViewById(R.id.tvProjectName);
                tvMeta = itemView.findViewById(R.id.tvProjectMeta);
                tvProgress = itemView.findViewById(R.id.tvProgressPercent);
                pbProgress = itemView.findViewById(R.id.pbProjectProgress);
            }
        }
    }

    private static class TeamWorkloadAdapter extends RecyclerView.Adapter<TeamWorkloadAdapter.ViewHolder> {
        private final List<TeamMemberDto> members = new ArrayList<>();

        void setTeam(List<TeamMemberDto> data) {
            members.clear();
            if (data != null) members.addAll(data);
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
            holder.tvTasks.setText(m.assignedTasksCount + " Assigned Tasks");
        }

        @Override
        public int getItemCount() { return members.size(); }

        static class ViewHolder extends RecyclerView.ViewHolder {
            TextView tvName, tvRole, tvTasks;
            ViewHolder(@NonNull View itemView) {
                super(itemView);
                tvName = itemView.findViewById(R.id.tvMemberName);
                tvRole = itemView.findViewById(R.id.tvMemberRole);
                tvTasks = itemView.findViewById(R.id.tvMemberProjects);
            }
        }
    }
}
