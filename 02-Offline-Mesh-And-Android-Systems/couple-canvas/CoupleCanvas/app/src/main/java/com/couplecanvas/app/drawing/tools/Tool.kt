package com.couplecanvas.app.drawing.tools

import com.couplecanvas.app.domain.model.ToolType

data class DrawingToolConfig(
    val type: ToolType = ToolType.PENCIL,
    val colorHex: String = "#FF2B55", // Default romantic crimson rose
    val strokeWidth: Float = 8.0f,
    val opacity: Float = 1.0f
)
