package com.projectx2.porncontroller.features.permissions

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.net.VpnService
import android.os.Build
import android.os.PowerManager
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import com.projectx2.porncontroller.core.theme.*
import com.projectx2.porncontroller.services.AccessibilityMonitorService
import com.projectx2.porncontroller.services.LocalVpnService

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PermissionSetupScreen(
    onNavigateBack: () -> Unit
) {
    val context = LocalContext.current

    // VPN Prepare Launcher
    val vpnLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val startIntent = Intent(context, LocalVpnService::class.java).apply {
                action = LocalVpnService.ACTION_START
            }
            ContextCompat.startForegroundService(context, startIntent)
        }
    }

    val isVpnAuthorized = VpnService.prepare(context) == null
    val isAccessibilityGranted = AccessibilityMonitorService.isRunning
    val isOverlayGranted = Settings.canDrawOverlays(context)

    val powerManager = context.getSystemService(Context.POWER_SERVICE) as PowerManager
    val isBatteryOptimized = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        powerManager.isIgnoringBatteryOptimizations(context.packageName)
    } else true

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Permission Center") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = TextPrimary)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = CharcoalBackground)
            )
        },
        containerColor = CharcoalBackground
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .background(SurfaceDark)
                        .border(1.dp, BorderDark, RoundedCornerShape(14.dp))
                        .padding(16.dp)
                ) {
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.VerifiedUser, contentDescription = null, tint = EmeraldActive)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "Strict Offline Privacy Guarantee",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = TextPrimary
                            )
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = "Every permission granted here operates 100% locally on your device. No cloud sync, no telemetry, and zero browsing data collection.",
                            fontSize = 12.sp,
                            color = TextSecondary,
                            lineHeight = 18.sp
                        )
                    }
                }
            }

            // 1. VPN Local DNS Filtering
            item {
                PermissionItemCard(
                    icon = Icons.Default.VpnLock,
                    title = "Local DNS Filtering (VPN)",
                    description = "Used solely to route DNS queries through an offline sinkhole to block adult domains without remote servers.",
                    isGranted = isVpnAuthorized,
                    actionText = if (isVpnAuthorized) "Active" else "Authorize",
                    onAction = {
                        val vpnIntent = VpnService.prepare(context)
                        if (vpnIntent != null) {
                            vpnLauncher.launch(vpnIntent)
                        } else {
                            val startIntent = Intent(context, LocalVpnService::class.java).apply {
                                action = LocalVpnService.ACTION_START
                            }
                            ContextCompat.startForegroundService(context, startIntent)
                        }
                    }
                )
            }

            // 2. Accessibility Service
            item {
                PermissionItemCard(
                    icon = Icons.Default.AccessibilityNew,
                    title = "Accessibility Monitoring",
                    description = "Inspects browser address/search bars for configured personal trigger keywords and repetitive compulsive loops. Never reads passwords.",
                    isGranted = isAccessibilityGranted,
                    actionText = if (isAccessibilityGranted) "Active" else "Enable",
                    onAction = {
                        val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS).apply {
                            flags = Intent.FLAG_ACTIVITY_NEW_TASK
                        }
                        context.startActivity(intent)
                    }
                )
            }

            // 3. Draw Over Other Apps (Intervention Overlay)
            item {
                PermissionItemCard(
                    icon = Icons.Default.Layers,
                    title = "Intervention Screen Overlay",
                    description = "Allows the app to display the full-screen non-shaming pause intervention when compulsive search repetition is triggered.",
                    isGranted = isOverlayGranted,
                    actionText = if (isOverlayGranted) "Active" else "Permit",
                    onAction = {
                        val intent = Intent(
                            Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                            Uri.parse("package:${context.packageName}")
                        ).apply {
                            flags = Intent.FLAG_ACTIVITY_NEW_TASK
                        }
                        context.startActivity(intent)
                    }
                )
            }

            // 4. Battery Optimization Exemption
            item {
                PermissionItemCard(
                    icon = Icons.Default.BatteryChargingFull,
                    title = "Background Battery Exemption",
                    description = "Prevents aggressive Android OEM battery managers from prematurely killing protection and focus timers.",
                    isGranted = isBatteryOptimized,
                    actionText = if (isBatteryOptimized) "Exempted" else "Configure",
                    onAction = {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                            val intent = Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS).apply {
                                flags = Intent.FLAG_ACTIVITY_NEW_TASK
                            }
                            context.startActivity(intent)
                        }
                    }
                )
            }

            item { Spacer(modifier = Modifier.height(24.dp)) }
        }
    }
}

@Composable
fun PermissionItemCard(
    icon: ImageVector,
    title: String,
    description: String,
    isGranted: Boolean,
    actionText: String,
    onAction: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(SurfaceDark)
            .border(
                1.dp,
                if (isGranted) EmeraldActive.copy(alpha = 0.4f) else BorderDark,
                RoundedCornerShape(16.dp)
            )
            .padding(16.dp)
    ) {
        Column {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth()
            ) {
                Box(
                    modifier = Modifier
                        .size(42.dp)
                        .clip(CircleShape)
                        .background(if (isGranted) EmeraldActive.copy(alpha = 0.2f) else SurfaceElevated),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = if (isGranted) EmeraldActive else TextSecondary,
                        modifier = Modifier.size(22.dp)
                    )
                }

                Spacer(modifier = Modifier.width(12.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = title,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = TextPrimary
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = if (isGranted) "Status: Granted" else "Status: Action Required",
                        fontSize = 11.sp,
                        color = if (isGranted) EmeraldActive else AmberWarning
                    )
                }

                Button(
                    onClick = onAction,
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (isGranted) SurfaceElevated else ElectricPurple,
                        contentColor = if (isGranted) EmeraldActive else TextPrimary
                    ),
                    modifier = Modifier.height(36.dp),
                    contentPadding = PaddingValues(horizontal = 14.dp, vertical = 0.dp)
                ) {
                    Text(text = actionText, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = description,
                fontSize = 12.sp,
                color = TextSecondary,
                lineHeight = 17.sp
            )
        }
    }
}
