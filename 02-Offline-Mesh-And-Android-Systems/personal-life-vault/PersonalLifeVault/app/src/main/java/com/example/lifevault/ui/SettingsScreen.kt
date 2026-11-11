package com.example.lifevault.ui

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.provider.Settings
import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifevault.LifeVaultApplication
import com.example.lifevault.collector.NotificationCollectorService
import com.example.lifevault.repository.VaultRepository
import com.example.lifevault.ui.theme.*
import kotlinx.coroutines.launch

@Composable
fun SettingsScreen(
    app: LifeVaultApplication,
    repository: VaultRepository,
    onBack: () -> Unit,
    onRequestPermissions: () -> Unit,
    isSecretVault: Boolean = false
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val scrollState = rememberScrollState()

    var serverUrl by remember { mutableStateOf(app.tokenStore.getServerUrl()) }
    var deviceName by remember { mutableStateOf(app.tokenStore.getDeviceName()) }
    var adminKey by remember { mutableStateOf(app.tokenStore.getAdminKey()) }

    var testStatusMessage by remember { mutableStateOf<String?>(null) }
    var isTesting by remember { mutableStateOf(false) }

    val hasNotificationAccess = remember { mutableStateOf(isNotificationServiceEnabled(context)) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(VaultCreamBg)
            .padding(horizontal = 20.dp, vertical = 16.dp)
            .verticalScroll(scrollState)
    ) {
        // Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onBack) {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Back",
                    tint = VaultCharcoal
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = "VAULT CONFIGURATION",
                fontSize = 15.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace,
                letterSpacing = 1.5.sp,
                color = VaultCharcoal
            )
        }

        // Server Settings (Visible ONLY inside Secret Vault)
        if (isSecretVault) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, VaultBorder, RoundedCornerShape(8.dp)),
                colors = CardDefaults.cardColors(containerColor = VaultCreamSurface),
                shape = RoundedCornerShape(8.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "NETWORK ENDPOINT",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.SemiBold,
                        fontFamily = FontFamily.Monospace,
                        letterSpacing = 1.sp,
                        color = VaultSlate
                    )
                    Spacer(modifier = Modifier.height(10.dp))

                    OutlinedTextField(
                        value = serverUrl,
                        onValueChange = {
                            serverUrl = it
                            app.tokenStore.setServerUrl(it)
                        },
                        label = { Text("Server Address (Tailscale / LAN IP)", fontSize = 12.sp) },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = VaultSlate,
                            unfocusedBorderColor = VaultBorder,
                            focusedLabelColor = VaultSlate
                        )
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    OutlinedTextField(
                        value = deviceName,
                        onValueChange = {
                            deviceName = it
                            app.tokenStore.setDeviceName(it)
                        },
                        label = { Text("Device Name Identifier", fontSize = 12.sp) },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = VaultSlate,
                            unfocusedBorderColor = VaultBorder,
                            focusedLabelColor = VaultSlate
                        )
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    OutlinedTextField(
                        value = adminKey,
                        onValueChange = {
                            adminKey = it
                            app.tokenStore.setAdminKey(it)
                        },
                        label = { Text("Master Registration Key", fontSize = 12.sp) },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = VaultSlate,
                            unfocusedBorderColor = VaultBorder,
                            focusedLabelColor = VaultSlate
                        )
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    Button(
                        onClick = {
                            isTesting = true
                            testStatusMessage = null
                            coroutineScope.launch {
                                val healthy = repository.checkHealth()
                                if (healthy) {
                                    val registered = repository.registerDevice()
                                    if (registered) {
                                        testStatusMessage = "Connection verified & authenticated successfully."
                                    } else {
                                        testStatusMessage = "Server connected, but registration key was rejected."
                                    }
                                } else {
                                    testStatusMessage = "Could not reach server. Verify Tailscale / Wi-Fi IP and port."
                                }
                                isTesting = false
                            }
                        },
                        enabled = !isTesting,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(44.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = VaultSlate,
                            contentColor = Color.White
                        ),
                        shape = RoundedCornerShape(6.dp)
                    ) {
                        if (isTesting) {
                            CircularProgressIndicator(
                                color = Color.White,
                                strokeWidth = 2.dp,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("TESTING CONNECTION...", fontFamily = FontFamily.Monospace, fontSize = 12.sp)
                        } else {
                            Text("TEST CONNECTION & AUTHENTICATE", fontFamily = FontFamily.Monospace, fontSize = 12.sp)
                        }
                    }

                    if (testStatusMessage != null) {
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            text = testStatusMessage!!,
                            fontSize = 12.sp,
                            fontFamily = FontFamily.Monospace,
                            color = if (testStatusMessage!!.contains("successfully")) VaultOnlineGreen else VaultOfflineRed
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(20.dp))
        }


        // Share App Card (WhatsApp & Apps Share)
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, VaultBorder, RoundedCornerShape(8.dp)),
            colors = CardDefaults.cardColors(containerColor = VaultCreamSurface),
            shape = RoundedCornerShape(8.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "SHARE APPLICATION",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    fontFamily = FontFamily.Monospace,
                    letterSpacing = 1.sp,
                    color = VaultSlate
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "Share the Personal Life Vault Android app download link directly to WhatsApp or contacts.",
                    fontSize = 12.sp,
                    color = VaultMuted
                )
                Spacer(modifier = Modifier.height(14.dp))

                Button(
                    onClick = {
                        try {
                            val apkFile = java.io.File(context.applicationInfo.sourceDir)
                            val apkUri = androidx.core.content.FileProvider.getUriForFile(
                                context,
                                "${context.packageName}.fileprovider",
                                apkFile
                            )
                            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                                type = "application/vnd.android.package-archive"
                                putExtra(Intent.EXTRA_STREAM, apkUri)
                                putExtra(Intent.EXTRA_SUBJECT, "Personal Life Vault App APK")
                                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                            }
                            val chooser = Intent.createChooser(shareIntent, "Share Personal Life Vault APK File via")
                            context.startActivity(chooser)
                        } catch (_: Exception) {
                            // Fallback to URL text share if FileProvider fails
                            val downloadUrl = "${app.tokenStore.getServerUrl()}/download"
                            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                                type = "text/plain"
                                putExtra(Intent.EXTRA_SUBJECT, "Personal Life Vault APK")
                                putExtra(Intent.EXTRA_TEXT, "📲 Download Personal Life Vault Android App:\n$downloadUrl")
                            }
                            val chooser = Intent.createChooser(shareIntent, "Share Personal Life Vault App via")
                            context.startActivity(chooser)
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(44.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF25D366),
                        contentColor = Color.White
                    ),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Share,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "SHARE APK FILE TO WHATSAPP / APPS",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        fontSize = 12.sp
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Device Permissions Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, VaultBorder, RoundedCornerShape(8.dp)),
            colors = CardDefaults.cardColors(containerColor = VaultCreamSurface),
            shape = RoundedCornerShape(8.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "COLLECTION PERMISSIONS",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    fontFamily = FontFamily.Monospace,
                    letterSpacing = 1.sp,
                    color = VaultSlate
                )
                Spacer(modifier = Modifier.height(12.dp))

                PermissionItem(
                    title = "Notification Listener Access",
                    status = if (hasNotificationAccess.value) "ENABLED" else "DISABLED",
                    isGranted = hasNotificationAccess.value,
                    actionLabel = "OPEN SETTINGS"
                ) {
                    val intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
                    context.startActivity(intent)
                }

                HorizontalDivider(color = VaultSilverLight, thickness = 1.dp, modifier = Modifier.padding(vertical = 8.dp))

                PermissionItem(
                    title = "Storage & Media Access",
                    status = "CONFIGURED",
                    isGranted = true,
                    actionLabel = "REQUEST"
                ) {
                    onRequestPermissions()
                }

                HorizontalDivider(color = VaultSilverLight, thickness = 1.dp, modifier = Modifier.padding(vertical = 8.dp))

                PermissionItem(
                    title = "Optional Telecom Logs",
                    status = "CONFIGURED",
                    isGranted = true,
                    actionLabel = "REQUEST"
                ) {
                    onRequestPermissions()
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Anti-Kill & Unrestricted Battery Saver Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, VaultBorder, RoundedCornerShape(8.dp)),
            colors = CardDefaults.cardColors(containerColor = VaultCreamSurface),
            shape = RoundedCornerShape(8.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "PREVENT BACKGROUND KILL (UNRESTRICTED)",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    fontFamily = FontFamily.Monospace,
                    letterSpacing = 1.sp,
                    color = VaultCharcoal
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "Android OS & Phone Battery Savers kill background sync apps when swiped. Enable Unrestricted battery mode and Auto-Start to keep 24/7 background sync 100% active.",
                    fontSize = 12.sp,
                    color = VaultMuted
                )
                Spacer(modifier = Modifier.height(14.dp))

                Button(
                    onClick = {
                        try {
                            val intent = Intent(
                                Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                                android.net.Uri.parse("package:${context.packageName}")
                            )
                            context.startActivity(intent)
                        } catch (_: Exception) {
                            val fallback = Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS)
                            context.startActivity(fallback)
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(44.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = VaultSlate,
                        contentColor = Color.White
                    ),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.BatteryFull,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "DISABLE BATTERY SAVER (UNRESTRICTED)",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        fontSize = 11.sp
                    )
                }

                Spacer(modifier = Modifier.height(10.dp))

                OutlinedButton(
                    onClick = {
                        val intent = Intent(Settings.ACTION_SETTINGS)
                        context.startActivity(intent)
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(44.dp),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Settings,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp),
                        tint = VaultSlate
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "OPEN SYSTEM AUTOSTART & APP SETTINGS",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        fontSize = 11.sp,
                        color = VaultSlate
                    )
                }
            }
        }
    }
}


@Composable
private fun PermissionItem(
    title: String,
    status: String,
    isGranted: Boolean,
    actionLabel: String,
    onAction: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(text = title, fontSize = 13.sp, color = VaultCharcoal)
            Text(
                text = status,
                fontSize = 10.sp,
                fontFamily = FontFamily.Monospace,
                color = if (isGranted) VaultOnlineGreen else VaultOfflineRed
            )
        }
        TextButton(onClick = onAction) {
            Text(
                text = actionLabel,
                fontSize = 11.sp,
                fontFamily = FontFamily.Monospace,
                fontWeight = FontWeight.Bold,
                color = VaultSlate
            )
        }
    }
}

private fun isNotificationServiceEnabled(context: Context): Boolean {
    val pkgName = context.packageName
    val flat = Settings.Secure.getString(context.contentResolver, "enabled_notification_listeners")
    if (flat != null && flat.isNotEmpty()) {
        val names = flat.split(":")
        for (name in names) {
            val cn = ComponentName.unflattenFromString(name)
            if (cn != null && cn.packageName == pkgName) {
                return true
            }
        }
    }
    return false
}
