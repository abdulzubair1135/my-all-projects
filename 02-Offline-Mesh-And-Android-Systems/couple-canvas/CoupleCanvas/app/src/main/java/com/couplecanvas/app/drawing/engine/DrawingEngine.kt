package com.couplecanvas.app.drawing.engine

import com.couplecanvas.app.domain.model.CanvasOperation
import com.couplecanvas.app.domain.model.Point
import com.couplecanvas.app.domain.model.ShapeObject
import com.couplecanvas.app.domain.model.StickerObject
import com.couplecanvas.app.domain.model.Stroke
import com.couplecanvas.app.domain.model.TextObject
import com.couplecanvas.app.domain.model.ToolType
import com.couplecanvas.app.drawing.tools.DrawingToolConfig
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.UUID

class DrawingEngine {

    private val _toolConfig = MutableStateFlow(DrawingToolConfig())
    val toolConfig: StateFlow<DrawingToolConfig> = _toolConfig.asStateFlow()

    private val _operations = MutableStateFlow<List<CanvasOperation>>(emptyList())
    val operations: StateFlow<List<CanvasOperation>> = _operations.asStateFlow()

    private val undoStack = mutableListOf<CanvasOperation>()
    private val redoStack = mutableListOf<CanvasOperation>()

    // Current active stroke being drawn by local user
    private val _currentActiveStroke = MutableStateFlow<Stroke?>(null)
    val currentActiveStroke: StateFlow<Stroke?> = _currentActiveStroke.asStateFlow()

    // Current active shape preview being drawn
    private val _currentActiveShape = MutableStateFlow<ShapeObject?>(null)
    val currentActiveShape: StateFlow<ShapeObject?> = _currentActiveShape.asStateFlow()

    // Listener for operations to send via P2P
    var onLocalOperationCommitted: ((CanvasOperation) -> Unit)? = null
    var onCursorMoved: ((x: Float, y: Float, isDrawing: Boolean) -> Unit)? = null

    private var currentUserId: String = "local_user"
    private var shapeStartX: Float = 0f
    private var shapeStartY: Float = 0f

    fun initialize(userId: String) {
        this.currentUserId = userId
    }

    fun updateToolConfig(newConfig: DrawingToolConfig) {
        _toolConfig.value = newConfig
    }

    fun setToolType(type: ToolType) {
        _toolConfig.value = _toolConfig.value.copy(type = type)
    }

    fun setColor(colorHex: String) {
        _toolConfig.value = _toolConfig.value.copy(colorHex = colorHex)
    }

    fun setStrokeWidth(width: Float) {
        _toolConfig.value = _toolConfig.value.copy(strokeWidth = width)
    }

    fun setOpacity(opacity: Float) {
        _toolConfig.value = _toolConfig.value.copy(opacity = opacity)
    }

    // Touch events for drawing
    fun onTouchDown(x: Float, y: Float, pressure: Float = 1.0f) {
        val config = _toolConfig.value
        onCursorMoved?.invoke(x, y, true)

        when (config.type) {
            ToolType.PENCIL, ToolType.BRUSH, ToolType.MARKER, ToolType.HIGHLIGHTER, ToolType.ERASER -> {
                val initialPoints = listOf(Point(x, y, pressure))
                _currentActiveStroke.value = Stroke(
                    id = UUID.randomUUID().toString(),
                    userId = currentUserId,
                    tool = config.type,
                    colorHex = if (config.type == ToolType.ERASER) "#FFFFFF" else config.colorHex,
                    strokeWidth = if (config.type == ToolType.ERASER) config.strokeWidth * 2.5f else config.strokeWidth,
                    opacity = if (config.type == ToolType.HIGHLIGHTER) 0.4f else config.opacity,
                    points = initialPoints
                )
            }
            ToolType.LINE, ToolType.RECTANGLE, ToolType.CIRCLE, ToolType.ARROW -> {
                shapeStartX = x
                shapeStartY = y
                _currentActiveShape.value = ShapeObject(
                    id = UUID.randomUUID().toString(),
                    userId = currentUserId,
                    tool = config.type,
                    colorHex = config.colorHex,
                    strokeWidth = config.strokeWidth,
                    opacity = config.opacity,
                    startX = x,
                    startY = y,
                    endX = x,
                    endY = y
                )
            }
            else -> {}
        }
    }

    fun onTouchMove(x: Float, y: Float, pressure: Float = 1.0f) {
        onCursorMoved?.invoke(x, y, true)

        val activeStroke = _currentActiveStroke.value
        if (activeStroke != null) {
            val updatedPoints = activeStroke.points + Point(x, y, pressure)
            _currentActiveStroke.value = activeStroke.copy(points = updatedPoints)
            return
        }

        val activeShape = _currentActiveShape.value
        if (activeShape != null) {
            _currentActiveShape.value = activeShape.copy(endX = x, endY = y)
        }
    }

    fun onTouchUp(x: Float, y: Float) {
        onCursorMoved?.invoke(x, y, false)

        val activeStroke = _currentActiveStroke.value
        if (activeStroke != null && activeStroke.points.isNotEmpty()) {
            val finalStroke = activeStroke.copy(points = activeStroke.points + Point(x, y))
            _currentActiveStroke.value = null

            val op = CanvasOperation.AddStroke(
                operationId = UUID.randomUUID().toString(),
                userId = currentUserId,
                stroke = finalStroke
            )
            applyOperation(op, isLocal = true)
            return
        }

        val activeShape = _currentActiveShape.value
        if (activeShape != null) {
            val finalShape = activeShape.copy(endX = x, endY = y)
            _currentActiveShape.value = null

            val op = CanvasOperation.AddShape(
                operationId = UUID.randomUUID().toString(),
                userId = currentUserId,
                shape = finalShape
            )
            applyOperation(op, isLocal = true)
        }
    }

    fun addText(text: String, x: Float, y: Float) {
        val config = _toolConfig.value
        val textObj = TextObject(
            id = UUID.randomUUID().toString(),
            userId = currentUserId,
            text = text,
            colorHex = config.colorHex,
            fontSize = config.strokeWidth * 3 + 12,
            x = x,
            y = y
        )
        val op = CanvasOperation.AddText(
            operationId = UUID.randomUUID().toString(),
            userId = currentUserId,
            textObject = textObj
        )
        applyOperation(op, isLocal = true)
    }

    fun addSticker(assetId: String, category: String, x: Float, y: Float) {
        val stickerObj = StickerObject(
            id = UUID.randomUUID().toString(),
            userId = currentUserId,
            stickerAssetId = assetId,
            category = category,
            x = x,
            y = y
        )
        val op = CanvasOperation.AddSticker(
            operationId = UUID.randomUUID().toString(),
            userId = currentUserId,
            sticker = stickerObj
        )
        applyOperation(op, isLocal = true)
    }

    fun moveSticker(stickerId: String, newX: Float, newY: Float, scale: Float, rotation: Float) {
        val op = CanvasOperation.MoveSticker(
            operationId = UUID.randomUUID().toString(),
            userId = currentUserId,
            stickerId = stickerId,
            newX = newX,
            newY = newY,
            newScale = scale,
            newRotation = rotation
        )
        applyOperation(op, isLocal = true)
    }

    fun deleteSticker(stickerId: String) {
        val op = CanvasOperation.DeleteSticker(
            operationId = UUID.randomUUID().toString(),
            userId = currentUserId,
            stickerId = stickerId
        )
        applyOperation(op, isLocal = true)
    }

    fun clearCanvas() {
        val op = CanvasOperation.ClearCanvas(
            operationId = UUID.randomUUID().toString(),
            userId = currentUserId
        )
        applyOperation(op, isLocal = true)
    }

    fun undo() {
        if (_operations.value.isNotEmpty()) {
            val lastOp = _operations.value.lastOrNull { it.userId == currentUserId }
            if (lastOp != null) {
                val undoOp = CanvasOperation.Undo(
                    operationId = UUID.randomUUID().toString(),
                    userId = currentUserId,
                    targetOperationId = lastOp.operationId
                )
                applyOperation(undoOp, isLocal = true)
            }
        }
    }

    fun redo() {
        if (redoStack.isNotEmpty()) {
            val redoOpToReapply = redoStack.removeAt(redoStack.size - 1)
            applyOperation(redoOpToReapply, isLocal = true)
        }
    }

    // Apply operation deterministically (local or incoming remote operation)
    fun applyOperation(op: CanvasOperation, isLocal: Boolean = false) {
        // Prevent duplicate processing if operationId is already present
        if (_operations.value.any { it.operationId == op.operationId }) return

        val currentList = _operations.value.toMutableList()

        when (op) {
            is CanvasOperation.AddStroke,
            is CanvasOperation.AddShape,
            is CanvasOperation.AddText,
            is CanvasOperation.AddSticker -> {
                currentList.add(op)
                if (isLocal) {
                    undoStack.add(op)
                    redoStack.clear()
                }
            }
            is CanvasOperation.MoveSticker -> {
                currentList.add(op)
            }
            is CanvasOperation.DeleteSticker -> {
                currentList.add(op)
            }
            is CanvasOperation.ClearCanvas -> {
                currentList.add(op)
            }
            is CanvasOperation.Undo -> {
                currentList.add(op)
            }
            is CanvasOperation.Redo -> {
                currentList.add(op)
            }
        }

        _operations.value = currentList

        if (isLocal) {
            onLocalOperationCommitted?.invoke(op)
        }
    }

    fun loadOperations(ops: List<CanvasOperation>) {
        _operations.value = ops
    }
}
