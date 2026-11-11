package com.couplecanvas.app.domain.model

import java.util.UUID

enum class ToolType {
    PENCIL,
    BRUSH,
    MARKER,
    HIGHLIGHTER,
    ERASER,
    LINE,
    RECTANGLE,
    CIRCLE,
    ARROW,
    TEXT
}

data class Point(
    val x: Float,
    val y: Float,
    val pressure: Float = 1.0f,
    val timestamp: Long = System.currentTimeMillis()
)

data class Stroke(
    val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val tool: ToolType,
    val colorHex: String,
    val strokeWidth: Float,
    val opacity: Float,
    val points: List<Point>,
    val timestamp: Long = System.currentTimeMillis()
)

data class ShapeObject(
    val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val tool: ToolType, // LINE, RECTANGLE, CIRCLE, ARROW
    val colorHex: String,
    val strokeWidth: Float,
    val opacity: Float,
    val startX: Float,
    val startY: Float,
    val endX: Float,
    val endY: Float,
    val timestamp: Long = System.currentTimeMillis()
)

data class TextObject(
    val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val text: String,
    val colorHex: String,
    val fontSize: Float,
    val x: Float,
    val y: Float,
    val timestamp: Long = System.currentTimeMillis()
)

data class StickerObject(
    val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val stickerAssetId: String,
    val category: String,
    val x: Float,
    val y: Float,
    val scale: Float = 1.0f,
    val rotation: Float = 0.0f,
    val timestamp: Long = System.currentTimeMillis()
)

sealed class CanvasOperation {
    abstract val operationId: String
    abstract val userId: String
    abstract val timestamp: Long

    data class AddStroke(
        override val operationId: String = UUID.randomUUID().toString(),
        override val userId: String,
        override val timestamp: Long = System.currentTimeMillis(),
        val stroke: Stroke
    ) : CanvasOperation()

    data class AddShape(
        override val operationId: String = UUID.randomUUID().toString(),
        override val userId: String,
        override val timestamp: Long = System.currentTimeMillis(),
        val shape: ShapeObject
    ) : CanvasOperation()

    data class AddText(
        override val operationId: String = UUID.randomUUID().toString(),
        override val userId: String,
        override val timestamp: Long = System.currentTimeMillis(),
        val textObject: TextObject
    ) : CanvasOperation()

    data class AddSticker(
        override val operationId: String = UUID.randomUUID().toString(),
        override val userId: String,
        override val timestamp: Long = System.currentTimeMillis(),
        val sticker: StickerObject
    ) : CanvasOperation()

    data class MoveSticker(
        override val operationId: String = UUID.randomUUID().toString(),
        override val userId: String,
        override val timestamp: Long = System.currentTimeMillis(),
        val stickerId: String,
        val newX: Float,
        val newY: Float,
        val newScale: Float,
        val newRotation: Float
    ) : CanvasOperation()

    data class DeleteSticker(
        override val operationId: String = UUID.randomUUID().toString(),
        override val userId: String,
        override val timestamp: Long = System.currentTimeMillis(),
        val stickerId: String
    ) : CanvasOperation()

    data class ClearCanvas(
        override val operationId: String = UUID.randomUUID().toString(),
        override val userId: String,
        override val timestamp: Long = System.currentTimeMillis()
    ) : CanvasOperation()

    data class Undo(
        override val operationId: String = UUID.randomUUID().toString(),
        override val userId: String,
        override val timestamp: Long = System.currentTimeMillis(),
        val targetOperationId: String
    ) : CanvasOperation()

    data class Redo(
        override val operationId: String = UUID.randomUUID().toString(),
        override val userId: String,
        override val timestamp: Long = System.currentTimeMillis(),
        val targetOperationId: String
    ) : CanvasOperation()
}

data class Drawing(
    val id: String = UUID.randomUUID().toString(),
    val title: String,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis(),
    val partnerName: String? = null,
    val previewImagePath: String? = null,
    val operations: List<CanvasOperation> = emptyList()
)
