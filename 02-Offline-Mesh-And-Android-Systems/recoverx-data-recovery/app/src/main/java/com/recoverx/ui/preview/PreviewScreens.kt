package com.recoverx.ui.preview

import android.content.Intent
import android.net.Uri
import androidx.annotation.OptIn
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.rememberTransformableState
import androidx.compose.foundation.gestures.transformable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.media3.common.MediaItem
import androidx.media3.common.util.UnstableApi
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import coil.compose.AsyncImage
import com.recoverx.core.storage.StorageInspector
import com.recoverx.data.database.RecoverXDatabaseHelper
import com.recoverx.data.entities.CandidateClassification
import com.recoverx.data.entities.DiscoveredItem
import com.recoverx.data.entities.FileCategory
import com.recoverx.scanner.DuplicateDetector
import com.recoverx.ui.components.CandidateStatusBadge
import com.recoverx.ui.components.RecoverXTopBar
import com.recoverx.ui.theme.BrandAmber
import com.recoverx.ui.theme.BrandCyan
import com.recoverx.ui.theme.BrandEmerald
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun ImagePreviewScreen(
    itemId: Long,
    dbHelper: RecoverXDatabaseHelper,
    onNavigateBack: () -> Unit,
    onNavigateRestore: (Long) -> Unit
) {
    val context = LocalContext.current
    var item by remember { mutableStateOf<DiscoveredItem?>(null) }

    LaunchedEffect(itemId) {
        item = dbHelper.getDiscoveredItemById(itemId)
            ?: dbHelper.getDiscoveredItems(category = FileCategory.IMAGES, limit = 100).firstOrNull()
    }

    var scale by remember { mutableFloatStateOf(1f) }
    var offset by remember { mutableStateOf(Offset.Zero) }

    val transformState = rememberTransformableState { zoomChange, panChange, _ ->
        scale = (scale * zoomChange).coerceIn(1f, 5f)
        offset += panChange
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = item?.displayName ?: "Image Preview",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack,
                actions = {
                    item?.let { currentItem ->
                        IconButton(onClick = {
                            try {
                                val shareIntent = Intent(Intent.ACTION_SEND).apply {
                                    type = currentItem.mimeType
                                    putExtra(Intent.EXTRA_STREAM, Uri.parse(currentItem.uriString))
                                    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                                }
                                context.startActivity(Intent.createChooser(shareIntent, "Share Image"))
                            } catch (e: Exception) {
                                // Fallback if direct file uri cannot be shared without provider
                            }
                        }) {
                            Icon(Icons.Default.Share, contentDescription = "Share")
                        }
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(Color.Black)
        ) {
            item?.let { currentItem ->
                if (currentItem.classification == CandidateClassification.THUMBNAIL_ONLY) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(BrandAmber.copy(alpha = 0.85f))
                            .padding(8.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "Cached Thumbnail Only — Original High-Res Media Deleted / Unavailable",
                            style = MaterialTheme.typography.labelSmall,
                            color = Color.Black,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                Box(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .transformable(state = transformState),
                    contentAlignment = Alignment.Center
                ) {
                    coil.compose.SubcomposeAsyncImage(
                        model = coil.request.ImageRequest.Builder(LocalContext.current)
                            .data(currentItem.uriString)
                            .crossfade(true)
                            .build(),
                        contentDescription = currentItem.displayName,
                        contentScale = ContentScale.Fit,
                        loading = {
                            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                CircularProgressIndicator(color = BrandCyan)
                            }
                        },
                        error = {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Icon(Icons.Default.BrokenImage, contentDescription = null, tint = Color.Gray, modifier = Modifier.size(64.dp))
                                Spacer(modifier = Modifier.height(8.dp))
                                Text("Unable to render image thumbnail", color = Color.Gray, style = MaterialTheme.typography.bodySmall)
                            }
                        },
                        modifier = Modifier
                            .fillMaxSize()
                            .graphicsLayer(
                                scaleX = scale,
                                scaleY = scale,
                                translationX = offset.x,
                                translationY = offset.y
                            )
                    )
                }

                Surface(
                    color = MaterialTheme.colorScheme.surface,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = currentItem.displayName,
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                maxLines = 1,
                                overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "${StorageInspector.formatBytes(currentItem.sizeBytes)} • ${currentItem.classification.title}",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                            )
                        }

                        Spacer(modifier = Modifier.width(12.dp))

                        Button(
                            onClick = { onNavigateRestore(currentItem.id) },
                            shape = RoundedCornerShape(10.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = BrandCyan)
                        ) {
                            Icon(Icons.Default.Restore, contentDescription = null)
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Restore")
                        }
                    }
                }
            } ?: run {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(color = BrandCyan)
                }
            }
        }
    }
}

@OptIn(UnstableApi::class)
@Composable
fun VideoPreviewScreen(
    itemId: Long,
    dbHelper: RecoverXDatabaseHelper,
    onNavigateBack: () -> Unit,
    onNavigateRestore: (Long) -> Unit
) {
    val context = LocalContext.current
    var item by remember { mutableStateOf<DiscoveredItem?>(null) }
    var exoPlayer by remember { mutableStateOf<ExoPlayer?>(null) }

    LaunchedEffect(itemId) {
        val found = dbHelper.getDiscoveredItemById(itemId)
            ?: dbHelper.getDiscoveredItems(category = FileCategory.VIDEOS, limit = 100).firstOrNull()
        item = found

        if (found != null) {
            val player = ExoPlayer.Builder(context).build().apply {
                val mediaItem = MediaItem.fromUri(Uri.parse(found.uriString))
                setMediaItem(mediaItem)
                prepare()
                playWhenReady = true
            }
            exoPlayer = player
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            exoPlayer?.release()
        }
    }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = item?.displayName ?: "Video Preview",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(Color.Black)
        ) {
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                exoPlayer?.let { player ->
                    AndroidView(
                        factory = { ctx ->
                            PlayerView(ctx).apply {
                                this.player = player
                                useController = true
                            }
                        },
                        modifier = Modifier.fillMaxSize()
                    )
                } ?: run {
                    CircularProgressIndicator(color = BrandCyan)
                }
            }

            item?.let { currentItem ->
                Surface(
                    color = MaterialTheme.colorScheme.surface,
                    modifier = Modifier.fillMaxWidth()
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
                                text = currentItem.displayName,
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = StorageInspector.formatBytes(currentItem.sizeBytes),
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                            )
                        }

                        Button(
                            onClick = { onNavigateRestore(currentItem.id) },
                            shape = RoundedCornerShape(10.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = BrandCyan)
                        ) {
                            Icon(Icons.Default.Restore, contentDescription = null)
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Restore")
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun FileDetailsScreen(
    itemId: Long,
    dbHelper: RecoverXDatabaseHelper,
    onNavigateBack: () -> Unit,
    onNavigatePreview: (DiscoveredItem) -> Unit,
    onNavigateRestore: (Long) -> Unit
) {
    val context = LocalContext.current
    var item by remember { mutableStateOf<DiscoveredItem?>(null) }
    var sha256Hash by remember { mutableStateOf<String?>("Computing...") }

    LaunchedEffect(itemId) {
        val found = dbHelper.getDiscoveredItemById(itemId)
            ?: dbHelper.getDiscoveredItems(limit = 100).firstOrNull()
        item = found
        if (found != null) {
            sha256Hash = DuplicateDetector.computeSha256(context, Uri.parse(found.uriString)) ?: "Unavailable"
        }
    }

    val dateFormat = remember { SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()) }

    Scaffold(
        topBar = {
            RecoverXTopBar(
                title = "File Details & Forensics",
                canNavigateBack = true,
                onNavigateBack = onNavigateBack
            )
        }
    ) { padding ->
        item?.let { currentItem ->
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
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = currentItem.displayName,
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.weight(1f)
                            )
                            CandidateStatusBadge(classification = currentItem.classification)
                        }

                        HorizontalDivider()

                        DetailRow("Category", currentItem.category.displayName)
                        DetailRow("MIME Type", currentItem.mimeType)
                        DetailRow("File Size", StorageInspector.formatBytes(currentItem.sizeBytes))
                        DetailRow("Modified", dateFormat.format(Date(currentItem.dateModifiedMs)))
                        DetailRow("Classification", currentItem.classification.title)
                        DetailRow("Readability", currentItem.readability.name)
                        DetailRow("Relative Path", currentItem.relativePath ?: "Root / Unknown")
                        DetailRow("Detected Extension", currentItem.detectedExtension ?: "None")

                        if (currentItem.isMimeMismatch) {
                            DetailRow("MIME Mismatch", "YES (Header signature differs from extension)")
                        }

                        DetailRow("SHA-256 Hash", sha256Hash ?: "Calculating...")
                    }
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    if (currentItem.category == FileCategory.IMAGES || currentItem.category == FileCategory.VIDEOS) {
                        OutlinedButton(
                            onClick = { onNavigatePreview(currentItem) },
                            modifier = Modifier.weight(1f).height(48.dp),
                            shape = RoundedCornerShape(10.dp)
                        ) {
                            Icon(Icons.Default.Visibility, contentDescription = null)
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Preview")
                        }
                    }

                    Button(
                        onClick = { onNavigateRestore(currentItem.id) },
                        modifier = Modifier.weight(1f).height(48.dp),
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = BrandCyan)
                    ) {
                        Icon(Icons.Default.Restore, contentDescription = null)
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Restore File")
                    }
                }
            }
        } ?: run {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = BrandCyan)
            }
        }
    }
}

@Composable
private fun DetailRow(label: String, value: String) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(text = label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
        Text(text = value, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
    }
}
