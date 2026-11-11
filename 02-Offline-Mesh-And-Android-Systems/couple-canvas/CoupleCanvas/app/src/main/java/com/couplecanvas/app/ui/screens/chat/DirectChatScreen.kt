package com.couplecanvas.app.ui.screens.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.PersonAdd
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.couplecanvas.app.domain.model.ChatMessage
import com.couplecanvas.app.ui.theme.CleanWhite
import com.couplecanvas.app.ui.theme.LightBlueAccent
import com.couplecanvas.app.ui.theme.LightBlueBg
import com.couplecanvas.app.ui.theme.PinkPrimary
import com.couplecanvas.app.ui.theme.SlateDark
import com.couplecanvas.app.ui.theme.SlateSub
import com.couplecanvas.app.ui.theme.SoftBorder

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DirectChatScreen(
    userPhone: String,
    partnerPhone: String,
    partnerName: String,
    messages: List<ChatMessage>,
    onSendMessage: (String) -> Unit,
    onAddPartnerSubmitted: (partnerPhone: String) -> Unit,
    onBackClick: () -> Unit
) {
    var messageText by remember { mutableStateOf("") }
    var showAddPartnerDialog by remember { mutableStateOf(false) }
    var addPartnerInput by remember { mutableStateOf("") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = if (partnerName.isNotBlank()) partnerName else "Partner Chat",
                            fontWeight = FontWeight.Bold,
                            color = SlateDark,
                            fontSize = 17.sp
                        )
                        if (partnerPhone.isNotBlank()) {
                            Text(text = partnerPhone, fontSize = 12.sp, color = SlateSub)
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = SlateDark)
                    }
                },
                actions = {
                    IconButton(onClick = { showAddPartnerDialog = true }) {
                        Icon(Icons.Default.PersonAdd, contentDescription = "Add Partner", tint = PinkPrimary)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = CleanWhite)
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(LightBlueBg)
        ) {
            if (partnerPhone.isBlank()) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = CleanWhite),
                        border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(SoftBorder))
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(20.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text("No Partner Added Yet 💕", fontWeight = FontWeight.Bold, fontSize = 16.sp, color = PinkPrimary)
                            Spacer(modifier = Modifier.height(4.dp))
                            Text("Click the top right icon or button below to add your partner by phone number.", fontSize = 13.sp, color = SlateSub)
                            Spacer(modifier = Modifier.height(12.dp))
                            TextButton(onClick = { showAddPartnerDialog = true }) {
                                Text("+ Add Partner Phone Number", color = LightBlueAccent, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }

            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                reverseLayout = false
            ) {
                items(messages) { msg ->
                    val isMe = msg.senderUserId == userPhone || msg.senderName == "Me"
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
                        horizontalArrangement = if (isMe) Arrangement.End else Arrangement.Start
                    ) {
                        Card(
                            shape = RoundedCornerShape(16.dp),
                            colors = CardDefaults.cardColors(
                                containerColor = if (isMe) PinkPrimary else CleanWhite
                            ),
                            elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
                        ) {
                            Column(modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp)) {
                                Text(
                                    text = msg.text,
                                    color = if (isMe) CleanWhite else SlateDark,
                                    fontSize = 15.sp
                                )
                            }
                        }
                    }
                }
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(CleanWhite)
                    .padding(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                OutlinedTextField(
                    value = messageText,
                    onValueChange = { messageText = it },
                    placeholder = { Text("Type a message to your partner...") },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = PinkPrimary,
                        unfocusedBorderColor = SoftBorder
                    ),
                    modifier = Modifier.weight(1f)
                )
                Spacer(modifier = Modifier.width(8.dp))
                IconButton(
                    onClick = {
                        if (messageText.trim().isNotEmpty()) {
                            onSendMessage(messageText.trim())
                            messageText = ""
                        }
                    }
                ) {
                    Icon(Icons.AutoMirrored.Filled.Send, contentDescription = "Send", tint = PinkPrimary)
                }
            }
        }
    }

    if (showAddPartnerDialog) {
        AlertDialog(
            onDismissRequest = { showAddPartnerDialog = false },
            title = { Text("Add Partner Phone Number 💕") },
            text = {
                Column {
                    Text("Enter your partner's phone number to connect and chat outside of drawing rooms:")
                    Spacer(modifier = Modifier.height(12.dp))
                    OutlinedTextField(
                        value = addPartnerInput,
                        onValueChange = { addPartnerInput = it },
                        label = { Text("Partner Phone (e.g. +91 9876543210)") },
                        singleLine = true,
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone)
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        if (addPartnerInput.trim().isNotEmpty()) {
                            onAddPartnerSubmitted(addPartnerInput.trim())
                            showAddPartnerDialog = false
                        }
                    }
                ) {
                    Text("Connect Partner", color = PinkPrimary, fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { showAddPartnerDialog = false }) { Text("Cancel") }
            }
        )
    }
}