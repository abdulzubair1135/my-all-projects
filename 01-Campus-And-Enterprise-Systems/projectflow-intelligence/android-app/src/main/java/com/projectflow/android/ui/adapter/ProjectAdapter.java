package com.projectflow.android.ui.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ProgressBar;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.projectflow.android.R;
import com.projectflow.android.data.local.ProjectEntity;

import java.util.ArrayList;
import java.util.List;

public class ProjectAdapter extends RecyclerView.Adapter<ProjectAdapter.ProjectViewHolder> {

    private List<ProjectEntity> projects = new ArrayList<>();
    private final OnProjectClickListener listener;

    public interface OnProjectClickListener {
        void onProjectClick(ProjectEntity project);
    }

    public ProjectAdapter(OnProjectClickListener listener) {
        this.listener = listener;
    }

    private List<com.projectflow.android.data.local.TaskEntity> tasks = new ArrayList<>();

    public void setTasks(List<com.projectflow.android.data.local.TaskEntity> list) {
        this.tasks = list != null ? list : new ArrayList<>();
        notifyDataSetChanged();
    }

    public void setProjects(List<ProjectEntity> list) {
        this.projects = list != null ? list : new ArrayList<>();
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ProjectViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_project, parent, false);
        return new ProjectViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull ProjectViewHolder holder, int position) {
        ProjectEntity p = projects.get(position);
        holder.tvName.setText(p.name);
        String status = p.status != null ? p.status : "Active";
        holder.tvMeta.setText(status + " • " + (p.code != null ? p.code : "PRJ"));

        if (holder.tvAssignee != null) {
            if (p.assigneeName != null && !p.assigneeName.isEmpty()) {
                holder.tvAssignee.setText("👤 Assigned: " + p.assigneeName);
                holder.tvAssignee.setVisibility(View.VISIBLE);
            } else if (p.assigneeEmail != null && !p.assigneeEmail.isEmpty()) {
                holder.tvAssignee.setText("👤 Assigned: " + p.assigneeEmail);
                holder.tvAssignee.setVisibility(View.VISIBLE);
            } else if (p.teamName != null && !p.teamName.isEmpty()) {
                holder.tvAssignee.setText("👥 Squad: " + p.teamName);
                holder.tvAssignee.setVisibility(View.VISIBLE);
            } else {
                holder.tvAssignee.setText("👤 Unassigned");
                holder.tvAssignee.setVisibility(View.VISIBLE);
            }
        }

        int total = 0;
        int completed = 0;
        for (com.projectflow.android.data.local.TaskEntity t : tasks) {
            if (t.projectId != null && t.projectId.equals(p.id)) {
                total++;
                if ("DONE".equalsIgnoreCase(t.statusCategory) || "COMPLETED".equalsIgnoreCase(t.statusCategory) || t.progressPercent == 100) {
                    completed++;
                }
            }
        }
        int progress = (total > 0) ? (completed * 100 / total) : 0;

        holder.tvProgress.setText(progress + "%");
        holder.pbProgress.setProgress(progress);

        holder.itemView.setOnClickListener(v -> {
            if (listener != null) listener.onProjectClick(p);
        });
    }

    @Override
    public int getItemCount() {
        return projects.size();
    }

    static class ProjectViewHolder extends RecyclerView.ViewHolder {
        TextView tvName, tvMeta, tvAssignee, tvProgress;
        ProgressBar pbProgress;

        public ProjectViewHolder(@NonNull View itemView) {
            super(itemView);
            tvName = itemView.findViewById(R.id.tvProjectName);
            tvMeta = itemView.findViewById(R.id.tvProjectMeta);
            tvAssignee = itemView.findViewById(R.id.tvProjectAssignee);
            tvProgress = itemView.findViewById(R.id.tvProgressPercent);
            pbProgress = itemView.findViewById(R.id.pbProjectProgress);
        }
    }
}
