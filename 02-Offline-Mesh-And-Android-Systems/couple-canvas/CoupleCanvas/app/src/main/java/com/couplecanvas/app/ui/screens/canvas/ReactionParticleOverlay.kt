package com.couplecanvas.app.ui.screens.canvas

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.offset
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.scale
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.couplecanvas.app.domain.model.ReactionEvent
import kotlin.math.roundToInt

@Composable
fun ReactionParticleOverlay(
    reactions: List<ReactionEvent>
) {
    Box(modifier = Modifier.fillMaxSize()) {
        reactions.forEach { reaction ->
            SingleParticle(reaction = reaction)
        }
    }
}

@Composable
private fun SingleParticle(reaction: ReactionEvent) {
    val offsetY = remember { Animatable(0f) }
    val alpha = remember { Animatable(1f) }
    val scale = remember { Animatable(0.5f) }

    LaunchedEffect(reaction.id) {
        scale.animateTo(1.4f, animationSpec = tween(300))
        offsetY.animateTo(-250f, animationSpec = tween(1200))
        alpha.animateTo(0f, animationSpec = tween(400))
    }

    Text(
        text = reaction.emoji,
        fontSize = 32.sp,
        modifier = Modifier
            .offset {
                IntOffset(
                    x = reaction.x.roundToInt(),
                    y = (reaction.y + offsetY.value).roundToInt()
                )
            }
            .scale(scale.value)
            .alpha(alpha.value)
    )
}
