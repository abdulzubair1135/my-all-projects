package com.example.meshlink.ai.ui;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.meshlink.R;
import com.example.meshlink.ai.model.LocalInferenceEngine;
import com.example.meshlink.ai.model.ModelManager;
import com.example.meshlink.ai.model.ModelMetadata;

import java.util.ArrayList;
import java.util.List;

public class NexusAiFragment extends Fragment implements AiMessageAdapter.OnChipClickListener {

    private RecyclerView rvAiMessages;
    private EditText etAiInput;
    private View btnAiSend;
    private View llAiWelcome;
    private TextView tvAiHeaderStatus;
    private View dotPocketAiServerRunning;

    // Bottom Chat Bar Mode Selector
    private View btnModeSelector;
    private TextView tvActiveModeIcon;
    private TextView tvActiveModeLabel;

    private AiMessageAdapter adapter;
    private final List<AiMessage> messageList = new ArrayList<>();
    private LocalInferenceEngine inferenceEngine;
    private ModelManager modelManager;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_nexus_ai, container, false);

        modelManager = ModelManager.getInstance(requireContext());
        inferenceEngine = LocalInferenceEngine.getInstance(requireContext());

        initViews(view);
        setupRecyclerView();
        updateModeSelectorUI();
        updateHeaderStatus();

        return view;
    }

    private void initViews(View v) {
        rvAiMessages = v.findViewById(R.id.rvAiMessages);
        etAiInput = v.findViewById(R.id.etAiInput);
        btnAiSend = v.findViewById(R.id.btnAiSend);
        llAiWelcome = v.findViewById(R.id.llAiWelcome);
        tvAiHeaderStatus = v.findViewById(R.id.tvAiHeaderStatus);

        btnModeSelector = v.findViewById(R.id.btnModeSelector);
        tvActiveModeIcon = v.findViewById(R.id.tvActiveModeIcon);
        tvActiveModeLabel = v.findViewById(R.id.tvActiveModeLabel);

        dotPocketAiServerRunning = v.findViewById(R.id.dotPocketAiServerRunning);
        View btnPocketAiServer = v.findViewById(R.id.btnPocketAiServer);
        if (btnPocketAiServer != null) {
            btnPocketAiServer.setOnClickListener(view ->
                    startActivity(new Intent(requireContext(), com.example.meshlink.ai.server.PocketAiServerActivity.class)));
        }

        v.findViewById(R.id.btnAiSettings).setOnClickListener(view ->
                startActivity(new Intent(requireContext(), NexusAiSettingsActivity.class)));

        if (tvAiHeaderStatus != null) {
            tvAiHeaderStatus.setOnClickListener(view -> showQuickModelSelectorDialog());
        }

        if (btnModeSelector != null) {
            btnModeSelector.setOnClickListener(view -> showChatModeSelectorDialog());
        }

        btnAiSend.setOnClickListener(view -> {
            String text = etAiInput.getText().toString().trim();
            if (!text.isEmpty()) {
                submitPrompt(text);
                etAiInput.setText("");
            }
        });

        // Quick chip actions in welcome screen
        v.findViewById(R.id.chipExplain).setOnClickListener(view -> submitPrompt("Bhai recursion kya hota hai simple samjhao"));
        v.findViewById(R.id.chipCode).setOnClickListener(view -> submitPrompt("Write a recursive factorial function in Java"));
        v.findViewById(R.id.chipPpt).setOnClickListener(view -> submitPrompt("Bhai AI presentation par PPT slide structure bana do"));
        v.findViewById(R.id.chipEmergency).setOnClickListener(view -> submitPrompt("Accident ho gaya hai, urgent first aid batao"));
    }

    private void setupRecyclerView() {
        adapter = new AiMessageAdapter(requireContext(), messageList, this);
        LinearLayoutManager lm = new LinearLayoutManager(requireContext());
        lm.setStackFromEnd(true);
        rvAiMessages.setLayoutManager(lm);
        rvAiMessages.setAdapter(adapter);
    }

    private void updateModeSelectorUI() {
        if (!isAdded() || modelManager == null) return;
        String mode = modelManager.getChatMode();

        if (ModelManager.MODE_QWEN.equals(mode)) {
            if (tvActiveModeIcon != null) tvActiveModeIcon.setText("🧠");
            if (tvActiveModeLabel != null) tvActiveModeLabel.setText("Qwen");
            if (etAiInput != null) etAiInput.setHint("Ask offline Qwen LLM...");
        } else if (ModelManager.MODE_DEFAULT.equals(mode)) {
            if (tvActiveModeIcon != null) tvActiveModeIcon.setText("⚡");
            if (tvActiveModeLabel != null) tvActiveModeLabel.setText("Default");
            if (etAiInput != null) etAiInput.setHint("Ask Nexus Brain (No Qwen)...");
        } else { // Hybrid
            if (tvActiveModeIcon != null) tvActiveModeIcon.setText("🤖");
            if (tvActiveModeLabel != null) tvActiveModeLabel.setText("Hybrid");
            if (etAiInput != null) etAiInput.setHint("Ask Nexus AI (Hybrid mode)...");
        }
        updateHeaderStatus();
    }

    private void updateHeaderStatus() {
        if (tvAiHeaderStatus != null && inferenceEngine != null) {
            tvAiHeaderStatus.setText(inferenceEngine.getStatusSummary());
        }
    }

    @Override
    public void onResume() {
        super.onResume();
        updateModeSelectorUI();
        updateHeaderStatus();
        if (dotPocketAiServerRunning != null) {
            boolean isRunning = com.example.meshlink.ai.server.PocketAiServerController.INSTANCE.getCurrentState() ==
                    com.example.meshlink.ai.server.PocketAiServerController.ServerState.RUNNING;
            dotPocketAiServerRunning.setVisibility(isRunning ? View.VISIBLE : View.GONE);
        }
    }

    private void submitPrompt(String prompt) {
        llAiWelcome.setVisibility(View.GONE);

        // Add user turn
        messageList.add(new AiMessage(prompt, true));

        // Add live thinking indicator
        String mode = modelManager.getChatMode();
        String thinkingLabel;
        if (ModelManager.MODE_QWEN.equals(mode)) {
            ModelMetadata active = modelManager.getActiveModel();
            thinkingLabel = "💭 " + active.displayName + " is thinking...";
        } else if (ModelManager.MODE_DEFAULT.equals(mode)) {
            thinkingLabel = "⚡ Nexus Brain is searching rules...";
        } else {
            thinkingLabel = "💭 Nexus AI (Hybrid) is thinking...";
        }

        AiMessage thinkingMsg = new AiMessage(thinkingLabel, false, true);
        messageList.add(thinkingMsg);

        final int thinkingIndex = messageList.size() - 1;
        adapter.notifyItemRangeInserted(thinkingIndex - 1, 2);
        rvAiMessages.smoothScrollToPosition(thinkingIndex);

        // Process through local inference engine
        inferenceEngine.processPrompt(prompt, result -> {
            if (!isAdded()) return;

            thinkingMsg.text = result.outputText;
            thinkingMsg.thought = result.thought; // Populate Qwen's thinking process!
            thinkingMsg.isThinking = false;
            thinkingMsg.actionType = result.actionType;
            thinkingMsg.actionPayload = result.actionPayload;
            thinkingMsg.addChips(result.quickChips);

            adapter.notifyItemChanged(thinkingIndex);
            rvAiMessages.smoothScrollToPosition(thinkingIndex);
        });
    }

    @Override
    public void onChipClick(String chipText) {
        if (chipText.contains("Download Qwen") || chipText.contains("Settings")) {
            startActivity(new Intent(requireContext(), NexusAiSettingsActivity.class));
        } else if (chipText.contains("Switch to Default")) {
            modelManager.setChatMode(ModelManager.MODE_DEFAULT);
            updateModeSelectorUI();
            Toast.makeText(requireContext(), "⚡ Switched to Default (Nexus Brain)", Toast.LENGTH_SHORT).show();
        } else if (chipText.contains("Explain")) {
            submitPrompt("Bhai OOP ke concepts simple language me samjha do");
        } else if (chipText.contains("Code")) {
            submitPrompt("Binary search ka Java code likh kar do");
        } else if (chipText.contains("PPT")) {
            submitPrompt("Off-grid Mesh Network par 5 slides ki presentation bana do");
        } else if (chipText.contains("Search Web")) {
            submitPrompt("Search latest Android features online");
        } else if (chipText.contains("Refresh Mesh")) {
            submitPrompt("Current mesh network status check karo");
        } else {
            submitPrompt(chipText);
        }
    }

    /**
     * Shows modal to choose between the 3 modes:
     * 1. Qwen (Pure offline LLM)
     * 2. Default (Nexus Brain without Qwen)
     * 3. Qwen and Default Hybrid
     */
    private void showChatModeSelectorDialog() {
        if (!isAdded()) return;

        View dialogView = getLayoutInflater().inflate(R.layout.dialog_ai_mode_selector, null);
        AlertDialog dialog = new AlertDialog.Builder(requireContext())
                .setView(dialogView)
                .create();
        if (dialog.getWindow() != null) {
            dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
        }

        dialogView.findViewById(R.id.btnModeHybrid).setOnClickListener(v -> {
            modelManager.setChatMode(ModelManager.MODE_HYBRID);
            updateModeSelectorUI();
            Toast.makeText(requireContext(), "🤖 Hybrid Mode Activated (Qwen + Tools)", Toast.LENGTH_SHORT).show();
            dialog.dismiss();
        });

        dialogView.findViewById(R.id.btnModeDefault).setOnClickListener(v -> {
            modelManager.setChatMode(ModelManager.MODE_DEFAULT);
            updateModeSelectorUI();
            Toast.makeText(requireContext(), "⚡ Default Nexus Brain (No Qwen) Activated", Toast.LENGTH_SHORT).show();
            dialog.dismiss();
        });

        dialogView.findViewById(R.id.btnModeQwen).setOnClickListener(v -> {
            modelManager.setChatMode(ModelManager.MODE_QWEN);
            updateModeSelectorUI();
            Toast.makeText(requireContext(), "🧠 Pure Qwen LLM Mode Activated", Toast.LENGTH_SHORT).show();
            dialog.dismiss();
        });

        dialogView.findViewById(R.id.btnModeCancel).setOnClickListener(v -> dialog.dismiss());

        dialog.show();
    }

    private void showQuickModelSelectorDialog() {
        if (!isAdded()) return;

        View dialogView = getLayoutInflater().inflate(R.layout.dialog_quick_model_selector, null);
        AlertDialog dialog = new AlertDialog.Builder(requireContext())
                .setView(dialogView)
                .create();
        if (dialog.getWindow() != null) {
            dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
        }

        dialogView.findViewById(R.id.btnModel06B).setOnClickListener(v -> {
            modelManager.setActiveModel(ModelMetadata.QWEN3_0_6B.id);
            updateModeSelectorUI();
            Toast.makeText(requireContext(), "Selected: " + ModelMetadata.QWEN3_0_6B.displayName, Toast.LENGTH_SHORT).show();
            dialog.dismiss();
        });

        dialogView.findViewById(R.id.btnModel17B).setOnClickListener(v -> {
            modelManager.setActiveModel(ModelMetadata.QWEN3_1_7B.id);
            updateModeSelectorUI();
            Toast.makeText(requireContext(), "Selected: " + ModelMetadata.QWEN3_1_7B.displayName, Toast.LENGTH_SHORT).show();
            dialog.dismiss();
        });

        dialogView.findViewById(R.id.btnModel4B).setOnClickListener(v -> {
            modelManager.setActiveModel(ModelMetadata.QWEN3_4B.id);
            updateModeSelectorUI();
            Toast.makeText(requireContext(), "Selected: " + ModelMetadata.QWEN3_4B.displayName, Toast.LENGTH_SHORT).show();
            dialog.dismiss();
        });

        dialogView.findViewById(R.id.btnQuickModelSettings).setOnClickListener(v -> {
            dialog.dismiss();
            startActivity(new Intent(requireContext(), NexusAiSettingsActivity.class));
        });

        dialogView.findViewById(R.id.btnQuickModelCancel).setOnClickListener(v -> dialog.dismiss());

        dialog.show();
    }
}
