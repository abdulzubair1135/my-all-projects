package com.projectflow.android.ui.fragment;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.projectflow.android.R;
import com.projectflow.android.data.local.AppDatabase;
import com.projectflow.android.data.local.TaskEntity;
import com.projectflow.android.ui.adapter.TaskAdapter;

import java.util.ArrayList;
import java.util.List;

public class KanbanFragment extends Fragment {

    private RecyclerView rvTodo, rvInProgress, rvDone;
    private TaskAdapter todoAdapter, inProgressAdapter, doneAdapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_kanban, container, false);
        rvTodo = v.findViewById(R.id.rvTodoTasks);
        rvInProgress = v.findViewById(R.id.rvInProgressTasks);
        rvDone = v.findViewById(R.id.rvDoneTasks);
        return v;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        todoAdapter = new TaskAdapter(task -> onTaskClicked(task));
        inProgressAdapter = new TaskAdapter(task -> onTaskClicked(task));
        doneAdapter = new TaskAdapter(task -> onTaskClicked(task));

        rvTodo.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvTodo.setAdapter(todoAdapter);

        rvInProgress.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvInProgress.setAdapter(inProgressAdapter);

        rvDone.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvDone.setAdapter(doneAdapter);

        AppDatabase.getInstance(requireContext()).taskDao().getAllLive().observe(getViewLifecycleOwner(), list -> {
            List<TaskEntity> todo = new ArrayList<>();
            List<TaskEntity> inProgress = new ArrayList<>();
            List<TaskEntity> done = new ArrayList<>();

            if (list != null) {
                for (TaskEntity t : list) {
                    String cat = t.statusCategory != null ? t.statusCategory.toUpperCase() : "TODO";
                    if (cat.contains("DONE")) {
                        done.add(t);
                    } else if (cat.contains("PROGRESS")) {
                        inProgress.add(t);
                    } else {
                        todo.add(t);
                    }
                }
            }

            todoAdapter.setTasks(todo);
            inProgressAdapter.setTasks(inProgress);
            doneAdapter.setTasks(done);
        });
    }

    private void onTaskClicked(TaskEntity task) {
        Toast.makeText(requireContext(), task.title + " (" + task.priority + ")", Toast.LENGTH_SHORT).show();
    }
}
