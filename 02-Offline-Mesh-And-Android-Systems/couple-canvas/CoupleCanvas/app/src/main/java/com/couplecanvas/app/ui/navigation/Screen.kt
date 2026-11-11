package com.couplecanvas.app.ui.navigation

sealed class Screen(val route: String) {
    object Splash : Screen("splash")
    object PhoneAuth : Screen("phone_auth")
    object Onboarding : Screen("onboarding")
    object Home : Screen("home")
    object DirectChat : Screen("direct_chat")
    object CreateRoom : Screen("create_room")
    object JoinRoom : Screen("join_room")
    object Canvas : Screen("canvas/{roomCode}/{isHost}") {
        fun createRoute(roomCode: String, isHost: Boolean) = "canvas/$roomCode/$isHost"
    }
    object Gallery : Screen("gallery")
    object ArtworkDetail : Screen("artwork_detail/{drawingId}") {
        fun createRoute(drawingId: String) = "artwork_detail/$drawingId"
    }
    object DailyChallenge : Screen("daily_challenge")
    object Profile : Screen("profile")
    object Settings : Screen("settings")
    object PrivacyPolicy : Screen("privacy_policy")
    object ReportBlock : Screen("report_block")
}
