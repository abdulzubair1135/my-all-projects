package com.example.meshlink.ai.server

import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.os.Handler
import android.os.Looper
import java.util.concurrent.CopyOnWriteArrayList

object PocketAiServerController {

    private const val PREFS_NAME = "pocketai_server_prefs"
    private const val KEY_PORT = "pocketai_port"
    private const val KEY_AUTH_TOKEN = "pocketai_auth_token"
    private const val KEY_AUTO_START = "pocketai_auto_start"

    const val DEFAULT_PORT = 8800

    enum class ServerState {
        STOPPED,
        STARTING,
        RUNNING,
        ERROR
    }

    enum class InferenceStatus {
        IDLE,
        QUEUED,
        GENERATING
    }

    data class ClientInfo(
        val ipAddress: String,
        val lastSeenTime: Long,
        val userAgent: String = "Unknown",
        var requestCount: Int = 1
    )

    data class RequestLogEntry(
        val id: Long,
        val timestamp: Long,
        val clientIp: String,
        val endpoint: String,
        val promptSnippet: String,
        val statusCode: Int,
        val durationMs: Long,
        val isError: Boolean = false,
        val errorDetails: String? = null
    )

    data class ErrorLogEntry(
        val id: Long,
        val timestamp: Long,
        val message: String,
        val stackTrace: String? = null
    )

    interface StateListener {
        fun onServerStateChanged(state: ServerState, ip: String, port: Int)
        fun onInferenceStatusChanged(status: InferenceStatus, currentPrompt: String?, queueSize: Int)
        fun onRequestLogAdded(entry: RequestLogEntry)
        fun onErrorLogAdded(entry: ErrorLogEntry)
        fun onClientConnected(client: ClientInfo)
    }

    private val mainHandler = Handler(Looper.getMainLooper())
    private val listeners = CopyOnWriteArrayList<StateListener>()

    @Volatile
    var currentState: ServerState = ServerState.STOPPED
        private set

    @Volatile
    var currentInferenceStatus: InferenceStatus = InferenceStatus.IDLE
        private set

    @Volatile
    var currentPrompt: String? = null
        private set

    @Volatile
    var currentQueueSize: Int = 0
        private set

    @Volatile
    var activeIp: String = "127.0.0.1"
        private set

    @Volatile
    var activePort: Int = DEFAULT_PORT
        private set

    @Volatile
    var totalRequestsProcessed: Int = 0
        private set

    @Volatile
    var totalInferenceDurationMs: Long = 0L
        private set

    val requestLogs = ArrayList<RequestLogEntry>()
    val errorLogs = ArrayList<ErrorLogEntry>()
    val connectedClients = HashMap<String, ClientInfo>()

    private var nextLogId: Long = 1
    private var nextErrorId: Long = 1

    fun getPort(context: Context): Int {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getInt(KEY_PORT, DEFAULT_PORT)
    }

    fun setPort(context: Context, port: Int) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putInt(KEY_PORT, port).apply()
        activePort = port
    }

    fun getAuthToken(context: Context): String {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getString(KEY_AUTH_TOKEN, "") ?: ""
    }

    fun setAuthToken(context: Context, token: String) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putString(KEY_AUTH_TOKEN, token.trim()).apply()
    }

    fun addListener(listener: StateListener) {
        if (!listeners.contains(listener)) {
            listeners.add(listener)
            // Emit current state immediately
            listener.onServerStateChanged(currentState, activeIp, activePort)
            listener.onInferenceStatusChanged(currentInferenceStatus, currentPrompt, currentQueueSize)
        }
    }

    fun removeListener(listener: StateListener) {
        listeners.remove(listener)
    }

    fun notifyServerState(state: ServerState, ip: String, port: Int) {
        currentState = state
        activeIp = ip
        activePort = port
        mainHandler.post {
            for (l in listeners) {
                l.onServerStateChanged(state, ip, port)
            }
        }
    }

    fun notifyInferenceStatus(status: InferenceStatus, prompt: String?, queueSize: Int) {
        currentInferenceStatus = status
        currentPrompt = prompt
        currentQueueSize = queueSize
        mainHandler.post {
            for (l in listeners) {
                l.onInferenceStatusChanged(status, prompt, queueSize)
            }
        }
    }

    @Synchronized
    fun logRequest(clientIp: String, endpoint: String, promptSnippet: String, statusCode: Int, durationMs: Long, isError: Boolean = false, error: String? = null) {
        val entry = RequestLogEntry(
            id = nextLogId++,
            timestamp = System.currentTimeMillis(),
            clientIp = clientIp,
            endpoint = endpoint,
            promptSnippet = promptSnippet,
            statusCode = statusCode,
            durationMs = durationMs,
            isError = isError,
            errorDetails = error
        )
        totalRequestsProcessed++
        totalInferenceDurationMs += durationMs

        synchronized(requestLogs) {
            if (requestLogs.size >= 150) {
                requestLogs.removeAt(0)
            }
            requestLogs.add(entry)
        }

        // Register client info
        synchronized(connectedClients) {
            val existing = connectedClients[clientIp]
            if (existing != null) {
                existing.requestCount++
            } else {
                val client = ClientInfo(clientIp, System.currentTimeMillis())
                connectedClients[clientIp] = client
                mainHandler.post {
                    for (l in listeners) l.onClientConnected(client)
                }
            }
        }

        mainHandler.post {
            for (l in listeners) {
                l.onRequestLogAdded(entry)
            }
        }
    }

    @Synchronized
    fun logError(message: String, stackTrace: String? = null) {
        val entry = ErrorLogEntry(
            id = nextErrorId++,
            timestamp = System.currentTimeMillis(),
            message = message,
            stackTrace = stackTrace
        )
        synchronized(errorLogs) {
            if (errorLogs.size >= 100) {
                errorLogs.removeAt(0)
            }
            errorLogs.add(entry)
        }
        mainHandler.post {
            for (l in listeners) {
                l.onErrorLogAdded(entry)
            }
        }
    }

    fun clearLogs() {
        synchronized(requestLogs) { requestLogs.clear() }
        synchronized(errorLogs) { errorLogs.clear() }
    }

    fun startServer(context: Context) {
        val intent = Intent(context, PocketAiServerService::class.java).apply {
            action = PocketAiServerService.ACTION_START
        }
        context.startForegroundService(intent)
    }

    fun stopServer(context: Context) {
        val intent = Intent(context, PocketAiServerService::class.java).apply {
            action = PocketAiServerService.ACTION_STOP
        }
        context.startService(intent)
    }
}
