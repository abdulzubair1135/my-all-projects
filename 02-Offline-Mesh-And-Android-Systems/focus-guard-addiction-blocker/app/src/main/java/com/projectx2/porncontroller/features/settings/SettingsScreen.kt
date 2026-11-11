package com.projectx2.porncontroller.features.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.projectx2.porncontroller.PornControllerApp
import com.projectx2.porncontroller.core.theme.*
import com.projectx2.porncontroller.core.utils.ApkShareHelper
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onNavigateBack: () -> Unit,
    onNavigateToAbout: () -> Unit
) {
    val context = LocalContext.current
    val repo = (context.applicationContext as PornControllerApp).repository
    val scope = rememberCoroutineScope()

    val settings by repo.settingsFlow.collectAsState(initial = null)
    var showWipeDialog by remember { mutableStateOf(false) }

    val categories = listOf("MOTIVATIONAL", "STRICT", "FUNNY", "FRIENDLY")

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "SETTINGS",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Black,
                            fontFamily = FontFamily.Monospace,
                            color = NeoBorderBlack
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Neo3DBadge(
                            text = "PREFERENCES",
                            textColor = NeoRedAccent,
                            backgroundColor = NeoSurfaceWhite
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = NeoBorderBlack)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = NeoCanvasBackground)
            )
        },
        containerColor = NeoCanvasBackground
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // ==========================================
            // 1. SHARE APK OPTION (WhatsApp / ShareSheet)
            // ==========================================
            item {
                Neo3DCard(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(18.dp),
                    backgroundColor = NeoSurfaceWhite,
                    borderColor = NeoBorderBlack,
                    borderWidth = 2.dp,
                    extrusionOffset = 4.dp,
                    extrusionColor = NeoBorderBlack,
                    onClick = {
                        ApkShareHelper.shareAppApk(context)
                    }
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(18.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(48.dp)
                                .clip(RoundedCornerShape(12.dp))
                                .background(NeoRedAccent)
                                .border(2.dp, NeoBorderBlack, RoundedCornerShape(12.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Share,
                                contentDescription = "Share APK",
                                tint = Color.White,
                                modifier = Modifier.size(24.dp)
                            )
                        }

                        Spacer(modifier = Modifier.width(14.dp))

                        Column(modifier = Modifier.weight(1f)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    text = "Share App APK",
                                    fontSize = 15.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = NeoTextBlack
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Neo3DBadge(
                                    text = "WHATSAPP",
                                    textColor = NeoRedAccent,
                                    backgroundColor = NeoSurfaceWhite
                                )
                            }
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "Send installable .apk file directly to friends on WhatsApp or any app",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Medium,
                                color = NeoTextMuted
                            )
                        }

                        Icon(
                            imageVector = Icons.Default.ChevronRight,
                            contentDescription = null,
                            tint = NeoBorderBlack
                        )
                    }
                }
            }

            // ==========================================
            // 2. Intervention Category Tone
            // ==========================================
            item {
                SectionCard(title = "INTERVENTION TONE") {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        categories.forEach { cat ->
                            val isSelected = settings?.interventionCategory == cat
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(10.dp))
                                    .background(if (isSelected) NeoSurfaceOffWhite else NeoSurfaceWhite)
                                    .border(
                                        if (isSelected) 1.5.dp else 1.dp,
                                        if (isSelected) NeoBorderBlack else Color(0xFFE2E8F0),
                                        RoundedCornerShape(10.dp)
                                    )
                                    .clickable {
                                        settings?.let { s ->
                                            scope.launch { repo.updateSettings(s.copy(interventionCategory = cat)) }
                                        }
                                    }
                                    .padding(horizontal = 12.dp, vertical = 8.dp)
                            ) {
                                RadioButton(
                                    selected = isSelected,
                                    onClick = {
                                        settings?.let { s ->
                                            scope.launch { repo.updateSettings(s.copy(interventionCategory = cat)) }
                                        }
                                    },
                                    colors = RadioButtonDefaults.colors(
                                        selectedColor = NeoRedAccent,
                                        unselectedColor = NeoBorderBlack
                                    )
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = cat.lowercase().replaceFirstChar { it.uppercase() },
                                    fontSize = 14.sp,
                                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                    color = NeoTextBlack
                                )
                            }
                        }
                    }
                }
            }

            // ==========================================
            // 3. Repetition Sensitivity & Cooldown
            // ==========================================
            item {
                SectionCard(title = "DETECTION SENSITIVITY") {
                    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                        Column {
                            val threshold = settings?.repetitionThreshold ?: 3
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    text = "Search Repetition Threshold",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = NeoTextBlack
                                )
                                Text(
                                    text = "$threshold times",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = NeoRedAccent
                                )
                            }
                            Slider(
                                value = threshold.toFloat(),
                                onValueChange = { value ->
                                    settings?.let { s ->
                                        scope.launch { repo.updateSettings(s.copy(repetitionThreshold = value.toInt())) }
                                    }
                                },
                                valueRange = 1f..5f,
                                steps = 3,
                                colors = SliderDefaults.colors(
                                    thumbColor = NeoBorderBlack,
                                    activeTrackColor = NeoRedAccent
                                )
                            )
                        }

                        Column {
                            val cooldown = settings?.cooldownPeriodMinutes ?: 5
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    text = "Intervention Cooldown",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = NeoTextBlack
                                )
                                Text(
                                    text = "$cooldown min",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = NeoRedAccent
                                )
                            }
                            Slider(
                                value = cooldown.toFloat(),
                                onValueChange = { value ->
                                    settings?.let { s ->
                                        scope.launch { repo.updateSettings(s.copy(cooldownPeriodMinutes = value.toInt())) }
                                    }
                                },
                                valueRange = 1f..15f,
                                steps = 13,
                                colors = SliderDefaults.colors(
                                    thumbColor = NeoBorderBlack,
                                    activeTrackColor = NeoRedAccent
                                )
                            )
                        }
                    }
                }
            }

            // ==========================================
            // 4. Sound & Haptics
            // ==========================================
            item {
                SectionCard(title = "SOUND & HAPTICS") {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        SettingSwitchRow(
                            title = "Startup Intro Chime",
                            subtitle = "Plays cyber intro sound when opening app",
                            checked = settings?.soundIntroEnabled ?: true,
                            onCheckedChange = { check ->
                                settings?.let { s ->
                                    scope.launch { repo.updateSettings(s.copy(soundIntroEnabled = check)) }
                                }
                            }
                        )
                        SettingSwitchRow(
                            title = "Haptic Vibration Alert",
                            subtitle = "Vibrates device when compulsive search is detected",
                            checked = settings?.hapticAlertsEnabled ?: true,
                            onCheckedChange = { check ->
                                settings?.let { s ->
                                    scope.launch { repo.updateSettings(s.copy(hapticAlertsEnabled = check)) }
                                }
                            }
                        )
                    }
                }
            }

            // ==========================================
            // 5. About & Privacy Navigation
            // ==========================================
            item {
                Neo3DCard(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    backgroundColor = NeoSurfaceWhite,
                    borderColor = NeoBorderBlack,
                    borderWidth = 2.dp,
                    extrusionOffset = 3.5.dp,
                    extrusionColor = NeoBorderBlack,
                    onClick = onNavigateToAbout
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(38.dp)
                                .clip(RoundedCornerShape(10.dp))
                                .background(NeoSurfaceWhite)
                                .border(1.5.dp, NeoBorderBlack, RoundedCornerShape(10.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(Icons.Default.Info, contentDescription = null, tint = NeoRedAccent, modifier = Modifier.size(20.dp))
                        }
                        Spacer(modifier = Modifier.width(14.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text("About P.RN Controller", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = NeoTextBlack)
                            Text("Branding by projectX², 100% Offline Privacy", fontSize = 11.sp, color = NeoTextMuted)
                        }
                        Icon(Icons.Default.ChevronRight, contentDescription = null, tint = NeoBorderBlack)
                    }
                }
            }

            // ==========================================
            // 6. Wipe All Data Danger Zone
            // ==========================================
            item {
                Neo3DCard(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    backgroundColor = NeoSurfaceWhite,
                    borderColor = NeoBorderBlack,
                    borderWidth = 2.dp,
                    extrusionOffset = 3.5.dp,
                    extrusionColor = NeoBorderBlack
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .clip(CircleShape)
                                    .background(NeoRedAccent)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("DANGER ZONE", fontSize = 11.sp, fontWeight = FontWeight.Black, color = NeoRedAccent)
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            "Permanently wipe all local statistics, history, custom domains, and reset settings.",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium,
                            color = NeoTextMuted
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        OutlinedButton(
                            onClick = { showWipeDialog = true },
                            colors = ButtonDefaults.outlinedButtonColors(contentColor = NeoRedAccent),
                            shape = RoundedCornerShape(10.dp),
                            border = ButtonDefaults.outlinedButtonBorder.copy(
                                brush = androidx.compose.ui.graphics.SolidColor(NeoBorderBlack),
                                width = 1.5.dp
                            )
                        ) {
                            Icon(Icons.Default.DeleteForever, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Wipe All Local Data", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }

            item { Spacer(modifier = Modifier.height(24.dp)) }
        }
    }

    if (showWipeDialog) {
        AlertDialog(
            onDismissRequest = { showWipeDialog = false },
            title = { Text("Erase All Data?", color = NeoTextBlack, fontWeight = FontWeight.Bold) },
            text = { Text("This will permanently reset your streak, delete all detection logs, and return all settings to factory default. This action cannot be undone.", color = NeoTextCharcoal) },
            confirmButton = {
                Button(
                    onClick = {
                        scope.launch { repo.wipeAllUserData() }
                        showWipeDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = NeoRedAccent),
                    shape = RoundedCornerShape(10.dp)
                ) {
                    Text("Erase Everything", color = Color.White, fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { showWipeDialog = false }) { Text("Cancel", color = NeoTextMuted) }
            },
            containerColor = NeoSurfaceWhite
        )
    }
}

@Composable
fun SectionCard(
    title: String,
    content: @Composable () -> Unit
) {
    Column {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .size(6.dp)
                    .clip(CircleShape)
                    .background(NeoRedAccent)
            )
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                text = title,
                fontSize = 11.sp,
                fontWeight = FontWeight.Black,
                color = NeoBorderBlack,
                letterSpacing = 1.sp
            )
        }
        Spacer(modifier = Modifier.height(8.dp))
        Neo3DCard(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            backgroundColor = NeoSurfaceWhite,
            borderColor = NeoBorderBlack,
            borderWidth = 2.dp,
            extrusionOffset = 3.5.dp,
            extrusionColor = NeoBorderBlack
        ) {
            Box(modifier = Modifier.padding(16.dp)) {
                content()
            }
        }
    }
}

@Composable
fun SettingSwitchRow(
    title: String,
    subtitle: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(title, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = NeoTextBlack)
            Text(subtitle, fontSize = 11.sp, color = NeoTextMuted)
        }
        Switch(
            checked = checked,
            onCheckedChange = onCheckedChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = Color.White,
                checkedTrackColor = NeoRedAccent,
                checkedBorderColor = NeoBorderBlack,
                uncheckedThumbColor = NeoBorderBlack,
                uncheckedTrackColor = NeoSurfaceOffWhite,
                uncheckedBorderColor = NeoBorderBlack
            )
        )
    }
}
