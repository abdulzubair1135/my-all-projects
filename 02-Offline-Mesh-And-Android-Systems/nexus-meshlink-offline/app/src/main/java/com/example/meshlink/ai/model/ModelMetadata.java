package com.example.meshlink.ai.model;

public class ModelMetadata {
    public final String id;
    public final String displayName;
    public final String tagLine;
    public final String fileName;
    public final long sizeBytes;
    public final int sizeMb;
    public final int minRamGb;
    public final String downloadUrl;
    public final DeviceCapabilityDetector.DeviceTier tier;

    public ModelMetadata(String id, String displayName, String tagLine, String fileName,
                         int sizeMb, int minRamGb, String downloadUrl, DeviceCapabilityDetector.DeviceTier tier) {
        this.id = id;
        this.displayName = displayName;
        this.tagLine = tagLine;
        this.fileName = fileName;
        this.sizeMb = sizeMb;
        this.sizeBytes = (long) sizeMb * 1024 * 1024;
        this.minRamGb = minRamGb;
        this.downloadUrl = downloadUrl;
        this.tier = tier;
    }

    public static final ModelMetadata QWEN3_0_6B = new ModelMetadata(
            "qwen3_0_6b",
            "Qwen3 0.6B Q4",
            "Fastest • Battery Saver • Works on 2GB+ RAM",
            "qwen3-0_6b-instruct-q4_k_m.gguf",
            395,
            2,
            "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf",
            DeviceCapabilityDetector.DeviceTier.LOW
    );

    public static final ModelMetadata QWEN3_1_7B = new ModelMetadata(
            "qwen3_1_7b",
            "Qwen3 1.7B Q4_K_M",
            "Recommended • Balanced • Deep Reasoning",
            "qwen3-1_7b-instruct-q4_k_m.gguf",
            1050,
            4,
            "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
            DeviceCapabilityDetector.DeviceTier.NORMAL
    );

    public static final ModelMetadata QWEN3_4B = new ModelMetadata(
            "qwen3_4b",
            "Qwen3 4B Q4",
            "Pro • Heavy Reasoning • For Flagship 8GB+ RAM",
            "qwen3-4b-instruct-q4_k_m.gguf",
            2450,
            8,
            "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf",
            DeviceCapabilityDetector.DeviceTier.HIGH
    );

    public static ModelMetadata[] ALL_MODELS = new ModelMetadata[]{
            QWEN3_0_6B,
            QWEN3_1_7B,
            QWEN3_4B
    };

    public static ModelMetadata getById(String id) {
        for (ModelMetadata m : ALL_MODELS) {
            if (m.id.equalsIgnoreCase(id)) return m;
        }
        return QWEN3_0_6B;
    }
}
