package com.recoverx.ui.diagnostics

import android.os.Build
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.recoverx.core.permissions.PermissionCoordinator
import com.recoverx.core.storage.StorageInspector
import com.recoverx.ui.components.RecoverXTopBar

@Composable
fun StorageDiagnosticsScreen(
    onNavigateBack: () -> Unit
) {
    val context = LocalContext.current
    val assessment = remember { StorageInspector.assessStorage(context) }
    val permStatus = remember { PermissionCoordinator.checkStoragePermissions(context) }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Storage & Device Diagnostics",
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
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text("Android OS & Device Specs", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    DiagRow("OS Release", Build.VERSION.RELEASE)
                    DiagRow("SDK API Level", "${Build.VERSION.SDK_INT}")
                    DiagRow("Device Manufacturer", Build.MANUFACTURER)
                    DiagRow("Device Model", Build.MODEL)
                    DiagRow("Security Patch", Build.VERSION.SECURITY_PATCH)
                }
            }

            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text("Filesystem & Capacity Metrics", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    DiagRow("Total Internal", StorageInspector.formatBytes(assessment.totalInternalBytes))
                    DiagRow("Used Internal", StorageInspector.formatBytes(assessment.usedInternalBytes))
                    DiagRow("Free Internal", StorageInspector.formatBytes(assessment.availableInternalBytes))
                    DiagRow("Removable Storage", if (assessment.hasRemovableStorage) "Detected" else "None")
                    if (assessment.hasRemovableStorage) {
                        DiagRow("Removable Volumes", assessment.removableVolumes.joinToString(", "))
                    }
                }
            }

            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text("Permission & Access Diagnosis", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    DiagRow("Full Media Access", "${permStatus.hasFullMediaAccess}")
                    DiagRow("Partial Visual Access", "${permStatus.hasPartialVisualAccess}")
                    DiagRow("Photo Access", "${permStatus.hasImageAccess}")
                    DiagRow("Video Access", "${permStatus.hasVideoAccess}")
                    DiagRow("Audio Access", "${permStatus.hasAudioAccess}")
                }
            }

            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text("Flash Storage & TRIM Forensics", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    DiagRow("Hardware TRIM", "Active (Device periodically discards freed sectors)")
                    DiagRow("Encryption Mode", "File-Based Encryption (FBE) enforced by Android Keystore")
                    DiagRow("Direct Block Carving", "Inaccessible (Restricted by Linux kernel & SELinux)")
                }
            }
        }
    }
}

@Composable
private fun DiagRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = label, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f))
        Text(text = value, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
    }
}
