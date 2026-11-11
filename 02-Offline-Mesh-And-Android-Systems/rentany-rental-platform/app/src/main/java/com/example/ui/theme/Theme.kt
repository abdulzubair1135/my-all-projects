package com.example.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

private val DarkColorScheme =
  darkColorScheme(
    primary = RentAnyGreen,
    secondary = RentAnyGreenDark,
    tertiary = RentAnyGold,
    background = DarkBg,
    surface = DarkSurface,
    surfaceVariant = DarkSurfaceVariant,
    onPrimary = Color.White,
    onSecondary = Color.White,
    onBackground = Color(0xFFF3F4F6),
    onSurface = Color(0xFFF3F4F6),
    onSurfaceVariant = Color(0xFF9CA3AF),
    outline = Color(0xFF4B5563),
    outlineVariant = Color(0xFF374151)
  )

private val LightColorScheme =
  lightColorScheme(
    primary = RentAnyGreen,
    secondary = RentAnyGreenDark,
    tertiary = RentAnyGold,
    background = LightBg,
    surface = LightSurface,
    surfaceVariant = Color(0xFFF1F3F4), // Light grey for unfilled backgrounds/borders
    onPrimary = Color.White, // White text on Green buttons
    onSecondary = Color.White,
    onBackground = Color(0xFF111827), // Deep charcoal for high readability
    onSurface = Color(0xFF111827),
    onSurfaceVariant = Color(0xFF6B7280), // Muted grey for descriptions
    outline = Color(0xFFD1D5DB), // Grey borders for fields
    outlineVariant = Color(0xFFE5E7EB) // Very light grey for separators
  )

@Composable
fun RentAnyTheme(
  darkTheme: Boolean = isSystemInDarkTheme(),
  content: @Composable () -> Unit,
) {
  val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

  MaterialTheme(
    colorScheme = colorScheme,
    typography = Typography,
    content = content
  )
}
