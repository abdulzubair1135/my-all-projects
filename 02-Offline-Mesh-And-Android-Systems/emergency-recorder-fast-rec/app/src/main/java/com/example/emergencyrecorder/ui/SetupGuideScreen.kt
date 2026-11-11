package com.example.emergencyrecorder.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.TouchApp
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.emergencyrecorder.permissions.PermissionManager
import com.example.emergencyrecorder.ui.theme.EmergencyRed
import com.example.emergencyrecorder.ui.theme.SuccessGreen

@Composable
fun SetupGuideScreen(
    hasMicPermission: Boolean,
    hasNotificationPermission: Boolean,
    hasAccessibilityEnabled: Boolean,
    onRequestPermissions: () -> Unit,
    onBack: () -> Unit
) {
    val context = LocalContext.current

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
                    text = "Setup Checklist & Guide",
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
                .padding(horizontal = 20.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Text(
                text = "Personal Safety & Privacy Notice",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = EmergencyRed
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Emergency Recorder is designed for personal emergency evidence gathering. To start recording when the phone is locked or the app is closed, Android requires specific user authorizations. We explain each one transparently below.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.8f)
            )

            Spacer(modifier = Modifier.height(20.dp))

            // Step 1: Microphone Permission
            StepCard(
                stepNumber = "1",
                title = "Microphone Permission",
                description = "Required to record ambient voice and emergency audio when triggered. Audio remains strictly local on your device.",
                isCompleted = hasMicPermission,
                buttonText = if (hasMicPermission) "Permission Granted" else "Grant Microphone Access",
                onAction = onRequestPermissions
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Step 2: Notifications Permission
            StepCard(
                stepNumber = "2",
                title = "Foreground Notification",
                description = "Android requires a visible notification whenever an app uses the microphone in the background. This ensures transparency and provides an immediate stop button.",
                isCompleted = hasNotificationPermission,
                buttonText = if (hasNotificationPermission) "Notification Enabled" else "Allow Notifications",
                onAction = onRequestPermissions
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Step 3: Accessibility Service for Hardware Key
            StepCard(
                stepNumber = "3",
                title = "Accessibility Service (Volume Down)",
                description = "Android does not allow normal background apps to listen to hardware volume buttons without Accessibility access. Our service only filters KEYCODE_VOLUME_DOWN double-presses and cannot read screen contents or text.",
                isCompleted = hasAccessibilityEnabled,
                buttonText = if (hasAccessibilityEnabled) "Accessibility Connected" else "Open Accessibility Settings",
                onAction = {
                    PermissionManager.openAccessibilitySettings(context)
                }
            )

            Spacer(modifier = Modifier.height(20.dp))

            // OEM Limitation Notice
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Warning,
                            contentDescription = null,
                            tint = EmergencyRed
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "OEM & Deep Sleep Note",
                            fontWeight = FontWeight.Bold,
                            color = EmergencyRed
                        )
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "On some devices, deep sleep (Doze) suspends key detection when the screen has been off for a prolonged period. If your phone does not wake on Volume Down double-press, wake the screen once (tap or power button) or use our Quick Settings Tile fallback.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f)
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Composable
private fun StepCard(
    stepNumber: String,
    title: String,
    description: String,
    isCompleted: Boolean,
    buttonText: String,
    onAction: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isCompleted) Color(0xFFF1F8E9) else MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Step $stepNumber: $title",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                if (isCompleted) {
                    Icon(
                        imageVector = Icons.Default.Check,
                        contentDescription = "Completed",
                        tint = SuccessGreen,
                        modifier = Modifier.size(24.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(6.dp))

            Text(
                text = description,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )

            Spacer(modifier = Modifier.height(12.dp))

            if (!isCompleted) {
                Button(
                    onClick = onAction,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(text = buttonText)
                }
            } else {
                OutlinedButton(
                    onClick = onAction,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(text = buttonText, color = SuccessGreen)
                }
            }
        }
    }
}
