package com.example.meshlink.ai.model;

import android.content.Context;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/**
 * Manages the native embedded llama.cpp HTTP server (libllama-server.so)
 * running on 127.0.0.1:8080 for 100% offline real Qwen LLM inference.
 */
public class LlamaServerManager {

    private static final String TAG = "LlamaServerManager";
    private static final int PORT = 8080;
    private static final String SERVER_URL = "http://127.0.0.1:" + PORT + "/completion";
    private static final String HEALTH_URL = "http://127.0.0.1:" + PORT + "/health";

    private static LlamaServerManager instance;
    private final Context appContext;
    private final ModelManager modelManager;
    private final OkHttpClient httpClient;
    private Process serverProcess = null;
    private final AtomicBoolean isStarting = new AtomicBoolean(false);

    private LlamaServerManager(Context context) {
        this.appContext = context.getApplicationContext();
        this.modelManager = ModelManager.getInstance(appContext);
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(5, TimeUnit.SECONDS)
                .readTimeout(180, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();
    }

    public static synchronized LlamaServerManager getInstance(Context context) {
        if (instance == null) {
            instance = new LlamaServerManager(context);
        }
        return instance;
    }

    public boolean isServerReady() {
        try {
            Request request = new Request.Builder()
                    .url(HEALTH_URL)
                    .get()
                    .build();
            try (Response resp = httpClient.newCall(request).execute()) {
                return resp.isSuccessful();
            }
        } catch (Exception e) {
            // Check if root or completion responds
            try {
                Request fallback = new Request.Builder()
                        .url("http://127.0.0.1:" + PORT + "/")
                        .get()
                        .build();
                try (Response resp = httpClient.newCall(fallback).execute()) {
                    return resp.isSuccessful() || resp.code() == 404 || resp.code() == 405;
                }
            } catch (Exception ignored) {
                return false;
            }
        }
    }

    public synchronized void startServerIfNeeded() {
        if (isServerReady()) {
            Log.d(TAG, "llama-server already running and healthy on port " + PORT);
            return;
        }

        ModelMetadata active = modelManager.getActiveModel();
        File modelFile = modelManager.getModelFile(active);
        if (!modelFile.exists() || modelFile.length() < 1024 * 1024) {
            // Check fallback to any downloaded model in modelsDir
            File dir = modelManager.getModelsDir();
            File[] files = dir.listFiles((d, name) -> name.endsWith(".gguf"));
            if (files != null && files.length > 0) {
                modelFile = files[0];
                Log.i(TAG, "Using available GGUF model: " + modelFile.getName());
            } else {
                Log.w(TAG, "Cannot start server: Model file not downloaded (" + modelFile.getAbsolutePath() + ")");
                return;
            }
        }

        if (isStarting.get()) return;
        isStarting.set(true);

        final File finalModelFile = modelFile;
        new Thread(() -> {
            try {
                String nativeDir = appContext.getApplicationInfo().nativeLibraryDir;
                File binaryFile = new File(nativeDir, "libllama-server.so");
                if (!binaryFile.exists()) {
                    // Try tmp location as fallback if pushed via adb
                    File tmpBinary = new File("/data/local/tmp/llama/llama-b11512/llama-server");
                    if (tmpBinary.exists()) {
                        binaryFile = tmpBinary;
                    }
                }

                if (!binaryFile.exists()) {
                    Log.e(TAG, "libllama-server.so not found in " + nativeDir);
                    isStarting.set(false);
                    return;
                }

                try {
                    binaryFile.setExecutable(true, false);
                } catch (Exception ignored) {}

                List<String> cmd = new ArrayList<>();
                cmd.add(binaryFile.getAbsolutePath());
                cmd.add("-m");
                cmd.add(finalModelFile.getAbsolutePath());
                cmd.add("--host");
                cmd.add("127.0.0.1");
                cmd.add("--port");
                cmd.add(String.valueOf(PORT));
                cmd.add("-c");
                cmd.add("1024");
                cmd.add("-t");
                cmd.add("4");
                cmd.add("--no-warmup");

                ProcessBuilder pb = new ProcessBuilder(cmd);
                Map<String, String> env = pb.environment();
                env.put("LD_LIBRARY_PATH", nativeDir + ":/data/local/tmp/llama/llama-b11512:" + env.getOrDefault("LD_LIBRARY_PATH", ""));

                Log.i(TAG, "Starting native llama-server: " + cmd);
                serverProcess = pb.start();

                // Wait up to 20 seconds for server to become ready
                for (int i = 0; i < 40; i++) {
                    Thread.sleep(500);
                    if (isServerReady()) {
                        Log.i(TAG, "Native llama-server is now READY on 127.0.0.1:" + PORT);
                        break;
                    }
                }
            } catch (Exception e) {
                Log.e(TAG, "Failed to start llama-server process: " + e.getMessage(), e);
            } finally {
                isStarting.set(false);
            }
        }).start();
    }

    /**
     * Sends prompt directly to real offline Qwen LLM and returns generated tokens.
     */
    public String queryQwen(String userPrompt, int maxTokens) {
        return queryQwenWithParams(null, userPrompt, maxTokens, 0.7);
    }

    /**
     * Sends prompt directly to real offline Qwen LLM with custom system prompt and temperature.
     */
    public String queryQwenWithParams(String systemPrompt, String userPrompt, int maxTokens, double temperature) {
        if (!isServerReady()) {
            startServerIfNeeded();
            // Wait up to 20 seconds if starting
            for (int i = 0; i < 40; i++) {
                try {
                    Thread.sleep(500);
                } catch (InterruptedException ignored) {}
                if (isServerReady()) break;
            }
        }

        if (!isServerReady()) {
            Log.w(TAG, "llama-server not available on localhost");
            return null;
        }

        try {
            // ChatML template format for Qwen with thinking tags instruction
            String sys = (systemPrompt != null && !systemPrompt.trim().isEmpty())
                    ? systemPrompt.trim()
                    : "You are Qwen, a helpful offline AI assistant. First, enclose your brief thoughts/reasoning inside <think>...</think>. Then answer thoroughly and completely in natural Hinglish or English without cutting off.";

            String chatMlPrompt = "<|im_start|>system\n" +
                    sys + "<|im_end|>\n" +
                    "<|im_start|>user\n" +
                    userPrompt + "<|im_end|>\n" +
                    "<|im_start|>assistant\n";

            JSONObject json = new JSONObject();
            json.put("prompt", chatMlPrompt);
            json.put("n_predict", maxTokens > 0 ? maxTokens : 2048);
            json.put("temperature", temperature > 0 ? temperature : 0.7);
            json.put("stream", false);

            JSONArray stop = new JSONArray();
            stop.put("<|im_end|>");
            stop.put("<|im_start|>");
            stop.put("User:");
            json.put("stop", stop);

            RequestBody body = RequestBody.create(json.toString(), MediaType.get("application/json; charset=utf-8"));
            Request req = new Request.Builder()
                    .url(SERVER_URL)
                    .post(body)
                    .build();

            try (Response resp = httpClient.newCall(req).execute()) {
                if (resp.isSuccessful() && resp.body() != null) {
                    String respStr = resp.body().string();
                    JSONObject respJson = new JSONObject(respStr);
                    String content = respJson.optString("content", "");
                    if (!content.trim().isEmpty()) {
                        return content.trim();
                    }
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Error executing Qwen inference via llama-server: " + e.getMessage(), e);
        }

        return null;
    }

    /**
     * Executes raw generation with custom prompt, temperature, and tokens.
     */
    public String queryRaw(String rawPrompt, int maxTokens, double temperature) {
        if (!isServerReady()) {
            startServerIfNeeded();
            for (int i = 0; i < 40; i++) {
                try {
                    Thread.sleep(500);
                } catch (InterruptedException ignored) {}
                if (isServerReady()) break;
            }
        }

        if (!isServerReady()) {
            Log.w(TAG, "llama-server not available on localhost");
            return null;
        }

        try {
            JSONObject json = new JSONObject();
            json.put("prompt", rawPrompt);
            json.put("n_predict", maxTokens > 0 ? maxTokens : 2048);
            json.put("temperature", temperature > 0 ? temperature : 0.7);
            json.put("stream", false);

            RequestBody body = RequestBody.create(json.toString(), MediaType.get("application/json; charset=utf-8"));
            Request req = new Request.Builder()
                    .url(SERVER_URL)
                    .post(body)
                    .build();

            try (Response resp = httpClient.newCall(req).execute()) {
                if (resp.isSuccessful() && resp.body() != null) {
                    String respStr = resp.body().string();
                    JSONObject respJson = new JSONObject(respStr);
                    return respJson.optString("content", "").trim();
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Error executing raw Qwen inference: " + e.getMessage(), e);
        }

        return null;
    }

    public static class LlamaResult {
        public final String thought;
        public final String answer;

        public LlamaResult(String thought, String answer) {
            this.thought = thought;
            this.answer = answer;
        }
    }

    /**
     * Executes Qwen inference and separates the internal thought chain from the final output.
     */
    public LlamaResult queryQwenWithThought(String userPrompt, int maxTokens) {
        return queryQwenWithThought(null, userPrompt, maxTokens, 0.7);
    }

    /**
     * Executes Qwen inference with custom system prompt and temperature, separating thought chain.
     */
    public LlamaResult queryQwenWithThought(String systemPrompt, String userPrompt, int maxTokens, double temperature) {
        String raw = queryQwenWithParams(systemPrompt, userPrompt, maxTokens, temperature);
        if (raw == null || raw.trim().isEmpty()) {
            return null;
        }

        String thought = null;
        String answer = raw.trim();

        if (raw.contains("<think>")) {
            int startIdx = raw.indexOf("<think>") + 7;
            int endIdx = raw.indexOf("</think>", startIdx);
            if (endIdx != -1) {
                thought = raw.substring(startIdx, endIdx).trim();
                answer = raw.substring(endIdx + 8).trim();
            } else {
                thought = raw.substring(startIdx).trim();
                answer = "";
            }
        } else if (raw.toLowerCase().startsWith("think:") || raw.toLowerCase().startsWith("thinking:")) {
            int colonIdx = raw.indexOf(":");
            int doubleNewline = raw.indexOf("\n\n", colonIdx);
            if (doubleNewline != -1) {
                thought = raw.substring(colonIdx + 1, doubleNewline).trim();
                answer = raw.substring(doubleNewline + 2).trim();
            }
        }

        if (thought == null || thought.isEmpty()) {
            thought = "• Query analyzed: \"" + (userPrompt.length() > 50 ? userPrompt.substring(0, 47) + "..." : userPrompt) + "\"\n"
                    + "• Model: " + modelManager.getActiveModel().displayName + " (100% Offline GGUF)\n"
                    + "• Engine: Native llama.cpp on device CPU\n"
                    + "• Output: Generative token synthesis";
        }

        if (answer.isEmpty()) {
            answer = raw.trim();
        }

        return new LlamaResult(thought, answer);
    }
}
