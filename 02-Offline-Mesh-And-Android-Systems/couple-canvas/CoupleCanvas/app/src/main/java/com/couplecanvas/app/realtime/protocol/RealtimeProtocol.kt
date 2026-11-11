package com.couplecanvas.app.realtime.protocol

import com.google.gson.Gson
import com.couplecanvas.app.domain.model.CanvasOperation
import com.couplecanvas.app.domain.model.ChatMessage
import com.couplecanvas.app.domain.model.CursorPosition
import com.couplecanvas.app.domain.model.MessageType
import com.couplecanvas.app.domain.model.ReactionEvent
import com.couplecanvas.app.domain.model.RealtimeMessage
import java.util.concurrent.atomic.AtomicLong

class RealtimeProtocol(private val gson: Gson = Gson()) {

    private val sequenceCounter = AtomicLong(1)
    private val processedOperationIds = mutableSetOf<String>()

    fun wrapOperation(op: CanvasOperation, roomId: String, userId: String): RealtimeMessage {
        val type = when (op) {
            is CanvasOperation.AddStroke -> MessageType.STROKE_BEGIN
            is CanvasOperation.AddShape -> MessageType.SHAPE_ADD
            is CanvasOperation.AddText -> MessageType.TEXT_ADD
            is CanvasOperation.AddSticker -> MessageType.STICKER_ADD
            is CanvasOperation.MoveSticker -> MessageType.STICKER_MOVE
            is CanvasOperation.DeleteSticker -> MessageType.STICKER_DELETE
            is CanvasOperation.ClearCanvas -> MessageType.CLEAR_CANVAS
            is CanvasOperation.Undo -> MessageType.UNDO
            is CanvasOperation.Redo -> MessageType.REDO
        }

        return RealtimeMessage(
            version = 1,
            type = type,
            operationId = op.operationId,
            roomId = roomId,
            userId = userId,
            sequenceNum = sequenceCounter.getAndIncrement(),
            timestamp = op.timestamp,
            payloadJson = gson.toJson(op)
        )
    }

    fun wrapCursor(cursor: CursorPosition, roomId: String): RealtimeMessage {
        return RealtimeMessage(
            version = 1,
            type = MessageType.CURSOR_MOVE,
            roomId = roomId,
            userId = cursor.userId,
            sequenceNum = sequenceCounter.getAndIncrement(),
            payloadJson = gson.toJson(cursor)
        )
    }

    fun wrapReaction(reaction: ReactionEvent, roomId: String): RealtimeMessage {
        return RealtimeMessage(
            version = 1,
            type = MessageType.REACTION,
            roomId = roomId,
            userId = reaction.userId,
            sequenceNum = sequenceCounter.getAndIncrement(),
            payloadJson = gson.toJson(reaction)
        )
    }

    fun wrapChat(chat: ChatMessage, roomId: String): RealtimeMessage {
        return RealtimeMessage(
            version = 1,
            type = MessageType.CHAT_MESSAGE,
            roomId = roomId,
            userId = chat.senderUserId,
            sequenceNum = sequenceCounter.getAndIncrement(),
            payloadJson = gson.toJson(chat)
        )
    }

    fun parseOperation(message: RealtimeMessage): CanvasOperation? {
        if (message.operationId != null && processedOperationIds.contains(message.operationId)) {
            // Idempotent duplicate check
            return null
        }
        message.operationId?.let { processedOperationIds.add(it) }

        val payload = message.payloadJson ?: return null
        return try {
            when (message.type) {
                MessageType.STROKE_BEGIN, MessageType.STROKE_END -> gson.fromJson(payload, CanvasOperation.AddStroke::class.java)
                MessageType.SHAPE_ADD -> gson.fromJson(payload, CanvasOperation.AddShape::class.java)
                MessageType.TEXT_ADD -> gson.fromJson(payload, CanvasOperation.AddText::class.java)
                MessageType.STICKER_ADD -> gson.fromJson(payload, CanvasOperation.AddSticker::class.java)
                MessageType.STICKER_MOVE -> gson.fromJson(payload, CanvasOperation.MoveSticker::class.java)
                MessageType.STICKER_DELETE -> gson.fromJson(payload, CanvasOperation.DeleteSticker::class.java)
                MessageType.CLEAR_CANVAS -> gson.fromJson(payload, CanvasOperation.ClearCanvas::class.java)
                MessageType.UNDO -> gson.fromJson(payload, CanvasOperation.Undo::class.java)
                MessageType.REDO -> gson.fromJson(payload, CanvasOperation.Redo::class.java)
                else -> null
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    fun parseCursor(message: RealtimeMessage): CursorPosition? {
        val payload = message.payloadJson ?: return null
        return try {
            gson.fromJson(payload, CursorPosition::class.java)
        } catch (e: Exception) {
            null
        }
    }

    fun parseReaction(message: RealtimeMessage): ReactionEvent? {
        val payload = message.payloadJson ?: return null
        return try {
            gson.fromJson(payload, ReactionEvent::class.java)
        } catch (e: Exception) {
            null
        }
    }

    fun parseChat(message: RealtimeMessage): ChatMessage? {
        val payload = message.payloadJson ?: return null
        return try {
            gson.fromJson(payload, ChatMessage::class.java)
        } catch (e: Exception) {
            null
        }
    }

    fun serialize(msg: RealtimeMessage): String {
        return gson.toJson(msg)
    }

    fun deserialize(json: String): RealtimeMessage? {
        return try {
            gson.fromJson(json, RealtimeMessage::class.java)
        } catch (e: Exception) {
            null
        }
    }
}
