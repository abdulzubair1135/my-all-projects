package com.projectx2.porncontroller.core.theme

import android.app.Activity
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val NeomorphicColorScheme = lightColorScheme(
    primary = NeoRedAccent,              // Vivid Crimson Red
    onPrimary = Color.White,
    primaryContainer = NeoSurfaceWhite,
    onPrimaryContainer = NeoTextBlack,
    secondary = NeoBorderBlack,          // Pitch Black
    onSecondary = Color.White,
    secondaryContainer = NeoSurfaceOffWhite,
    onSecondaryContainer = NeoTextBlack,
    tertiary = NeoRedBright,
    background = NeoCanvasBackground,    // Crisp Porcelain White
    onBackground = NeoTextBlack,
    surface = NeoSurfaceWhite,           // Crisp Pure White Cards
    onSurface = NeoTextBlack,
    surfaceVariant = NeoSurfaceOffWhite,
    onSurfaceVariant = NeoTextCharcoal,
    outline = NeoBorderBlack             // Solid Black Borders
)

@Composable
fun PornControllerTheme(
    content: @Composable () -> Unit
) {
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as? Activity)?.window
            window?.let {
                it.statusBarColor = NeoCanvasBackground.toArgb()
                it.navigationBarColor = NeoCanvasBackground.toArgb()
                WindowCompat.getInsetsController(it, view).apply {
                    isAppearanceLightStatusBars = true
                    isAppearanceLightNavigationBars = true
                }
            }
        }
    }

    MaterialTheme(
        colorScheme = NeomorphicColorScheme,
        content = content
    )
}
