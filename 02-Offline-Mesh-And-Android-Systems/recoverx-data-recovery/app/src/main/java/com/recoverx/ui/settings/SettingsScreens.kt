package com.recoverx.ui.settings

import android.widget.Toast
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.recoverx.data.database.RecoverXDatabaseHelper
import com.recoverx.ui.components.RecoverXTopBar
import com.recoverx.ui.theme.BrandCyan
import kotlinx.coroutines.launch

@Composable
fun SettingsScreen(
    dbHelper: RecoverXDatabaseHelper,
    onNavigateBack: () -> Unit,
    onNavigatePrivacyCenter: () -> Unit,
    onNavigateHelp: () -> Unit,
    onNavigateKnownIssues: () -> Unit
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var showClearConfirm by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Settings & Support",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(8.dp)) {
                    SettingNavRow("Privacy & Data Architecture", Icons.Default.Security, onNavigatePrivacyCenter)
                    HorizontalDivider()
                    SettingNavRow("Recovery Limitations & TRIM Guide", Icons.Default.Info, onNavigateHelp)
                    HorizontalDivider()
                    SettingNavRow("Device Compatibility & Known Issues", Icons.Default.BugReport, onNavigateKnownIssues)
                }
            }

            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Database & Storage", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Text(
                        "Clear scan session history and discovered item records. This does not delete any of your restored files.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                    OutlinedButton(
                        onClick = { showClearConfirm = true },
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.error)
                    ) {
                        Icon(Icons.Default.DeleteSweep, contentDescription = null)
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Clear Scan & Recovery Logs")
                    }
                }
            }

            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("About RecoverX", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(6.dp))
                    Text("Version 1.0.0 (Native Release)", style = MaterialTheme.typography.bodyMedium)
                    Text("Engine: Jetpack Compose + Room + MediaStore + Media3", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
                }
            }
        }

        if (showClearConfirm) {
            AlertDialog(
                onDismissRequest = { showClearConfirm = false },
                title = { Text("Clear All History?") },
                text = { Text("All past scan sessions, item discovery records, and recovery logs will be purged from the database.") },
                confirmButton = {
                    TextButton(onClick = {
                        showClearConfirm = false
                        scope.launch {
                            dbHelper.clearAllHistory()
                            Toast.makeText(context, "History Cleared", Toast.LENGTH_SHORT).show()
                        }
                    }) {
                        Text("Clear", color = MaterialTheme.colorScheme.error)
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showClearConfirm = false }) {
                        Text("Cancel")
                    }
                }
            )
        }
    }
}

@Composable
fun PrivacyCenterScreen(onNavigateBack: () -> Unit) {
    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Privacy Center",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            InfoBlock(
                title = "100% Offline Architecture",
                body = "RecoverX never establishes network connections during scan or recovery operations. No internet permission is required or requested for storage inspection."
            )
            InfoBlock(
                title = "No Cloud Uploads",
                body = "Every file discovered, inspected, or restored remains exclusively on your physical device. We operate no remote servers, cloud backups, or analytics endpoints."
            )
            InfoBlock(
                title = "Safe File Operations",
                body = "RecoverX is strictly read-only on your source files. It NEVER deletes, overwrites, or alters source media during scans or restoration."
            )
        }
    }
}

@Composable
fun HelpLimitationsScreen(onNavigateBack: () -> Unit) {
    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Recovery Limitations & TRIM",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            InfoBlock(
                title = "Hardware Flash Storage & TRIM",
                body = "Modern Android devices use internal eMMC/UFS flash memory. When a file is deleted, Android runs the TRIM command to notify flash controllers that physical blocks are unallocated. Once TRIM runs, reading those blocks physically returns zeros."
            )
            InfoBlock(
                title = "File-Based Encryption (FBE)",
                body = "Starting with Android 7 and mandatory on Android 10+, every file is encrypted with an individual cryptographic key. Once the file inode is deleted, the per-file key is discarded, making raw sector carving mathematically impossible without the key."
            )
            InfoBlock(
                title = "How RecoverX Genuinely Recovers Data",
                body = "1. Gallery & File Manager Trash: Discovering items retained in 30-day recycle bins.\n2. Alternate Copies: Finding duplicates in downloads, backups, or sync directories.\n3. Cached Thumbnails: Extracting high-resolution thumbnails created by system media scanners.\n4. Corrupted & Mismatched Files: Detecting files renamed with false extensions whose binary signatures are intact."
            )
        }
    }
}

@Composable
fun KnownIssuesScreen(onNavigateBack: () -> Unit) {
    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Known Issues & Compatibility",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            InfoBlock(
                title = "Android 11+ Restricted /Android/data",
                body = "Starting in Android 11, Google closed direct Storage Access Framework (SAF) folder picker access to the root of /Android/data and /Android/obb to safeguard third-party app privacy. RecoverX respects this boundary."
            )
            InfoBlock(
                title = "OEM Specific Gallery Trash",
                body = "Certain manufacturers (Samsung OneUI, Xiaomi MIUI/HyperOS, Vivo Funtouch) implement proprietary cloud trash bins inside their custom gallery apps that are not exposed via standard MediaStore APIs. For these, users can restore items directly through the OEM Gallery app's trash menu."
            )
        }
    }
}

@Composable
private fun SettingNavRow(title: String, icon: ImageVector, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(vertical = 12.dp, horizontal = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(imageVector = icon, contentDescription = null, tint = BrandCyan, modifier = Modifier.size(22.dp))
            Spacer(modifier = Modifier.width(12.dp))
            Text(text = title, style = MaterialTheme.typography.bodyLarge)
        }
        Icon(imageVector = Icons.AutoMirrored.Filled.ArrowForward, contentDescription = null, tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f), modifier = Modifier.size(18.dp))
    }
}

@Composable
private fun InfoBlock(title: String, body: String) {
    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = BrandCyan)
            Spacer(modifier = Modifier.height(6.dp))
            Text(text = body, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f))
        }
    }
}
