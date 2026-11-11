package com.couplecanvas.app.ui.navigation

import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.WifiOff
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.google.gson.Gson
import com.couplecanvas.app.CoupleCanvasApplication
import com.couplecanvas.app.data.repository.DrawingRepository
import com.couplecanvas.app.domain.model.CanvasOperation
import com.couplecanvas.app.domain.model.ChatMessage
import com.couplecanvas.app.domain.model.ConnectionState
import com.couplecanvas.app.domain.model.CursorPosition
import com.couplecanvas.app.domain.model.Drawing
import com.couplecanvas.app.domain.model.MessageType
import com.couplecanvas.app.domain.model.ReactionEvent
import com.couplecanvas.app.domain.model.RealtimeMessage
import com.couplecanvas.app.domain.model.Stroke
import com.couplecanvas.app.drawing.engine.DrawingEngine
import com.couplecanvas.app.realtime.protocol.RealtimeProtocol
import com.couplecanvas.app.realtime.signaling.SignalingClient
import com.couplecanvas.app.realtime.webrtc.WebRTCManager
import com.couplecanvas.app.ui.screens.auth.PhoneAuthScreen
import com.couplecanvas.app.ui.screens.chat.DirectChatScreen
import com.couplecanvas.app.ui.screens.challenge.DailyChallengeScreen
import com.couplecanvas.app.ui.screens.gallery.ArtworkDetailScreen
import com.couplecanvas.app.ui.screens.gallery.GalleryScreen
import com.couplecanvas.app.ui.screens.home.HomeScreen
import com.couplecanvas.app.ui.screens.onboarding.OnboardingScreen
import com.couplecanvas.app.ui.screens.privacy.PrivacyPolicyScreen
import com.couplecanvas.app.ui.screens.profile.ProfileScreen
import com.couplecanvas.app.ui.screens.report.ReportBlockScreen
import com.couplecanvas.app.ui.screens.room.CreateRoomScreen
import com.couplecanvas.app.ui.screens.room.JoinRoomScreen
import com.couplecanvas.app.ui.screens.settings.SettingsScreen
import com.couplecanvas.app.ui.screens.splash.SplashScreen
import com.couplecanvas.app.ui.screens.canvas.LiveCanvasScreen
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.webrtc.IceCandidate
import org.webrtc.SessionDescription
import java.util.UUID

fun generateRandomRoomCode(): String {
    val chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return (1..6).map { chars.random() }.joinToString("")
}

@Composable
fun NavGraph(
    navController: NavHostController,
    app: CoupleCanvasApplication,
    deepLinkRoomCode: String? = null
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val prefsRepo = app.userPreferencesRepository
    val drawingDao = app.database.drawingDao()
    val drawingRepo = remember { DrawingRepository(context, drawingDao) }

    val userId by prefsRepo.userId.collectAsState(initial = "CC-LOCAL")
    val userName by prefsRepo.displayName.collectAsState(initial = "Artist")
    val userPhone by prefsRepo.phoneNumber.collectAsState(initial = "")
    val partnerPhonePref by prefsRepo.partnerPhone.collectAsState(initial = "")
    val partnerNamePref by prefsRepo.partnerName.collectAsState(initial = "")
    val serverUrl by prefsRepo.signalingServerUrl.collectAsState(initial = "wss://psychological-streams-centres-fell.trycloudflare.com")
    val isDarkMode by prefsRepo.isDarkMode.collectAsState(initial = false)
    val isHaptic by prefsRepo.isHapticEnabled.collectAsState(initial = true)

    val recentDrawings by drawingRepo.allDrawings.collectAsState(initial = emptyList())
    val directChatMessages = remember { mutableStateListOf<ChatMessage>() }

    // Core Managers
    val gson = remember { Gson() }
    val protocol = remember { RealtimeProtocol(gson) }
    val drawingEngine = remember { DrawingEngine().apply { initialize(userId) } }
    val webrtcManager = remember { WebRTCManager(context) }
    val signalingClient = remember { SignalingClient(serverUrl, gson) }

    LaunchedEffect(serverUrl) {
        signalingClient.updateServerUrl(serverUrl)
    }

    // Realtime Room State
    var activeRoomCode by remember { mutableStateOf("") }
    var partnerJoined by remember { mutableStateOf(false) }
    var partnerName by remember { mutableStateOf<String?>(null) }
    var partnerUserId by remember { mutableStateOf<String?>(null) }
    val rtcConnectionState by webrtcManager.connectionState.collectAsState()

    var partnerCursor by remember { mutableStateOf<CursorPosition?>(null) }
    var partnerActiveStroke by remember { mutableStateOf<Stroke?>(null) }
    val reactions = remember { mutableStateListOf<ReactionEvent>() }
    val chatMessages = remember { mutableStateListOf<ChatMessage>() }

    // Auth UI state
    var authIsLoading by remember { mutableStateOf(false) }
    var authServerError by remember { mutableStateOf<String?>(null) }

    // Join failure state (room not found / host offline)
    var joinFailedReason by remember { mutableStateOf<String?>(null) }

    // Deep link auto-join handler
    LaunchedEffect(deepLinkRoomCode) {
        if (!deepLinkRoomCode.isNullOrBlank()) {
            activeRoomCode = deepLinkRoomCode
            signalingClient.connect()
            signalingClient.send(
                RealtimeMessage(
                    type = MessageType.JOIN_ROOM,
                    roomId = deepLinkRoomCode,
                    userId = userId,
                    payloadJson = userName
                )
            )
            navController.navigate(Screen.Canvas.createRoute(deepLinkRoomCode, false))
        }
    }

    // Signaling WebSocket listener setup
    LaunchedEffect(signalingClient) {
        signalingClient.messages.collectLatest { msg ->
            if (msg.userId == userId) return@collectLatest // Ignore self messages

            when (msg.type) {
                MessageType.ROOM_CREATED -> {
                    msg.roomId?.let { activeRoomCode = it }
                }
                MessageType.ROOM_JOINED -> {
                    msg.roomId?.let { activeRoomCode = it }
                    partnerJoined = true
                }
                MessageType.PARTNER_JOINED -> {
                    partnerJoined = true
                    partnerName = msg.payloadJson ?: msg.userId ?: "Partner"
                    webrtcManager.createPeerConnection()
                    webrtcManager.initHostDataChannel()
                    webrtcManager.createOffer()

                    // Solo-to-Live stroke synchronization: Send all existing operations to joining partner
                    drawingEngine.operations.value.forEach { op ->
                        val syncMsg = protocol.wrapOperation(op, activeRoomCode, userId)
                        signalingClient.send(syncMsg)
                    }
                }
                MessageType.OFFER -> {
                    msg.payloadJson?.let { sdpText ->
                        val sdp = SessionDescription(SessionDescription.Type.OFFER, sdpText)
                        webrtcManager.createPeerConnection()
                        webrtcManager.setRemoteDescription(sdp)
                        webrtcManager.createAnswer()
                    }
                }
                MessageType.ANSWER -> {
                    msg.payloadJson?.let { sdpText ->
                        val sdp = SessionDescription(SessionDescription.Type.ANSWER, sdpText)
                        webrtcManager.setRemoteDescription(sdp)
                    }
                }
                MessageType.ICE_CANDIDATE -> {
                    msg.payloadJson?.let { candJson ->
                        val cand = gson.fromJson(candJson, IceCandidate::class.java)
                        webrtcManager.addRemoteIceCandidate(cand)
                    }
                }
                MessageType.PARTNER_DISCONNECTED -> {
                    partnerJoined = false
                }
                MessageType.JOIN_FAILED -> {
                    // Room not found or host not online — pop back and show error
                    val reason = msg.payloadJson ?: "ROOM_NOT_FOUND"
                    joinFailedReason = when {
                        reason.contains("ROOM_NOT_FOUND") -> "Room not found or expired. Ask your partner to create a new room."
                        reason.contains("ROOM_FULL") -> "This room already has 2 people. Please join a different room."
                        else -> "Could not join room: $reason"
                    }
                    navController.popBackStack()
                }
                MessageType.ERROR -> {
                    val errorText = msg.payloadJson ?: "Unknown server error"
                    joinFailedReason = "Server error: $errorText"
                }
                MessageType.CURSOR_MOVE -> {
                    partnerCursor = protocol.parseCursor(msg)
                }
                MessageType.REACTION -> {
                    protocol.parseReaction(msg)?.let { reaction ->
                        reactions.add(reaction)
                    }
                }
                MessageType.CHAT_MESSAGE -> {
                    protocol.parseChat(msg)?.let { chat ->
                        chatMessages.add(chat)
                    }
                }
                else -> {
                    protocol.parseOperation(msg)?.let { op ->
                        drawingEngine.applyOperation(op, isLocal = false)
                    }
                }
            }
        }
    }

    // WebRTC Candidate & SDP callbacks
    webrtcManager.onIceCandidateGenerated = { cand ->
        signalingClient.send(
            RealtimeMessage(
                type = MessageType.ICE_CANDIDATE,
                roomId = activeRoomCode,
                userId = userId,
                payloadJson = gson.toJson(cand)
            )
        )
    }

    webrtcManager.onLocalSdpGenerated = { sdp ->
        val type = if (sdp.type == SessionDescription.Type.OFFER) MessageType.OFFER else MessageType.ANSWER
        signalingClient.send(
            RealtimeMessage(
                type = type,
                roomId = activeRoomCode,
                userId = userId,
                payloadJson = sdp.description
            )
        )
    }

    // WebRTC DataChannel message listener
    LaunchedEffect(webrtcManager) {
        webrtcManager.incomingDataChannelMessages.collectLatest { text ->
            val msg = protocol.deserialize(text) ?: return@collectLatest
            if (msg.userId == userId) return@collectLatest
            when (msg.type) {
                MessageType.CURSOR_MOVE -> {
                    partnerCursor = protocol.parseCursor(msg)
                }
                MessageType.REACTION -> {
                    protocol.parseReaction(msg)?.let { reaction ->
                        reactions.add(reaction)
                    }
                }
                MessageType.CHAT_MESSAGE -> {
                    protocol.parseChat(msg)?.let { chat ->
                        chatMessages.add(chat)
                    }
                }
                else -> {
                    protocol.parseOperation(msg)?.let { op ->
                        drawingEngine.applyOperation(op, isLocal = false)
                    }
                }
            }
        }
    }

    drawingEngine.onLocalOperationCommitted = { op ->
        val msg = protocol.wrapOperation(op, activeRoomCode, userId)
        val json = protocol.serialize(msg)
        val sentDataChannel = webrtcManager.sendData(json)
        if (!sentDataChannel) {
            signalingClient.send(msg)
        }
    }

    drawingEngine.onCursorMoved = { x, y, isDrawing ->
        val cursor = CursorPosition(userId = userId, x = x, y = y, isDrawing = isDrawing)
        val msg = protocol.wrapCursor(cursor, activeRoomCode)
        val sentDataChannel = webrtcManager.sendData(protocol.serialize(msg))
        if (!sentDataChannel) {
            signalingClient.send(msg)
        }
    }

    // Global join failure dialog
    if (joinFailedReason != null) {
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { joinFailedReason = null },
            title = {
                androidx.compose.foundation.layout.Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                    androidx.compose.material3.Icon(
                        androidx.compose.material.icons.Icons.Default.WifiOff,
                        contentDescription = null,
                        tint = com.couplecanvas.app.ui.theme.PinkPrimary
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    androidx.compose.material3.Text(
                        "Cannot Join Room",
                        fontWeight = FontWeight.Bold,
                        color = com.couplecanvas.app.ui.theme.SlateDark
                    )
                }
            },
            text = {
                androidx.compose.material3.Text(
                    joinFailedReason ?: "",
                    color = com.couplecanvas.app.ui.theme.SlateSub,
                    fontSize = 14.sp
                )
            },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { joinFailedReason = null }) {
                    androidx.compose.material3.Text("OK", color = com.couplecanvas.app.ui.theme.PinkPrimary, fontWeight = FontWeight.Bold)
                }
            },
            containerColor = com.couplecanvas.app.ui.theme.CleanWhite
        )
    }

    NavHost(
        navController = navController,
        startDestination = Screen.Splash.route
    ) {
        composable(Screen.Splash.route) {
            SplashScreen(
                onNavigateToNext = {
                    if (userPhone.isBlank()) {
                        navController.navigate(Screen.PhoneAuth.route) {
                            popUpTo(Screen.Splash.route) { inclusive = true }
                        }
                    } else {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Splash.route) { inclusive = true }
                        }
                    }
                }
            )
        }

        composable(Screen.PhoneAuth.route) {
            PhoneAuthScreen(
                initialPhone = userPhone,
                initialName = userName,
                isLoading = authIsLoading,
                serverError = authServerError,
                onServerErrorDismiss = { authServerError = null },
                onAuthComplete = { phone, name ->
                    authIsLoading = true
                    scope.launch {
                        // Save locally first — user can use app offline
                        prefsRepo.savePhoneNumber(phone)
                        prefsRepo.saveDisplayName(name)
                        authIsLoading = false
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.PhoneAuth.route) { inclusive = true }
                        }
                        // Sync to server in background (non-blocking)
                        try {
                            sendPhoneAuthRequest(serverUrl, phone, name)
                        } catch (e: Exception) {
                            // Server sync failed — data is saved locally, user can still use app
                            // We'll show a toast/indicator next time they open settings
                            e.printStackTrace()
                        }
                    }
                }
            )
        }

        composable(Screen.Onboarding.route) {
            OnboardingScreen(
                onCompleteOnboarding = { name ->
                    scope.launch { prefsRepo.saveDisplayName(name) }
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Onboarding.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.Home.route) {
            HomeScreen(
                userName = userName,
                recentDrawings = recentDrawings,
                onStartSoloClick = {
                    val code = generateRandomRoomCode()
                    activeRoomCode = code
                    partnerJoined = false
                    drawingEngine.clearCanvas()
                    signalingClient.connect()
                    signalingClient.send(
                        RealtimeMessage(
                            type = MessageType.CREATE_ROOM,
                            roomId = code,
                            userId = userId,
                            payloadJson = userName
                        )
                    )
                    navController.navigate(Screen.Canvas.createRoute(code, true))
                },
                onCreateRoomClick = {
                    val code = generateRandomRoomCode()
                    activeRoomCode = code
                    partnerJoined = false
                    signalingClient.connect()
                    signalingClient.send(
                        RealtimeMessage(
                            type = MessageType.CREATE_ROOM,
                            roomId = code,
                            userId = userId,
                            payloadJson = userName
                        )
                    )
                    navController.navigate(Screen.CreateRoom.route)
                },
                onJoinRoomClick = {
                    signalingClient.connect()
                    navController.navigate(Screen.JoinRoom.route)
                },
                onDirectChatClick = {
                    navController.navigate(Screen.DirectChat.route)
                },
                onGalleryClick = { navController.navigate(Screen.Gallery.route) },
                onChallengeClick = { navController.navigate(Screen.DailyChallenge.route) },
                onProfileClick = { navController.navigate(Screen.Profile.route) },
                onSettingsClick = { navController.navigate(Screen.Settings.route) },
                onDrawingClick = { id -> navController.navigate(Screen.ArtworkDetail.createRoute(id)) }
            )
        }

        composable(Screen.DirectChat.route) {
            DirectChatScreen(
                userPhone = userPhone,
                partnerPhone = partnerPhonePref,
                partnerName = partnerNamePref,
                messages = directChatMessages,
                onSendMessage = { text ->
                    val chat = ChatMessage(id = UUID.randomUUID().toString(), senderUserId = userPhone, senderName = "Me", text = text)
                    directChatMessages.add(chat)
                    scope.launch {
                        sendDirectChatMessageApi(serverUrl, userPhone, partnerPhonePref, text)
                    }
                },
                onAddPartnerSubmitted = { newPartnerPhone ->
                    scope.launch {
                        val resultName = addPartnerApi(serverUrl, userPhone, newPartnerPhone)
                        prefsRepo.savePartnerInfo(newPartnerPhone, resultName)
                    }
                },
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(Screen.CreateRoom.route) {
            val validCode = if (activeRoomCode.isBlank()) generateRandomRoomCode().also { activeRoomCode = it } else activeRoomCode
            CreateRoomScreen(
                roomCode = validCode,
                partnerJoined = partnerJoined,
                onStartDrawingClick = {
                    navController.navigate(Screen.Canvas.createRoute(validCode, true))
                },
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(Screen.JoinRoom.route) {
            JoinRoomScreen(
                onJoinRoomSubmitted = { code ->
                    val cleanCode = code.trim().uppercase()
                    activeRoomCode = cleanCode
                    signalingClient.connect()
                    signalingClient.send(
                        RealtimeMessage(
                            type = MessageType.JOIN_ROOM,
                            roomId = cleanCode,
                            userId = userId,
                            payloadJson = userName
                        )
                    )
                    navController.navigate(Screen.Canvas.createRoute(cleanCode, false))
                },
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(
            route = Screen.Canvas.route,
            arguments = listOf(
                navArgument("roomCode") { type = NavType.StringType },
                navArgument("isHost") { type = NavType.BoolType }
            )
        ) { backStackEntry ->
            val roomCodeArg = backStackEntry.arguments?.getString("roomCode") ?: activeRoomCode.ifEmpty { "SOLO" }

            LiveCanvasScreen(
                roomCode = roomCodeArg,
                partnerName = partnerName,
                partnerJoined = partnerJoined,
                connectionState = rtcConnectionState,
                drawingEngine = drawingEngine,
                partnerCursor = partnerCursor,
                partnerActiveStroke = partnerActiveStroke,
                reactions = reactions,
                chatMessages = chatMessages,
                currentUserId = userId,
                onSendReaction = { emoji ->
                    val reaction = ReactionEvent(
                        id = UUID.randomUUID().toString(),
                        userId = userId,
                        emoji = emoji,
                        x = 200f,
                        y = 400f
                    )
                    reactions.add(reaction)
                    val msg = protocol.wrapReaction(reaction, roomCodeArg)
                    webrtcManager.sendData(protocol.serialize(msg))
                },
                onSendChatMessage = { text ->
                    val chat = ChatMessage(
                        id = UUID.randomUUID().toString(),
                        senderUserId = userId,
                        senderName = userName,
                        text = text
                    )
                    chatMessages.add(chat)
                    val msg = protocol.wrapChat(chat, roomCodeArg)
                    webrtcManager.sendData(protocol.serialize(msg))
                },
                onSaveDrawing = { title ->
                    scope.launch {
                        val drawing = Drawing(
                            title = title,
                            partnerName = partnerName,
                            operations = drawingEngine.operations.value
                        )
                        drawingRepo.saveDrawing(drawing)
                    }
                },
                onShareRoomClick = { shareRoomCodeIntent(context, roomCodeArg) },
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(Screen.Gallery.route) {
            GalleryScreen(
                drawings = recentDrawings,
                onDrawingClick = { id -> navController.navigate(Screen.ArtworkDetail.createRoute(id)) },
                onDeleteDrawing = { id -> scope.launch { drawingRepo.deleteDrawing(id) } },
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(
            route = Screen.ArtworkDetail.route,
            arguments = listOf(navArgument("drawingId") { type = NavType.StringType })
        ) { backStackEntry ->
            val drawingId = backStackEntry.arguments?.getString("drawingId") ?: ""
            val drawing = recentDrawings.find { it.id == drawingId }

            ArtworkDetailScreen(
                drawing = drawing,
                onExportClick = {},
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(Screen.DailyChallenge.route) {
            DailyChallengeScreen(
                onStartChallenge = { challenge ->
                    val code = generateRandomRoomCode()
                    activeRoomCode = code
                    navController.navigate(Screen.Canvas.createRoute(code, true))
                },
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(Screen.Profile.route) {
            ProfileScreen(
                currentName = userName,
                userId = userId,
                onSaveName = { newName ->
                    scope.launch { prefsRepo.saveDisplayName(newName) }
                    navController.popBackStack()
                },
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(Screen.Settings.route) {
            SettingsScreen(
                signalingServerUrl = serverUrl,
                isDarkMode = isDarkMode,
                isHapticEnabled = isHaptic,
                onServerUrlChanged = { url -> scope.launch { prefsRepo.saveSignalingServerUrl(url) } },
                onDarkModeToggled = { dark -> scope.launch { prefsRepo.setDarkMode(dark) } },
                onHapticToggled = { haptic -> scope.launch { prefsRepo.setHapticFeedback(haptic) } },
                onClearLocalDataClick = {
                    scope.launch {
                        drawingRepo.deleteAllDrawings()
                        prefsRepo.clearAllData()
                    }
                },
                onPrivacyPolicyClick = { navController.navigate(Screen.PrivacyPolicy.route) },
                onReportBlockClick = { navController.navigate(Screen.ReportBlock.route) },
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(Screen.PrivacyPolicy.route) {
            PrivacyPolicyScreen(onBackClick = { navController.popBackStack() })
        }

        composable(Screen.ReportBlock.route) {
            ReportBlockScreen(
                onReportSubmitted = { reason ->
                    webrtcManager.close()
                    signalingClient.disconnect()
                },
                onBackClick = { navController.popBackStack() }
            )
        }
    }
}

private suspend fun sendPhoneAuthRequest(serverUrl: String, phone: String, displayName: String) {
    withContext(Dispatchers.IO) {
        val httpUrl = serverUrl.replace("wss://", "https://").replace("ws://", "http://") + "/api/auth/phone-login"
        val json = Gson().toJson(mapOf("phone" to phone, "displayName" to displayName))
        val body = json.toRequestBody("application/json".toMediaType())
        val req = Request.Builder().url(httpUrl).post(body).build()
        val response = OkHttpClient.Builder()
            .connectTimeout(10, java.util.concurrent.TimeUnit.SECONDS)
            .readTimeout(10, java.util.concurrent.TimeUnit.SECONDS)
            .build()
            .newCall(req).execute()
        if (!response.isSuccessful) {
            val err = response.body?.string() ?: "HTTP ${response.code}"
            response.close()
            throw Exception("Server returned error: $err")
        }
        response.close()
    }
}

private fun shareRoomCodeIntent(context: android.content.Context, code: String) {
    val deepLinkUrl = "https://psychological-streams-centres-fell.trycloudflare.com/join?code=$code"
    val sendIntent = android.content.Intent().apply {
        action = android.content.Intent.ACTION_SEND
        putExtra(
            android.content.Intent.EXTRA_TEXT,
            "Join my drawing room on Couple Canvas! 💕\nRoom Code: $code\nClick to join directly: $deepLinkUrl"
        )
        type = "text/plain"
    }
    val shareIntent = android.content.Intent.createChooser(sendIntent, "Share Room Code")
    shareIntent.addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)
    context.startActivity(shareIntent)
}

private suspend fun addPartnerApi(serverUrl: String, userPhone: String, partnerPhone: String): String {
    return withContext(Dispatchers.IO) {
        try {
            val httpUrl = serverUrl.replace("wss://", "https://").replace("ws://", "http://") + "/api/partner/add"
            val json = Gson().toJson(mapOf("userPhone" to userPhone, "partnerPhone" to partnerPhone))
            val body = json.toRequestBody("application/json".toMediaType())
            val req = Request.Builder().url(httpUrl).post(body).build()
            val resp = OkHttpClient().newCall(req).execute()
            resp.close()
            "Partner"
        } catch (e: Exception) {
            e.printStackTrace()
            "Partner"
        }
    }
}

private suspend fun sendDirectChatMessageApi(serverUrl: String, senderPhone: String, recipientPhone: String, text: String) {
    withContext(Dispatchers.IO) {
        try {
            if (senderPhone.isBlank() || recipientPhone.isBlank()) return@withContext
            val httpUrl = serverUrl.replace("wss://", "https://").replace("ws://", "http://") + "/api/chat/send"
            val json = Gson().toJson(mapOf("senderPhone" to senderPhone, "recipientPhone" to recipientPhone, "text" to text))
            val body = json.toRequestBody("application/json".toMediaType())
            val req = Request.Builder().url(httpUrl).post(body).build()
            OkHttpClient().newCall(req).execute().close()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
