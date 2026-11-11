package com.projectx2.porncontroller.features.splash

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.projectx2.porncontroller.core.theme.*
import com.projectx2.porncontroller.utils.IntroAudioPlayer
import kotlinx.coroutines.delay

@Composable
fun SplashScreen(
    onSplashFinished: () -> Unit
) {
    var startAnimation by remember { mutableStateOf(false) }

    val scaleAnim = animateFloatAsState(
        targetValue = if (startAnimation) 1f else 0.6f,
        animationSpec = spring(dampingRatio = 0.6f, stiffness = Spring.StiffnessLow),
        label = "scale"
    )

    val alphaAnim = animateFloatAsState(
        targetValue = if (startAnimation) 1f else 0f,
        animationSpec = tween(durationMillis = 800),
        label = "alpha"
    )

    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseGlow by infiniteTransition.animateFloat(
        initialValue = 0.95f,
        targetValue = 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow"
    )

    LaunchedEffect(Unit) {
        startAnimation = true
        IntroAudioPlayer.playIntroChime()
        delay(2200L)
        onSplashFinished()
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(NeoCanvasBackground),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier
                .scale(scaleAnim.value)
                .alpha(alphaAnim.value)
        ) {
            // 3D Neomorphic Emblem
            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier
                    .size(110.dp)
                    .scale(pulseGlow)
            ) {
                Neo3DCard(
                    modifier = Modifier.size(90.dp),
                    shape = RoundedCornerShape(24.dp),
                    backgroundColor = NeoSurfaceWhite,
                    borderColor = NeoBorderBlack,
                    borderWidth = 2.5.dp,
                    extrusionOffset = 5.dp,
                    extrusionColor = NeoBorderBlack
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Shield,
                            contentDescription = "Shield Logo",
                            tint = NeoRedAccent,
                            modifier = Modifier.size(52.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(28.dp))

            // Main Brand Title
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "P.RN ",
                    fontSize = 34.sp,
                    fontWeight = FontWeight.Black,
                    fontFamily = FontFamily.Monospace,
                    color = NeoRedAccent,
                    letterSpacing = 2.sp
                )
                Text(
                    text = "CTRL",
                    fontSize = 34.sp,
                    fontWeight = FontWeight.Black,
                    fontFamily = FontFamily.Monospace,
                    color = NeoBorderBlack,
                    letterSpacing = 2.sp
                )
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Brand Subtitle: made by projectX² (Neomorphic 3D Pill)
            Neo3DCard(
                modifier = Modifier.wrapContentSize(),
                shape = RoundedCornerShape(20.dp),
                backgroundColor = NeoSurfaceWhite,
                borderColor = NeoBorderBlack,
                borderWidth = 2.dp,
                extrusionOffset = 3.dp,
                extrusionColor = NeoBorderBlack
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = "made by ",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold,
                        color = NeoTextMuted
                    )
                    Text(
                        text = "projectX",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Black,
                        color = NeoTextBlack
                    )
                    Text(
                        text = "²",
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Black,
                        color = NeoRedAccent
                    )
                }
            }

            Spacer(modifier = Modifier.height(18.dp))

            Text(
                text = "Offline Self-Control & Protection",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = NeoTextMuted,
                letterSpacing = 0.5.sp
            )
        }
    }
}
