package com.example.meshlink.ai.model;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

public class ModelManager {

    private static final String TAG = "ModelManager";
    private static final String PREF_NAME = "nexus_ai_prefs";
    private static final String KEY_ACTIVE_MODEL_ID = "active_model_id";
    private static final String KEY_AI_MODE = "ai_mode"; // "battery", "balanced", "performance"

    private static ModelManager instance;
    private final Context appContext;
    private final SharedPreferences prefs;
    private final ExecutorService downloadExecutor = Executors.newSingleThreadExecutor();
    private final AtomicBoolean isDownloading = new AtomicBoolean(false);
    private final AtomicBoolean cancelDownload = new AtomicBoolean(false);

    public interface DownloadCallback {
        void onProgress(int percent, long downloadedBytes, long totalBytes, String speedText);
        void onSuccess(File modelFile);
        void onError(String error);
    }

    private ModelManager(Context context) {
        this.appContext = context.getApplicationContext();
        this.prefs = appContext.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
    }

    public static synchronized ModelManager getInstance(Context context) {
        if (instance == null) {
            instance = new ModelManager(context);
        }
        return instance;
    }

    public File getModelsDir() {
        File dir = appContext.getExternalFilesDir("nexus_models");
        if (dir == null) {
            dir = new File(appContext.getFilesDir(), "nexus_models");
        }
        if (!dir.exists()) {
            dir.mkdirs();
        }
        return dir;
    }

    public File getModelFile(ModelMetadata metadata) {
        return new File(getModelsDir(), metadata.fileName);
    }

    public boolean isModelDownloaded(ModelMetadata metadata) {
        File file = getModelFile(metadata);
        return file.exists() && file.length() > 1024 * 1024; // > 1MB
    }

    public ModelMetadata getActiveModel() {
        String activeId = prefs.getString(KEY_ACTIVE_MODEL_ID, null);
        if (activeId != null) {
            return ModelMetadata.getById(activeId);
        }
        // Auto-recommend by hardware
        DeviceCapabilityDetector.DeviceProfile profile = DeviceCapabilityDetector.detect(appContext);
        if (profile.recommendedTier == DeviceCapabilityDetector.DeviceTier.LOW) {
            return ModelMetadata.QWEN3_0_6B;
        } else if (profile.recommendedTier == DeviceCapabilityDetector.DeviceTier.NORMAL) {
            return ModelMetadata.QWEN3_1_7B;
        } else {
            return ModelMetadata.QWEN3_4B;
        }
    }

    public void setActiveModel(String modelId) {
        prefs.edit().putString(KEY_ACTIVE_MODEL_ID, modelId).apply();
    }

    public static final String MODE_QWEN = "qwen";       // Pure offline Qwen LLM only
    public static final String MODE_DEFAULT = "default"; // Default brain only (no Qwen)
    public static final String MODE_HYBRID = "hybrid";   // Qwen LLM + Default tools/search

    public String getChatMode() {
        return prefs.getString("chat_execution_mode", MODE_HYBRID);
    }

    public void setChatMode(String mode) {
        prefs.edit().putString("chat_execution_mode", mode).apply();
    }

    public String getAiMode() {
        return prefs.getString(KEY_AI_MODE, "balanced");
    }

    public void setAiMode(String mode) {
        prefs.edit().putString(KEY_AI_MODE, mode).apply();
    }

    public boolean isDownloading() {
        return isDownloading.get();
    }

    public void cancelDownload() {
        cancelDownload.set(true);
    }

    public boolean deleteModel(ModelMetadata metadata) {
        File file = getModelFile(metadata);
        if (file.exists()) {
            return file.delete();
        }
        return false;
    }

    public void downloadModel(ModelMetadata metadata, DownloadCallback callback) {
        if (!isDownloading.compareAndSet(false, true)) {
            if (callback != null) callback.onError("Another download is already in progress.");
            return;
        }
        cancelDownload.set(false);

        downloadExecutor.execute(() -> {
            Handler mainHandler = new Handler(Looper.getMainLooper());
            HttpURLConnection connection = null;
            InputStream in = null;
            FileOutputStream out = null;
            File tempFile = new File(getModelsDir(), metadata.fileName + ".tmp");
            File targetFile = getModelFile(metadata);

            try {
                URL url = new URL(metadata.downloadUrl);
                connection = (HttpURLConnection) url.openConnection();
                connection.setConnectTimeout(15000);
                connection.setReadTimeout(30000);
                connection.setRequestProperty("User-Agent", "NexusMeshLink-Mobile/1.0");
                connection.connect();

                int responseCode = connection.getResponseCode();
                if (responseCode != HttpURLConnection.HTTP_OK && responseCode != HttpURLConnection.HTTP_PARTIAL) {
                    throw new Exception("HTTP error code: " + responseCode);
                }

                long totalBytes = connection.getContentLengthLong();
                if (totalBytes <= 0) {
                    totalBytes = metadata.sizeBytes;
                }

                in = connection.getInputStream();
                out = new FileOutputStream(tempFile);

                byte[] buffer = new byte[32768];
                long downloaded = 0;
                long startTime = System.currentTimeMillis();
                long lastProgressTime = 0;

                int read;
                while ((read = in.read(buffer)) != -1) {
                    if (cancelDownload.get()) {
                        tempFile.delete();
                        throw new Exception("Download cancelled by user.");
                    }
                    out.write(buffer, 0, read);
                    downloaded += read;

                    long now = System.currentTimeMillis();
                    if (now - lastProgressTime > 400 || downloaded == totalBytes) {
                        lastProgressTime = now;
                        int percent = (int) ((downloaded * 100) / totalBytes);
                        long elapsedSec = Math.max(1, (now - startTime) / 1000);
                        long speedKb = (downloaded / 1024) / elapsedSec;
                        String speedText = (speedKb > 1024) ? String.format("%.1f MB/s", speedKb / 1024.0) : speedKb + " KB/s";

                        final long dBytes = downloaded;
                        final long tBytes = totalBytes;
                        mainHandler.post(() -> {
                            if (callback != null) callback.onProgress(percent, dBytes, tBytes, speedText);
                        });
                    }
                }

                out.flush();
                out.close();
                out = null;

                if (targetFile.exists()) targetFile.delete();
                if (!tempFile.renameTo(targetFile)) {
                    throw new Exception("Failed to rename temporary model file.");
                }

                setActiveModel(metadata.id);
                mainHandler.post(() -> {
                    isDownloading.set(false);
                    if (callback != null) callback.onSuccess(targetFile);
                });

            } catch (Exception e) {
                Log.e(TAG, "Download error: " + e.getMessage(), e);
                if (tempFile.exists()) tempFile.delete();
                mainHandler.post(() -> {
                    isDownloading.set(false);
                    if (callback != null) callback.onError(e.getMessage());
                });
            } finally {
                isDownloading.set(false);
                try { if (in != null) in.close(); } catch (Exception ignored) {}
                try { if (out != null) out.close(); } catch (Exception ignored) {}
                if (connection != null) connection.disconnect();
            }
        });
    }
}
