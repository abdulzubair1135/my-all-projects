package com.couplecanvas.app.ui.screens.canvas

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Redo
import androidx.compose.material.icons.filled.Save
import androidx.compose.material.icons.filled.Undo
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.couplecanvas.app.domain.model.ConnectionState
import com.couplecanvas.app.ui.theme.RosePrimary

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CanvasTopBar(
    roomCode: String,
    partnerName: String?,
    partnerJoined: Boolean = false,
    connectionState: ConnectionState,
    onShareRoomClick: () -> Unit = {},
    onUndoClick: () -> Unit,
    onRedoClick: () -> Unit,
    onSaveClick: () -> Unit,
    onChatClick: () -> Unit,
    onBackClick: () -> Unit
) {
    TopAppBar(
        title = {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // Connection Indicator Status Dot
                val dotColor = when {
                    partnerJoined && connectionState == ConnectionState.CONNECTED -> Color(0xFF10B981) // Green
                    connectionState == ConnectionState.CONNECTING || connectionState == ConnectionState.RECONNECTING -> Color(0xFFF59E0B) // Amber
                    partnerJoined && connectionState == ConnectionState.DISCONNECTED -> Color(0xFFEF4444) // Red
                    else -> Color(0xFF3B82F6) // Solo Blue
                }

                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .clip(CircleShape)
                        .background(dotColor)
                )

                Spacer(modifier = Modifier.width(8.dp))

                val statusText = when {
                    partnerJoined && connectionState == ConnectionState.CONNECTED -> "🟢 ${partnerName ?: "Partner"} Online"
                    partnerJoined && connectionState == ConnectionState.CONNECTING -> "🟡 Connecting..."
                    partnerJoined && connectionState == ConnectionState.DISCONNECTED -> "🔴 Partner Offline"
                    else -> "🎨 Solo (Code: $roomCode)"
                }

                Text(
                    text = statusText,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onBackground
                )
            }
        },
        navigationIcon = {
            IconButton(onClick = onBackClick) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
            }
        },
        actions = {
            IconButton(onClick = onShareRoomClick) {
                Icon(Icons.Default.Favorite, contentDescription = "Share Room", tint = RosePrimary)
            }
            IconButton(onClick = onUndoClick) {
                Icon(Icons.Default.Undo, contentDescription = "Undo")
            }
            IconButton(onClick = onRedoClick) {
                Icon(Icons.Default.Redo, contentDescription = "Redo")
            }
            IconButton(onClick = onChatClick) {
                Icon(Icons.Default.Chat, contentDescription = "Chat", tint = RosePrimary)
            }
            IconButton(onClick = onSaveClick) {
                Icon(Icons.Default.Save, contentDescription = "Save Drawing", tint = RosePrimary)
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = MaterialTheme.colorScheme.background.copy(alpha = 0.95f)
        )
    )
}
