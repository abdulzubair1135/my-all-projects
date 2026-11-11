package com.recoverx.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.recoverx.core.storage.StorageAssessment
import com.recoverx.core.storage.StorageInspector
import com.recoverx.data.entities.CandidateClassification
import com.recoverx.data.entities.DiscoveredItem
import com.recoverx.data.entities.FileCategory
import com.recoverx.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecoverXTopBar(
    title: String,
    canNavigateBack: Boolean = false,
    onNavigateBack: () -> Unit = {},
    actions: @Composable RowScope.() -> Unit = {}
) {
    TopAppBar(
        title = {
            Text(
                text = title,
                style = MaterialTheme.typography.titleLarge,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        },
        navigationIcon = {
            if (canNavigateBack) {
                IconButton(onClick = onNavigateBack) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = "Back"
                    )
                }
            }
        },
        actions = actions,
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = MaterialTheme.colorScheme.background,
            titleContentColor = MaterialTheme.colorScheme.onBackground
        )
    )
}

@Composable
fun StorageOverviewCard(
    assessment: StorageAssessment,
    modifier: Modifier = Modifier
) {
    val usedRatio = if (assessment.totalInternalBytes > 0) {
        (assessment.usedInternalBytes.toFloat() / assessment.totalInternalBytes.toFloat()).coerceIn(0f, 1f)
    } else 0f

    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Internal Storage",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${StorageInspector.formatBytes(assessment.availableInternalBytes)} free",
                    style = MaterialTheme.typography.bodyMedium,
                    color = BrandCyan
                )
            }

            Spacer(modifier = Modifier.height(10.dp))

            LinearProgressIndicator(
                progress = { usedRatio },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .clip(RoundedCornerShape(4.dp)),
                color = BrandCyan,
                trackColor = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.12f),
            )

            Spacer(modifier = Modifier.height(10.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Used: ${StorageInspector.formatBytes(assessment.usedInternalBytes)}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                )
                Text(
                    text = "Total: ${StorageInspector.formatBytes(assessment.totalInternalBytes)}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                )
            }

            if (assessment.hasRemovableStorage) {
                Spacer(modifier = Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.SdCard,
                        contentDescription = "SD Card",
                        tint = BrandEmerald,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "SD Card Mounted: ${assessment.removableVolumes.joinToString(", ")}",
                        style = MaterialTheme.typography.labelSmall,
                        color = BrandEmerald
                    )
                }
            }
        }
    }
}

@Composable
fun CandidateStatusBadge(classification: CandidateClassification) {
    val (bgColor, textColor, label) = when (classification) {
        CandidateClassification.EXISTING_FILE -> Triple(MaterialTheme.colorScheme.surfaceVariant, MaterialTheme.colorScheme.onSurfaceVariant, "Existing File")
        CandidateClassification.ALTERNATE_COPY -> Triple(BrandEmerald.copy(alpha = 0.2f), BrandEmerald, "Backup / Copy")
        CandidateClassification.THUMBNAIL_ONLY -> Triple(BrandAmber.copy(alpha = 0.2f), BrandAmber, "Thumbnail Only")
        CandidateClassification.MEDIA_TRASH -> Triple(BrandCyan.copy(alpha = 0.2f), BrandCyan, "Trash Item")
        CandidateClassification.SIGNATURE_CARVED -> Triple(BrandTeal.copy(alpha = 0.2f), BrandTeal, "Carved Header")
        CandidateClassification.CORRUPTED_FILE -> Triple(BrandRose.copy(alpha = 0.2f), BrandRose, "Corrupted")
        CandidateClassification.NOT_RECOVERABLE -> Triple(Color.Gray.copy(alpha = 0.2f), Color.Gray, "Unrecoverable")
    }

    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(6.dp))
            .background(bgColor)
            .padding(horizontal = 8.dp, vertical = 3.dp)
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = textColor,
            fontWeight = FontWeight.SemiBold
        )
    }
}

@Composable
fun DiscoveredItemRow(
    item: DiscoveredItem,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            val icon = when (item.category) {
                FileCategory.IMAGES -> Icons.Default.Image
                FileCategory.VIDEOS -> Icons.Default.Videocam
                FileCategory.AUDIO -> Icons.Default.Audiotrack
                FileCategory.DOCUMENTS -> Icons.Default.Description
                FileCategory.ARCHIVES -> Icons.Default.FolderZip
                FileCategory.DOWNLOADS -> Icons.Default.Download
                FileCategory.OTHER -> Icons.Default.InsertDriveFile
            }

            val isMedia = item.category == FileCategory.IMAGES ||
                    item.classification == CandidateClassification.THUMBNAIL_ONLY ||
                    item.category == FileCategory.VIDEOS

            Box(
                modifier = Modifier
                    .size(54.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(MaterialTheme.colorScheme.surfaceVariant),
                contentAlignment = Alignment.Center
            ) {
                if (isMedia && item.uriString.isNotBlank()) {
                    coil.compose.AsyncImage(
                        model = item.uriString,
                        contentDescription = item.displayName,
                        contentScale = androidx.compose.ui.layout.ContentScale.Crop,
                        modifier = Modifier.fillMaxSize()
                    )
                } else {
                    Icon(
                        imageVector = icon,
                        contentDescription = item.category.name,
                        tint = BrandCyan,
                        modifier = Modifier.size(26.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.displayName,
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Spacer(modifier = Modifier.height(2.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = StorageInspector.formatBytes(item.sizeBytes),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    CandidateStatusBadge(classification = item.classification)
                }
            }
        }
    }
}

@Composable
fun EmptyStateView(
    icon: ImageVector,
    title: String,
    description: String,
    modifier: Modifier = Modifier,
    actionButton: (@Composable () -> Unit)? = null
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(64.dp)
                .clip(CircleShape)
                .background(MaterialTheme.colorScheme.surfaceVariant),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(32.dp)
            )
        }
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = title,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            text = description,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
            modifier = Modifier.padding(horizontal = 16.dp),
            lineHeight = MaterialTheme.typography.bodyMedium.lineHeight
        )
        if (actionButton != null) {
            Spacer(modifier = Modifier.height(18.dp))
            actionButton()
        }
    }
}
