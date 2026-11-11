package com.recoverx.ui.home

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import com.recoverx.core.storage.StorageAssessment
import com.recoverx.core.storage.StorageInspector
import com.recoverx.data.database.RecoverXDatabaseHelper
import com.recoverx.data.entities.FileCategory
import com.recoverx.data.entities.ScanSession
import com.recoverx.ui.components.EmptyStateView
import com.recoverx.ui.components.RecoverXTopBar
import com.recoverx.ui.components.StorageOverviewCard
import com.recoverx.ui.theme.BrandCyan
import com.recoverx.ui.theme.BrandEmerald
import com.recoverx.ui.theme.BrandTeal
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun HomeDashboardScreen(
    dbHelper: RecoverXDatabaseHelper,
    onNavigateQuickScan: () -> Unit,
    onNavigateAdvancedScan: () -> Unit,
    onNavigateStorageExplorer: () -> Unit,
    onNavigateRecoveryCenter: () -> Unit,
    onNavigateCategory: (String) -> Unit,
    onNavigateDiagnostics: () -> Unit,
    onNavigateSettings: () -> Unit
) {
    val context = LocalContext.current
    val assessment = remember { StorageInspector.assessStorage(context) }
    var recentSessions by remember { mutableStateOf<List<ScanSession>>(emptyList()) }

    LaunchedEffect(Unit) {
        recentSessions = dbHelper.getRecentScanSessions(5)
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "RecoverX Dashboard",
                actions = {
                    IconButton(onClick = onNavigateDiagnostics) {
                        Icon(imageVector = Icons.Default.Analytics, contentDescription = "Diagnostics")
                    }
                    IconButton(onClick = onNavigateSettings) {
                        Icon(imageVector = Icons.Default.Settings, contentDescription = "Settings")
                    }
                }
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Storage Overview
            item {
                StorageOverviewCard(assessment = assessment)
            }

            // Primary Action Buttons
            item {
                Text(
                    text = "Primary Operations",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    ActionTile(
                        title = "Quick Scan",
                        subtitle = "Scan Media & Trash",
                        icon = Icons.Default.FlashOn,
                        accentColor = BrandCyan,
                        onClick = onNavigateQuickScan,
                        modifier = Modifier.weight(1f)
                    )
                    ActionTile(
                        title = "Deep Scan",
                        subtitle = "Signatures & SAF",
                        icon = Icons.Default.Search,
                        accentColor = BrandTeal,
                        onClick = onNavigateAdvancedScan,
                        modifier = Modifier.weight(1f)
                    )
                }
                Spacer(modifier = Modifier.height(10.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    ActionTile(
                        title = "Browse Storage",
                        subtitle = "Explore Categories",
                        icon = Icons.Default.FolderOpen,
                        accentColor = BrandEmerald,
                        onClick = onNavigateStorageExplorer,
                        modifier = Modifier.weight(1f)
                    )
                    ActionTile(
                        title = "Recovery Center",
                        subtitle = "Restore Candidates",
                        icon = Icons.Default.Restore,
                        accentColor = BrandCyan,
                        onClick = onNavigateRecoveryCenter,
                        modifier = Modifier.weight(1f)
                    )
                }
            }

            // Category Shortcuts
            item {
                Text(
                    text = "File Categories",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    CategoryChip("Photos", Icons.Default.Image, onNavigateCategory, Modifier.weight(1f))
                    CategoryChip("Videos", Icons.Default.Videocam, onNavigateCategory, Modifier.weight(1f))
                    CategoryChip("Audio", Icons.Default.Audiotrack, onNavigateCategory, Modifier.weight(1f))
                }
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    CategoryChip("Documents", Icons.Default.Description, onNavigateCategory, Modifier.weight(1f))
                    CategoryChip("Archives", Icons.Default.FolderZip, onNavigateCategory, Modifier.weight(1f))
                    CategoryChip("Other", Icons.Default.InsertDriveFile, onNavigateCategory, Modifier.weight(1f))
                }
            }

            // Recent Scan Activity
            item {
                Text(
                    text = "Recent Scan Activity",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
            }

            if (recentSessions.isEmpty()) {
                item {
                    EmptyStateView(
                        icon = Icons.Default.History,
                        title = "No Scan History",
                        description = "Run a Quick or Deep scan to inspect accessible storage and candidates."
                    )
                }
            } else {
                items(recentSessions) { session ->
                    ScanSessionCard(session = session)
                }
            }

            item {
                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}

@Composable
private fun ActionTile(
    title: String,
    subtitle: String,
    icon: ImageVector,
    accentColor: Color,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .height(100.dp)
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(accentColor.copy(alpha = 0.15f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(imageVector = icon, contentDescription = null, tint = accentColor, modifier = Modifier.size(20.dp))
            }
            Column {
                Text(text = title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text(text = subtitle, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
            }
        }
    }
}

@Composable
private fun CategoryChip(
    name: String,
    icon: ImageVector,
    onCategoryClick: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .height(44.dp)
            .clickable { onCategoryClick(name) },
        shape = RoundedCornerShape(10.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Row(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            Icon(imageVector = icon, contentDescription = null, tint = BrandCyan, modifier = Modifier.size(18.dp))
            Spacer(modifier = Modifier.width(6.dp))
            Text(text = name, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
        }
    }
}

@Composable
private fun ScanSessionCard(session: ScanSession) {
    val dateFormat = remember { SimpleDateFormat("MMM dd, yyyy HH:mm", Locale.getDefault()) }
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
                Text(
                    text = "${session.scanType.name} SCAN",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = BrandCyan
                )
                Text(
                    text = session.status,
                    style = MaterialTheme.typography.labelSmall,
                    color = if (session.status == "COMPLETED") BrandEmerald else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = dateFormat.format(Date(session.startTimeMs)),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = "Files: ${session.filesInspected}", style = MaterialTheme.typography.bodyMedium)
                Text(text = "Candidates: ${session.candidateCount}", style = MaterialTheme.typography.bodyMedium, color = BrandTeal)
            }
        }
    }
}
