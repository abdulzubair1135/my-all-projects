package com.couplecanvas.app.ui.screens.settings

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.DeleteForever
import androidx.compose.material.icons.filled.Dns
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.ReportProblem
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Vibration
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.couplecanvas.app.ui.theme.CleanWhite
import com.couplecanvas.app.ui.theme.LightBlueBg
import com.couplecanvas.app.ui.theme.PinkPrimary
import com.couplecanvas.app.ui.theme.SlateDark
import com.couplecanvas.app.ui.theme.SlateSub
import com.couplecanvas.app.ui.theme.SoftBorder

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    signalingServerUrl: String,
    isDarkMode: Boolean,
    isHapticEnabled: Boolean,
    onServerUrlChanged: (String) -> Unit,
    onDarkModeToggled: (Boolean) -> Unit,
    onHapticToggled: (Boolean) -> Unit,
    onClearLocalDataClick: () -> Unit,
    onPrivacyPolicyClick: () -> Unit,
    onReportBlockClick: () -> Unit,
    onBackClick: () -> Unit
) {
    val context = LocalContext.current
    var showServerDialog by remember { mutableStateOf(false) }
    var serverUrlInput by remember { mutableStateOf(signalingServerUrl) }
    var showClearDataDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings", fontWeight = FontWeight.Bold, color = SlateDark) },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = SlateDark)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = CleanWhite
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(LightBlueBg)
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            // Section 1: Share App Feature
            Text("Share & Invite", fontWeight = FontWeight.Bold, color = PinkPrimary, fontSize = 14.sp)
            Spacer(modifier = Modifier.height(8.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = CleanWhite),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(SoftBorder)),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { shareAppIntent(context) }
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Share, contentDescription = null, tint = PinkPrimary)
                    Spacer(modifier = Modifier.width(16.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Share App via WhatsApp / Apps 💕", fontWeight = FontWeight.SemiBold, fontSize = 15.sp, color = SlateDark)
                        Text("Invite partners & friends to draw together", fontSize = 12.sp, color = SlateSub)
                    }
                    Icon(Icons.Default.ChevronRight, contentDescription = null, tint = SlateSub)
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Section 2: Connection & Signaling Configuration
            Text("Network & Signaling", fontWeight = FontWeight.Bold, color = PinkPrimary, fontSize = 14.sp)
            Spacer(modifier = Modifier.height(8.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = CleanWhite),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(SoftBorder)),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { showServerDialog = true }
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Dns, contentDescription = null, tint = PinkPrimary)
                    Spacer(modifier = Modifier.width(16.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Signaling Server URL", fontWeight = FontWeight.SemiBold, fontSize = 15.sp, color = SlateDark)
                        Text(signalingServerUrl, fontSize = 12.sp, color = SlateSub)
                    }
                    Icon(Icons.Default.ChevronRight, contentDescription = null, tint = SlateSub)
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Section 3: Preferences
            Text("Preferences", fontWeight = FontWeight.Bold, color = PinkPrimary, fontSize = 14.sp)
            Spacer(modifier = Modifier.height(8.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = CleanWhite),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(SoftBorder)),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.Vibration, contentDescription = null, tint = PinkPrimary)
                        Spacer(modifier = Modifier.width(16.dp))
                        Text("Haptic Feedback", fontWeight = FontWeight.SemiBold, fontSize = 15.sp, color = SlateDark, modifier = Modifier.weight(1f))
                        Switch(
                            checked = isHapticEnabled,
                            onCheckedChange = onHapticToggled,
                            colors = SwitchDefaults.colors(checkedThumbColor = PinkPrimary)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Section 4: Safety & Privacy
            Text("Privacy & Safety", fontWeight = FontWeight.Bold, color = PinkPrimary, fontSize = 14.sp)
            Spacer(modifier = Modifier.height(8.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = CleanWhite),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(SoftBorder)),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onPrivacyPolicyClick() }
                            .padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.Lock, contentDescription = null, tint = PinkPrimary)
                        Spacer(modifier = Modifier.width(16.dp))
                        Text("Privacy Policy & Data Principles", fontWeight = FontWeight.SemiBold, fontSize = 15.sp, color = SlateDark, modifier = Modifier.weight(1f))
                        Icon(Icons.Default.ChevronRight, contentDescription = null, tint = SlateSub)
                    }

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onReportBlockClick() }
                            .padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.ReportProblem, contentDescription = null, tint = PinkPrimary)
                        Spacer(modifier = Modifier.width(16.dp))
                        Text("Report or Block User", fontWeight = FontWeight.SemiBold, fontSize = 15.sp, color = SlateDark, modifier = Modifier.weight(1f))
                        Icon(Icons.Default.ChevronRight, contentDescription = null, tint = SlateSub)
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Section 5: Data Management
            Text("Data Management", fontWeight = FontWeight.Bold, color = Color.Red, fontSize = 14.sp)
            Spacer(modifier = Modifier.height(8.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = CleanWhite),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(SoftBorder)),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { showClearDataDialog = true }
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.DeleteForever, contentDescription = null, tint = Color.Red)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Clear All Local Drawings & Data", fontWeight = FontWeight.SemiBold, fontSize = 15.sp, color = Color.Red)
                }
            }
        }
    }

    if (showServerDialog) {
        AlertDialog(
            onDismissRequest = { showServerDialog = false },
            title = { Text("Signaling Server URL") },
            text = {
                OutlinedTextField(
                    value = serverUrlInput,
                    onValueChange = { serverUrlInput = it },
                    label = { Text("URL (ws:// or wss://)") },
                    singleLine = true
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        onServerUrlChanged(serverUrlInput.trim())
                        showServerDialog = false
                    }
                ) {
                    Text("Save", color = PinkPrimary)
                }
            },
            dismissButton = {
                TextButton(onClick = { showServerDialog = false }) { Text("Cancel") }
            }
        )
    }

    if (showClearDataDialog) {
        AlertDialog(
            onDismissRequest = { showClearDataDialog = false },
            title = { Text("Delete Local App Data?") },
            text = { Text("This will delete all saved drawings, exported cache, and settings permanently from this phone.") },
            confirmButton = {
                TextButton(
                    onClick = {
                        onClearLocalDataClick()
                        showClearDataDialog = false
                    }
                ) {
                    Text("Delete", color = Color.Red)
                }
            },
            dismissButton = {
                TextButton(onClick = { showClearDataDialog = false }) { Text("Cancel") }
            }
        )
    }
}

private fun shareAppIntent(context: Context) {
    try {
        val srcFile = java.io.File(context.applicationInfo.sourceDir)
        val destFile = java.io.File(context.cacheDir, "CoupleCanvas.apk")
        srcFile.copyTo(destFile, overwrite = true)

        val apkUri: android.net.Uri = androidx.core.content.FileProvider.getUriForFile(
            context,
            "${context.packageName}.fileprovider",
            destFile
        )

        val sendIntent = android.content.Intent().apply {
            action = android.content.Intent.ACTION_SEND
            type = "application/vnd.android.package-archive"
            putExtra(android.content.Intent.EXTRA_STREAM, apkUri)
            putExtra(
                android.content.Intent.EXTRA_TEXT,
                "Hey! 💕 Draw together in real-time on a private canvas with Couple Canvas! Install the attached APK to join."
            )
            addFlags(android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }

        val shareIntent = android.content.Intent.createChooser(sendIntent, "Share Couple Canvas APK via")
        shareIntent.addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(shareIntent)
    } catch (e: Exception) {
        e.printStackTrace()
        val sendIntent = android.content.Intent().apply {
            action = android.content.Intent.ACTION_SEND
            putExtra(
                android.content.Intent.EXTRA_TEXT,
                "Hey! 💕 Draw together in real-time on a private canvas with Couple Canvas! Download & draw with your favorite person: https://psychological-streams-centres-fell.trycloudflare.com"
            )
            type = "text/plain"
        }
        val shareIntent = android.content.Intent.createChooser(sendIntent, "Share Couple Canvas App via")
        context.startActivity(shareIntent)
    }
}
