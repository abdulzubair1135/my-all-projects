package com.couplecanvas.app.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.navigation.compose.rememberNavController
import com.couplecanvas.app.CoupleCanvasApplication
import com.couplecanvas.app.ui.navigation.NavGraph
import com.couplecanvas.app.ui.theme.CoupleCanvasTheme

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as CoupleCanvasApplication
        val initialDeepLinkCode = extractDeepLinkRoomCode(intent)

        setContent {
            val isDarkModePref by app.userPreferencesRepository.isDarkMode.collectAsState(initial = false)
            // Only use dark theme if user explicitly enabled it in settings — never follow system dark mode
            CoupleCanvasTheme(darkTheme = isDarkModePref) {
                val navController = rememberNavController()
                NavGraph(navController = navController, app = app, deepLinkRoomCode = initialDeepLinkCode)
            }
        }
    }

    private fun extractDeepLinkRoomCode(intent: android.content.Intent?): String? {
        val data = intent?.data ?: return null
        return data.getQueryParameter("code")
    }
}
