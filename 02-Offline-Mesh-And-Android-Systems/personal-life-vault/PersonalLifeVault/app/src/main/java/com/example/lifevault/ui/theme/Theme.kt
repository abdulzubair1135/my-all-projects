package com.example.lifevault.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColorScheme = lightColorScheme(
    primary = VaultSlate,
    onPrimary = Color.White,
    primaryContainer = VaultSilverLight,
    onPrimaryContainer = VaultCharcoal,
    secondary = VaultSilverDark,
    onSecondary = Color.White,
    background = VaultCreamBg,
    onBackground = VaultCharcoal,
    surface = VaultCreamSurface,
    onSurface = VaultCharcoal,
    surfaceVariant = VaultCreamCard,
    onSurfaceVariant = VaultSlate,
    outline = VaultBorder
)

@Composable
fun LifeVaultTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = LightColorScheme,
        typography = Typography(),
        content = content
    )
}
