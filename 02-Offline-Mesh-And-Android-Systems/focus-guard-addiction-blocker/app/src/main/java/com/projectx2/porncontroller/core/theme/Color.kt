package com.projectx2.porncontroller.core.theme

import androidx.compose.ui.graphics.Color

// ============================================================
// 3D NEOMORPHIC THEME: PREDOMINANT WHITE + BLACK BORDERS + RED ACCENTS
// ============================================================

// Dominant Pure White & Clean Neomorphic Backgrounds
val NeoCanvasBackground = Color(0xFFF2F4F8)  // Soft Porcelain White background
val NeoSurfaceWhite = Color(0xFFFFFFFF)      // Crisp Pure White Card Surface
val NeoSurfaceOffWhite = Color(0xFFF8FAFC)   // Subtle Off-White Tactile Surface
val CharcoalBackground = NeoCanvasBackground // Backward-compatibility alias
val SurfaceDark = NeoSurfaceWhite            // Backward-compatibility alias
val SurfaceElevated = NeoSurfaceOffWhite     // Backward-compatibility alias

// 3D Neomorphic Black Borders & Extrusions
val NeoBorderBlack = Color(0xFF000000)       // Solid Pitch Black Border (User: "black se border")
val NeoExtrusionShadow = Color(0xFF000000)   // Solid 3D Drop Extrusion
val NeoSoftShadow = Color(0x2B000000)        // Soft Neomorphic Ambient Shadow
val BorderDark = NeoBorderBlack              // Backward-compatibility alias
val BorderRedSubtle = Color(0xFFDC2626)      // Red Accent Border

// Vivid Crimson Red Accents (User: "red se thoda thoda text")
val NeoRedAccent = Color(0xFFDC2626)         // Vivid Crimson Red
val NeoRedBright = Color(0xFFEF4444)         // Bright Crimson Highlight
val NeoRedDeep = Color(0xFFB91C1C)           // Deep Blood Red
val NeoRedSoft = Color(0xFFFEE2E2)           // Light Red Tint for Badges
val ElectricPurple = NeoRedAccent            // Backward-compatibility alias
val PurpleGlow = NeoRedBright                // Backward-compatibility alias
val FlameRed = NeoRedDeep                    // Backward-compatibility alias
val RubyDark = Color(0xFF991B1B)
val CoralAlert = NeoRedAccent
val EmeraldActive = NeoRedAccent             // Active badges highlighted in Red

// High-Contrast Black & Charcoal Typography
val NeoTextBlack = Color(0xFF090A0F)         // Pure Pitch Black for readability
val NeoTextCharcoal = Color(0xFF334155)      // Slate Charcoal
val NeoTextMuted = Color(0xFF64748B)         // Cool Slate Grey
val TextPrimary = NeoTextBlack               // Backward-compatibility alias
val TextSecondary = NeoTextCharcoal          // Backward-compatibility alias
val TextMuted = NeoTextMuted                 // Backward-compatibility alias

// White & Accent Highlights
val PureBlack = Color(0xFF000000)
val CyberBlue = Color(0xFF000000)            // High contrast text alias
val CyanAccent = Color(0xFFFFFFFF)           // Pure white
val AmberWarning = Color(0xFFD97706)         // Amber Warning
