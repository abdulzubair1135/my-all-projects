package com.example.meshlink.ai.ui;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.meshlink.R;
import com.example.meshlink.ai.model.DeviceCapabilityDetector;
import com.example.meshlink.ai.model.ModelManager;
import com.example.meshlink.ai.model.ModelMetadata;

import java.io.File;

public class NexusAiSettingsActivity extends AppCompatActivity {

    private TextView tvDeviceStats, tvModelName, tvModelDesc, tvModelStatus, tvDownloadProgress;
    private ProgressBar pbDownload;
    private Button btnDownloadModel, btnDeleteModel;
    private RadioGroup rgAiMode, rgModelSelector;
    private RadioButton rbBattery, rbBalanced, rbPerformance;
    private RadioButton rbModel06B, rbModel17B, rbModel4B;

    private ModelManager modelManager;
    private ModelMetadata activeModel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_nexus_ai_settings);

        modelManager = ModelManager.getInstance(this);
        activeModel = modelManager.getActiveModel();

        initViews();
        displayDeviceStats();
        updateModelCard();
    }

    private void initViews() {
        findViewById(R.id.btnBackSettings).setOnClickListener(v -> finish());

        tvDeviceStats = findViewById(R.id.tvDeviceStats);
        tvModelName = findViewById(R.id.tvModelName);
        tvModelDesc = findViewById(R.id.tvModelDesc);
        tvModelStatus = findViewById(R.id.tvModelStatus);
        tvDownloadProgress = findViewById(R.id.tvDownloadProgress);
        pbDownload = findViewById(R.id.pbDownload);
        btnDownloadModel = findViewById(R.id.btnDownloadModel);
        btnDeleteModel = findViewById(R.id.btnDeleteModel);

        rgModelSelector = findViewById(R.id.rgModelSelector);
        rbModel06B = findViewById(R.id.rbModel06B);
        rbModel17B = findViewById(R.id.rbModel17B);
        rbModel4B = findViewById(R.id.rbModel4B);

        // Pre-select active model in RadioGroup
        if (ModelMetadata.QWEN3_0_6B.id.equals(activeModel.id)) {
            rbModel06B.setChecked(true);
        } else if (ModelMetadata.QWEN3_4B.id.equals(activeModel.id)) {
            rbModel4B.setChecked(true);
        } else {
            rbModel17B.setChecked(true);
        }

        rgModelSelector.setOnCheckedChangeListener((group, checkedId) -> {
            if (modelManager.isDownloading()) {
                Toast.makeText(this, "Please cancel active download before switching models", Toast.LENGTH_SHORT).show();
                return;
            }

            if (checkedId == R.id.rbModel06B) {
                activeModel = ModelMetadata.QWEN3_0_6B;
            } else if (checkedId == R.id.rbModel4B) {
                activeModel = ModelMetadata.QWEN3_4B;
            } else {
                activeModel = ModelMetadata.QWEN3_1_7B;
            }

            modelManager.setActiveModel(activeModel.id);
            Toast.makeText(this, "Active model selected: " + activeModel.displayName, Toast.LENGTH_SHORT).show();
            updateModelCard();
        });

        rgAiMode = findViewById(R.id.rgAiMode);
        rbBattery = findViewById(R.id.rbBattery);
        rbBalanced = findViewById(R.id.rbBalanced);
        rbPerformance = findViewById(R.id.rbPerformance);

        String currentMode = modelManager.getAiMode();
        if ("battery".equalsIgnoreCase(currentMode)) rbBattery.setChecked(true);
        else if ("performance".equalsIgnoreCase(currentMode)) rbPerformance.setChecked(true);
        else rbBalanced.setChecked(true);

        rgAiMode.setOnCheckedChangeListener((group, checkedId) -> {
            if (checkedId == R.id.rbBattery) modelManager.setAiMode("battery");
            else if (checkedId == R.id.rbPerformance) modelManager.setAiMode("performance");
            else modelManager.setAiMode("balanced");
            Toast.makeText(this, "AI mode updated", Toast.LENGTH_SHORT).show();
        });

        btnDownloadModel.setOnClickListener(v -> startDownload());
        btnDeleteModel.setOnClickListener(v -> deleteModel());

        View btnOpenServer = findViewById(R.id.btnOpenPocketAiServer);
        if (btnOpenServer != null) {
            btnOpenServer.setOnClickListener(v ->
                    startActivity(new android.content.Intent(this, com.example.meshlink.ai.server.PocketAiServerActivity.class)));
        }
    }

    private void displayDeviceStats() {
        DeviceCapabilityDetector.DeviceProfile p = DeviceCapabilityDetector.detect(this);
        String stats = "• RAM: " + p.ramTotalGb + " GB total (" + (p.availableRamBytes / (1024 * 1024)) + " MB free)\n" +
                "• CPU: " + p.cpuCores + " Cores (" + p.cpuArchitecture + ")\n" +
                "• Storage: " + p.storageAvailableMb + " MB available\n" +
                "• Battery: " + p.batteryPct + "% " + (p.isCharging ? "⚡ Charging" : "🔋") + "\n" +
                "• Android: Version " + p.androidVersion + " (API " + p.androidSdk + ")\n" +
                "• Detected Hardware Tier: " + p.recommendedTier;
        tvDeviceStats.setText(stats);
    }

    private void updateModelCard() {
        tvModelName.setText(activeModel.displayName);
        tvModelDesc.setText(activeModel.tagLine + "\nSize: ~" + activeModel.sizeMb + " MB");

        boolean isDownloaded = modelManager.isModelDownloaded(activeModel);
        if (isDownloaded) {
            tvModelStatus.setText("Status: Downloaded & Active Locally ✓");
            tvModelStatus.setTextColor(getColor(R.color.green_text));
            btnDownloadModel.setVisibility(View.GONE);
            btnDeleteModel.setVisibility(View.VISIBLE);
            pbDownload.setVisibility(View.GONE);
            tvDownloadProgress.setVisibility(View.GONE);
        } else {
            tvModelStatus.setText("Status: Using Fast Built-in Knowledge Base (Offline)");
            tvModelStatus.setTextColor(getColor(R.color.primary));
            btnDownloadModel.setVisibility(View.VISIBLE);
            btnDeleteModel.setVisibility(View.GONE);
        }
    }

    private void startDownload() {
        if (modelManager.isDownloading()) {
            modelManager.cancelDownload();
            btnDownloadModel.setText("📥 Download Model");
            pbDownload.setVisibility(View.GONE);
            tvDownloadProgress.setVisibility(View.GONE);
            return;
        }

        pbDownload.setVisibility(View.VISIBLE);
        pbDownload.setProgress(0);
        tvDownloadProgress.setVisibility(View.VISIBLE);
        tvDownloadProgress.setText("Starting download...");
        btnDownloadModel.setText("❌ Cancel Download");

        modelManager.downloadModel(activeModel, new ModelManager.DownloadCallback() {
            @Override
            public void onProgress(int percent, long downloadedBytes, long totalBytes, String speedText) {
                pbDownload.setProgress(percent);
                long dMb = downloadedBytes / (1024 * 1024);
                long tMb = totalBytes / (1024 * 1024);
                tvDownloadProgress.setText(dMb + "MB / " + tMb + "MB (" + percent + "%) • " + speedText);
            }

            @Override
            public void onSuccess(File modelFile) {
                Toast.makeText(NexusAiSettingsActivity.this, "Model downloaded successfully!", Toast.LENGTH_SHORT).show();
                updateModelCard();
            }

            @Override
            public void onError(String error) {
                Toast.makeText(NexusAiSettingsActivity.this, "Download failed: " + error, Toast.LENGTH_LONG).show();
                updateModelCard();
                btnDownloadModel.setText("📥 Retry Download");
            }
        });
    }

    private void deleteModel() {
        if (modelManager.deleteModel(activeModel)) {
            Toast.makeText(this, "Model deleted. Reverted to built-in knowledge base.", Toast.LENGTH_SHORT).show();
            updateModelCard();
        } else {
            Toast.makeText(this, "Failed to delete model file.", Toast.LENGTH_SHORT).show();
        }
    }
}
