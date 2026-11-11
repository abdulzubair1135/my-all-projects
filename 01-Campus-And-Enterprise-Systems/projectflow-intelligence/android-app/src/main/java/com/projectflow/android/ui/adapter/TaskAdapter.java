package com.projectflow.android.ui.adapter;

import android.graphics.Color;
import android.graphics.Paint;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;
import com.projectflow.android.R;
import com.projectflow.android.data.local.TaskEntity;
import java.util.ArrayList;
import java.util.List;

public class TaskAdapter extends RecyclerView.Adapter<TaskAdapter.TaskViewHolder> {

    private List<TaskEntity> tasks = new ArrayList<>();
    private final OnTaskClickListener listener;

    public interface OnTaskClickListener {
        void onTaskClick(TaskEntity task);
    }

    public TaskAdapter(OnTaskClickListener listener) {
        this.listener = listener;
    }

    public void setTasks(List<TaskEntity> list) {
        this.tasks = list != null ? list : new ArrayList<>();
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public TaskViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_task, parent, false);
        return new TaskViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull TaskViewHolder holder, int position) {
        TaskEntity t = tasks.get(position);
        holder.tvTitle.setText(t.title != null ? t.title : "Untitled Task");

        String priority = (t.priority != null) ? t.priority.toUpperCase() : "MEDIUM";
        holder.tvPriority.setText(priority);

        // Dynamic priority coloring
        if (priority.contains("HIGH") || priority.contains("CRIT")) {
            holder.tvPriority.setTextColor(Color.parseColor("#E05D52"));
        } else if (priority.contains("MED")) {
            holder.tvPriority.setTextColor(ContextCompat.getColor(holder.itemView.getContext(), R.color.chart_progress));
        } else {
            holder.tvPriority.setTextColor(ContextCompat.getColor(holder.itemView.getContext(), R.color.chart_done));
        }

        String dueDate = (t.dueDate != null && t.dueDate.contains("T")) ? t.dueDate.split("T")[0] : (t.dueDate != null ? t.dueDate : "28 Apr");
        holder.tvDueDate.setText(dueDate);

        String prj = (t.projectId != null && !t.projectId.isEmpty()) ? "PRJ-" + t.projectId : "PF-CORE";
        holder.tvProject.setText(prj);

        if (holder.tvAssignee != null) {
            if (t.assigneeName != null && !t.assigneeName.isEmpty()) {
                holder.tvAssignee.setText("👤 " + t.assigneeName);
                holder.tvAssignee.setVisibility(View.VISIBLE);
            } else if (t.teamName != null && !t.teamName.isEmpty()) {
                holder.tvAssignee.setText("👥 " + t.teamName);
                holder.tvAssignee.setVisibility(View.VISIBLE);
            } else {
                holder.tvAssignee.setVisibility(View.GONE);
            }
        }

        boolean isDone = "DONE".equalsIgnoreCase(t.statusCategory);
        holder.cbComplete.setOnCheckedChangeListener(null);
        holder.cbComplete.setChecked(isDone);

        applyCompletionStyle(holder, isDone);

        holder.cbComplete.setOnCheckedChangeListener((btn, checked) -> {
            t.statusCategory = checked ? "DONE" : "IN_PROGRESS";
            t.progressPercent = checked ? 100 : 50;
            applyCompletionStyle(holder, checked);
            new Thread(() -> {
                com.projectflow.android.data.local.AppDatabase.getInstance(holder.itemView.getContext()).taskDao().insert(t);
                if (t.id != null && !t.id.isEmpty()) {
                    new com.projectflow.android.data.repository.ProjectFlowRepository(holder.itemView.getContext())
                            .updateTaskStatus(t.id, t.statusCategory, t.progressPercent, null);
                }
            }).start();
        });

        View.OnClickListener clickListener = v -> {
            if (listener != null) listener.onTaskClick(t);
        };
        holder.itemView.setOnClickListener(clickListener);
        holder.tvTitle.setOnClickListener(clickListener);
        if (holder.ivAction != null) {
            holder.ivAction.setOnClickListener(clickListener);
        }
    }

    private void applyCompletionStyle(TaskViewHolder holder, boolean isDone) {
        if (isDone) {
            holder.tvTitle.setPaintFlags(holder.tvTitle.getPaintFlags() | Paint.STRIKE_THRU_TEXT_FLAG);
            holder.tvTitle.setAlpha(0.55f);
        } else {
            holder.tvTitle.setPaintFlags(holder.tvTitle.getPaintFlags() & (~Paint.STRIKE_THRU_TEXT_FLAG));
            holder.tvTitle.setAlpha(1.0f);
        }
    }

    @Override
    public int getItemCount() {
        return tasks.size();
    }

    static class TaskViewHolder extends RecyclerView.ViewHolder {
        TextView tvTitle, tvPriority, tvDueDate, tvProject, tvAssignee;
        CheckBox cbComplete;
        ImageView ivAction;

        public TaskViewHolder(@NonNull View itemView) {
            super(itemView);
            tvTitle = itemView.findViewById(R.id.tvTaskTitle);
            tvPriority = itemView.findViewById(R.id.tvTaskPriority);
            tvDueDate = itemView.findViewById(R.id.tvTaskDueDate);
            tvProject = itemView.findViewById(R.id.tvTaskProject);
            tvAssignee = itemView.findViewById(R.id.tvTaskAssignee);
            cbComplete = itemView.findViewById(R.id.cbTaskComplete);
            ivAction = itemView.findViewById(R.id.ivTaskAction);
        }
    }
}
