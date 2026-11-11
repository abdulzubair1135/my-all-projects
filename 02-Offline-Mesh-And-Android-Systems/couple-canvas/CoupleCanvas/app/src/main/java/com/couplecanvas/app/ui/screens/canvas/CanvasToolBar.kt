package com.couplecanvas.app.ui.screens.canvas

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Brush
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.FormatColorFill
import androidx.compose.material.icons.filled.Hexagon
import androidx.compose.material.icons.filled.Highlight
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material.icons.filled.Rectangle
import androidx.compose.material.icons.filled.SentimentSatisfied
import androidx.compose.material.icons.filled.TextFields
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.couplecanvas.app.domain.model.ToolType
import com.couplecanvas.app.drawing.tools.DrawingToolConfig
import com.couplecanvas.app.ui.theme.RosePrimary

val PresetColors = listOf(
    "#FF2B55", // Crimson Rose
    "#FF6584", // Hot Pink
    "#FF9800", // Sunset Orange
    "#FFD700", // Gold
    "#4CAF50", // Emerald Green
    "#2196F3", // Sky Blue
    "#9C27B0", // Purple
    "#2C2527", // Warm Charcoal
    "#FFFFFF"  // White
)

@Composable
fun CanvasToolBar(
    config: DrawingToolConfig,
    onToolSelected: (ToolType) -> Unit,
    onColorSelected: (String) -> Unit,
    onStrokeWidthChanged: (Float) -> Unit,
    onStickersClick: () -> Unit,
    onSendReaction: (String) -> Unit,
    onClearCanvasClick: () -> Unit
) {
    var showSizeSlider by remember { mutableStateOf(false) }

    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 12.dp, vertical = 8.dp),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surface,
        shadowElevation = 8.dp
    ) {
        Column(
            modifier = Modifier.padding(12.dp)
        ) {
            // Optional Stroke Size Slider
            if (showSizeSlider) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Size: ${config.strokeWidth.toInt()}",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Slider(
                        value = config.strokeWidth,
                        onValueChange = onStrokeWidthChanged,
                        valueRange = 2f..60f,
                        modifier = Modifier.weight(1f),
                        colors = SliderDefaults.colors(
                            thumbColor = RosePrimary,
                            activeTrackColor = RosePrimary
                        )
                    )
                }
                Spacer(modifier = Modifier.height(8.dp))
            }

            // Quick Emoji Reaction Bar
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                val reactions = listOf("❤️", "💖", "✨", "🌸", "🔥")
                reactions.forEach { emoji ->
                    Text(
                        text = emoji,
                        fontSize = 22.sp,
                        modifier = Modifier
                            .clip(CircleShape)
                            .clickable { onSendReaction(emoji) }
                            .padding(4.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Main Tools Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Pencil Tool
                IconButton(onClick = { onToolSelected(ToolType.PENCIL) }) {
                    Icon(
                        imageVector = Icons.Default.Edit,
                        contentDescription = "Pencil",
                        tint = if (config.type == ToolType.PENCIL) RosePrimary else Color.Gray
                    )
                }

                // Brush Tool
                IconButton(onClick = { onToolSelected(ToolType.BRUSH) }) {
                    Icon(
                        imageVector = Icons.Default.Brush,
                        contentDescription = "Brush",
                        tint = if (config.type == ToolType.BRUSH) RosePrimary else Color.Gray
                    )
                }

                // Highlighter Tool
                IconButton(onClick = { onToolSelected(ToolType.HIGHLIGHTER) }) {
                    Icon(
                        imageVector = Icons.Default.Highlight,
                        contentDescription = "Highlighter",
                        tint = if (config.type == ToolType.HIGHLIGHTER) RosePrimary else Color.Gray
                    )
                }

                // Eraser Tool
                IconButton(onClick = { onToolSelected(ToolType.ERASER) }) {
                    Icon(
                        imageVector = Icons.Default.FormatColorFill,
                        contentDescription = "Eraser",
                        tint = if (config.type == ToolType.ERASER) RosePrimary else Color.Gray
                    )
                }

                // Rectangle Shape
                IconButton(onClick = { onToolSelected(ToolType.RECTANGLE) }) {
                    Icon(
                        imageVector = Icons.Default.Rectangle,
                        contentDescription = "Rectangle",
                        tint = if (config.type == ToolType.RECTANGLE) RosePrimary else Color.Gray
                    )
                }

                // Circle Shape
                IconButton(onClick = { onToolSelected(ToolType.CIRCLE) }) {
                    Icon(
                        imageVector = Icons.Default.RadioButtonUnchecked,
                        contentDescription = "Circle",
                        tint = if (config.type == ToolType.CIRCLE) RosePrimary else Color.Gray
                    )
                }

                // Text Tool
                IconButton(onClick = { onToolSelected(ToolType.TEXT) }) {
                    Icon(
                        imageVector = Icons.Default.TextFields,
                        contentDescription = "Text",
                        tint = if (config.type == ToolType.TEXT) RosePrimary else Color.Gray
                    )
                }

                // Stickers Picker
                IconButton(onClick = onStickersClick) {
                    Icon(
                        imageVector = Icons.Default.SentimentSatisfied,
                        contentDescription = "Stickers",
                        tint = RosePrimary
                    )
                }

                // Size Slider Toggle
                IconButton(onClick = { showSizeSlider = !showSizeSlider }) {
                    Icon(
                        imageVector = Icons.Default.AutoAwesome,
                        contentDescription = "Size",
                        tint = if (showSizeSlider) RosePrimary else Color.Gray
                    )
                }

                // Clear Canvas
                IconButton(onClick = onClearCanvasClick) {
                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = "Clear Canvas",
                        tint = Color.Red.copy(alpha = 0.7f)
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Color Swatch Palette Row
            LazyRow(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                items(PresetColors) { hex ->
                    val color = parseHexColor(hex)
                    val isSelected = config.colorHex.equals(hex, ignoreCase = true)

                    Box(
                        modifier = Modifier
                            .size(28.dp)
                            .clip(CircleShape)
                            .background(color)
                            .border(
                                width = if (isSelected) 3.dp else 1.dp,
                                color = if (isSelected) RosePrimary else Color.LightGray,
                                shape = CircleShape
                            )
                            .clickable { onColorSelected(hex) }
                    )
                }
            }
        }
    }
}

private fun parseHexColor(hex: String): Color {
    return try {
        val cleanHex = hex.removePrefix("#")
        val argb = when (cleanHex.length) {
            6 -> "FF$cleanHex".toLong(16).toInt()
            8 -> cleanHex.toLong(16).toInt()
            else -> android.graphics.Color.RED
        }
        Color(argb)
    } catch (e: Exception) {
        Color.Red
    }
}
