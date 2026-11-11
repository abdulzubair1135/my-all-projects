package com.projectx2.porncontroller.features.intervention

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.projectx2.porncontroller.core.theme.*

@Composable
fun InterventionScreen(
    triggerSource: String,
    message: String,
    category: String,
    onReturnToWork: () -> Unit,
    onTakeBreak: () -> Unit,
    onCompleteTask: () -> Unit,
    onDismiss: () -> Unit
) {
    // Pulsing alert animation
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 0.95f,
        targetValue = 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseScale"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(NeoCanvasBackground),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // 3D Neomorphic Alert Shield
            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier
                    .size(96.dp)
                    .scale(pulseScale)
            ) {
                Neo3DCard(
                    modifier = Modifier.size(80.dp),
                    shape = RoundedCornerShape(22.dp),
                    backgroundColor = NeoSurfaceWhite,
                    borderColor = NeoBorderBlack,
                    borderWidth = 2.dp,
                    extrusionOffset = 4.dp,
                    extrusionColor = NeoBorderBlack
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.WarningAmber,
                            contentDescription = "Alert",
                            tint = NeoRedAccent,
                            modifier = Modifier.size(46.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // 3D Brand Badge
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "P.RN CTRL",
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Black,
                    fontSize = 14.sp,
                    color = NeoRedAccent
                )
                Spacer(modifier = Modifier.width(6.dp))
                Neo3DBadge(
                    text = "SENSOR ACTIVE",
                    textColor = NeoRedAccent,
                    backgroundColor = NeoSurfaceWhite
                )
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Main Intervention Title
            Text(
                text = "PAUSE & REFLECT",
                fontSize = 24.sp,
                fontWeight = FontWeight.Black,
                letterSpacing = 1.sp,
                color = NeoTextBlack
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Trigger Keyword Badge (Red text + Black border)
            if (triggerSource.isNotBlank()) {
                Neo3DBadge(
                    text = "TRIGGER: \"$triggerSource\"",
                    textColor = NeoRedAccent,
                    backgroundColor = NeoSurfaceWhite
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            // 3D Neomorphic Message Box: Pure White + 2.dp Black Border + 3D Extrusion
            Neo3DCard(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(18.dp),
                backgroundColor = NeoSurfaceWhite,
                borderColor = NeoBorderBlack,
                borderWidth = 2.dp,
                extrusionOffset = 4.dp,
                extrusionColor = NeoBorderBlack
            ) {
                Text(
                    text = "\"$message\"",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    lineHeight = 24.sp,
                    textAlign = TextAlign.Center,
                    color = NeoTextBlack,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp)
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            // 3D Neomorphic Action Buttons
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Primary Action: Return to Home
                Neo3DButton(
                    text = "Return to Home Screen",
                    onClick = onReturnToWork,
                    isRedAccent = true,
                    icon = {
                        Icon(
                            imageVector = Icons.Default.Home,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                )

                // Secondary Action: Replacement Task
                Neo3DButton(
                    text = "Complete a Replacement Task",
                    onClick = onCompleteTask,
                    containerColor = NeoSurfaceWhite,
                    textColor = NeoTextBlack,
                    icon = {
                        Icon(
                            imageVector = Icons.Default.SelfImprovement,
                            contentDescription = null,
                            tint = NeoRedAccent,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                )

                // Two side-by-side 3D buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Box(modifier = Modifier.weight(1f)) {
                        Neo3DButton(
                            text = "5m Break",
                            onClick = onTakeBreak,
                            containerColor = NeoSurfaceWhite,
                            textColor = NeoTextBlack,
                            icon = {
                                Icon(
                                    imageVector = Icons.Default.Coffee,
                                    contentDescription = null,
                                    tint = NeoRedAccent,
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        )
                    }

                    Box(modifier = Modifier.weight(1f)) {
                        Neo3DButton(
                            text = "Dismiss to Home",
                            onClick = onDismiss,
                            containerColor = NeoSurfaceWhite,
                            textColor = NeoRedAccent,
                            icon = {
                                Icon(
                                    imageVector = Icons.Default.Close,
                                    contentDescription = null,
                                    tint = NeoRedAccent,
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        )
                    }
                }
            }
        }
    }
}
