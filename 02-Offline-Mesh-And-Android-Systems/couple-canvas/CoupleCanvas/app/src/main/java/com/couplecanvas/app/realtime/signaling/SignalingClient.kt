package com.couplecanvas.app.realtime.signaling

import com.google.gson.Gson
import com.couplecanvas.app.domain.model.MessageType
import com.couplecanvas.app.domain.model.RealtimeMessage
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import java.util.concurrent.TimeUnit

class SignalingClient(
    private var serverUrl: String,
    private val gson: Gson = Gson()
) {
    private var webSocket: WebSocket? = null
    private var isConnected = false
    private val pendingMessages = mutableListOf<RealtimeMessage>()

    private val client = OkHttpClient.Builder()
        .readTimeout(15, TimeUnit.SECONDS)
        .connectTimeout(15, TimeUnit.SECONDS)
        .build()

    private val _messages = MutableSharedFlow<RealtimeMessage>()
    val messages: SharedFlow<RealtimeMessage> = _messages.asSharedFlow()

    private val _connectionState = MutableSharedFlow<Boolean>()
    val connectionState: SharedFlow<Boolean> = _connectionState.asSharedFlow()

    private val scope = CoroutineScope(Dispatchers.IO)

    fun updateServerUrl(newUrl: String) {
        if (serverUrl != newUrl) {
            serverUrl = newUrl
            disconnect()
            connect()
        }
    }

    fun connect() {
        if (webSocket != null) return

        val request = Request.Builder()
            .url(serverUrl)
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                isConnected = true
                scope.launch {
                    _connectionState.emit(true)
                    // Flush pending messages queued prior to socket open
                    val pending = synchronized(pendingMessages) {
                        val list = ArrayList(pendingMessages)
                        pendingMessages.clear()
                        list
                    }
                    pending.forEach { msg ->
                        webSocket.send(gson.toJson(msg))
                    }
                }
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val msg = gson.fromJson(text, RealtimeMessage::class.java)
                    scope.launch {
                        _messages.emit(msg)
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                isConnected = false
                scope.launch {
                    _connectionState.emit(false)
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                isConnected = false
                webSocket.close(1001, "Connection failure")
                this@SignalingClient.webSocket = null
                scope.launch {
                    _connectionState.emit(false)
                }
            }
        })
    }

    fun send(message: RealtimeMessage) {
        val ws = webSocket
        if (ws != null && isConnected) {
            ws.send(gson.toJson(message))
        } else {
            synchronized(pendingMessages) {
                pendingMessages.add(message)
            }
            if (ws == null) {
                connect()
            }
        }
    }

    fun disconnect() {
        webSocket?.close(1000, "User disconnected")
        webSocket = null
        isConnected = false
    }
}
