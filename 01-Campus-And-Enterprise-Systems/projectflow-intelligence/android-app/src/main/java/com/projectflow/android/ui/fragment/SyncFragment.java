package com.projectflow.android.ui.fragment;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.work.OneTimeWorkRequest;
import androidx.work.WorkManager;
import com.projectflow.android.R;
import com.projectflow.android.data.local.AppDatabase;
import com.projectflow.android.data.remote.ApiClient;
import com.projectflow.android.data.repository.ProjectFlowRepository;
import com.projectflow.android.worker.SyncWorker;

public class SyncFragment extends Fragment {

    private TextView tvPendingCount;
    private Button btnForceSync, btnSaveUrl;
    private EditText etServerUrl;
    private ProjectFlowRepository repository;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_sync, container, false);
        tvPendingCount = v.findViewById(R.id.tvPendingCount);
        btnForceSync = v.findViewById(R.id.btnForceSync);
        etServerUrl = v.findViewById(R.id.etServerUrl);
        btnSaveUrl = v.findViewById(R.id.btnSaveServerUrl);
        return v;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        repository = new ProjectFlowRepository(requireContext());

        SharedPreferences prefs = requireContext().getSharedPreferences("projectflow_prefs", Context.MODE_PRIVATE);
        etServerUrl.setText(prefs.getString("api_base_url", ApiClient.DEFAULT_URL));

        AppDatabase.getInstance(requireContext()).syncQueueDao().getPendingCountLive().observe(getViewLifecycleOwner(), count -> {
            tvPendingCount.setText((count != null ? count : 0) + " Operations Pending");
        });

        btnForceSync.setOnClickListener(v -> {
            OneTimeWorkRequest syncRequest = new OneTimeWorkRequest.Builder(SyncWorker.class).build();
            WorkManager.getInstance(requireContext()).enqueue(syncRequest);
            repository.refreshWorkspaces();
            repository.refreshProjects();
            Toast.makeText(requireContext(), "Synchronization Enqueued", Toast.LENGTH_SHORT).show();
        });

        btnSaveUrl.setOnClickListener(v -> {
            String newUrl = etServerUrl.getText().toString().trim();
            if (!newUrl.isEmpty()) {
                prefs.edit().putString("api_base_url", newUrl).apply();
                ApiClient.resetService();
                Toast.makeText(requireContext(), "Server URL Updated", Toast.LENGTH_SHORT).show();
            }
        });
    }
}
