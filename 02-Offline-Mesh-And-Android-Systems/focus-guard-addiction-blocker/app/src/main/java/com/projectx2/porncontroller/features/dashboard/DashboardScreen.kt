package com.projectx2.porncontroller.features.dashboard

import android.app.Activity
import android.content.Intent
import android.net.VpnService
import android.provider.Settings
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import com.projectx2.porncontroller.core.theme.*
import com.projectx2.porncontroller.services.LocalVpnService

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    viewModel: DashboardViewModel,
    onNavigateToDomains: () -> Unit,
    onNavigateToKeywords: () -> Unit,
    onNavigateToTasks: () -> Unit,
    onNavigateToFocus: () -> Unit,
    onNavigateToAnalytics: () -> Unit,
    onNavigateToHistory: () -> Unit,
    onNavigateToPermissions: () -> Unit,
    onNavigateToSettings: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
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
            viewModel.toggleDomainProtection(true)
            viewModel.refreshServiceStates()
        }
    }

    LaunchedEffect(Unit) {
        viewModel.refreshServiceStates()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "P.RN ",
                            fontSize = 22.sp,
                            fontWeight = FontWeight.Black,
                            fontFamily = FontFamily.Monospace,
                            color = NeoRedAccent
                        )
                        Text(
                            text = "CTRL",
                            fontSize = 22.sp,
                            fontWeight = FontWeight.Black,
                            fontFamily = FontFamily.Monospace,
                            color = NeoBorderBlack
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Neo3DBadge(
                            text = "projectX²",
                            textColor = NeoRedAccent,
                            backgroundColor = NeoSurfaceWhite
                        )
                    }
                },
                actions = {
                    IconButton(onClick = onNavigateToPermissions) {
                        Icon(
                            imageVector = Icons.Default.Security,
                            contentDescription = "Permissions",
                            tint = NeoBorderBlack
                        )
                    }
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(
                            imageVector = Icons.Default.Settings,
                            contentDescription = "Settings",
                            tint = NeoBorderBlack
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = NeoCanvasBackground
                )
            )
        },
        containerColor = NeoCanvasBackground
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 3D Neomorphic Clean Streak Banner
            item {
                StreakBannerCard(
                    streakDays = uiState.streak?.currentStreakDays ?: 1
                )
            }

            // Quick Metrics 3D Grid
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    MetricCard(
                        modifier = Modifier.weight(1f),
                        icon = Icons.Default.Block,
                        title = "Blocked",
                        value = "${(uiState.todayStats?.blockedDomainsCount ?: 0) + (uiState.todayStats?.blockedKeywordsCount ?: 0)}",
                        subtitle = "Today"
                    )
                    MetricCard(
                        modifier = Modifier.weight(1f),
                        icon = Icons.Default.Timer,
                        title = "Focus Time",
                        value = "${uiState.todayStats?.focusMinutesTotal ?: 0}m",
                        subtitle = "Today"
                    )
                    MetricCard(
                        modifier = Modifier.weight(1f),
                        icon = Icons.Default.CheckCircle,
                        title = "Tasks Done",
                        value = "${uiState.todayStats?.completedTasksCount ?: 0}",
                        subtitle = "Replacements"
                    )
                }
            }

            // Protection Controls Section Header
            item {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(CircleShape)
                            .background(NeoRedAccent)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "OFFLINE SHIELD CONTROLS",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Black,
                        color = NeoBorderBlack,
                        letterSpacing = 1.sp
                    )
                }
            }

            // Adult Content Domain Shield Card (3D Neomorphic)
            item {
                val isDomainActive = uiState.settings?.isDomainProtectionEnabled ?: true
                val isVpnShieldOn = uiState.isVpnRunning && isDomainActive

                ProtectionSwitchCard(
                    icon = Icons.Default.VpnLock,
                    title = "Adult Domain Filtering",
                    subtitle = if (isVpnShieldOn) {
                        "ACTIVE • ${uiState.activeDomainCount} adult domains blocked"
                    } else {
                        "TAP TO ACTIVATE • Local DNS adult sinkhole"
                    },
                    isActive = isVpnShieldOn,
                    onToggle = { enable ->
                        if (enable) {
                            val vpnIntent = VpnService.prepare(context)
                            if (vpnIntent != null) {
                                vpnLauncher.launch(vpnIntent)
                            } else {
                                val startIntent = Intent(context, LocalVpnService::class.java).apply {
                                    action = LocalVpnService.ACTION_START
                                }
                                ContextCompat.startForegroundService(context, startIntent)
                                viewModel.toggleDomainProtection(true)
                                Toast.makeText(context, "Activating Adult Domain Shield...", Toast.LENGTH_SHORT).show()
                            }
                        } else {
                            val stopIntent = Intent(context, LocalVpnService::class.java).apply {
                                action = LocalVpnService.ACTION_STOP
                            }
                            context.startService(stopIntent)
                            viewModel.toggleDomainProtection(false)
                            Toast.makeText(context, "Adult Domain Shield Deactivated", Toast.LENGTH_SHORT).show()
                        }
                    },
                    onClick = {
                        if (!isVpnShieldOn) {
                            val vpnIntent = VpnService.prepare(context)
                            if (vpnIntent != null) {
                                vpnLauncher.launch(vpnIntent)
                            } else {
                                val startIntent = Intent(context, LocalVpnService::class.java).apply {
                                    action = LocalVpnService.ACTION_START
                                }
                                ContextCompat.startForegroundService(context, startIntent)
                                viewModel.toggleDomainProtection(true)
                                Toast.makeText(context, "Activating Adult Domain Shield...", Toast.LENGTH_SHORT).show()
                            }
                        } else {
                            onNavigateToDomains()
                        }
                    }
                )
            }

            // Keyword & Repetition Monitor Card (3D Neomorphic)
            item {
                val isKeywordPref = uiState.settings?.isKeywordMonitoringEnabled ?: true
                val isAccEnabled = uiState.isAccessibilityRunning
                val isKeywordFullyActive = isAccEnabled && isKeywordPref

                ProtectionSwitchCard(
                    icon = Icons.Default.FindInPage,
                    title = "Keyword & Search Blocker",
                    subtitle = if (isKeywordFullyActive) {
                        "ACTIVE • Intercepting repeated obsessive searches"
                    } else if (!isAccEnabled) {
                        "TAP HERE TO TURN ON • Accessibility required"
                    } else {
                        "PAUSED • Tap switch to resume keyword monitor"
                    },
                    isActive = isKeywordFullyActive,
                    onToggle = { enable ->
                        if (enable) {
                            viewModel.toggleKeywordMonitoring(true)
                            if (!uiState.isAccessibilityRunning) {
                                Toast.makeText(
                                    context,
                                    "Please turn ON 'P.RN Controller' in Accessibility",
                                    Toast.LENGTH_LONG
                                ).show()
                                val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS).apply {
                                    flags = Intent.FLAG_ACTIVITY_NEW_TASK
                                }
                                context.startActivity(intent)
                            } else {
                                Toast.makeText(context, "Keyword Monitor Activated", Toast.LENGTH_SHORT).show()
                            }
                        } else {
                            viewModel.toggleKeywordMonitoring(false)
                            Toast.makeText(context, "Keyword Monitor Paused", Toast.LENGTH_SHORT).show()
                        }
                    },
                    onClick = {
                        if (!uiState.isAccessibilityRunning) {
                            Toast.makeText(
                                context,
                                "Please turn ON 'P.RN Controller' in Accessibility",
                                Toast.LENGTH_LONG
                            ).show()
                            val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS).apply {
                                flags = Intent.FLAG_ACTIVITY_NEW_TASK
                            }
                            context.startActivity(intent)
                        } else {
                            onNavigateToKeywords()
                        }
                    }
                )
            }

            // Redirection Section Header
            item {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(CircleShape)
                            .background(NeoRedAccent)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "REDIRECTION & PRODUCTIVITY",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Black,
                        color = NeoBorderBlack,
                        letterSpacing = 1.sp
                    )
                }
            }

            // Quick Action Buttons (3D Neomorphic Cards)
            item {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        ActionCard(
                            modifier = Modifier.weight(1f),
                            icon = Icons.Default.HourglassTop,
                            title = "Focus Mode",
                            description = "Start Pomodoro session",
                            onClick = onNavigateToFocus
                        )
                        ActionCard(
                            modifier = Modifier.weight(1f),
                            icon = Icons.Default.SelfImprovement,
                            title = "Healthy Tasks",
                            description = "Water, Breathing, Books",
                            onClick = onNavigateToTasks
                        )
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        ActionCard(
                            modifier = Modifier.weight(1f),
                            icon = Icons.Default.BarChart,
                            title = "Habit Analytics",
                            description = "Weekly trends & streaks",
                            onClick = onNavigateToAnalytics
                        )
                        ActionCard(
                            modifier = Modifier.weight(1f),
                            icon = Icons.Default.History,
                            title = "Event History",
                            description = "Detailed local logs",
                            onClick = onNavigateToHistory
                        )
                    }
                }
            }

            item { Spacer(modifier = Modifier.height(20.dp)) }
        }
    }
}

/**
 * 3D Neomorphic Streak Banner: Pure White surface + 2.dp Solid Black Border + 3D offset extrusion.
 * Red text accents for streak title and fire icon.
 */
@Composable
fun StreakBannerCard(streakDays: Int) {
    Neo3DCard(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        backgroundColor = NeoSurfaceWhite,
        borderColor = NeoBorderBlack,
        borderWidth = 2.dp,
        extrusionOffset = 4.dp,
        extrusionColor = NeoBorderBlack
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp)
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = "CLEAN STREAK",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 1.5.sp,
                        color = NeoRedAccent
                    )
                }
                Spacer(modifier = Modifier.height(4.dp))
                Row(verticalAlignment = Alignment.Bottom) {
                    Text(
                        text = "$streakDays",
                        fontSize = 38.sp,
                        fontWeight = FontWeight.Black,
                        color = NeoRedAccent
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = if (streakDays == 1) "day strong" else "days strong",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = NeoTextBlack,
                        modifier = Modifier.padding(bottom = 6.dp)
                    )
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Building neural rewiring through discipline.",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                    color = NeoTextMuted
                )
            }

            Box(
                modifier = Modifier
                    .size(54.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .background(NeoSurfaceWhite)
                    .border(2.dp, NeoBorderBlack, RoundedCornerShape(16.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Whatshot,
                    contentDescription = "Streak Fire",
                    tint = NeoRedAccent,
                    modifier = Modifier.size(32.dp)
                )
            }
        }
    }
}

/**
 * 3D Neomorphic Metric Card: Pure White + 2.dp Black Border + 3D Extrusion + Red value text.
 */
@Composable
fun MetricCard(
    modifier: Modifier = Modifier,
    icon: ImageVector,
    title: String,
    value: String,
    subtitle: String
) {
    Neo3DCard(
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        backgroundColor = NeoSurfaceWhite,
        borderColor = NeoBorderBlack,
        borderWidth = 2.dp,
        extrusionOffset = 3.5.dp,
        extrusionColor = NeoBorderBlack
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Box(
                modifier = Modifier
                    .size(34.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(NeoSurfaceWhite)
                    .border(1.5.dp, NeoBorderBlack, RoundedCornerShape(10.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    tint = NeoRedAccent,
                    modifier = Modifier.size(20.dp)
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            Text(
                text = value,
                fontSize = 22.sp,
                fontWeight = FontWeight.Black,
                color = NeoRedAccent
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = title,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                color = NeoTextBlack
            )
            Text(
                text = subtitle,
                fontSize = 10.sp,
                fontWeight = FontWeight.Medium,
                color = NeoTextMuted
            )
        }
    }
}

/**
 * 3D Neomorphic Protection Switch Card.
 * Pure White + 2.dp Solid Black Border + 3D Extrusion + Bold Red status text.
 */
@Composable
fun ProtectionSwitchCard(
    icon: ImageVector,
    title: String,
    subtitle: String,
    isActive: Boolean,
    onToggle: (Boolean) -> Unit,
    onClick: () -> Unit
) {
    Neo3DCard(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(18.dp),
        backgroundColor = NeoSurfaceWhite,
        borderColor = NeoBorderBlack,
        borderWidth = 2.dp,
        extrusionOffset = 4.dp,
        extrusionColor = NeoBorderBlack,
        onClick = onClick
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(46.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(if (isActive) NeoRedAccent else NeoSurfaceWhite)
                    .border(2.dp, NeoBorderBlack, RoundedCornerShape(12.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    tint = if (isActive) Color.White else NeoBorderBlack,
                    modifier = Modifier.size(24.dp)
                )
            }

            Spacer(modifier = Modifier.width(14.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Bold,
                    color = NeoTextBlack
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = subtitle,
                    fontSize = 12.sp,
                    fontWeight = if (isActive) FontWeight.Bold else FontWeight.Medium,
                    color = if (isActive) NeoRedAccent else NeoTextMuted
                )
            }

            Switch(
                checked = isActive,
                onCheckedChange = onToggle,
                colors = SwitchDefaults.colors(
                    checkedThumbColor = Color.White,
                    checkedTrackColor = NeoRedAccent,
                    checkedBorderColor = NeoBorderBlack,
                    uncheckedThumbColor = NeoBorderBlack,
                    uncheckedTrackColor = NeoSurfaceOffWhite,
                    uncheckedBorderColor = NeoBorderBlack
                )
            )
        }
    }
}

/**
 * 3D Neomorphic Action Card.
 * Pure White + 2.dp Solid Black Border + 3D Extrusion.
 */
@Composable
fun ActionCard(
    modifier: Modifier = Modifier,
    icon: ImageVector,
    title: String,
    description: String,
    onClick: () -> Unit
) {
    Neo3DCard(
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        backgroundColor = NeoSurfaceWhite,
        borderColor = NeoBorderBlack,
        borderWidth = 2.dp,
        extrusionOffset = 3.5.dp,
        extrusionColor = NeoBorderBlack,
        onClick = onClick
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Box(
                modifier = Modifier
                    .size(38.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(NeoSurfaceWhite)
                    .border(1.5.dp, NeoBorderBlack, RoundedCornerShape(10.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    tint = NeoRedAccent,
                    modifier = Modifier.size(20.dp)
                )
            }
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = title,
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                color = NeoTextBlack
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = description,
                fontSize = 11.sp,
                fontWeight = FontWeight.Medium,
                color = NeoTextMuted
            )
        }
    }
}
