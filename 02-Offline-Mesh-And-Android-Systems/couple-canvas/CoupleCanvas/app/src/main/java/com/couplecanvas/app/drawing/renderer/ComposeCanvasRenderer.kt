package com.couplecanvas.app.drawing.renderer

import android.graphics.Color as AndroidColor
import android.graphics.Paint as AndroidPaint
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.calculatePan
import androidx.compose.foundation.gestures.calculateZoom
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke as ComposeStroke
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.drawscope.translate
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.input.pointer.pointerInput
import com.couplecanvas.app.domain.model.CanvasOperation
import com.couplecanvas.app.domain.model.CursorPosition
import com.couplecanvas.app.domain.model.ShapeObject
import com.couplecanvas.app.domain.model.StickerObject
import com.couplecanvas.app.domain.model.Stroke
import com.couplecanvas.app.domain.model.TextObject
import com.couplecanvas.app.domain.model.ToolType
import com.couplecanvas.app.drawing.engine.DrawingEngine
import com.couplecanvas.app.drawing.tools.DrawingToolConfig
import kotlin.math.abs
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.sin

@Composable
fun ComposeCanvasRenderer(
    operations: List<CanvasOperation>,
    activeLocalStroke: Stroke? = null,
    activeLocalShape: ShapeObject? = null,
    activePartnerStroke: Stroke? = null,
    partnerCursor: CursorPosition? = null,
    partnerName: String? = null,
    scale: Float = 1.0f,
    offset: Offset = Offset.Zero,
    toolConfig: DrawingToolConfig = DrawingToolConfig(),
    drawingEngine: DrawingEngine? = null,
    onTransform: (zoomChange: Float, panChange: Offset) -> Unit = { _, _ -> },
    onTextTap: (Offset) -> Unit = {},
    modifier: Modifier = Modifier
) {
    val computedState = computeCanvasObjects(operations)

    Canvas(
        modifier = modifier
            .pointerInput(toolConfig.type, scale, offset, drawingEngine) {
                awaitEachGesture {
                    val down = awaitFirstDown(requireUnconsumed = false)
                    var isMultiTouch = false

                    fun toCanvasCoords(screenPos: Offset): Offset {
                        return Offset(
                            x = (screenPos.x - offset.x) / scale,
                            y = (screenPos.y - offset.y) / scale
                        )
                    }

                    if (drawingEngine == null) {
                        do {
                            val event = awaitPointerEvent()
                            val zoomChange = event.calculateZoom()
                            val panChange = event.calculatePan()
                            onTransform(zoomChange, panChange)
                            event.changes.forEach { it.consume() }
                        } while (event.changes.any { it.pressed })
                    } else if (toolConfig.type == ToolType.TEXT) {
                        val canvasPos = toCanvasCoords(down.position)
                        onTextTap(canvasPos)
                        down.consume()
                    } else {
                        val initialPos = toCanvasCoords(down.position)
                        var lastCanvasPos = initialPos
                        drawingEngine.onTouchDown(initialPos.x, initialPos.y)

                        do {
                            val event = awaitPointerEvent()
                            val activePointers = event.changes.filter { it.pressed }

                            if (activePointers.size >= 2) {
                                if (!isMultiTouch) {
                                    isMultiTouch = true
                                    drawingEngine.onTouchUp(lastCanvasPos.x, lastCanvasPos.y)
                                }
                                val zoomChange = event.calculateZoom()
                                val panChange = event.calculatePan()
                                onTransform(zoomChange, panChange)
                                event.changes.forEach { it.consume() }
                            } else if (activePointers.size == 1 && !isMultiTouch) {
                                val pointer = activePointers.first()
                                pointer.consume()
                                lastCanvasPos = toCanvasCoords(pointer.position)
                                drawingEngine.onTouchMove(lastCanvasPos.x, lastCanvasPos.y)
                            }
                        } while (event.changes.any { it.pressed })

                        if (!isMultiTouch) {
                            drawingEngine.onTouchUp(lastCanvasPos.x, lastCanvasPos.y)
                        }
                    }
                }
            }
    ) {
        translate(left = offset.x, top = offset.y) {
            scale(scale = scale, pivot = Offset.Zero) {
                drawBackgroundGrid()

                computedState.strokes.forEach { stroke ->
                    drawSingleStroke(stroke)
                }

                computedState.shapes.forEach { shape ->
                    drawSingleShape(shape)
                }

                computedState.texts.forEach { textObj ->
                    drawSingleText(textObj)
                }

                computedState.stickers.forEach { stickerObj ->
                    drawSingleSticker(stickerObj)
                }

                activeLocalStroke?.let { stroke ->
                    drawSingleStroke(stroke)
                }

                activeLocalShape?.let { shape ->
                    drawSingleShape(shape)
                }

                activePartnerStroke?.let { stroke ->
                    drawSingleStroke(stroke)
                }

                partnerCursor?.let { cursor ->
                    drawPartnerCursor(cursor, partnerName ?: "Partner")
                }
            }
        }
    }
}

private data class ComputedCanvasState(
    val strokes: List<Stroke> = emptyList(),
    val shapes: List<ShapeObject> = emptyList(),
    val texts: List<TextObject> = emptyList(),
    val stickers: List<StickerObject> = emptyList()
)

private fun computeCanvasObjects(operations: List<CanvasOperation>): ComputedCanvasState {
    val strokes = mutableListOf<Stroke>()
    val shapes = mutableListOf<ShapeObject>()
    val texts = mutableListOf<TextObject>()
    val stickersMap = mutableMapOf<String, StickerObject>()

    for (op in operations) {
        when (op) {
            is CanvasOperation.AddStroke -> {
                strokes.add(op.stroke)
            }
            is CanvasOperation.AddShape -> {
                shapes.add(op.shape)
            }
            is CanvasOperation.AddText -> {
                texts.add(op.textObject)
            }
            is CanvasOperation.AddSticker -> {
                stickersMap[op.sticker.id] = op.sticker
            }
            is CanvasOperation.MoveSticker -> {
                stickersMap[op.stickerId]?.let { existing ->
                    stickersMap[op.stickerId] = existing.copy(
                        x = op.newX,
                        y = op.newY,
                        scale = op.newScale,
                        rotation = op.newRotation
                    )
                }
            }
            is CanvasOperation.DeleteSticker -> {
                stickersMap.remove(op.stickerId)
            }
            is CanvasOperation.ClearCanvas -> {
                strokes.clear()
                shapes.clear()
                texts.clear()
                stickersMap.clear()
            }
            is CanvasOperation.Undo -> {
                val targetOp = operations.find { it.operationId == op.targetOperationId }
                if (targetOp is CanvasOperation.AddStroke) {
                    strokes.removeAll { it.id == targetOp.stroke.id }
                } else if (targetOp is CanvasOperation.AddShape) {
                    shapes.removeAll { it.id == targetOp.shape.id }
                } else if (targetOp is CanvasOperation.AddText) {
                    texts.removeAll { it.id == targetOp.textObject.id }
                } else if (targetOp is CanvasOperation.AddSticker) {
                    stickersMap.remove(targetOp.sticker.id)
                }
            }
            is CanvasOperation.Redo -> {}
        }
    }

    return ComputedCanvasState(
        strokes = strokes,
        shapes = shapes,
        texts = texts,
        stickers = stickersMap.values.toList()
    )
}

private fun DrawScope.drawBackgroundGrid() {
    val step = 40f
    val gridColor = Color(0x15000000)
    var x = 0f
    while (x < size.width) {
        var y = 0f
        while (y < size.height) {
            drawCircle(
                color = gridColor,
                radius = 2f,
                center = Offset(x, y)
            )
            y += step
        }
        x += step
    }
}

private fun DrawScope.drawSingleStroke(stroke: Stroke) {
    if (stroke.points.isEmpty()) return

    val color = parseColorHex(stroke.colorHex, stroke.opacity)

    if (stroke.points.size == 1) {
        val p = stroke.points.first()
        drawCircle(
            color = color,
            radius = stroke.strokeWidth / 2,
            center = Offset(p.x, p.y)
        )
        return
    }

    val path = Path().apply {
        moveTo(stroke.points[0].x, stroke.points[0].y)
        if (stroke.points.size == 2) {
            lineTo(stroke.points[1].x, stroke.points[1].y)
        } else {
            for (i in 1 until stroke.points.size - 1) {
                val p0 = stroke.points[i]
                val p1 = stroke.points[i + 1]
                val midX = (p0.x + p1.x) / 2f
                val midY = (p0.y + p1.y) / 2f
                quadraticBezierTo(p0.x, p0.y, midX, midY)
            }
            lineTo(stroke.points.last().x, stroke.points.last().y)
        }
    }

    val strokeStyle = ComposeStroke(
        width = stroke.strokeWidth,
        cap = StrokeCap.Round,
        join = StrokeJoin.Round
    )

    drawPath(path = path, color = color, style = strokeStyle)
}

private fun DrawScope.drawSingleShape(shape: ShapeObject) {
    val color = parseColorHex(shape.colorHex, shape.opacity)
    val strokeStyle = ComposeStroke(
        width = shape.strokeWidth,
        cap = StrokeCap.Round,
        join = StrokeJoin.Round
    )

    val start = Offset(shape.startX, shape.startY)
    val end = Offset(shape.endX, shape.endY)

    when (shape.tool) {
        ToolType.LINE -> {
            drawLine(color = color, start = start, end = end, strokeWidth = shape.strokeWidth, cap = StrokeCap.Round)
        }
        ToolType.RECTANGLE -> {
            val left = minOf(shape.startX, shape.endX)
            val top = minOf(shape.startY, shape.endY)
            val width = abs(shape.endX - shape.startX)
            val height = abs(shape.endY - shape.startY)
            drawRect(
                color = color,
                topLeft = Offset(left, top),
                size = Size(width, height),
                style = strokeStyle
            )
        }
        ToolType.CIRCLE -> {
            val left = minOf(shape.startX, shape.endX)
            val top = minOf(shape.startY, shape.endY)
            val width = abs(shape.endX - shape.startX)
            val height = abs(shape.endY - shape.startY)
            drawOval(
                color = color,
                topLeft = Offset(left, top),
                size = Size(width, height),
                style = strokeStyle
            )
        }
        ToolType.ARROW -> {
            drawLine(color = color, start = start, end = end, strokeWidth = shape.strokeWidth, cap = StrokeCap.Round)
            val angle = atan2(end.y - start.y, end.x - start.x)
            val arrowRadius = shape.strokeWidth * 3
            val x1 = end.x - arrowRadius * cos(angle - Math.PI / 6).toFloat()
            val y1 = end.y - arrowRadius * sin(angle - Math.PI / 6).toFloat()
            val x2 = end.x - arrowRadius * cos(angle + Math.PI / 6).toFloat()
            val y2 = end.y - arrowRadius * sin(angle + Math.PI / 6).toFloat()

            drawLine(color = color, start = end, end = Offset(x1, y1), strokeWidth = shape.strokeWidth, cap = StrokeCap.Round)
            drawLine(color = color, start = end, end = Offset(x2, y2), strokeWidth = shape.strokeWidth, cap = StrokeCap.Round)
        }
        else -> {}
    }
}

private fun DrawScope.drawSingleText(textObj: TextObject) {
    val paint = AndroidPaint().apply {
        color = parseColorHex(textObj.colorHex, 1.0f).toArgb()
        textSize = textObj.fontSize
        isAntiAlias = true
    }
    drawContext.canvas.nativeCanvas.drawText(
        textObj.text,
        textObj.x,
        textObj.y,
        paint
    )
}

private fun DrawScope.drawSingleSticker(stickerObj: StickerObject) {
    val emojiText = getEmojiForStickerAsset(stickerObj.stickerAssetId)
    val paint = AndroidPaint().apply {
        textSize = 64f * stickerObj.scale
        isAntiAlias = true
    }
    drawContext.canvas.nativeCanvas.drawText(
        emojiText,
        stickerObj.x,
        stickerObj.y,
        paint
    )
}

private fun DrawScope.drawPartnerCursor(cursor: CursorPosition, partnerName: String) {
    val cursorColor = Color(0xFFFF4081)
    val position = Offset(cursor.x, cursor.y)

    drawCircle(
        color = cursorColor,
        radius = 8f,
        center = position
    )

    val paint = AndroidPaint().apply {
        color = AndroidColor.WHITE
        textSize = 24f
        isAntiAlias = true
    }
    val bgPaint = AndroidPaint().apply {
        color = cursorColor.toArgb()
        isAntiAlias = true
    }

    val textWidth = paint.measureText(partnerName)
    val bannerLeft = cursor.x + 12f
    val bannerTop = cursor.y - 30f
    val bannerRight = bannerLeft + textWidth + 16f
    val bannerBottom = cursor.y - 6f

    drawContext.canvas.nativeCanvas.drawRoundRect(
        bannerLeft, bannerTop, bannerRight, bannerBottom, 12f, 12f, bgPaint
    )
    drawContext.canvas.nativeCanvas.drawText(
        partnerName,
        bannerLeft + 8f,
        bannerBottom - 6f,
        paint
    )
}

private fun parseColorHex(hex: String, opacity: Float): Color {
    return try {
        val cleanHex = hex.removePrefix("#")
        val argb = when (cleanHex.length) {
            6 -> "FF$cleanHex".toLong(16).toInt()
            8 -> cleanHex.toLong(16).toInt()
            else -> AndroidColor.RED
        }
        Color(argb).copy(alpha = opacity)
    } catch (e: Exception) {
        Color.Red.copy(alpha = opacity)
    }
}

private fun getEmojiForStickerAsset(assetId: String): String {
    return when (assetId) {
        "heart_rose" -> "❤️"
        "heart_sparkle" -> "💖"
        "heart_two" -> "💕"
        "rose" -> "🌹"
        "flower_cherry" -> "🌸"
        "star" -> "⭐"
        "sparkles" -> "✨"
        "bear" -> "🧸"
        "cat_love" -> "😻"
        "cake" -> "🎂"
        "cupcake" -> "🧁"
        "sunset" -> "🌅"
        "love_letter" -> "💌"
        else -> "❤️"
    }
}
