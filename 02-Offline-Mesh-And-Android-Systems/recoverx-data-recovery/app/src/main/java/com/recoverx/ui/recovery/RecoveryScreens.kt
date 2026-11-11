package com.recoverx.ui.recovery

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.recoverx.core.storage.StorageInspector
import com.recoverx.data.database.RecoverXDatabaseHelper
import com.recoverx.data.entities.CandidateClassification
import com.recoverx.data.entities.DiscoveredItem
import com.recoverx.data.entities.FileCategory
import com.recoverx.data.entities.RecoveryRecord
import com.recoverx.data.entities.RecoveryStatus
import com.recoverx.recovery.RecoveryManager
import com.recoverx.ui.components.DiscoveredItemRow
import com.recoverx.ui.components.EmptyStateView
import com.recoverx.ui.components.RecoverXTopBar
import com.recoverx.ui.theme.BrandAmber
import com.recoverx.ui.theme.BrandCyan
import com.recoverx.ui.theme.BrandEmerald
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlinx.coroutines.launch

@Composable
fun RecoveryCenterScreen(
    dbHelper: RecoverXDatabaseHelper,
    onNavigateBack: () -> Unit,
    onNavigateImagePreview: (Long) -> Unit,
    onNavigateVideoPreview: (Long) -> Unit,
    onNavigateItemDetails: (Long) -> Unit,
    onNavigateHistory: () -> Unit
) {
    var candidates by remember { mutableStateOf<List<DiscoveredItem>>(emptyList()) }

    LaunchedEffect(Unit) {
        val all = dbHelper.getDiscoveredItems(limit = 1000)
        candidates = all.filter { it.classification != CandidateClassification.EXISTING_FILE }
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Data Recovery Center",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack,
                actions = {
                    IconButton(onClick = onNavigateHistory) {
                        Icon(Icons.Default.History, contentDescription = "Recovery History")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Recovery Candidates Discovered",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Items identified from accessible trash bins, alternative sync copies, cached thumbnails, and signature carved streams.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                }
            }

            if (candidates.isEmpty()) {
                EmptyStateView(
                    icon = Icons.Default.CheckCircle,
                    title = "No Pending Candidates",
                    description = "Run a Quick or Deep scan to detect salvageable trash items, thumbnails, or carved files."
                )
            } else {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    items(candidates) { item ->
                        DiscoveredItemRow(
                            item = item,
                            onClick = {
                                val ext = item.detectedExtension?.lowercase() ?: ""
                                val isImg = item.category == FileCategory.IMAGES ||
                                        item.classification == CandidateClassification.THUMBNAIL_ONLY ||
                                        ext in listOf("jpg", "jpeg", "png", "webp", "gif", "bmp")
                                val isVid = item.category == FileCategory.VIDEOS ||
                                        ext in listOf("mp4", "mkv", "3gp", "mov", "avi")

                                when {
                                    isImg -> onNavigateImagePreview(item.id)
                                    isVid -> onNavigateVideoPreview(item.id)
                                    else -> onNavigateItemDetails(item.id)
                                }
                            }
                        )
                    }
                    item { Spacer(modifier = Modifier.height(16.dp)) }
                }
            }
        }
    }
}

@Composable
fun RecoveryDestinationPickerScreen(
    itemId: Long,
    dbHelper: RecoverXDatabaseHelper,
    onNavigateBack: () -> Unit,
    onStartRestoration: (Long, Uri?) -> Unit
) {
    var item by remember { mutableStateOf<DiscoveredItem?>(null) }
    var customTreeUri by remember { mutableStateOf<Uri?>(null) }

    val folderPicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocumentTree()
    ) { uri ->
        if (uri != null) {
            customTreeUri = uri
        }
    }

    LaunchedEffect(itemId) {
        item = dbHelper.getDiscoveredItemById(itemId)
            ?: dbHelper.getDiscoveredItems(limit = 100).firstOrNull()
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Select Recovery Target",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Text(
                    text = "Where should the restored file be saved?",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )

                item?.let {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                    ) {
                        Column(modifier = Modifier.padding(14.dp)) {
                            Text(text = "File to Restore: ${it.displayName}", fontWeight = FontWeight.Bold)
                            Text(text = "Size: ${StorageInspector.formatBytes(it.sizeBytes)}", style = MaterialTheme.typography.bodyMedium)
                        }
                    }
                }

                // Option 1: App Managed Restored Directory
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { customTreeUri = null },
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = if (customTreeUri == null) BrandCyan.copy(alpha = 0.15f) else MaterialTheme.colorScheme.surface
                    )
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = customTreeUri == null,
                            onClick = { customTreeUri = null }
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Column {
                            Text(text = "Standard App Directory", fontWeight = FontWeight.Bold)
                            Text(text = "Downloads/RecoverX_Restored", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
                        }
                    }
                }

                // Option 2: Custom User Selected Folder
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { folderPicker.launch(null) },
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = if (customTreeUri != null) BrandCyan.copy(alpha = 0.15f) else MaterialTheme.colorScheme.surface
                    )
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = customTreeUri != null,
                            onClick = { folderPicker.launch(null) }
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Column {
                            Text(text = "Custom User Folder (SAF)", fontWeight = FontWeight.Bold)
                            Text(
                                text = customTreeUri?.lastPathSegment ?: "Tap to choose folder / SD card...",
                                style = MaterialTheme.typography.bodyMedium,
                                color = BrandCyan
                            )
                        }
                    }
                }
            }

            Button(
                onClick = { onStartRestoration(itemId, customTreeUri) },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = BrandCyan)
            ) {
                Text("Confirm & Restore", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun RecoveryProgressScreen(
    itemId: Long,
    dbHelper: RecoverXDatabaseHelper,
    recoveryManager: RecoveryManager,
    destinationTreeUri: Uri?,
    onNavigateBack: () -> Unit,
    onRestorationComplete: (Long) -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    val state by recoveryManager.state.collectAsState()
    var targetItem by remember { mutableStateOf<DiscoveredItem?>(null) }

    LaunchedEffect(itemId) {
        val found = dbHelper.getDiscoveredItemById(itemId)
            ?: dbHelper.getDiscoveredItems(limit = 100).firstOrNull()
        targetItem = found

        if (found != null && !state.isRunning) {
            coroutineScope.launch {
                val record = recoveryManager.restoreItem(found, destinationTreeUri)
                onRestorationComplete(record.id)
            }
        }
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Restoring File",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            CircularProgressIndicator(modifier = Modifier.size(72.dp), color = BrandCyan, strokeWidth = 6.dp)
            Spacer(modifier = Modifier.height(28.dp))
            Text(
                text = "Streaming File Content...",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = targetItem?.displayName ?: "Restoring...",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.7f)
            )
            Spacer(modifier = Modifier.height(20.dp))

            val progressRatio = if (state.totalBytes > 0) {
                (state.progressBytes.toFloat() / state.totalBytes.toFloat()).coerceIn(0f, 1f)
            } else 0f

            LinearProgressIndicator(
                progress = { progressRatio },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .clip(RoundedCornerShape(4.dp)),
                color = BrandCyan
            )

            Spacer(modifier = Modifier.height(10.dp))
            Text(
                text = "${StorageInspector.formatBytes(state.progressBytes)} / ${StorageInspector.formatBytes(state.totalBytes)}",
                style = MaterialTheme.typography.labelSmall
            )
        }
    }
}

@Composable
fun RecoveryReportScreen(
    recordId: Long,
    dbHelper: RecoverXDatabaseHelper,
    onNavigateBack: () -> Unit,
    onNavigateHome: () -> Unit
) {
    var record by remember { mutableStateOf<RecoveryRecord?>(null) }

    LaunchedEffect(recordId) {
        record = dbHelper.getRecoveryRecordById(recordId)
            ?: dbHelper.getRecoveryRecords(limit = 10).firstOrNull()
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Restoration Report",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            record?.let { rec ->
                Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    val isSuccess = rec.status == RecoveryStatus.COMPLETED || rec.status == RecoveryStatus.COMPLETED_WITH_WARNINGS
                    Box(
                        modifier = Modifier
                            .size(72.dp)
                            .clip(CircleShape)
                            .background(if (isSuccess) BrandEmerald.copy(alpha = 0.15f) else MaterialTheme.colorScheme.error.copy(alpha = 0.15f))
                            .align(Alignment.CenterHorizontally),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = if (isSuccess) Icons.Default.CheckCircle else Icons.Default.Error,
                            contentDescription = null,
                            tint = if (isSuccess) BrandEmerald else MaterialTheme.colorScheme.error,
                            modifier = Modifier.size(40.dp)
                        )
                    }

                    Text(
                        text = if (isSuccess) "File Successfully Restored" else "Restoration Failed",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.align(Alignment.CenterHorizontally)
                    )

                    Card(
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                    ) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Text(text = "File: ${rec.originalName}", fontWeight = FontWeight.Bold)
                            Text(text = "Bytes Written: ${StorageInspector.formatBytes(rec.bytesWritten)}")
                            Text(text = "Status: ${rec.status.name}")
                            Text(text = "Destination: ${rec.destinationPath ?: "None"}")
                            rec.validationSummary?.let {
                                Text(text = "Validation: $it", style = MaterialTheme.typography.bodyMedium, color = BrandCyan)
                            }
                            rec.errorMessage?.let {
                                Text(text = "Error: $it", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.error)
                            }
                        }
                    }
                }
            } ?: run {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(color = BrandCyan)
                }
            }

            Button(
                onClick = onNavigateHome,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = BrandCyan)
            ) {
                Text("Return to Dashboard", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun RecoveryHistoryScreen(
    dbHelper: RecoverXDatabaseHelper,
    onNavigateBack: () -> Unit
) {
    var records by remember { mutableStateOf<List<RecoveryRecord>>(emptyList()) }
    val dateFormat = remember { SimpleDateFormat("MMM dd, yyyy HH:mm", Locale.getDefault()) }

    LaunchedEffect(Unit) {
        records = dbHelper.getRecoveryRecords(100)
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Recovery History",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        if (records.isEmpty()) {
            EmptyStateView(
                icon = Icons.Default.HistoryToggleOff,
                title = "No Past Restorations",
                description = "Files you restore will appear in this persistent log."
            )
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                items(records) { rec ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                    ) {
                        Column(modifier = Modifier.padding(14.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(text = rec.originalName, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                                Text(
                                    text = rec.status.name,
                                    style = MaterialTheme.typography.labelSmall,
                                    color = if (rec.status == RecoveryStatus.COMPLETED) BrandEmerald else BrandAmber
                                )
                            }
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(text = dateFormat.format(Date(rec.startTimeMs)), style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(text = "Saved to: ${rec.destinationPath ?: "N/A"}", style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
                item { Spacer(modifier = Modifier.height(16.dp)) }
            }
        }
    }
}
