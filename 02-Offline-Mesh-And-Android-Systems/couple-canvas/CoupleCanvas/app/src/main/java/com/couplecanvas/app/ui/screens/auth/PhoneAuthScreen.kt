package com.couplecanvas.app.ui.screens.auth

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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material.icons.filled.WifiOff
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.couplecanvas.app.ui.theme.CleanWhite
import com.couplecanvas.app.ui.theme.LightBlueAccent
import com.couplecanvas.app.ui.theme.LightBlueBg
import com.couplecanvas.app.ui.theme.PinkPrimary
import com.couplecanvas.app.ui.theme.SlateDark
import com.couplecanvas.app.ui.theme.SlateSub
import com.couplecanvas.app.ui.theme.SoftBorder

@Composable
fun PhoneAuthScreen(
    initialPhone: String,
    initialName: String,
    isLoading: Boolean = false,
    serverError: String? = null,
    onServerErrorDismiss: () -> Unit = {},
    onAuthComplete: (phone: String, name: String) -> Unit
) {
    var phoneInput by remember { mutableStateOf(initialPhone) }
    var nameInput by remember { mutableStateOf(initialName) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // Server unreachable dialog
    if (serverError != null) {
        AlertDialog(
            onDismissRequest = onServerErrorDismiss,
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.WifiOff, contentDescription = null, tint = PinkPrimary)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Server Unreachable", fontWeight = FontWeight.Bold, color = SlateDark)
                }
            },
            text = {
                Text(
                    "Could not reach the server.\n\n$serverError\n\nCheck your internet connection and try again.",
                    color = SlateSub,
                    fontSize = 14.sp
                )
            },
            confirmButton = {
                TextButton(onClick = onServerErrorDismiss) {
                    Text("Try Again", color = PinkPrimary, fontWeight = FontWeight.Bold)
                }
            },
            containerColor = CleanWhite
        )
    }

    Box(
        modifier = Modifier.fillMaxSize().background(LightBlueBg),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Box(
                modifier = Modifier.size(80.dp).clip(CircleShape).background(PinkPrimary.copy(alpha = 0.12f)),
                contentAlignment = Alignment.Center
            ) { Text(text = "💕", fontSize = 36.sp) }

            Spacer(modifier = Modifier.height(16.dp))
            Text("Couple Canvas", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = PinkPrimary)
            Spacer(modifier = Modifier.height(4.dp))
            Text("Draw together in real-time 🎨", fontSize = 14.sp, color = SlateSub, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(32.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(24.dp),
                colors = CardDefaults.cardColors(containerColor = CleanWhite),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(SoftBorder)),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(
                    modifier = Modifier.fillMaxWidth().padding(28.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = if (initialPhone.isBlank()) "Create Account" else "Welcome Back",
                        fontSize = 20.sp, fontWeight = FontWeight.Bold, color = SlateDark
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = if (initialPhone.isBlank()) "Enter phone & name to get started" else "Verify your number to continue",
                        fontSize = 13.sp, color = SlateSub, textAlign = TextAlign.Center
                    )
                    Spacer(modifier = Modifier.height(24.dp))

                    OutlinedTextField(
                        value = phoneInput,
                        onValueChange = { phoneInput = it; errorMessage = null },
                        label = { Text("Phone Number *") },
                        placeholder = { Text("+91 9876543210") },
                        leadingIcon = { Icon(Icons.Default.Phone, contentDescription = null, tint = PinkPrimary) },
                        singleLine = true,
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = PinkPrimary,
                            unfocusedBorderColor = SoftBorder,
                            focusedLabelColor = PinkPrimary,
                            unfocusedLabelColor = SlateSub,
                            focusedTextColor = SlateDark,
                            unfocusedTextColor = SlateDark,
                            cursorColor = PinkPrimary,
                            focusedContainerColor = CleanWhite,
                            unfocusedContainerColor = CleanWhite
                        ),
                        isError = errorMessage != null && phoneInput.length < 8,
                        modifier = Modifier.fillMaxWidth()
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    OutlinedTextField(
                        value = nameInput,
                        onValueChange = { nameInput = it },
                        label = { Text("Display Name *") },
                        placeholder = { Text("e.g. Aisha") },
                        leadingIcon = { Icon(Icons.Default.Person, contentDescription = null, tint = LightBlueAccent) },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = LightBlueAccent,
                            unfocusedBorderColor = SoftBorder,
                            focusedLabelColor = LightBlueAccent,
                            unfocusedLabelColor = SlateSub,
                            focusedTextColor = SlateDark,
                            unfocusedTextColor = SlateDark,
                            cursorColor = LightBlueAccent,
                            focusedContainerColor = CleanWhite,
                            unfocusedContainerColor = CleanWhite
                        ),
                        isError = errorMessage != null && nameInput.isBlank(),
                        modifier = Modifier.fillMaxWidth()
                    )

                    errorMessage?.let { err ->
                        Spacer(modifier = Modifier.height(10.dp))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.WifiOff, contentDescription = null, tint = Color(0xFFEF4444), modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(err, color = Color(0xFFEF4444), fontSize = 13.sp, fontWeight = FontWeight.Medium)
                        }
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    Button(
                        onClick = {
                            val cleanPhone = phoneInput.trim()
                            val cleanName = nameInput.trim()
                            when {
                                cleanPhone.length < 8 -> errorMessage = "Enter a valid phone number (min 8 digits)"
                                cleanName.isBlank() -> errorMessage = "Please enter your display name"
                                else -> onAuthComplete(cleanPhone, cleanName)
                            }
                        },
                        modifier = Modifier.fillMaxWidth().height(52.dp),
                        shape = RoundedCornerShape(26.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = PinkPrimary),
                        enabled = !isLoading
                    ) {
                        if (isLoading) {
                            CircularProgressIndicator(modifier = Modifier.size(24.dp), color = CleanWhite, strokeWidth = 2.dp)
                        } else {
                            Text(
                                text = if (initialPhone.isBlank()) "Create Account 💕" else "Continue to App 💕",
                                fontSize = 16.sp, fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.CheckCircle, contentDescription = null, tint = Color(0xFF10B981), modifier = Modifier.size(14.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Your data is stored securely on our server", fontSize = 11.sp, color = SlateSub)
                    }
                }
            }
        }
    }
}