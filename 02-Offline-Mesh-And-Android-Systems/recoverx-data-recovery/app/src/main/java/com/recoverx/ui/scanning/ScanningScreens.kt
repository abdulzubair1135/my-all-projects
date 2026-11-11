package com.recoverx.ui.scanning

import android.net.Uri
import androidx.compose.foundation.background
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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.recoverx.data.database.RecoverXDatabaseHelper
import com.recoverx.data.entities.CandidateClassification
import com.recoverx.data.entities.DiscoveredItem
import com.recoverx.data.entities.FileCategory
import com.recoverx.data.entities.ScanType
import com.recoverx.scanner.ScanCoordinator
import com.recoverx.scanner.ScanProgressState
import com.recoverx.ui.components.DiscoveredItemRow
import com.recoverx.ui.components.EmptyStateView
import com.recoverx.ui.components.RecoverXTopBar
import com.recoverx.ui.theme.BrandCyan
import com.recoverx.ui.theme.BrandEmerald
import com.recoverx.ui.theme.BrandTeal

@Composable
fun QuickScanScreen(
    onNavigateBack: () -> Unit,
    onStartScan: () -> Unit
) {
    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Quick Scan",
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
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
                modifier = Modifier.weight(1f)
            ) {
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .clip(CircleShape)
                        .background(BrandCyan.copy(alpha = 0.15f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(imageVector = Icons.Default.FlashOn, contentDescription = null, tint = BrandCyan, modifier = Modifier.size(44.dp))
                }
                Spacer(modifier = Modifier.height(20.dp))
                Text(
                    text = "Fast Media & Trash Inspection",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = "Quickly inspects Android MediaStore for available photos, videos, audio recordings, trash bin items, and accessible media thumbnails.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.7f),
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
            }

            Button(
                onClick = onStartScan,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = BrandCyan)
            ) {
                Text("Start Quick Scan", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun AdvancedScanScreen(
    onNavigateBack: () -> Unit,
    onStartScan: () -> Unit,
    onPickFolder: () -> Unit
) {
    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Deep Advanced Scan",
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
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
                modifier = Modifier.weight(1f)
            ) {
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .clip(CircleShape)
                        .background(BrandTeal.copy(alpha = 0.15f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(imageVector = Icons.Default.Search, contentDescription = null, tint = BrandTeal, modifier = Modifier.size(44.dp))
                }
                Spacer(modifier = Modifier.height(20.dp))
                Text(
                    text = "Deep Signature & Directory Scan",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = "Traverses accessible file trees, inspects magic byte headers for JPEG, PNG, GIF, MP4, PDF, and ZIP, and checks for extension mismatches.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.7f),
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
                Spacer(modifier = Modifier.height(20.dp))

                OutlinedButton(
                    onClick = onPickFolder,
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.Default.FolderOpen, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Select Specific Folder (SAF)...")
                }
            }

            Button(
                onClick = onStartScan,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = BrandTeal)
            ) {
                Text("Start Full Deep Scan", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun ScanProgressScreen(
    scanCoordinator: ScanCoordinator,
    onNavigateBack: () -> Unit,
    onScanFinished: () -> Unit
) {
    val state by scanCoordinator.state.collectAsState()

    LaunchedEffect(state.isScanning) {
        if (!state.isScanning && state.lastCompletedSession != null) {
            onScanFinished()
        }
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Scanning Storage",
                canNavigateBack = true,
                onNavigateBack = {
                    scanCoordinator.cancelCurrentScan()
                    onNavigateBack()
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
                modifier = Modifier.weight(1f)
            ) {
                CircularProgressIndicator(
                    modifier = Modifier.size(72.dp),
                    color = BrandCyan,
                    strokeWidth = 6.dp
                )
                Spacer(modifier = Modifier.height(28.dp))
                Text(
                    text = state.currentPhase,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Source: ${state.currentSource}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.7f)
                )

                if (state.currentItemName.isNotBlank()) {
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = state.currentItemName,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.5f),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }

                Spacer(modifier = Modifier.height(24.dp))

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Files Inspected", style = MaterialTheme.typography.labelSmall)
                            Text(
                                text = "${state.inspectedCount}",
                                style = MaterialTheme.typography.headlineMedium,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Candidates Found", style = MaterialTheme.typography.labelSmall)
                            Text(
                                text = "${state.candidateCount}",
                                style = MaterialTheme.typography.headlineMedium,
                                fontWeight = FontWeight.Bold,
                                color = BrandCyan
                            )
                        }
                    }
                }
            }

            OutlinedButton(
                onClick = {
                    scanCoordinator.cancelCurrentScan()
                    onNavigateBack()
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.error)
            ) {
                Text("Cancel Scan", fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun ScanResultsScreen(
    scanCoordinator: ScanCoordinator,
    onNavigateBack: () -> Unit,
    onNavigateImagePreview: (Long) -> Unit,
    onNavigateVideoPreview: (Long) -> Unit,
    onNavigateItemDetails: (Long) -> Unit,
    onNavigateRecoveryCenter: () -> Unit
) {
    val state by scanCoordinator.state.collectAsState()
    val session = state.lastCompletedSession
    val allItems = state.latestDiscoveredItems
    val recoveryItems = remember(allItems) {
        allItems.filter { it.classification != CandidateClassification.EXISTING_FILE }
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Recoverable Deleted Media",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
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
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Recovery Candidates Found",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = BrandEmerald
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "Showing ONLY deleted media, trash items, and cached thumbnails. Existing phone storage files are excluded.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Files Inspected: ${session?.filesInspected ?: allItems.size}")
                        Text("Deleted / Candidates: ${recoveryItems.size}", color = BrandCyan, fontWeight = FontWeight.Bold)
                    }
                }
            }

            if (recoveryItems.isEmpty()) {
                EmptyStateView(
                    icon = Icons.Default.SearchOff,
                    title = "No Deleted Items Detected",
                    description = "No salvageable trash items, cached thumbnails, or deleted file signatures were found."
                )
            } else {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    items(recoveryItems) { item ->
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
fun FilteredResultListScreen(
    filter: String,
    dbHelper: RecoverXDatabaseHelper,
    onNavigateBack: () -> Unit,
    onNavigateImagePreview: (Long) -> Unit,
    onNavigateVideoPreview: (Long) -> Unit,
    onNavigateItemDetails: (Long) -> Unit
) {
    val classification = remember(filter) {
        try {
            CandidateClassification.valueOf(filter)
        } catch (e: Exception) {
            null
        }
    }

    var items by remember { mutableStateOf<List<DiscoveredItem>>(emptyList()) }

    LaunchedEffect(classification) {
        items = dbHelper.getDiscoveredItems(classification = classification, limit = 200)
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = classification?.title ?: "Filtered Candidates",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        if (items.isEmpty()) {
            EmptyStateView(
                icon = Icons.Default.FilterListOff,
                title = "No Matching Candidates",
                description = "No files matched this recovery classification category."
            )
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                items(items) { item ->
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
