package com.example.meshlink.ai.server

import android.app.ActivityManager
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.View
import android.widget.EditText
import android.widget.ImageView
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.meshlink.R
import com.example.meshlink.ai.model.ModelManager
import com.google.android.material.button.MaterialButton
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class PocketAiServerActivity : AppCompatActivity(), PocketAiServerController.StateListener {

    private lateinit var dotServerStatus: View
    private lateinit var tvServerStatusTitle: TextView
    private lateinit var tvServerBadge: TextView
    private lateinit var tvServerFullUrl: TextView
    private lateinit var btnCopyUrl: ImageView
    private lateinit var etServerPort: EditText
    private lateinit var etServerToken: EditText
    private lateinit var btnToggleServer: MaterialButton

    private lateinit var tvActiveModelTitle: TextView
    private lateinit var tvModelRuntimeBadge: TextView
    private lateinit var pbInferenceActive: ProgressBar
    private lateinit var tvInferenceStateText: TextView
    private lateinit var tvHardwareStats: TextView

    private lateinit var tvDetectedInterfaces: TextView
    private lateinit var tvConnectedClients: TextView

    private lateinit var rvServerLogs: RecyclerView
    private lateinit var tvEmptyLogs: TextView
    private lateinit var btnClearLogs: TextView
    private lateinit var btnQuickTest: TextView

    private lateinit var logAdapter: PocketAiLogAdapter
    private val modelManager by lazy { ModelManager.getInstance(this) }
    private val inferenceEngine by lazy { PocketAiInferenceEngine.getInstance(this) }

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(180, TimeUnit.SECONDS)
        .build()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_pocket_ai_server)

        initViews()
        setupLogsRecyclerView()
        refreshHardwareAndModelStats()
        updateServerUI(PocketAiServerController.currentState, PocketAiServerController.activeIp, PocketAiServerController.activePort)
        updateInferenceUI(PocketAiServerController.currentInferenceStatus, PocketAiServerController.currentPrompt, PocketAiServerController.currentQueueSize)

        PocketAiServerController.addListener(this)
    }

    override fun onDestroy() {
        PocketAiServerController.removeListener(this)
        super.onDestroy()
    }

    private fun initViews() {
        findViewById<View>(R.id.btnBackServer).setOnClickListener { finish() }

        dotServerStatus = findViewById(R.id.dotServerStatus)
        tvServerStatusTitle = findViewById(R.id.tvServerStatusTitle)
        tvServerBadge = findViewById(R.id.tvServerBadge)
        tvServerFullUrl = findViewById(R.id.tvServerFullUrl)
        btnCopyUrl = findViewById(R.id.btnCopyUrl)
        etServerPort = findViewById(R.id.etServerPort)
        etServerToken = findViewById(R.id.etServerToken)
        btnToggleServer = findViewById(R.id.btnToggleServer)

        tvActiveModelTitle = findViewById(R.id.tvActiveModelTitle)
        tvModelRuntimeBadge = findViewById(R.id.tvModelRuntimeBadge)
        pbInferenceActive = findViewById(R.id.pbInferenceActive)
        tvInferenceStateText = findViewById(R.id.tvInferenceStateText)
        tvHardwareStats = findViewById(R.id.tvHardwareStats)

        tvDetectedInterfaces = findViewById(R.id.tvDetectedInterfaces)
        tvConnectedClients = findViewById(R.id.tvConnectedClients)

        rvServerLogs = findViewById(R.id.rvServerLogs)
        tvEmptyLogs = findViewById(R.id.tvEmptyLogs)
        btnClearLogs = findViewById(R.id.btnClearLogs)
        btnQuickTest = findViewById(R.id.btnQuickTest)

        // Load saved port & token
        val savedPort = PocketAiServerController.getPort(this)
        etServerPort.setText(savedPort.toString())

        val savedToken = PocketAiServerController.getAuthToken(this)
        etServerToken.setText(savedToken)

        // Copy URL
        btnCopyUrl.setOnClickListener {
            val url = tvServerFullUrl.text.toString()
            copyToClipboard(url)
            Toast.makeText(this, "Copied server URL: $url", Toast.LENGTH_SHORT).show()
        }

        findViewById<View>(R.id.llServerUrlContainer).setOnClickListener {
            val url = tvServerFullUrl.text.toString()
            copyToClipboard(url)
            Toast.makeText(this, "Copied server URL: $url", Toast.LENGTH_SHORT).show()
        }

        // Toggle Server Button
        btnToggleServer.setOnClickListener {
            val portText = etServerPort.text.toString().trim()
            val port = portText.toIntOrNull() ?: PocketAiServerController.DEFAULT_PORT
            PocketAiServerController.setPort(this, port)

            val token = etServerToken.text.toString().trim()
            PocketAiServerController.setAuthToken(this, token)

            if (PocketAiServerController.currentState == PocketAiServerController.ServerState.RUNNING ||
                PocketAiServerController.currentState == PocketAiServerController.ServerState.STARTING) {
                PocketAiServerController.stopServer(this)
                Toast.makeText(this, "Stopping PocketAI server...", Toast.LENGTH_SHORT).show()
            } else {
                PocketAiServerController.startServer(this)
                Toast.makeText(this, "Starting PocketAI server on port $port...", Toast.LENGTH_SHORT).show()
            }
        }

        // Clear Logs Button
        btnClearLogs.setOnClickListener {
            PocketAiServerController.clearLogs()
            logAdapter.setLogs(emptyList())
            tvEmptyLogs.visibility = View.VISIBLE
            rvServerLogs.visibility = View.GONE
        }

        // Quick Test Button
        btnQuickTest.setOnClickListener {
            performQuickTest()
        }
    }

    private fun setupLogsRecyclerView() {
        val initialLogs = synchronized(PocketAiServerController.requestLogs) {
            ArrayList(PocketAiServerController.requestLogs)
        }
        logAdapter = PocketAiLogAdapter(initialLogs.reversed().toMutableList())
        rvServerLogs.layoutManager = LinearLayoutManager(this)
        rvServerLogs.adapter = logAdapter

        if (initialLogs.isEmpty()) {
            tvEmptyLogs.visibility = View.VISIBLE
            rvServerLogs.visibility = View.GONE
        } else {
            tvEmptyLogs.visibility = View.GONE
            rvServerLogs.visibility = View.VISIBLE
        }
    }

    private fun refreshHardwareAndModelStats() {
        val activeModel = modelManager.activeModel
        tvActiveModelTitle.text = activeModel?.displayName ?: "Qwen3"

        val isReady = inferenceEngine.isModelReady()
        if (isReady) {
            tvModelRuntimeBadge.text = "llama.cpp Ready"
            tvModelRuntimeBadge.setBackgroundResource(R.drawable.bg_badge_green)
        } else {
            tvModelRuntimeBadge.text = "Initializing"
            tvModelRuntimeBadge.setBackgroundResource(R.drawable.bg_badge_orange)
        }

        val actManager = getSystemService(Context.ACTIVITY_SERVICE) as? ActivityManager
        val memInfo = ActivityManager.MemoryInfo()
        actManager?.getMemoryInfo(memInfo)
        val ramFreeMb = memInfo.availMem / (1024 * 1024)

        tvHardwareStats.text = "RAM: ~$ramFreeMb MB Free • Processed: ${PocketAiServerController.totalRequestsProcessed} • Queue: ${PocketAiServerController.currentQueueSize}"

        // Network interfaces
        val ifaces = NetworkUtils.getAvailableNetworkInterfaces()
        if (ifaces.isEmpty()) {
            tvDetectedInterfaces.text = "No active network interfaces. Turn ON phone Hotspot or connect Wi-Fi."
        } else {
            val sb = StringBuilder()
            for (iface in ifaces) {
                sb.append("• ${iface.name}: ${iface.ipAddress}")
                if (iface.isHotspotCandidate) sb.append(" [Hotspot]")
                sb.append("\n")
            }
            tvDetectedInterfaces.text = sb.toString().trim()
        }

        // Connected clients
        val clients = PocketAiServerController.connectedClients.values
        if (clients.isEmpty()) {
            tvConnectedClients.text = "No clients yet. Run 'python ask.py test.txt' on your Windows laptop."
        } else {
            val sb = StringBuilder()
            for (c in clients) {
                sb.append("• ${c.ipAddress} (${c.requestCount} requests)\n")
            }
            tvConnectedClients.text = sb.toString().trim()
        }
    }

    private fun updateServerUI(state: PocketAiServerController.ServerState, ip: String, port: Int) {
        val fullUrl = "http://$ip:$port"
        tvServerFullUrl.text = fullUrl

        when (state) {
            PocketAiServerController.ServerState.RUNNING -> {
                dotServerStatus.setBackgroundResource(R.drawable.bg_status_dot_online)
                tvServerStatusTitle.text = "Server Online"
                tvServerBadge.text = "ACTIVE"
                tvServerBadge.setBackgroundResource(R.drawable.bg_badge_green)
                btnToggleServer.text = "Stop Server"
                btnToggleServer.backgroundTintList = getColorStateList(R.color.danger_red)
                etServerPort.isEnabled = false
                etServerToken.isEnabled = false
            }
            PocketAiServerController.ServerState.STARTING -> {
                dotServerStatus.setBackgroundResource(R.drawable.bg_status_dot_busy)
                tvServerStatusTitle.text = "Starting Server..."
                tvServerBadge.text = "STARTING"
                tvServerBadge.setBackgroundResource(R.drawable.bg_badge_orange)
                btnToggleServer.text = "Starting..."
                btnToggleServer.isEnabled = false
            }
            PocketAiServerController.ServerState.STOPPED -> {
                dotServerStatus.setBackgroundResource(R.drawable.bg_status_dot_offline)
                tvServerStatusTitle.text = "Server Stopped"
                tvServerBadge.text = "OFFLINE"
                tvServerBadge.setBackgroundResource(R.drawable.bg_badge_slate)
                btnToggleServer.text = "Start Server"
                btnToggleServer.isEnabled = true
                btnToggleServer.backgroundTintList = getColorStateList(R.color.primary)
                etServerPort.isEnabled = true
                etServerToken.isEnabled = true
            }
            PocketAiServerController.ServerState.ERROR -> {
                dotServerStatus.setBackgroundResource(R.drawable.bg_status_dot_busy)
                tvServerStatusTitle.text = "Server Error"
                tvServerBadge.text = "ERROR"
                tvServerBadge.setBackgroundResource(R.drawable.bg_badge_red)
                btnToggleServer.text = "Retry Start"
                btnToggleServer.isEnabled = true
                btnToggleServer.backgroundTintList = getColorStateList(R.color.primary)
                etServerPort.isEnabled = true
                etServerToken.isEnabled = true
            }
        }
    }

    private fun updateInferenceUI(status: PocketAiServerController.InferenceStatus, prompt: String?, queueSize: Int) {
        when (status) {
            PocketAiServerController.InferenceStatus.IDLE -> {
                pbInferenceActive.visibility = View.GONE
                tvInferenceStateText.text = "Idle • Ready for requests from Windows CMD"
            }
            PocketAiServerController.InferenceStatus.GENERATING -> {
                pbInferenceActive.visibility = View.VISIBLE
                val snippet = if (!prompt.isNullOrBlank() && prompt.length > 35) prompt.substring(0, 32) + "..." else prompt ?: ""
                tvInferenceStateText.text = "Generating: \"$snippet\" (Queue: $queueSize)"
            }
            PocketAiServerController.InferenceStatus.QUEUED -> {
                pbInferenceActive.visibility = View.VISIBLE
                tvInferenceStateText.text = "Request queued ($queueSize in queue)..."
            }
        }
        refreshHardwareAndModelStats()
    }

    private fun performQuickTest() {
        if (PocketAiServerController.currentState != PocketAiServerController.ServerState.RUNNING) {
            Toast.makeText(this, "Please start the server first before testing", Toast.LENGTH_SHORT).show()
            return
        }

        val progressDialog = AlertDialog.Builder(this)
            .setTitle("⚡ Testing Local Inference")
            .setMessage("Sending test question to Qwen3 via localhost HTTP API...\nPlease wait...")
            .setCancelable(false)
            .create()
        progressDialog.show()

        val port = PocketAiServerController.activePort
        val token = PocketAiServerController.getAuthToken(this)

        Thread {
            try {
                val testPayload = JSONObject().apply {
                    put("question", "What is an Operating System? Explain in 2 sentences.")
                    put("temperature", 0.6)
                    put("max_tokens", 128)
                }

                val reqBuilder = Request.Builder()
                    .url("http://127.0.0.1:$port/api/chat")
                    .post(testPayload.toString().toRequestBody("application/json; charset=utf-8".toMediaType()))

                if (token.isNotBlank()) {
                    reqBuilder.addHeader("X-PocketAI-Token", token)
                }

                val resp = httpClient.newCall(reqBuilder.build()).execute()
                val respStr = resp.body?.string() ?: ""
                val respJson = JSONObject(respStr)

                runOnUiThread {
                    progressDialog.dismiss()
                    val answer = respJson.optString("answer", "No answer field in response")
                    val time = respJson.optDouble("processing_time", 0.0)

                    AlertDialog.Builder(this)
                        .setTitle("✓ Quick Test Succeeded")
                        .setMessage("Question: What is an Operating System?\n\nAnswer: $answer\n\nProcessing Time: ${time}s\n\nStatus: 100% Ready for Windows Laptop!")
                        .setPositiveButton("OK", null)
                        .show()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    progressDialog.dismiss()
                    AlertDialog.Builder(this)
                        .setTitle("Test Failed")
                        .setMessage("Error connecting to local server: ${e.message}")
                        .setPositiveButton("Dismiss", null)
                        .show()
                }
            }
        }.start()
    }

    private fun copyToClipboard(text: String) {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = ClipData.newPlainText("PocketAI Server URL", text)
        clipboard.setPrimaryClip(clip)
    }

    // StateListener Callbacks
    override fun onServerStateChanged(state: PocketAiServerController.ServerState, ip: String, port: Int) {
        runOnUiThread {
            updateServerUI(state, ip, port)
        }
    }

    override fun onInferenceStatusChanged(status: PocketAiServerController.InferenceStatus, currentPrompt: String?, queueSize: Int) {
        runOnUiThread {
            updateInferenceUI(status, currentPrompt, queueSize)
        }
    }

    override fun onRequestLogAdded(entry: PocketAiServerController.RequestLogEntry) {
        runOnUiThread {
            logAdapter.addLog(entry)
            tvEmptyLogs.visibility = View.GONE
            rvServerLogs.visibility = View.VISIBLE
            rvServerLogs.scrollToPosition(0)
            refreshHardwareAndModelStats()
        }
    }

    override fun onErrorLogAdded(entry: PocketAiServerController.ErrorLogEntry) {
        runOnUiThread {
            refreshHardwareAndModelStats()
        }
    }

    override fun onClientConnected(client: PocketAiServerController.ClientInfo) {
        runOnUiThread {
            refreshHardwareAndModelStats()
        }
    }
}
