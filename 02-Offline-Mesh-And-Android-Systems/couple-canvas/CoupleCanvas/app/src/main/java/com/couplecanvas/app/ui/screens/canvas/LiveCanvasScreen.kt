package com.couplecanvas.app.ui.screens.canvas

import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp
import com.couplecanvas.app.domain.model.ChatMessage
import com.couplecanvas.app.domain.model.ConnectionState
import com.couplecanvas.app.domain.model.CursorPosition
import com.couplecanvas.app.domain.model.ReactionEvent
import com.couplecanvas.app.domain.model.Stroke
import com.couplecanvas.app.domain.model.ToolType
import com.couplecanvas.app.drawing.engine.DrawingEngine
import com.couplecanvas.app.drawing.renderer.ComposeCanvasRenderer
import com.couplecanvas.app.ui.theme.PinkPrimary

@Composable
fun LiveCanvasScreen(
    roomCode: String,
    partnerName: String?,
    partnerJoined: Boolean = false,
    connectionState: ConnectionState,
    drawingEngine: DrawingEngine,
    partnerCursor: CursorPosition?,
    partnerActiveStroke: Stroke?,
    reactions: List<ReactionEvent>,
    chatMessages: List<ChatMessage>,
    currentUserId: String,
    onSendReaction: (String) -> Unit,
    onSendChatMessage: (String) -> Unit,
    onSaveDrawing: (title: String) -> Unit,
    onShareRoomClick: () -> Unit = {},
    onBackClick: () -> Unit
) {
    val operations by drawingEngine.operations.collectAsState()
    val toolConfig by drawingEngine.toolConfig.collectAsState()
    val activeLocalStroke by drawingEngine.currentActiveStroke.collectAsState()
    val activeLocalShape by drawingEngine.currentActiveShape.collectAsState()

    var scale by remember { mutableStateOf(1.0f) }
    var offset by remember { mutableStateOf(Offset.Zero) }

    var showStickerSheet by remember { mutableStateOf(false) }
    var showChatSheet by remember { mutableStateOf(false) }
    var showSaveDialog by remember { mutableStateOf(false) }
    var drawingTitleInput by remember { mutableStateOf("Our Creation ❤️") }
    var textInputPosition by remember { mutableStateOf<Offset?>(null) }
    var showTextInputDialog by remember { mutableStateOf(false) }
    var textValue by remember { mutableStateOf("") }

    Scaffold(
        topBar = {
            CanvasTopBar(
                roomCode = roomCode,
                partnerName = partnerName,
                partnerJoined = partnerJoined,
                connectionState = connectionState,
                onShareRoomClick = onShareRoomClick,
                onUndoClick = { drawingEngine.undo() },
                onRedoClick = { drawingEngine.redo() },
                onSaveClick = { showSaveDialog = true },
                onChatClick = { showChatSheet = true },
                onBackClick = onBackClick
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(MaterialTheme.colorScheme.background)
        ) {
            ComposeCanvasRenderer(
                operations = operations,
                activeLocalStroke = activeLocalStroke,
                activeLocalShape = activeLocalShape,
                activePartnerStroke = partnerActiveStroke,
                partnerCursor = partnerCursor,
                partnerName = partnerName,
                scale = scale,
                offset = offset,
                toolConfig = toolConfig,
                drawingEngine = drawingEngine,
                onTransform = { zoom, pan ->
                    scale = (scale * zoom).coerceIn(0.5f, 5.0f)
                    offset += pan
                },
                onTextTap = { pos ->
                    textInputPosition = pos
                    showTextInputDialog = true
                },
                modifier = Modifier.fillMaxSize()
            )

            ReactionParticleOverlay(reactions = reactions)

            Box(
                modifier = Modifier.align(Alignment.BottomCenter)
            ) {
                CanvasToolBar(
                    config = toolConfig,
                    onToolSelected = { type -> drawingEngine.setToolType(type) },
                    onColorSelected = { hex -> drawingEngine.setColor(hex) },
                    onStrokeWidthChanged = { width -> drawingEngine.setStrokeWidth(width) },
                    onStickersClick = { showStickerSheet = true },
                    onSendReaction = onSendReaction,
                    onClearCanvasClick = { drawingEngine.clearCanvas() }
                )
            }
        }
    }

    if (showStickerSheet) {
        StickerPickerBottomSheet(
            onDismissRequest = { showStickerSheet = false },
            onStickerSelected = { assetId, category ->
                drawingEngine.addSticker(assetId, category, x = 300f, y = 400f)
            }
        )
    }

    if (showChatSheet) {
        MiniChatBottomSheet(
            messages = chatMessages,
            currentUserId = currentUserId,
            onSendMessage = onSendChatMessage,
            onDismissRequest = { showChatSheet = false }
        )
    }

    if (showSaveDialog) {
        AlertDialog(
            onDismissRequest = { showSaveDialog = false },
            title = { Text("Save Artwork Locally ❤️") },
            text = {
                Column {
                    Text("Enter a title for your shared drawing gallery:")
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(
                        value = drawingTitleInput,
                        onValueChange = { drawingTitleInput = it },
                        singleLine = true
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        onSaveDrawing(drawingTitleInput.ifEmpty { "Our Creation" })
                        showSaveDialog = false
                    }
                ) {
                    Text("Save", color = PinkPrimary)
                }
            },
            dismissButton = {
                TextButton(onClick = { showSaveDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }

    if (showTextInputDialog) {
        AlertDialog(
            onDismissRequest = { showTextInputDialog = false },
            title = { Text("Add Text to Canvas") },
            text = {
                OutlinedTextField(
                    value = textValue,
                    onValueChange = { textValue = it },
                    placeholder = { Text("Type something sweet...") },
                    singleLine = true
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        val pos = textInputPosition ?: Offset(100f, 100f)
                        if (textValue.trim().isNotEmpty()) {
                            drawingEngine.addText(textValue.trim(), pos.x, pos.y)
                        }
                        textValue = ""
                        showTextInputDialog = false
                    }
                ) {
                    Text("Add", color = PinkPrimary)
                }
            },
            dismissButton = {
                TextButton(onClick = { showTextInputDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}
