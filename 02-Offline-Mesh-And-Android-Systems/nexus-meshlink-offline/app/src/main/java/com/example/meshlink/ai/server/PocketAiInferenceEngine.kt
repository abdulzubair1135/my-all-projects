package com.example.meshlink.ai.server

import android.content.Context
import android.os.PowerManager
import android.util.Log
import com.example.meshlink.ai.model.LlamaServerManager
import com.example.meshlink.ai.model.ModelManager
import java.util.concurrent.Callable
import java.util.concurrent.Executors
import java.util.concurrent.Future
import java.util.concurrent.atomic.AtomicInteger

class PocketAiInferenceEngine(private val context: Context) {

    private val executor = Executors.newSingleThreadExecutor()
    private val queuedTasksCount = AtomicInteger(0)
    private val powerManager = context.getSystemService(Context.POWER_SERVICE) as? PowerManager
    private var wakeLock: PowerManager.WakeLock? = null
    private val llamaServer = LlamaServerManager.getInstance(context)
    private val modelManager = ModelManager.getInstance(context)

    companion object {
        private const val TAG = "PocketAiInference"
        @Volatile
        private var instance: PocketAiInferenceEngine? = null

        fun getInstance(context: Context): PocketAiInferenceEngine {
            return instance ?: synchronized(this) {
                instance ?: PocketAiInferenceEngine(context.applicationContext).also { instance = it }
            }
        }
    }

    init {
        try {
            wakeLock = powerManager?.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "PocketAi::InferenceWakeLock"
            )?.apply {
                setReferenceCounted(false)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error acquiring WakeLock handle: ${e.message}")
        }
    }

    data class GenerationResult(
        val success: Boolean,
        val question: String,
        val answer: String,
        val thought: String?,
        val durationMs: Long,
        val errorMessage: String? = null
    )

    fun isModelReady(): Boolean {
        return llamaServer.isServerReady
    }

    fun getModelName(): String {
        return modelManager.activeModel?.displayName ?: "Qwen3"
    }

    /**
     * Submits a question into the sequential FIFO inference queue.
     * Blocks calling thread until inference finishes (safe inside worker thread of HTTP server).
     */
    fun processQuestion(
        question: String,
        systemPrompt: String?,
        maxTokens: Int,
        temperature: Double
    ): GenerationResult {
        val qSize = queuedTasksCount.incrementAndGet()
        PocketAiServerController.notifyInferenceStatus(
            PocketAiServerController.InferenceStatus.QUEUED,
            question,
            qSize
        )

        val task: Future<GenerationResult> = executor.submit(Callable {
            val startTime = System.currentTimeMillis()
            var acquiredWakeLock = false

            try {
                // Acquire partial wake lock while computing tokens
                wakeLock?.let {
                    it.acquire(10 * 60 * 1000L) // 10 min max timeout
                    acquiredWakeLock = true
                }

                queuedTasksCount.decrementAndGet()
                PocketAiServerController.notifyInferenceStatus(
                    PocketAiServerController.InferenceStatus.GENERATING,
                    question,
                    queuedTasksCount.get()
                )

                // Ensure llama server is warm
                if (!llamaServer.isServerReady) {
                    llamaServer.startServerIfNeeded()
                    // Wait up to 30 seconds for native server warmup
                    for (i in 0 until 60) {
                        Thread.sleep(500)
                        if (llamaServer.isServerReady) break
                    }
                }

                if (!llamaServer.isServerReady) {
                    val duration = System.currentTimeMillis() - startTime
                    return@Callable GenerationResult(
                        success = false,
                        question = question,
                        answer = "",
                        thought = null,
                        durationMs = duration,
                        errorMessage = "Local llama.cpp inference engine failed to initialize on device."
                    )
                }

                val tokens = if (maxTokens in 1..8192) maxTokens else 2048
                val temp = if (temperature in 0.05..2.0) temperature else 0.7

                val llamaRes = llamaServer.queryQwenWithThought(systemPrompt, question, tokens, temp)
                val duration = System.currentTimeMillis() - startTime

                if (llamaRes != null && llamaRes.answer.isNotBlank()) {
                    GenerationResult(
                        success = true,
                        question = question,
                        answer = llamaRes.answer.trim(),
                        thought = llamaRes.thought,
                        durationMs = duration
                    )
                } else {
                    GenerationResult(
                        success = false,
                        question = question,
                        answer = "",
                        thought = null,
                        durationMs = duration,
                        errorMessage = "No tokens generated by Qwen3 model."
                    )
                }

            } catch (e: Exception) {
                val duration = System.currentTimeMillis() - startTime
                Log.e(TAG, "Inference error: ${e.message}", e)
                GenerationResult(
                    success = false,
                    question = question,
                    answer = "",
                    thought = null,
                    durationMs = duration,
                    errorMessage = e.message ?: "Unknown inference exception"
                )
            } finally {
                if (acquiredWakeLock) {
                    try {
                        if (wakeLock?.isHeld == true) {
                            wakeLock?.release()
                        }
                    } catch (ignored: Exception) {}
                }

                val remaining = queuedTasksCount.get()
                if (remaining == 0) {
                    PocketAiServerController.notifyInferenceStatus(
                        PocketAiServerController.InferenceStatus.IDLE,
                        null,
                        0
                    )
                }
            }
        })

        return try {
            task.get()
        } catch (e: Exception) {
            queuedTasksCount.decrementAndGet()
            GenerationResult(
                success = false,
                question = question,
                answer = "",
                thought = null,
                durationMs = 0L,
                errorMessage = "Task execution failed: ${e.message}"
            )
        }
    }

    /**
     * Executes raw generation with custom prompt.
     */
    fun processRaw(
        prompt: String,
        maxTokens: Int,
        temperature: Double
    ): GenerationResult {
        return processQuestion(
            question = prompt,
            systemPrompt = "",
            maxTokens = maxTokens,
            temperature = temperature
        )
    }
}
