package com.recoverx.ui.storage

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.recoverx.data.database.RecoverXDatabaseHelper
import com.recoverx.data.entities.CandidateClassification
import com.recoverx.data.entities.DiscoveredItem
import com.recoverx.data.entities.FileCategory
import com.recoverx.ui.components.DiscoveredItemRow
import com.recoverx.ui.components.EmptyStateView
import com.recoverx.ui.components.RecoverXTopBar
import com.recoverx.ui.theme.BrandCyan
import java.util.Locale

@Composable
fun StorageExplorerScreen(
    dbHelper: RecoverXDatabaseHelper,
    onNavigateBack: () -> Unit,
    onNavigateImagePreview: (Long) -> Unit,
    onNavigateVideoPreview: (Long) -> Unit,
    onNavigateItemDetails: (Long) -> Unit
) {
    var items by remember { mutableStateOf<List<DiscoveredItem>>(emptyList()) }
    var searchQuery by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableStateOf<FileCategory?>(null) }
    var sortAscending by remember { mutableStateOf(false) }

    LaunchedEffect(selectedCategory) {
        items = dbHelper.getDiscoveredItems(category = selectedCategory, limit = 250)
    }

    val filteredItems = remember(items, searchQuery, sortAscending) {
        val filtered = if (searchQuery.isBlank()) items else {
            items.filter { it.displayName.contains(searchQuery, ignoreCase = true) }
        }
        if (sortAscending) filtered.sortedBy { it.dateModifiedMs }
        else filtered.sortedByDescending { it.dateModifiedMs }
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Storage Explorer",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack,
                actions = {
                    IconButton(onClick = { sortAscending = !sortAscending }) {
                        Icon(
                            imageVector = if (sortAscending) Icons.Default.ArrowUpward else Icons.Default.ArrowDownward,
                            contentDescription = "Sort Date"
                        )
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
            // Search Input
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                placeholder = { Text("Search discovered files...") },
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
                singleLine = true,
                shape = RoundedCornerShape(12.dp)
            )

            // Category Filter Row
            LazyRow(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                item {
                    FilterChip(
                        selected = selectedCategory == null,
                        onClick = { selectedCategory = null },
                        label = { Text("All Files") }
                    )
                }
                items(FileCategory.values()) { cat ->
                    FilterChip(
                        selected = selectedCategory == cat,
                        onClick = { selectedCategory = if (selectedCategory == cat) null else cat },
                        label = { Text(cat.displayName) }
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            if (filteredItems.isEmpty()) {
                EmptyStateView(
                    icon = Icons.Default.SearchOff,
                    title = "No Files Found",
                    description = "Run a scan from the dashboard to discover accessible files on this device."
                )
            } else {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    items(filteredItems) { item ->
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
fun FolderBrowserScreen(
    onNavigateBack: () -> Unit,
    onStartTreeScan: (Uri) -> Unit
) {
    var selectedTreeUri by remember { mutableStateOf<Uri?>(null) }

    val folderPicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocumentTree()
    ) { uri ->
        if (uri != null) {
            selectedTreeUri = uri
        }
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "Folder Browser (SAF)",
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
                        .clip(RoundedCornerShape(16.dp))
                        .background(BrandCyan.copy(alpha = 0.15f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(imageVector = Icons.Default.FolderOpen, contentDescription = null, tint = BrandCyan, modifier = Modifier.size(44.dp))
                }
                Spacer(modifier = Modifier.height(20.dp))
                Text(
                    text = "Select Folder for Custom Scanning",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(10.dp))
                Text(
                    text = "Use Android's official Storage Access Framework (SAF) to pick a folder on internal storage or an external SD card. RecoverX will inspect files and binary signatures recursively.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.7f),
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
                Spacer(modifier = Modifier.height(20.dp))

                OutlinedButton(
                    onClick = { folderPicker.launch(null) },
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(imageVector = Icons.Default.CreateNewFolder, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(if (selectedTreeUri != null) "Change Selected Folder" else "Pick Folder...")
                }

                if (selectedTreeUri != null) {
                    Spacer(modifier = Modifier.height(14.dp))
                    Text(
                        text = "Selected: ${selectedTreeUri?.lastPathSegment}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = BrandCyan,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }

            Button(
                onClick = {
                    selectedTreeUri?.let { onStartTreeScan(it) }
                },
                enabled = selectedTreeUri != null,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = BrandCyan)
            ) {
                Text("Start Deep Scan on Folder", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun CategoryBrowserScreen(
    categoryName: String,
    dbHelper: RecoverXDatabaseHelper,
    onNavigateBack: () -> Unit,
    onNavigateImagePreview: (Long) -> Unit,
    onNavigateVideoPreview: (Long) -> Unit,
    onNavigateItemDetails: (Long) -> Unit
) {
    val category = remember(categoryName) {
        when (categoryName.lowercase(Locale.ROOT)) {
            "photos", "images" -> FileCategory.IMAGES
            "videos" -> FileCategory.VIDEOS
            "audio" -> FileCategory.AUDIO
            "documents" -> FileCategory.DOCUMENTS
            "archives" -> FileCategory.ARCHIVES
            "downloads" -> FileCategory.DOWNLOADS
            else -> FileCategory.OTHER
        }
    }

    var items by remember { mutableStateOf<List<DiscoveredItem>>(emptyList()) }

    LaunchedEffect(category) {
        items = dbHelper.getDiscoveredItems(category = category, limit = 200)
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = category.displayName,
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        if (items.isEmpty()) {
            EmptyStateView(
                icon = Icons.Default.Folder,
                title = "No ${category.displayName} Discovered",
                description = "Run a scan from the home dashboard to discover files in this category.",
                modifier = Modifier.padding(padding)
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
