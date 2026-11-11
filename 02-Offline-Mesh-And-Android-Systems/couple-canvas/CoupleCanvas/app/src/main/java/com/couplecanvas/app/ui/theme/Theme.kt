package com.couplecanvas.app.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val LightColorScheme = lightColorScheme(
    primary = PinkPrimary,
    secondary = LightBlueAccent,
    tertiary = LightBlueSoft,
    background = LightBlueBg,
    surface = CleanWhite,
    onPrimary = CleanWhite,
    onSecondary = CleanWhite,
    onBackground = SlateDark,
    onSurface = SlateDark,
    outline = SoftBorder
)

private val DarkColorScheme = darkColorScheme(
    primary = PinkPrimary,
    secondary = LightBlueAccent,
    tertiary = LightBlueSoft,
    background = SlateDark,
    surface = Color(0xFF1E293B),
    onPrimary = CleanWhite,
    onSecondary = CleanWhite,
    onBackground = CleanWhite,
    onSurface = CleanWhite,
    outline = Color(0xFF334155)
)

@Composable
fun CoupleCanvasTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    val view = LocalView.current

    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
