package com.couplecanvas.app.domain.model

enum class MessageType {
    // Signaling Server Messages
    CREATE_ROOM,
    ROOM_CREATED,
    JOIN_ROOM,
    ROOM_JOINED,
    JOIN_FAILED,
    PARTNER_JOINED,
    OFFER,
    ANSWER,
    ICE_CANDIDATE,
    LEAVE_ROOM,
    PARTNER_DISCONNECTED,
    ERROR,

    // DataChannel P2P Live Sync Messages
    STROKE_BEGIN,
    STROKE_POINTS,
    STROKE_END,
    SHAPE_ADD,
    TEXT_ADD,
    STICKER_ADD,
    STICKER_MOVE,
    STICKER_DELETE,
    CLEAR_CANVAS,
    UNDO,
    REDO,
    CURSOR_MOVE,
    REACTION,
    CHAT_MESSAGE,
    SYNC_REQUEST,
    SYNC_RESPONSE
}

data class CursorPosition(
    val userId: String,
    val x: Float,
    val y: Float,
    val isDrawing: Boolean = false,
    val activeTool: ToolType = ToolType.PENCIL
)

data class ReactionEvent(
    val id: String,
    val userId: String,
    val emoji: String, // e.g. "❤️", "💖", "✨", "🌸", "🔥"
    val x: Float,
    val y: Float,
    val timestamp: Long = System.currentTimeMillis()
)

data class ChatMessage(
    val id: String,
    val senderUserId: String,
    val senderName: String,
    val text: String,
    val timestamp: Long = System.currentTimeMillis()
)

data class RealtimeMessage(
    val version: Int = 1,
    val type: MessageType,
    val operationId: String? = null,
    val roomId: String? = null,
    val userId: String? = null,
    val sequenceNum: Long = 0,
    val timestamp: Long = System.currentTimeMillis(),
    val payloadJson: String? = null
)
