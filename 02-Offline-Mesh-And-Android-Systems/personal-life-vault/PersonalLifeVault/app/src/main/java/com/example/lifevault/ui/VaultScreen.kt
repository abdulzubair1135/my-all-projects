package com.example.lifevault.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifevault.LifeVaultApplication
import com.example.lifevault.database.entities.NotificationEntity
import com.example.lifevault.repository.VaultRepository
import com.example.lifevault.ui.theme.*
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun VaultScreen(
    app: LifeVaultApplication,
    repository: VaultRepository,
    onBack: () -> Unit
) {
    val recentNotifications by app.database.notificationDao().getRecentNotifications(50).collectAsState(initial = emptyList())
    val totalNotifs by app.database.notificationDao().getCount().collectAsState(initial = 0)
    val totalMedia by app.database.mediaDao().getCount().collectAsState(initial = 0)
    val totalTelecom by app.database.telecomDao().getCount().collectAsState(initial = 0)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(VaultCreamBg)
            .padding(horizontal = 20.dp, vertical = 16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
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
                text = "VAULT DATABASE STATUS",
                fontSize = 15.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace,
                letterSpacing = 1.5.sp,
                color = VaultCharcoal
            )
        }

        // Summary Counts Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, VaultBorder, RoundedCornerShape(8.dp)),
            colors = CardDefaults.cardColors(containerColor = VaultCreamSurface),
            shape = RoundedCornerShape(8.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "LOCAL PERSISTENCE STATS",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    fontFamily = FontFamily.Monospace,
                    letterSpacing = 1.sp,
                    color = VaultSlate
                )
                Spacer(modifier = Modifier.height(10.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    CountItem("NOTIFICATIONS", totalNotifs.toString())
                    CountItem("MEDIA", totalMedia.toString())
                    CountItem("TELECOM", totalTelecom.toString())
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "RECENT CAPTURED RECORDS",
            fontSize = 12.sp,
            fontWeight = FontWeight.SemiBold,
            fontFamily = FontFamily.Monospace,
            letterSpacing = 1.sp,
            color = VaultSlate
        )

        Spacer(modifier = Modifier.height(8.dp))

        if (recentNotifications.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .background(VaultCreamSurface, RoundedCornerShape(8.dp))
                    .border(1.dp, VaultBorder, RoundedCornerShape(8.dp)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "No recorded events yet.\nEvents will populate when notifications arrive.",
                    fontSize = 12.sp,
                    fontFamily = FontFamily.Monospace,
                    color = VaultMuted,
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(recentNotifications) { notif ->
                    NotificationRow(notif)
                }
            }
        }
    }
}

@Composable
private fun CountItem(title: String, count: String) {
    Column {
        Text(text = title, fontSize = 10.sp, fontFamily = FontFamily.Monospace, color = VaultMuted)
        Text(text = count, fontSize = 16.sp, fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold, color = VaultCharcoal)
    }
}

@Composable
private fun NotificationRow(notif: NotificationEntity) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, VaultBorder, RoundedCornerShape(6.dp)),
        colors = CardDefaults.cardColors(containerColor = VaultCreamSurface),
        shape = RoundedCornerShape(6.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = notif.appName,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    color = VaultSlate
                )
                Text(
                    text = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date(notif.timestamp)),
                    fontSize = 10.sp,
                    fontFamily = FontFamily.Monospace,
                    color = VaultMuted
                )
            }
            if (!notif.title.isNullOrEmpty()) {
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = notif.title,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = VaultCharcoal
                )
            }
            if (!notif.content.isNullOrEmpty()) {
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = notif.content,
                    fontSize = 11.sp,
                    color = VaultMuted,
                    maxLines = 2
                )
            }
        }
    }
}
