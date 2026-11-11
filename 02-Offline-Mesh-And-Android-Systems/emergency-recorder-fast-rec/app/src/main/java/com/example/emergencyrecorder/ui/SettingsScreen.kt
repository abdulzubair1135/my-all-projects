package com.example.emergencyrecorder.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
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
import com.example.emergencyrecorder.accessibility.BackgroundTriggerService
import com.example.emergencyrecorder.permissions.PermissionManager
import com.example.emergencyrecorder.settings.AppSettings
import kotlin.math.roundToLong

@Composable
fun SettingsScreen(onBack: () -> Unit) {
    val context = LocalContext.current
    val appSettings = remember { AppSettings.getInstance(context) }

    var shortcutEnabled by remember { mutableStateOf(appSettings.isShortcutEnabled) }
    var doublePressInterval by remember { mutableFloatStateOf(appSettings.doublePressIntervalMs.toFloat()) }
    var vibrationEnabled by remember { mutableStateOf(appSettings.isVibrationEnabled) }
    var selectedQuality by remember { mutableStateOf(appSettings.recordingQuality) }
    var autoStopMinutes by remember { mutableIntStateOf(appSettings.autoStopMinutes) }
    var autoCallRecording by remember { mutableStateOf(appSettings.isAutoCallRecordingEnabled) }
    var screenOffTriggerEnabled by remember { mutableStateOf(appSettings.isScreenOffTriggerEnabled) }
    var autoSpeakerOnCall by remember { mutableStateOf(appSettings.isAutoSpeakerOnCallEnabled) }
    var selectedCallSource by remember { mutableStateOf(appSettings.callAudioSource) }

    Scaffold(
        topBar = {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 8.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBack) {
                    Icon(imageVector = Icons.Default.ArrowBack, contentDescription = "Back")
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Settings",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp)
                .verticalScroll(rememberScrollState())
        ) {
            // Trigger Settings Card
            SettingsSectionHeader(title = "TRIGGER SHORTCUT")
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Emergency Shortcut",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                text = "Double-press Volume Down to toggle recording",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                            )
                        }
                        Switch(
                            checked = shortcutEnabled,
                            onCheckedChange = {
                                shortcutEnabled = it
                                appSettings.isShortcutEnabled = it
                            }
                        )
                    }

                    Divider(modifier = Modifier.padding(vertical = 12.dp), thickness = 0.5.dp)

                    // Interval Slider
                    Text(
                        text = "Double-Press Timing Window: ${doublePressInterval.toInt()} ms",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = "Shorter window prevents accidental triggers; longer window makes double-pressing easier.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                    Slider(
                        value = doublePressInterval,
                        onValueChange = {
                            doublePressInterval = it
                            appSettings.doublePressIntervalMs = it.roundToLong()
                        },
                        valueRange = 250f..800f,
                        steps = 10
                    )

                    Divider(modifier = Modifier.padding(vertical = 12.dp), thickness = 0.5.dp)

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Screen-Off Deep Sleep Trigger",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                text = "Enables hardware key interception when screen is dark. Note: Displays a Cast icon on Android 14/15.",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                            )
                        }
                        Switch(
                            checked = screenOffTriggerEnabled,
                            onCheckedChange = {
                                screenOffTriggerEnabled = it
                                appSettings.isScreenOffTriggerEnabled = it
                                if (it) {
                                    BackgroundTriggerService.start(context)
                                } else {
                                    BackgroundTriggerService.stop(context)
                                }
                            }
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Call Recording Card
            SettingsSectionHeader(title = "CALL RECORDING")
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Auto Record Phone Calls",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                text = "Automatically records calls tagged with caller's Name & Number",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                            )
                        }
                        Switch(
                            checked = autoCallRecording,
                            onCheckedChange = {
                                autoCallRecording = it
                                appSettings.isAutoCallRecordingEnabled = it
                            }
                        )
                    }

                    Divider(modifier = Modifier.padding(vertical = 12.dp), thickness = 0.5.dp)

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Auto Turn On Loudspeaker",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                text = "Enables speakerphone on calls so the mic can record both your voice and the caller's voice clearly.",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                            )
                        }
                        Switch(
                            checked = autoSpeakerOnCall,
                            onCheckedChange = {
                                autoSpeakerOnCall = it
                                appSettings.isAutoSpeakerOnCallEnabled = it
                            }
                        )
                    }

                    Divider(modifier = Modifier.padding(vertical = 12.dp), thickness = 0.5.dp)

                    Text(
                        text = "Call Audio Recording Source",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = "Voice Recognition prevents Android 14/15 from muting the recording stream during phone calls.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    AppSettings.CallAudioSource.values().forEach { sourceOption ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            RadioButton(
                                selected = selectedCallSource == sourceOption,
                                onClick = {
                                    selectedCallSource = sourceOption
                                    appSettings.callAudioSource = sourceOption
                                }
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = sourceOption.label,
                                style = MaterialTheme.typography.bodyMedium
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Feedback & Audio Settings Card
            SettingsSectionHeader(title = "AUDIO & FEEDBACK")
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Tactile Vibration",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                text = "Subtle haptic pulses on start, stop, and error",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                            )
                        }
                        Switch(
                            checked = vibrationEnabled,
                            onCheckedChange = {
                                vibrationEnabled = it
                                appSettings.isVibrationEnabled = it
                            }
                        )
                    }

                    Divider(modifier = Modifier.padding(vertical = 12.dp), thickness = 0.5.dp)

                    Text(
                        text = "Recording Quality",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    Spacer(modifier = Modifier.height(4.dp))

                    AppSettings.RecordingQuality.values().forEach { quality ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 2.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            RadioButton(
                                selected = selectedQuality == quality,
                                onClick = {
                                    selectedQuality = quality
                                    appSettings.recordingQuality = quality
                                }
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(text = quality.label, style = MaterialTheme.typography.bodyMedium)
                        }
                    }

                    Divider(modifier = Modifier.padding(vertical = 12.dp), thickness = 0.5.dp)

                    Text(
                        text = "Automatic Safety Stop",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    Spacer(modifier = Modifier.height(4.dp))

                    listOf(
                        0 to "Disabled (Manual stop only)",
                        5 to "After 5 minutes",
                        15 to "After 15 minutes",
                        30 to "After 30 minutes"
                    ).forEach { (minutes, label) ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 2.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            RadioButton(
                                selected = autoStopMinutes == minutes,
                                onClick = {
                                    autoStopMinutes = minutes
                                    appSettings.autoStopMinutes = minutes
                                }
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(text = label, style = MaterialTheme.typography.bodyMedium)
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // System Permissions Guidance
            SettingsSectionHeader(title = "SYSTEM CONFIGURATION")
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    OutlinedButton(
                        onClick = { PermissionManager.openAccessibilitySettings(context) },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text(text = "Manage Accessibility Service")
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedButton(
                        onClick = { PermissionManager.openAppSettings(context) },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text(text = "Manage App Permissions & Notifications")
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Privacy & About
            SettingsSectionHeader(title = "ABOUT & PRIVACY")
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Emergency Recorder v1.0.0",
                        fontWeight = FontWeight.Bold,
                        style = MaterialTheme.typography.titleSmall
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "• Zero internet permission requested.\n• Audio files stored exclusively in your device's Scoped MediaStore (Recordings/EmergencyRecorder).\n• Accessibility service does not read text, windows, or keyboard input.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                        lineHeight = 18.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Composable
private fun SettingsSectionHeader(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.labelMedium,
        fontWeight = FontWeight.Bold,
        color = MaterialTheme.colorScheme.primary,
        modifier = Modifier.padding(horizontal = 4.dp, vertical = 8.dp)
    )
}
