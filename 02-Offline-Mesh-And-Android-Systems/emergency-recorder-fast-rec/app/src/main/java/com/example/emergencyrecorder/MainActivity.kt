package com.example.emergencyrecorder

import android.Manifest
import android.content.Intent
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.Crossfade
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.example.emergencyrecorder.accessibility.BackgroundTriggerService
import com.example.emergencyrecorder.permissions.PermissionManager
import com.example.emergencyrecorder.settings.AppSettings
import com.example.emergencyrecorder.ui.HistoryScreen
import com.example.emergencyrecorder.ui.MainDashboardScreen
import com.example.emergencyrecorder.ui.SettingsScreen
import com.example.emergencyrecorder.ui.SetupGuideScreen
import com.example.emergencyrecorder.ui.theme.EmergencyRecorderTheme

class MainActivity : ComponentActivity() {

    enum class Screen {
        DASHBOARD,
        SETUP_GUIDE,
        HISTORY,
        SETTINGS
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            EmergencyRecorderTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    var currentScreen by remember { mutableStateOf(Screen.DASHBOARD) }

                    var hasMicPermission by remember {
                        mutableStateOf(PermissionManager.hasRecordAudioPermission(this))
                    }
                    var hasNotificationPermission by remember {
                        mutableStateOf(PermissionManager.hasNotificationPermission(this))
                    }
                    var hasAccessibilityEnabled by remember {
                        mutableStateOf(PermissionManager.isAccessibilityServiceEnabled(this))
                    }

                    // Refresh status when Activity resumes (e.g. coming back from Android Settings)
                    DisposableEffect(Unit) {
                        val observer = LifecycleEventObserver { _, event ->
                            if (event == Lifecycle.Event.ON_RESUME) {
                                hasMicPermission = PermissionManager.hasRecordAudioPermission(this@MainActivity)
                                hasNotificationPermission = PermissionManager.hasNotificationPermission(this@MainActivity)
                                hasAccessibilityEnabled = PermissionManager.isAccessibilityServiceEnabled(this@MainActivity)
                            }
                        }
                        lifecycle.addObserver(observer)
                        onDispose {
                            lifecycle.removeObserver(observer)
                        }
                    }

                    // Runtime Permission Launcher
                    val permissionLauncher = rememberLauncherForActivityResult(
                        contract = ActivityResultContracts.RequestMultiplePermissions()
                    ) { permissions ->
                        hasMicPermission = permissions[Manifest.permission.RECORD_AUDIO] ?: hasMicPermission
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                            hasNotificationPermission = permissions[Manifest.permission.POST_NOTIFICATIONS] ?: hasNotificationPermission
                        }
                    }

                    fun requestRequiredPermissions() {
                        val toRequest = mutableListOf(
                            Manifest.permission.RECORD_AUDIO,
                            Manifest.permission.READ_PHONE_STATE,
                            Manifest.permission.READ_CALL_LOG,
                            Manifest.permission.READ_CONTACTS
                        )
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                            toRequest.add(Manifest.permission.POST_NOTIFICATIONS)
                        }
                        permissionLauncher.launch(toRequest.toTypedArray())
                    }

                    // First launch auto-prompt permissions
                    LaunchedEffect(Unit) {
                        if (!hasMicPermission || !hasNotificationPermission) {
                            requestRequiredPermissions()
                        }
                    }

                    // Control Screen-Off Volume Down background listener
                    LaunchedEffect(hasMicPermission) {
                        val settings = AppSettings.getInstance(this@MainActivity)
                        if (hasMicPermission && settings.isShortcutEnabled && settings.isScreenOffTriggerEnabled) {
                            BackgroundTriggerService.start(this@MainActivity)
                        } else {
                            BackgroundTriggerService.stop(this@MainActivity)
                        }
                    }

                    // Handle back press
                    BackHandler(enabled = currentScreen != Screen.DASHBOARD) {
                        currentScreen = Screen.DASHBOARD
                    }

                    Crossfade(targetState = currentScreen, label = "ScreenTransition") { screen ->
                        when (screen) {
                            Screen.DASHBOARD -> {
                                MainDashboardScreen(
                                    hasMicPermission = hasMicPermission,
                                    hasAccessibilityEnabled = hasAccessibilityEnabled,
                                    onNavigateSetup = { currentScreen = Screen.SETUP_GUIDE },
                                    onNavigateHistory = { currentScreen = Screen.HISTORY },
                                    onNavigateSettings = { currentScreen = Screen.SETTINGS }
                                )
                            }
                            Screen.SETUP_GUIDE -> {
                                SetupGuideScreen(
                                    hasMicPermission = hasMicPermission,
                                    hasNotificationPermission = hasNotificationPermission,
                                    hasAccessibilityEnabled = hasAccessibilityEnabled,
                                    onRequestPermissions = { requestRequiredPermissions() },
                                    onBack = { currentScreen = Screen.DASHBOARD }
                                )
                            }
                            Screen.HISTORY -> {
                                HistoryScreen(
                                    onBack = { currentScreen = Screen.DASHBOARD }
                                )
                            }
                            Screen.SETTINGS -> {
                                SettingsScreen(
                                    onBack = { currentScreen = Screen.DASHBOARD }
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
