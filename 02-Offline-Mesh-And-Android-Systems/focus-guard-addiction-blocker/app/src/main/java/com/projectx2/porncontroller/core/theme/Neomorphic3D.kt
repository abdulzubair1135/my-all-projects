package com.projectx2.porncontroller.core.theme

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * Authentic 3D Neomorphic Extruded Card.
 * Renders a crisp 3D solid black offset extrusion shadow under a pure white surface
 * with a high-contrast 2.dp solid black border.
 */
@Composable
fun Neo3DCard(
    modifier: Modifier = Modifier,
    shape: Shape = RoundedCornerShape(20.dp),
    backgroundColor: Color = NeoSurfaceWhite,
    borderColor: Color = NeoBorderBlack,
    borderWidth: Dp = 2.dp,
    extrusionOffset: Dp = 4.dp,
    extrusionColor: Color = NeoBorderBlack,
    onClick: (() -> Unit)? = null,
    content: @Composable BoxScope.() -> Unit
) {
    Box(
        modifier = modifier.then(
            if (onClick != null) {
                Modifier.clickable(
                    interactionSource = remember { MutableInteractionSource() },
                    indication = null,
                    onClick = onClick
                )
            } else Modifier
        )
    ) {
        // 1. Bottom 3D solid extrusion block
        Box(
            modifier = Modifier
                .matchParentSize()
                .offset(x = extrusionOffset, y = extrusionOffset)
                .clip(shape)
                .background(extrusionColor)
        )

        // 2. Foreground pure white tactile surface with 2.dp black border
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .clip(shape)
                .background(backgroundColor)
                .border(borderWidth, borderColor, shape),
            content = content
        )
    }
}

/**
 * 3D Tactile Neomorphic Button with solid black border & extrusion.
 */
@Composable
fun Neo3DButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    containerColor: Color = NeoSurfaceWhite,
    textColor: Color = NeoTextBlack,
    isRedAccent: Boolean = false,
    icon: (@Composable () -> Unit)? = null
) {
    val finalContainer = if (isRedAccent) NeoRedAccent else containerColor
    val finalTextColor = if (isRedAccent) Color.White else textColor

    Neo3DCard(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        backgroundColor = finalContainer,
        borderColor = NeoBorderBlack,
        borderWidth = 2.dp,
        extrusionOffset = 3.5.dp,
        extrusionColor = NeoBorderBlack,
        onClick = onClick
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 14.dp, horizontal = 18.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            if (icon != null) {
                icon()
                Spacer(modifier = Modifier.width(8.dp))
            }
            Text(
                text = text,
                fontSize = 15.sp,
                fontWeight = FontWeight.Bold,
                color = finalTextColor
            )
        }
    }
}

/**
 * 3D Tactile Status Badge (e.g., "ACTIVE", "SHIELD", "1 DAY STRONG")
 * Solid black border + white surface + bold Crimson Red text.
 */
@Composable
fun Neo3DBadge(
    text: String,
    modifier: Modifier = Modifier,
    textColor: Color = NeoRedAccent,
    backgroundColor: Color = NeoSurfaceWhite
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(backgroundColor)
            .border(1.5.dp, NeoBorderBlack, RoundedCornerShape(8.dp))
            .padding(horizontal = 8.dp, vertical = 3.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            fontSize = 11.sp,
            fontWeight = FontWeight.Black,
            fontFamily = FontFamily.Monospace,
            letterSpacing = 0.5.sp,
            color = textColor
        )
    }
}
