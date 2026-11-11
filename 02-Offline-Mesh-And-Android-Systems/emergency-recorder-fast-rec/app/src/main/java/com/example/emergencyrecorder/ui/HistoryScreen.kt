package com.example.emergencyrecorder.ui

import android.content.Context
import android.content.Intent
import android.media.MediaPlayer
import android.net.Uri
import android.text.format.Formatter
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.FastForward
import androidx.compose.material.icons.filled.FastRewind
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.emergencyrecorder.storage.RecordingItem
import com.example.emergencyrecorder.storage.RecordingStorage
import com.example.emergencyrecorder.ui.theme.EmergencyRed
import kotlinx.coroutines.delay
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun HistoryScreen(onBack: () -> Unit) {
    val context = LocalContext.current

    var recordings by remember { mutableStateOf<List<RecordingItem>>(emptyList()) }
    var playingUri by remember { mutableStateOf<Uri?>(null) }
    var isPlaying by remember { mutableStateOf(false) }
    var currentProgressMs by remember { mutableIntStateOf(0) }
    var currentDurationMs by remember { mutableIntStateOf(0) }

    var itemToDelete by remember { mutableStateOf<RecordingItem?>(null) }

    val mediaPlayer = remember { MediaPlayer() }

    fun refreshList() {
        recordings = RecordingStorage.queryAllRecordings(context)
    }

    LaunchedEffect(Unit) {
        refreshList()
    }

    // Playback progress ticker
    LaunchedEffect(isPlaying) {
        while (isPlaying) {
            try {
                if (mediaPlayer.isPlaying) {
                    currentProgressMs = mediaPlayer.currentPosition
                }
            } catch (ignored: Exception) {}
            delay(150)
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            try {
                if (mediaPlayer.isPlaying) mediaPlayer.stop()
                mediaPlayer.release()
            } catch (ignored: Exception) {}
        }
    }

    fun playAudio(uri: Uri, itemDuration: Long) {
        try {
            if (playingUri == uri && isPlaying) {
                mediaPlayer.pause()
                isPlaying = false
                return
            }

            if (playingUri == uri && !isPlaying) {
                // If it reached completion, start from beginning
                if (currentDurationMs > 0 && currentProgressMs >= currentDurationMs - 500) {
                    mediaPlayer.seekTo(0)
                    currentProgressMs = 0
                }
                mediaPlayer.start()
                isPlaying = true
                return
            }

            mediaPlayer.reset()
            mediaPlayer.setDataSource(context, uri)
            mediaPlayer.prepare()
            mediaPlayer.start()

            playingUri = uri
            isPlaying = true
            val dur = mediaPlayer.duration
            currentDurationMs = if (dur > 0) dur else itemDuration.toInt()
            currentProgressMs = 0

            mediaPlayer.setOnCompletionListener {
                isPlaying = false
                currentProgressMs = currentDurationMs
            }
        } catch (e: Exception) {
            isPlaying = false
            playingUri = null
        }
    }

    fun seekTo(positionMs: Int) {
        try {
            val target = positionMs.coerceIn(0, currentDurationMs)
            mediaPlayer.seekTo(target)
            currentProgressMs = target
        } catch (ignored: Exception) {}
    }

    fun seekBy(deltaMs: Int) {
        try {
            val current = try { mediaPlayer.currentPosition } catch (e: Exception) { currentProgressMs }
            val target = (current + deltaMs).coerceIn(0, currentDurationMs)
            mediaPlayer.seekTo(target)
            currentProgressMs = target
        } catch (ignored: Exception) {}
    }

    fun shareAudio(uri: Uri) {
        val shareIntent = Intent(Intent.ACTION_SEND).apply {
            type = "audio/mp4"
            putExtra(Intent.EXTRA_STREAM, uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        context.startActivity(Intent.createChooser(shareIntent, "Share Emergency Recording"))
    }

    Scaffold(
        topBar = {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 8.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(onClick = onBack) {
                        Icon(imageVector = Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Recording History",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                }
                IconButton(onClick = { refreshList() }) {
                    Icon(imageVector = Icons.Default.Refresh, contentDescription = "Refresh")
                }
            }
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            if (recordings.isEmpty()) {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = "No recordings found",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.6f)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Double-press Volume Down to capture emergency audio. Recordings will appear here automatically.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.4f)
                    )
                }
            } else {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    items(recordings, key = { it.id }) { item ->
                        val isSelected = playingUri == item.uri
                        RecordingListItem(
                            item = item,
                            isSelectedForPlayback = isSelected,
                            isPlaying = isSelected && isPlaying,
                            progressMs = if (isSelected) currentProgressMs else 0,
                            durationMs = if (isSelected) currentDurationMs else item.durationMs.toInt(),
                            onTogglePlay = { playAudio(item.uri, item.durationMs) },
                            onSeekTo = { seekTo(it) },
                            onSeekBy = { seekBy(it) },
                            onShare = { shareAudio(item.uri) },
                            onDelete = { itemToDelete = item }
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                    }
                }
            }
        }
    }

    // Delete Confirmation Dialog
    if (itemToDelete != null) {
        val target = itemToDelete!!
        AlertDialog(
            onDismissRequest = { itemToDelete = null },
            title = { Text(text = "Delete Recording?") },
            text = { Text(text = "Are you sure you want to permanently delete '${target.displayName}'?") },
            confirmButton = {
                TextButton(
                    onClick = {
                        if (playingUri == target.uri) {
                            try {
                                if (mediaPlayer.isPlaying) mediaPlayer.stop()
                                isPlaying = false
                                playingUri = null
                            } catch (ignored: Exception) {}
                        }
                        RecordingStorage.deleteAudioFile(context, target.uri)
                        itemToDelete = null
                        refreshList()
                    }
                ) {
                    Text(text = "Delete", color = EmergencyRed, fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { itemToDelete = null }) {
                    Text(text = "Cancel")
                }
            }
        )
    }
}

@Composable
private fun RecordingListItem(
    item: RecordingItem,
    isSelectedForPlayback: Boolean,
    isPlaying: Boolean,
    progressMs: Int,
    durationMs: Int,
    onTogglePlay: () -> Unit,
    onSeekTo: (Int) -> Unit,
    onSeekBy: (Int) -> Unit,
    onShare: () -> Unit,
    onDelete: () -> Unit
) {
    val context = LocalContext.current
    val dateStr = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
        .format(Date(item.dateAddedMs))

    val sizeStr = Formatter.formatFileSize(context, item.sizeBytes)

    var isDragging by remember { mutableStateOf(false) }
    var dragValue by remember { mutableFloatStateOf(0f) }

    val safeDuration = if (durationMs > 0) durationMs.toFloat() else 1f
    val currentPosition = if (isDragging) dragValue else progressMs.toFloat().coerceIn(0f, safeDuration)

    Card(
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelectedForPlayback)
                MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.25f)
            else
                MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = if (isSelectedForPlayback) 4.dp else 1.5.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            // Header Row: File Details + Share/Delete
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = item.displayName,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 15.sp
                    )
                    Spacer(modifier = Modifier.height(3.dp))
                    Text(
                        text = "$dateStr  •  $sizeStr",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (!isSelectedForPlayback) {
                        IconButton(onClick = onTogglePlay) {
                            Icon(
                                imageVector = Icons.Default.PlayArrow,
                                contentDescription = "Play",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(28.dp)
                            )
                        }
                    }

                    IconButton(onClick = onShare) {
                        Icon(
                            imageVector = Icons.Default.Share,
                            contentDescription = "Share",
                            modifier = Modifier.size(20.dp)
                        )
                    }

                    IconButton(onClick = onDelete) {
                        Icon(
                            imageVector = Icons.Default.Delete,
                            contentDescription = "Delete",
                            tint = EmergencyRed,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }
            }

            // Expanded Player Section (Scrubber + Seek Controls)
            if (isSelectedForPlayback) {
                Spacer(modifier = Modifier.height(10.dp))

                // Interactive Audio Slider (Seek bar)
                Slider(
                    value = currentPosition,
                    onValueChange = {
                        isDragging = true
                        dragValue = it
                    },
                    onValueChangeFinished = {
                        onSeekTo(dragValue.toInt())
                        isDragging = false
                    },
                    valueRange = 0f..safeDuration,
                    colors = SliderDefaults.colors(
                        thumbColor = MaterialTheme.colorScheme.primary,
                        activeTrackColor = MaterialTheme.colorScheme.primary
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                // Timestamp: Elapsed vs Total
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = formatTimeMs(if (isDragging) dragValue.toInt() else progressMs),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = formatTimeMs(durationMs),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                        fontWeight = FontWeight.Medium
                    )
                }

                // Audio Seek & Transport Buttons: -5s, Play/Pause, +5s
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 2.dp),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Rewind 5 seconds
                    IconButton(
                        onClick = { onSeekBy(-5000) },
                        modifier = Modifier.size(44.dp)
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                imageVector = Icons.Default.FastRewind,
                                contentDescription = "Rewind 5s",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(26.dp)
                            )
                            Text(
                                text = "-5s",
                                style = MaterialTheme.typography.labelSmall,
                                fontSize = 10.sp,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }
                    }

                    Spacer(modifier = Modifier.width(20.dp))

                    // Play / Pause Toggle
                    IconButton(
                        onClick = onTogglePlay,
                        modifier = Modifier.size(50.dp)
                    ) {
                        Icon(
                            imageVector = if (isPlaying) Icons.Default.Pause else Icons.Default.PlayArrow,
                            contentDescription = if (isPlaying) "Pause" else "Play",
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(36.dp)
                        )
                    }

                    Spacer(modifier = Modifier.width(20.dp))

                    // Fast Forward 5 seconds
                    IconButton(
                        onClick = { onSeekBy(5000) },
                        modifier = Modifier.size(44.dp)
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                imageVector = Icons.Default.FastForward,
                                contentDescription = "Forward 5s",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(26.dp)
                            )
                            Text(
                                text = "+5s",
                                style = MaterialTheme.typography.labelSmall,
                                fontSize = 10.sp,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }
                    }
                }
            }
        }
    }
}

private fun formatTimeMs(ms: Int): String {
    val totalSeconds = (ms / 1000).coerceAtLeast(0)
    val minutes = totalSeconds / 60
    val seconds = totalSeconds % 60
    return String.format(Locale.getDefault(), "%02d:%02d", minutes, seconds)
}
