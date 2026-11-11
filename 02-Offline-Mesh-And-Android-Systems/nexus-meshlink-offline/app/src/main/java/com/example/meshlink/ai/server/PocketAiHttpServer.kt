package com.example.meshlink.ai.server

import android.app.ActivityManager
import android.content.Context
import android.os.Build
import android.util.Log
import com.example.meshlink.ai.model.DeviceCapabilityDetector
import com.example.meshlink.ai.model.ModelManager
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStream
import java.net.InetAddress
import java.net.ServerSocket
import java.net.Socket
import java.net.SocketTimeoutException
import java.nio.charset.StandardCharsets
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class PocketAiHttpServer(
    private val context: Context,
    private val port: Int
) {

    companion object {
        private const val TAG = "PocketAiHttpServer"
        private const val MAX_BODY_BYTES = 2 * 1024 * 1024 // 2MB
        private const val SERVER_VERSION = "1.0.0"
    }

    private var serverSocket: ServerSocket? = null
    @Volatile
    private var isRunning = false
    private val startTimeMs = System.currentTimeMillis()
    private val workerExecutor: ExecutorService = Executors.newCachedThreadPool()
    private val inferenceEngine = PocketAiInferenceEngine.getInstance(context)
    private val modelManager = ModelManager.getInstance(context)

    @Synchronized
    fun start() {
        if (isRunning) return
        isRunning = true

        workerExecutor.execute {
            try {
                // Bind to 0.0.0.0 to accept connections on Hotspot, Wi-Fi, and USB tethering
                serverSocket = ServerSocket(port, 50, InetAddress.getByName("0.0.0.0"))
                val primaryIp = NetworkUtils.getPrimaryIpAddress(context)
                Log.i(TAG, "PocketAI HTTP Server started successfully on $primaryIp:$port (0.0.0.0:$port)")

                PocketAiServerController.notifyServerState(
                    PocketAiServerController.ServerState.RUNNING,
                    primaryIp,
                    port
                )

                while (isRunning && serverSocket?.isClosed == false) {
                    try {
                        val clientSocket = serverSocket?.accept() ?: break
                        clientSocket.soTimeout = 300_000 // 5 minutes timeout for long generations
                        workerExecutor.execute {
                            handleClient(clientSocket)
                        }
                    } catch (e: Exception) {
                        if (!isRunning) break
                        Log.e(TAG, "Socket accept error: ${e.message}")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Failed to start PocketAI server on port $port: ${e.message}", e)
                val primaryIp = NetworkUtils.getPrimaryIpAddress(context)
                PocketAiServerController.notifyServerState(
                    PocketAiServerController.ServerState.ERROR,
                    primaryIp,
                    port
                )
                PocketAiServerController.logError("Server bind error: ${e.message}")
            } finally {
                stop()
            }
        }
    }

    @Synchronized
    fun stop() {
        if (!isRunning && serverSocket?.isClosed != false) return
        isRunning = false
        try {
            serverSocket?.close()
        } catch (ignored: Exception) {}
        serverSocket = null

        val primaryIp = NetworkUtils.getPrimaryIpAddress(context)
        PocketAiServerController.notifyServerState(
            PocketAiServerController.ServerState.STOPPED,
            primaryIp,
            port
        )
        Log.i(TAG, "PocketAI HTTP Server stopped.")
    }

    private fun handleClient(socket: Socket) {
        val clientIp = socket.inetAddress?.hostAddress ?: "Unknown"
        val requestStartTime = System.currentTimeMillis()
        var endpoint = "/"
        var method = "GET"

        try {
            val reader = BufferedReader(InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8))
            val out = socket.getOutputStream()

            val requestLine = reader.readLine()
            if (requestLine.isNullOrBlank()) {
                socket.close()
                return
            }

            val parts = requestLine.split(" ")
            if (parts.size < 2) {
                sendErrorResponse(out, 400, "Bad Request: Malformed HTTP request line")
                socket.close()
                return
            }

            method = parts[0].uppercase()
            val fullPath = parts[1]
            endpoint = if (fullPath.contains("?")) fullPath.substring(0, fullPath.indexOf("?")) else fullPath

            // Parse headers
            val headers = HashMap<String, String>()
            var contentLength = 0
            var headerLine: String?
            while (reader.readLine().also { headerLine = it } != null) {
                if (headerLine.isNullOrBlank()) break
                val colonIdx = headerLine!!.indexOf(":")
                if (colonIdx != -1) {
                    val key = headerLine!!.substring(0, colonIdx).trim().lowercase()
                    val value = headerLine!!.substring(colonIdx + 1).trim()
                    headers[key] = value
                    if (key == "content-length") {
                        contentLength = value.toIntOrNull() ?: 0
                    }
                }
            }

            // Handle CORS preflight OPTIONS
            if (method == "OPTIONS") {
                sendCorsPreflightResponse(out)
                socket.close()
                return
            }

            // Check authentication token if configured
            val configuredToken = PocketAiServerController.getAuthToken(context)
            if (configuredToken.isNotBlank()) {
                val authHeader = headers["authorization"] ?: ""
                val customTokenHeader = headers["x-pocketai-token"] ?: ""
                val providedToken = if (authHeader.startsWith("Bearer ", ignoreCase = true)) {
                    authHeader.substring(7).trim()
                } else if (customTokenHeader.isNotBlank()) {
                    customTokenHeader.trim()
                } else {
                    ""
                }

                if (providedToken != configuredToken) {
                    val duration = System.currentTimeMillis() - requestStartTime
                    sendErrorResponse(out, 401, "Unauthorized: Invalid or missing PocketAI authentication token")
                    PocketAiServerController.logRequest(
                        clientIp = clientIp,
                        endpoint = endpoint,
                        promptSnippet = "[Auth Failed]",
                        statusCode = 401,
                        durationMs = duration,
                        isError = true,
                        error = "Token mismatch"
                    )
                    socket.close()
                    return
                }
            }

            // Read request body if present
            var body = ""
            if (contentLength > 0) {
                if (contentLength > MAX_BODY_BYTES) {
                    sendErrorResponse(out, 413, "Payload Too Large: Maximum allowed size is 2MB")
                    socket.close()
                    return
                }

                val bodyChars = CharArray(contentLength)
                var totalRead = 0
                while (totalRead < contentLength) {
                    val read = reader.read(bodyChars, totalRead, contentLength - totalRead)
                    if (read == -1) break
                    totalRead += read
                }
                body = String(bodyChars, 0, totalRead)
            }

            // Route endpoints
            when {
                // 1. GET /health
                endpoint == "/health" && method == "GET" -> {
                    handleHealth(out, clientIp, requestStartTime)
                }

                // 2. GET /info
                endpoint == "/info" && method == "GET" -> {
                    handleInfo(out, clientIp, requestStartTime)
                }

                // 3. POST /api/chat
                endpoint == "/api/chat" && method == "POST" -> {
                    handleChat(out, body, clientIp, requestStartTime)
                }

                // 4. POST /api/generate
                endpoint == "/api/generate" && method == "POST" -> {
                    handleGenerate(out, body, clientIp, requestStartTime)
                }

                // 5. GET /api/status
                endpoint == "/api/status" && method == "GET" -> {
                    handleStatus(out, clientIp, requestStartTime)
                }

                // 6. POST /api/stop
                endpoint == "/api/stop" && method == "POST" -> {
                    handleStop(out, clientIp, requestStartTime)
                }

                else -> {
                    val duration = System.currentTimeMillis() - requestStartTime
                    sendErrorResponse(out, 404, "Endpoint not found: $method $endpoint")
                    PocketAiServerController.logRequest(
                        clientIp = clientIp,
                        endpoint = endpoint,
                        promptSnippet = "[404 Not Found]",
                        statusCode = 404,
                        durationMs = duration,
                        isError = true,
                        error = "Route not found"
                    )
                }
            }

        } catch (e: SocketTimeoutException) {
            val duration = System.currentTimeMillis() - requestStartTime
            PocketAiServerController.logError("Client timeout from $clientIp on $endpoint: ${e.message}")
            PocketAiServerController.logRequest(clientIp, endpoint, "[Timeout]", 504, duration, true, e.message)
        } catch (e: Exception) {
            val duration = System.currentTimeMillis() - requestStartTime
            PocketAiServerController.logError("Client handling exception ($clientIp): ${e.message}", Log.getStackTraceString(e))
            PocketAiServerController.logRequest(clientIp, endpoint, "[Server Error]", 500, duration, true, e.message)
        } finally {
            try {
                socket.close()
            } catch (ignored: Exception) {}
        }
    }

    private fun handleHealth(out: OutputStream, clientIp: String, startTime: Long) {
        val modelReady = inferenceEngine.isModelReady()
        val activeModel = modelManager.activeModel
        val json = JSONObject().apply {
            put("status", "ok")
            put("server", "PocketAI Server")
            put("version", SERVER_VERSION)
            put("model_loaded", modelReady)
            put("model_name", activeModel?.displayName ?: "Qwen3")
            put("model_id", activeModel?.id ?: "unknown")
            put("runtime_status", if (modelReady) "ready" else "initializing")
            put("device_model", Build.MODEL)
        }

        val duration = System.currentTimeMillis() - startTime
        sendJsonResponse(out, 200, json.toString())
        PocketAiServerController.logRequest(clientIp, "/health", "Health check", 200, duration)
    }

    private fun handleInfo(out: OutputStream, clientIp: String, startTime: Long) {
        val activeModel = modelManager.activeModel
        val actManager = context.getSystemService(Context.ACTIVITY_SERVICE) as? ActivityManager
        val memInfo = ActivityManager.MemoryInfo()
        actManager?.getMemoryInfo(memInfo)

        val deviceJson = JSONObject().apply {
            put("model", Build.MODEL)
            put("manufacturer", Build.MANUFACTURER)
            put("android_version", Build.VERSION.RELEASE)
            put("api_level", Build.VERSION.SDK_INT)
            put("ram_total_mb", memInfo.totalMem / (1024 * 1024))
            put("ram_avail_mb", memInfo.availMem / (1024 * 1024))
        }

        val modelJson = JSONObject().apply {
            put("id", activeModel?.id ?: "")
            put("name", activeModel?.displayName ?: "Qwen3")
            put("file", activeModel?.fileName ?: "")
            put("size_mb", activeModel?.sizeMb ?: 0)
            put("backend", "llama.cpp")
            put("is_loaded", inferenceEngine.isModelReady())
        }

        val uptimeSec = (System.currentTimeMillis() - startTimeMs) / 1000
        val root = JSONObject().apply {
            put("device", deviceJson)
            put("model", modelJson)
            put("api_version", SERVER_VERSION)
            put("port", port)
            put("uptime_seconds", uptimeSec)
            put("auth_required", PocketAiServerController.getAuthToken(context).isNotBlank())
        }

        val duration = System.currentTimeMillis() - startTime
        sendJsonResponse(out, 200, root.toString())
        PocketAiServerController.logRequest(clientIp, "/info", "Info query", 200, duration)
    }

    private fun handleChat(out: OutputStream, body: String, clientIp: String, startTime: Long) {
        if (body.isBlank()) {
            val duration = System.currentTimeMillis() - startTime
            sendErrorResponse(out, 400, "Bad Request: Empty request body")
            PocketAiServerController.logRequest(clientIp, "/api/chat", "[Empty body]", 400, duration, true)
            return
        }

        val json: JSONObject
        try {
            json = JSONObject(body)
        } catch (e: Exception) {
            val duration = System.currentTimeMillis() - startTime
            sendErrorResponse(out, 400, "Bad Request: Invalid JSON payload: ${e.message}")
            PocketAiServerController.logRequest(clientIp, "/api/chat", "[Invalid JSON]", 400, duration, true)
            return
        }

        val question = json.optString("question", "").trim()
        if (question.isBlank()) {
            val duration = System.currentTimeMillis() - startTime
            sendErrorResponse(out, 400, "Bad Request: 'question' field is required")
            PocketAiServerController.logRequest(clientIp, "/api/chat", "[Missing question]", 400, duration, true)
            return
        }

        val temperature = json.optDouble("temperature", 0.6)
        val maxTokens = json.optInt("max_tokens", 2048)
        val systemPrompt = json.optString("system_prompt", "")

        val snippet = if (question.length > 50) question.substring(0, 47) + "..." else question

        // Submit to sequential inference engine
        val result = inferenceEngine.processQuestion(
            question = question,
            systemPrompt = if (systemPrompt.isNotBlank()) systemPrompt else null,
            maxTokens = maxTokens,
            temperature = temperature
        )

        val totalDuration = System.currentTimeMillis() - startTime

        if (result.success) {
            val respJson = JSONObject().apply {
                put("success", true)
                put("question", result.question)
                put("answer", result.answer)
                if (result.thought != null) {
                    put("thought", result.thought)
                }
                put("processing_time", Math.round(result.durationMs / 100.0) / 10.0) // e.g. 12.5 seconds
            }

            sendJsonResponse(out, 200, respJson.toString())
            PocketAiServerController.logRequest(
                clientIp = clientIp,
                endpoint = "/api/chat",
                promptSnippet = snippet,
                statusCode = 200,
                durationMs = totalDuration
            )
        } else {
            val respJson = JSONObject().apply {
                put("success", false)
                put("question", question)
                put("error", result.errorMessage ?: "Inference error")
                put("processing_time", Math.round(result.durationMs / 100.0) / 10.0)
            }

            sendJsonResponse(out, 500, respJson.toString())
            PocketAiServerController.logRequest(
                clientIp = clientIp,
                endpoint = "/api/chat",
                promptSnippet = snippet,
                statusCode = 500,
                durationMs = totalDuration,
                isError = true,
                error = result.errorMessage
            )
        }
    }

    private fun handleGenerate(out: OutputStream, body: String, clientIp: String, startTime: Long) {
        if (body.isBlank()) {
            sendErrorResponse(out, 400, "Bad Request: Empty request body")
            return
        }

        val json = try {
            JSONObject(body)
        } catch (e: Exception) {
            sendErrorResponse(out, 400, "Bad Request: Invalid JSON")
            return
        }

        val prompt = json.optString("prompt", "").trim()
        if (prompt.isBlank()) {
            sendErrorResponse(out, 400, "Bad Request: 'prompt' field is required")
            return
        }

        val temperature = json.optDouble("temperature", 0.7)
        val maxTokens = json.optInt("max_tokens", 2048)
        val snippet = if (prompt.length > 50) prompt.substring(0, 47) + "..." else prompt

        val result = inferenceEngine.processRaw(prompt, maxTokens, temperature)
        val totalDuration = System.currentTimeMillis() - startTime

        if (result.success) {
            val respJson = JSONObject().apply {
                put("success", true)
                put("prompt", result.question)
                put("response", result.answer)
                put("processing_time", Math.round(result.durationMs / 100.0) / 10.0)
            }
            sendJsonResponse(out, 200, respJson.toString())
            PocketAiServerController.logRequest(clientIp, "/api/generate", snippet, 200, totalDuration)
        } else {
            val respJson = JSONObject().apply {
                put("success", false)
                put("error", result.errorMessage ?: "Generation error")
                put("processing_time", Math.round(result.durationMs / 100.0) / 10.0)
            }
            sendJsonResponse(out, 500, respJson.toString())
            PocketAiServerController.logRequest(clientIp, "/api/generate", snippet, 500, totalDuration, true, result.errorMessage)
        }
    }

    private fun handleStatus(out: OutputStream, clientIp: String, startTime: Long) {
        val actManager = context.getSystemService(Context.ACTIVITY_SERVICE) as? ActivityManager
        val memInfo = ActivityManager.MemoryInfo()
        actManager?.getMemoryInfo(memInfo)

        val statusStr = when (PocketAiServerController.currentInferenceStatus) {
            PocketAiServerController.InferenceStatus.IDLE -> "idle"
            PocketAiServerController.InferenceStatus.QUEUED -> "queued"
            PocketAiServerController.InferenceStatus.GENERATING -> "generating"
        }

        val json = JSONObject().apply {
            put("status", statusStr)
            put("current_question", PocketAiServerController.currentPrompt ?: "")
            put("queue_length", PocketAiServerController.currentQueueSize)
            put("total_requests_processed", PocketAiServerController.totalRequestsProcessed)
            put("ram_free_mb", memInfo.availMem / (1024 * 1024))
            put("model_ready", inferenceEngine.isModelReady())
            put("active_model", inferenceEngine.getModelName())
        }

        val duration = System.currentTimeMillis() - startTime
        sendJsonResponse(out, 200, json.toString())
        PocketAiServerController.logRequest(clientIp, "/api/status", "Status check", 200, duration)
    }

    private fun handleStop(out: OutputStream, clientIp: String, startTime: Long) {
        val json = JSONObject().apply {
            put("success", true)
            put("message", "PocketAI Server is shutting down")
        }
        sendJsonResponse(out, 200, json.toString())
        val duration = System.currentTimeMillis() - startTime
        PocketAiServerController.logRequest(clientIp, "/api/stop", "Server shutdown command", 200, duration)

        // Asynchronously stop the service
        workerExecutor.execute {
            Thread.sleep(500)
            PocketAiServerController.stopServer(context)
        }
    }

    private fun sendJsonResponse(out: OutputStream, statusCode: Int, json: String) {
        val statusText = when (statusCode) {
            200 -> "OK"
            400 -> "Bad Request"
            401 -> "Unauthorized"
            404 -> "Not Found"
            405 -> "Method Not Allowed"
            413 -> "Payload Too Large"
            500 -> "Internal Server Error"
            503 -> "Service Unavailable"
            504 -> "Gateway Timeout"
            else -> "OK"
        }

        val bytes = json.toByteArray(StandardCharsets.UTF_8)
        val header = "HTTP/1.1 $statusCode $statusText\r\n" +
                "Content-Type: application/json; charset=utf-8\r\n" +
                "Content-Length: ${bytes.size}\r\n" +
                "Connection: close\r\n" +
                "Access-Control-Allow-Origin: *\r\n" +
                "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n" +
                "Access-Control-Allow-Headers: Content-Type, Authorization, X-PocketAI-Token\r\n\r\n"

        out.write(header.toByteArray(StandardCharsets.UTF_8))
        out.write(bytes)
        out.flush()
    }

    private fun sendErrorResponse(out: OutputStream, statusCode: Int, message: String) {
        val json = JSONObject().apply {
            put("success", false)
            put("error", message)
            put("status_code", statusCode)
        }
        sendJsonResponse(out, statusCode, json.toString())
    }

    private fun sendCorsPreflightResponse(out: OutputStream) {
        val header = "HTTP/1.1 204 No Content\r\n" +
                "Access-Control-Allow-Origin: *\r\n" +
                "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n" +
                "Access-Control-Allow-Headers: Content-Type, Authorization, X-PocketAI-Token\r\n" +
                "Access-Control-Max-Age: 86400\r\n" +
                "Connection: close\r\n\r\n"

        out.write(header.toByteArray(StandardCharsets.UTF_8))
        out.flush()
    }
}
