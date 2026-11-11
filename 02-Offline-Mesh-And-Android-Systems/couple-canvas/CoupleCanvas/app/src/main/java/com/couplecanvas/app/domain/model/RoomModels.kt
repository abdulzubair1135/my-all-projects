package com.couplecanvas.app.domain.model

enum class ConnectionState {
    IDLE,
    CONNECTING,
    CONNECTED,
    DISCONNECTED,
    RECONNECTING,
    FAILED,
    CLOSED
}

data class Participant(
    val userId: String,
    val displayName: String,
    val isHost: Boolean
)

data class RoomInfo(
    val roomCode: String,
    val myUserId: String,
    val myName: String,
    val partnerUserId: String? = null,
    val partnerName: String? = null,
    val isHost: Boolean,
    val connectionState: ConnectionState = ConnectionState.IDLE
)
