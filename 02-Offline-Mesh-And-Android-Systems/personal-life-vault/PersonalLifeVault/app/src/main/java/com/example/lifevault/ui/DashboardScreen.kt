package com.example.lifevault.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifevault.LifeVaultApplication
import com.example.lifevault.repository.VaultRepository
import com.example.lifevault.ui.theme.*
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun DashboardScreen(
    app: LifeVaultApplication,
    repository: VaultRepository,
    onNavigateToSettings: () -> Unit,
    onNavigateToVault: () -> Unit,
    onBackToPublic: (() -> Unit)? = null
) {
    val coroutineScope = rememberCoroutineScope()
    val scrollState = rememberScrollState()

    var isConnected by remember { mutableStateOf<Boolean?>(null) }
    var isSyncing by remember { mutableStateOf(false) }

    val pendingTextCount by app.database.syncQueueDao().getPendingTextCountFlow().collectAsState(initial = 0)
    val pendingMediaCount by app.database.syncQueueDao().getPendingMediaCountFlow().collectAsState(initial = 0)
    val syncedCount by app.database.syncQueueDao().getSyncedCountFlow().collectAsState(initial = 0)
    val failedCount by app.database.syncQueueDao().getFailedCountFlow().collectAsState(initial = 0)

    var autoSync by remember { mutableStateOf(app.tokenStore.isAutoSyncEnabled()) }
    var wifiOnly by remember { mutableStateOf(app.tokenStore.isWifiOnly()) }
    var chargingOnly by remember { mutableStateOf(app.tokenStore.isChargingOnly()) }
    val lastSyncTs = app.tokenStore.getLastSyncTimestamp()

    LaunchedEffect(Unit) {
        val healthy = repository.checkHealth()
        isConnected = healthy
        if (healthy) {
            if (app.tokenStore.getAuthToken().isNullOrEmpty()) {
                repository.registerDevice()
            }
            repository.syncTextQueue()
            repository.syncMediaQueue()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(VaultCreamBg)
            .padding(horizontal = 20.dp, vertical = 16.dp)
            .verticalScroll(scrollState)
    ) {
        // Top Bar
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 24.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "PERSONAL LIFE VAULT",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    letterSpacing = 2.sp,
                    color = VaultCharcoal
                )
                Text(
                    text = "PRIVATE SELF-HOSTED STORAGE",
                    fontSize = 11.sp,
                    fontFamily = FontFamily.Monospace,
                    letterSpacing = 1.sp,
                    color = VaultMuted
                )
            }
            Row {
                IconButton(onClick = onNavigateToVault) {
                    Icon(
                        imageVector = Icons.Default.Folder,
                        contentDescription = "Vault",
                        tint = VaultSlate
                    )
                }
                IconButton(onClick = onNavigateToSettings) {
                    Icon(
                        imageVector = Icons.Default.Settings,
                        contentDescription = "Settings",
                        tint = VaultSlate
                    )
                }
                if (onBackToPublic != null) {
                    IconButton(onClick = onBackToPublic) {
                        Icon(
                            imageVector = Icons.Default.Lock,
                            contentDescription = "Lock Vault",
                            tint = VaultSlate
                        )
                    }
                }
            }
        }

        // Server Connection Status Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, VaultBorder, RoundedCornerShape(8.dp)),
            colors = CardDefaults.cardColors(containerColor = VaultCreamSurface),
            shape = RoundedCornerShape(8.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "SERVER CONNECTION",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        fontFamily = FontFamily.Monospace,
                        letterSpacing = 1.sp,
                        color = VaultSlate
                    )
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(10.dp)
                                .clip(CircleShape)
                                .background(
                                    when (isConnected) {
                                        true -> VaultOnlineGreen
                                        false -> VaultOfflineRed
                                        null -> VaultSilverDark
                                    }
                                )
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = when (isConnected) {
                                true -> "CONNECTED"
                                false -> "OFFLINE"
                                null -> "CHECKING..."
                            },
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace,
                            color = when (isConnected) {
                                true -> VaultOnlineGreen
                                false -> VaultOfflineRed
                                null -> VaultMuted
                            }
                        )
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = app.tokenStore.getServerUrl(),
                    fontSize = 13.sp,
                    fontFamily = FontFamily.Monospace,
                    color = VaultMuted
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Last Sync Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, VaultBorder, RoundedCornerShape(8.dp)),
            colors = CardDefaults.cardColors(containerColor = VaultCreamSurface),
            shape = RoundedCornerShape(8.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "LAST SYNCHRONIZED",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        fontFamily = FontFamily.Monospace,
                        letterSpacing = 1.sp,
                        color = VaultSlate
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = if (lastSyncTs > 0) {
                            SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(Date(lastSyncTs))
                        } else {
                            "Never"
                        },
                        fontSize = 14.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Medium,
                        color = VaultCharcoal
                    )
                }
                Icon(
                    imageVector = Icons.Default.Schedule,
                    contentDescription = null,
                    tint = VaultSilverDark,
                    modifier = Modifier.size(24.dp)
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Queue Breakdown
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, VaultBorder, RoundedCornerShape(8.dp)),
            colors = CardDefaults.cardColors(containerColor = VaultCreamSurface),
            shape = RoundedCornerShape(8.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "LOCAL ROOM QUEUE",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    fontFamily = FontFamily.Monospace,
                    letterSpacing = 1.sp,
                    color = VaultSlate
                )
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    QueueStatBox("PENDING TEXT", pendingTextCount.toString(), Modifier.weight(1f))
                    Spacer(modifier = Modifier.width(8.dp))
                    QueueStatBox("PENDING MEDIA", pendingMediaCount.toString(), Modifier.weight(1f))
                }
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    QueueStatBox("SYNCED TOTAL", syncedCount.toString(), Modifier.weight(1f))
                    Spacer(modifier = Modifier.width(8.dp))
                    QueueStatBox("FAILED", failedCount.toString(), Modifier.weight(1f))
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Sync Now Button
        Button(
            onClick = {
                isSyncing = true
                coroutineScope.launch {
                    isConnected = repository.checkHealth()
                    app.triggerImmediateSync()
                    isSyncing = false
                }
            },
            enabled = !isSyncing,
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp)
                .border(1.dp, VaultSilverDark, RoundedCornerShape(6.dp)),
            colors = ButtonDefaults.buttonColors(
                containerColor = VaultCharcoal,
                contentColor = VaultCreamBg
            ),
            shape = RoundedCornerShape(6.dp)
        ) {
            if (isSyncing) {
                CircularProgressIndicator(
                    color = VaultCreamBg,
                    strokeWidth = 2.dp,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(10.dp))
                Text(
                    text = "SYNCHRONIZING...",
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp,
                    letterSpacing = 1.5.sp
                )
            } else {
                Icon(
                    imageVector = Icons.Default.Sync,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "SYNCHRONIZE NOW",
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp,
                    letterSpacing = 1.5.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Constraint Switches
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, VaultBorder, RoundedCornerShape(8.dp)),
            colors = CardDefaults.cardColors(containerColor = VaultCreamSurface),
            shape = RoundedCornerShape(8.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "SYNC CONSTRAINTS",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    fontFamily = FontFamily.Monospace,
                    letterSpacing = 1.sp,
                    color = VaultSlate
                )
                Spacer(modifier = Modifier.height(8.dp))

                ConstraintRow("Automatic Background Sync", autoSync) {
                    autoSync = it
                    app.tokenStore.setAutoSyncEnabled(it)
                    app.scheduleSyncWorkers()
                }

                HorizontalDivider(color = VaultSilverLight, thickness = 1.dp, modifier = Modifier.padding(vertical = 8.dp))

                ConstraintRow("Wi-Fi Connection Only", wifiOnly) {
                    wifiOnly = it
                    app.tokenStore.setWifiOnly(it)
                    app.scheduleSyncWorkers()
                }

                HorizontalDivider(color = VaultSilverLight, thickness = 1.dp, modifier = Modifier.padding(vertical = 8.dp))

                ConstraintRow("Device Charging Only", chargingOnly) {
                    chargingOnly = it
                    app.tokenStore.setChargingOnly(it)
                    app.scheduleSyncWorkers()
                }
            }
        }
    }
}

@Composable
private fun QueueStatBox(title: String, value: String, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .background(VaultCreamCard, RoundedCornerShape(6.dp))
            .border(1.dp, VaultBorder, RoundedCornerShape(6.dp))
            .padding(12.dp)
    ) {
        Column {
            Text(
                text = title,
                fontSize = 10.sp,
                fontFamily = FontFamily.Monospace,
                fontWeight = FontWeight.SemiBold,
                color = VaultMuted
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = value,
                fontSize = 18.sp,
                fontFamily = FontFamily.Monospace,
                fontWeight = FontWeight.Bold,
                color = VaultCharcoal
            )
        }
    }
}

@Composable
private fun ConstraintRow(label: String, checked: Boolean, onCheckedChange: (Boolean) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            fontSize = 13.sp,
            color = VaultCharcoal
        )
        Switch(
            checked = checked,
            onCheckedChange = onCheckedChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = VaultCreamSurface,
                checkedTrackColor = VaultSlate,
                uncheckedThumbColor = VaultSilver,
                uncheckedTrackColor = VaultSilverLight
            )
        )
    }
}
