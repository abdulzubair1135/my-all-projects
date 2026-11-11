package com.projectflow.android.ui.fragment;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.projectflow.android.R;
import com.projectflow.android.data.local.AppDatabase;
import com.projectflow.android.data.local.ProjectEntity;
import com.projectflow.android.data.repository.ProjectFlowRepository;
import com.projectflow.android.ui.adapter.RiskAdapter;

import java.util.List;

public class RiskRadarFragment extends Fragment {

    private ProjectFlowRepository repository;
    private RiskAdapter adapter;
    private RecyclerView rvRisks;
    private Button btnRun;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_risks, container, false);
        rvRisks = v.findViewById(R.id.rvRisks);
        btnRun = v.findViewById(R.id.btnEvaluateRisks);
        return v;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        repository = new ProjectFlowRepository(requireContext());

        adapter = new RiskAdapter();
        rvRisks.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvRisks.setAdapter(adapter);

        AppDatabase.getInstance(requireContext()).riskDao().getAllLive().observe(getViewLifecycleOwner(), list -> {
            adapter.setRisks(list);
        });

        btnRun.setOnClickListener(v -> {
            new Thread(() -> {
                List<ProjectEntity> projects = AppDatabase.getInstance(requireContext()).projectDao().getByWorkspaceSync("00000000-0000-0000-0000-000000000001");
                if (projects != null && !projects.isEmpty()) {
                    repository.evaluateRisks(projects.get(0).id);
                    requireActivity().runOnUiThread(() -> Toast.makeText(requireContext(), "Risk Radar evaluation running...", Toast.LENGTH_SHORT).show());
                } else {
                    requireActivity().runOnUiThread(() -> Toast.makeText(requireContext(), "No projects available to evaluate", Toast.LENGTH_SHORT).show());
                }
            }).start();
        });
    }
}
