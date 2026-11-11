package com.couplecanvas.app.ui.screens.privacy

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.couplecanvas.app.ui.theme.RosePrimary

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PrivacyPolicyScreen(
    onBackClick: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Privacy Policy") },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.background
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(MaterialTheme.colorScheme.background)
                .verticalScroll(rememberScrollState())
                .padding(20.dp)
        ) {
            Text(
                text = "Privacy & Local-First Principles",
                style = MaterialTheme.typography.headlineMedium.copy(
                    fontWeight = FontWeight.Bold,
                    color = RosePrimary
                )
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "1. Local Storage Guarantee\n" +
                        "Your saved drawings, exported images, canvas strokes, and gallery artwork are stored exclusively on your device. We do not permanently upload or store your drawings on any server or cloud database.\n\n" +
                        "2. Peer-to-Peer Drawing Transmission\n" +
                        "Live drawing strokes and real-time operations are transmitted directly between your phone and your partner's phone using WebRTC DataChannels.\n\n" +
                        "3. Minimal Signaling Data\n" +
                        "Our signaling server is used strictly for short-lived session coordination (room creation, room joining, WebRTC offer/answer handshakes). Signaling tokens are kept in temporary memory and are deleted as soon as sessions terminate.\n\n" +
                        "4. Data Retention & Control\n" +
                        "You retain 100% ownership and control over your artwork. You can delete individual drawings or clear all local application data at any time in Settings.",
                style = MaterialTheme.typography.bodyLarge.copy(
                    lineHeight = 24.sp
                )
            )
        }
    }
}
