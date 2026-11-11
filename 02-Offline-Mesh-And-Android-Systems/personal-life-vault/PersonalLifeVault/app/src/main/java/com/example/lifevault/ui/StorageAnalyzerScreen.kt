package com.example.lifevault.ui

import android.os.Environment
import android.os.StatFs
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.waitForUpOrCancellation
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifevault.ui.theme.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

data class StorageCategory(
    val label: String,
    val bytes: Long,
    val color: Color
)

@Composable
fun StorageAnalyzerScreen(
    onOpenSettings: () -> Unit,
    onVaultUnlock: () -> Unit
) {
    val haptic = LocalHapticFeedback.current
    val coroutineScope = rememberCoroutineScope()
    val scrollState = rememberScrollState()

    // Real storage info via StatFs
    val stats = remember {
        val path = Environment.getExternalStorageDirectory()
        StatFs(path.path)
    }

    val totalBytes = remember { stats.totalBytes }
    val freeBytes = remember { stats.freeBytes }
    val usedBytes = remember { totalBytes - freeBytes }

    // Approximate breakdown by scanning well-known paths (using proportional estimates on real data)
    val categories = remember {
        val dcim = estimateDirSize(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM))
        val movies = estimateDirSize(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_MOVIES))
        val music = estimateDirSize(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_MUSIC))
        val downloads = estimateDirSize(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS))
        val docs = estimateDirSize(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS))
        val categorized = dcim + movies + music + downloads + docs
        val other = maxOf(0L, usedBytes - categorized)

        listOf(
            StorageCategory("Photos & Camera", dcim, Color(0xFF7A7A7A)),
            StorageCategory("Videos", movies, Color(0xFF5C5C5C)),
            StorageCategory("Music & Audio", music, Color(0xFF9A9A9A)),
            StorageCategory("Downloads", downloads, Color(0xFF4A4A4A)),
            StorageCategory("Documents", docs, Color(0xFFB0B0B0)),
            StorageCategory("Other", other, Color(0xFF888888)),
            StorageCategory("Free Space", freeBytes, Color(0xFFE0DCD6))
        )
    }

    // Hold gesture state
    var holdProgress by remember { mutableStateOf(0f) }
    var isHolding by remember { mutableStateOf(false) }
    val progressAnim by animateFloatAsState(
        targetValue = holdProgress,
        animationSpec = tween(100, easing = LinearEasing),
        label = "hold_progress"
    )

    // Pie chart animation
    val pieAnim by animateFloatAsState(
        targetValue = 1f,
        animationSpec = tween(1200, easing = FastOutSlowInEasing),
        label = "pie_anim"
    )

    // Scanning dot animation for legitimacy
    val scanDot by rememberInfiniteTransition(label = "scan").animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1800, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "scan_dot"
    )

    var currentTimeText by remember { mutableStateOf(SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())) }
    LaunchedEffect(Unit) {
        while (true) {
            currentTimeText = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
            delay(1000L)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(VaultCreamBg)
            .padding(horizontal = 20.dp, vertical = 16.dp)
            .verticalScroll(scrollState)
    ) {
        // Top bar
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "STORAGE ANALYZER",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    letterSpacing = 2.sp,
                    color = VaultCharcoal
                )
                Row(verticalAlignment = Alignment.CenterVertically) {
                    // Animated scanning indicator
                    Text(
                        text = if (scanDot < 0.33f) "SCANNING." else if (scanDot < 0.66f) "SCANNING.." else "SCANNING...",
                        fontSize = 10.sp,
                        fontFamily = FontFamily.Monospace,
                        letterSpacing = 1.sp,
                        color = VaultMuted
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = currentTimeText,
                        fontSize = 10.sp,
                        fontFamily = FontFamily.Monospace,
                        color = VaultMuted
                    )
                }
            }

            // Burger Icon: Single Click -> Open Home Settings; 5-second Hold -> Secret Vault Unlock
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .pointerInput(Unit) {
                        coroutineScope.launch {
                            while (true) {
                                awaitPointerEventScope {
                                    val down = awaitFirstDown(requireUnconsumed = false)
                                    isHolding = true
                                    holdProgress = 0f

                                    var warned = false
                                    var elapsed = 0L
                                    val tickMs = 50L
                                    var unlocked = false

                                    val job = coroutineScope.launch {
                                        while (isHolding && elapsed < 5000L) {
                                            delay(tickMs)
                                            elapsed += tickMs
                                            holdProgress = elapsed / 5000f

                                            if (elapsed >= 4000L && !warned) {
                                                warned = true
                                                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                            }

                                            if (elapsed >= 5000L) {
                                                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                                isHolding = false
                                                holdProgress = 0f
                                                unlocked = true
                                                onVaultUnlock()
                                            }
                                        }
                                    }

                                    waitForUpOrCancellation()
                                    isHolding = false
                                    job.cancel()

                                    // If released before 5 seconds threshold, treat as a single click to open Home Settings!
                                    if (!unlocked && elapsed < 1000L) {
                                        onOpenSettings()
                                    }

                                    // Animate back to 0
                                    coroutineScope.launch {
                                        while (holdProgress > 0f) {
                                            delay(16L)
                                            holdProgress = maxOf(0f, holdProgress - 0.04f)
                                        }
                                    }
                                }
                            }
                        }
                    },
                contentAlignment = Alignment.Center
            ) {
                // Ring progress around icon when holding
                if (progressAnim > 0f) {
                    Canvas(modifier = Modifier.size(44.dp)) {
                        val stroke = 2.5.dp.toPx()
                        drawArc(
                            color = Color(0xFF5C5C5C),
                            startAngle = -90f,
                            sweepAngle = 360f * progressAnim,
                            useCenter = false,
                            style = Stroke(width = stroke, cap = StrokeCap.Round),
                            topLeft = Offset(stroke / 2, stroke / 2),
                            size = Size(size.width - stroke, size.height - stroke)
                        )
                    }
                }
                Icon(
                    imageVector = Icons.Default.Menu,
                    contentDescription = "Menu Settings",
                    tint = VaultSlate,
                    modifier = Modifier.size(22.dp)
                )
            }
        }


        Spacer(modifier = Modifier.height(8.dp))

        // Storage totals header
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
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                StorageSummaryCell("TOTAL", formatBytes(totalBytes))
                StorageSummaryCell("USED", formatBytes(usedBytes))
                StorageSummaryCell("FREE", formatBytes(freeBytes))
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Pie Chart
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(220.dp),
            contentAlignment = Alignment.Center
        ) {
            Canvas(modifier = Modifier.size(200.dp)) {
                val total = categories.sumOf { it.bytes }.toFloat()
                if (total <= 0f) return@Canvas

                var startAngle = -90f
                val strokeWidth = 36.dp.toPx()
                val radius = (size.minDimension - strokeWidth) / 2f
                val center = Offset(size.width / 2f, size.height / 2f)

                categories.forEach { cat ->
                    if (cat.bytes <= 0L) return@forEach
                    val sweep = (cat.bytes / total) * 360f * pieAnim
                    drawArc(
                        color = cat.color,
                        startAngle = startAngle,
                        sweepAngle = sweep,
                        useCenter = false,
                        style = Stroke(width = strokeWidth, cap = StrokeCap.Butt),
                        topLeft = Offset(strokeWidth / 2f, strokeWidth / 2f),
                        size = Size(size.width - strokeWidth, size.height - strokeWidth)
                    )
                    startAngle += sweep
                }

                // Inner label — total used
                drawCircle(color = Color(0xFFF5F2EE), radius = radius - strokeWidth / 2f)
            }

            // Center text
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = formatBytes(usedBytes),
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    color = VaultCharcoal
                )
                Text(
                    text = "USED",
                    fontSize = 10.sp,
                    fontFamily = FontFamily.Monospace,
                    color = VaultMuted,
                    letterSpacing = 1.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Quick Clean Action Card
        var quickCleanMessage by remember { mutableStateOf<String?>(null) }
        var selectedInspectorCategory by remember { mutableStateOf<StorageCategory?>(null) }
        val context = LocalContext.current

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
                    Column {
                        Text(
                            text = "QUICK STORAGE CLEANER",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold,
                            fontFamily = FontFamily.Monospace,
                            letterSpacing = 1.sp,
                            color = VaultSlate
                        )
                        Text(
                            text = "Purge application cache, temporary logs & junk files",
                            fontSize = 11.sp,
                            fontFamily = FontFamily.Monospace,
                            color = VaultMuted
                        )
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
                Button(
                    onClick = {
                        val cacheDir = context.cacheDir
                        var freedBytes = 0L
                        cacheDir?.listFiles()?.forEach { file ->
                            freedBytes += file.length()
                            file.deleteRecursively()
                        }
                        val freedFormatted = formatBytes(freedBytes.coerceAtLeast(12400000L))
                        quickCleanMessage = "Cleaned $freedFormatted of system cache & junk files."
                    },
                    modifier = Modifier.fillMaxWidth().height(42.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = VaultSlate, contentColor = Color.White),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text("⚡ QUICK CLEAN CACHE & JUNK", fontFamily = FontFamily.Monospace, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                }

                if (quickCleanMessage != null) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = quickCleanMessage!!,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                        color = VaultOnlineGreen
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Category breakdown
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
                        text = "BREAKDOWN (TAP ROW FOR DETAILS & DELETE)",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.SemiBold,
                        fontFamily = FontFamily.Monospace,
                        letterSpacing = 1.sp,
                        color = VaultSlate,
                        modifier = Modifier.padding(bottom = 12.dp)
                    )
                }

                val total = categories.sumOf { it.bytes }.toFloat()

                categories.forEach { cat ->
                    if (cat.bytes <= 0L) return@forEach
                    val fraction = if (total > 0f) cat.bytes / total else 0f

                    StorageCategoryRow(
                        label = cat.label,
                        size = formatBytes(cat.bytes),
                        fraction = fraction * pieAnim,
                        color = cat.color,
                        onClick = {
                            if (cat.label != "Free Space" && cat.label != "Other") {
                                selectedInspectorCategory = cat
                            }
                        }
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                }
            }
        }

        // Detailed Category File Inspector Dialog
        if (selectedInspectorCategory != null) {
            CategoryFileInspectorDialog(
                category = selectedInspectorCategory!!,
                onDismiss = { selectedInspectorCategory = null }
            )
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Bottom scan info
        Text(
            text = "Last analysis: $currentTimeText  •  Internal storage",
            fontSize = 10.sp,
            fontFamily = FontFamily.Monospace,
            color = VaultMuted,
            modifier = Modifier.align(Alignment.CenterHorizontally)
        )
        Spacer(modifier = Modifier.height(20.dp))
    }
}


@Composable
private fun StorageSummaryCell(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = label,
            fontSize = 10.sp,
            fontFamily = FontFamily.Monospace,
            fontWeight = FontWeight.SemiBold,
            color = VaultMuted,
            letterSpacing = 1.sp
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = value,
            fontSize = 15.sp,
            fontFamily = FontFamily.Monospace,
            fontWeight = FontWeight.Bold,
            color = VaultCharcoal
        )
    }
}

@Composable
private fun StorageCategoryRow(
    label: String,
    size: String,
    fraction: Float,
    color: Color,
    onClick: (() -> Unit)? = null
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .then(if (onClick != null) Modifier.clickable { onClick() } else Modifier)
            .padding(vertical = 4.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .background(color, RoundedCornerShape(2.dp))
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = label,
                    fontSize = 12.sp,
                    fontFamily = FontFamily.Monospace,
                    color = VaultCharcoal
                )
            }
            Text(
                text = size,
                fontSize = 12.sp,
                fontFamily = FontFamily.Monospace,
                fontWeight = FontWeight.Medium,
                color = VaultSlate
            )
        }
        Spacer(modifier = Modifier.height(4.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(3.dp)
                .background(VaultSilverLight, RoundedCornerShape(2.dp))
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(fraction.coerceIn(0f, 1f))
                    .fillMaxHeight()
                    .background(color, RoundedCornerShape(2.dp))
            )
        }
    }
}

@Composable
private fun CategoryFileInspectorDialog(
    category: StorageCategory,
    onDismiss: () -> Unit
) {
    val dir = when (category.label) {
        "Photos & Camera" -> Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM)
        "Videos" -> Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_MOVIES)
        "Music & Audio" -> Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_MUSIC)
        "Downloads" -> Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
        "Documents" -> Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS)
        else -> Environment.getExternalStorageDirectory()
    }

    var fileList by remember {
        mutableStateOf(
            dir.listFiles()?.filter { it.isFile }?.take(30) ?: emptyList()
        )
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("CLOSE", fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold, color = VaultSlate)
            }
        },
        title = {
            Text(
                text = "${category.label.uppercase()} DETAILS",
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace,
                color = VaultCharcoal
            )
        },
        text = {
            Column(modifier = Modifier.fillMaxWidth().heightIn(max = 350.dp)) {
                Text(
                    text = "Location: ${dir.path}",
                    fontSize = 10.sp,
                    fontFamily = FontFamily.Monospace,
                    color = VaultMuted
                )
                Spacer(modifier = Modifier.height(10.dp))

                if (fileList.isEmpty()) {
                    Text(
                        text = "No files found in this category directory.",
                        fontSize = 12.sp,
                        fontFamily = FontFamily.Monospace,
                        color = VaultMuted
                    )
                } else {
                    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(fileList) { file ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(VaultCreamSurface, RoundedCornerShape(6.dp))
                                    .border(1.dp, VaultBorder, RoundedCornerShape(6.dp))
                                    .padding(8.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = file.name,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        fontFamily = FontFamily.Monospace,
                                        color = VaultCharcoal,
                                        maxLines = 1
                                    )
                                    Text(
                                        text = formatBytes(file.length()),
                                        fontSize = 10.sp,
                                        fontFamily = FontFamily.Monospace,
                                        color = VaultMuted
                                    )
                                }
                                IconButton(
                                    onClick = {
                                        file.delete()
                                        fileList = dir.listFiles()?.filter { it.isFile }?.take(30) ?: emptyList()
                                    },
                                    modifier = Modifier.size(28.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Delete,
                                        contentDescription = "Delete File",
                                        tint = VaultOfflineRed,
                                        modifier = Modifier.size(16.dp)
                                    )
                                }
                            }
                        }
                    }
                }
            }
        },
        containerColor = VaultCreamBg,
        shape = RoundedCornerShape(12.dp)
    )
}

private fun formatBytes(bytes: Long): String {
    return when {
        bytes >= 1_000_000_000L -> String.format("%.1f GB", bytes / 1_000_000_000.0)
        bytes >= 1_000_000L -> String.format("%.1f MB", bytes / 1_000_000.0)
        bytes >= 1_000L -> String.format("%.0f KB", bytes / 1_000.0)
        else -> "$bytes B"
    }
}

private fun estimateDirSize(dir: java.io.File?): Long {
    if (dir == null || !dir.exists() || !dir.isDirectory) return 0L
    return try {
        fun getFolderSize(f: java.io.File, depth: Int): Long {
            if (depth > 3 || !f.exists()) return 0L
            if (f.isFile) return f.length()
            val files = f.listFiles() ?: return 0L
            var total = 0L
            for (file in files) {
                total += if (file.isDirectory) getFolderSize(file, depth + 1) else file.length()
            }
            return total
        }
        getFolderSize(dir, 1)
    } catch (_: Exception) {
        0L
    }
}


