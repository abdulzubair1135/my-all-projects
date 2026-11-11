package com.recoverx.core.permissions

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.content.ContextCompat

data class StoragePermissionStatus(
    val hasFullMediaAccess: Boolean,
    val hasPartialVisualAccess: Boolean,
    val hasImageAccess: Boolean,
    val hasVideoAccess: Boolean,
    val hasAudioAccess: Boolean,
    val requiredPermissions: List<String>,
    val explanation: String
)

object PermissionCoordinator {

    fun getRequiredMediaPermissions(): Array<String> {
        return when {
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE -> {
                arrayOf(
                    Manifest.permission.READ_MEDIA_IMAGES,
                    Manifest.permission.READ_MEDIA_VIDEO,
                    Manifest.permission.READ_MEDIA_AUDIO,
                    Manifest.permission.READ_MEDIA_VISUAL_USER_SELECTED
                )
            }
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU -> {
                arrayOf(
                    Manifest.permission.READ_MEDIA_IMAGES,
                    Manifest.permission.READ_MEDIA_VIDEO,
                    Manifest.permission.READ_MEDIA_AUDIO
                )
            }
            else -> {
                arrayOf(
                    Manifest.permission.READ_EXTERNAL_STORAGE
                )
            }
        }
    }

    fun checkStoragePermissions(context: Context): StoragePermissionStatus {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            val img = isGranted(context, Manifest.permission.READ_MEDIA_IMAGES)
            val vid = isGranted(context, Manifest.permission.READ_MEDIA_VIDEO)
            val aud = isGranted(context, Manifest.permission.READ_MEDIA_AUDIO)
            val partial = isGranted(context, Manifest.permission.READ_MEDIA_VISUAL_USER_SELECTED)

            val full = img && vid && aud
            return StoragePermissionStatus(
                hasFullMediaAccess = full,
                hasPartialVisualAccess = partial && !full,
                hasImageAccess = img || partial,
                hasVideoAccess = vid || partial,
                hasAudioAccess = aud,
                requiredPermissions = getRequiredMediaPermissions().toList(),
                explanation = if (full) "Full Media Library Access Granted"
                else if (partial) "Partial Access Granted (User Selected Items)"
                else "Storage permissions required to discover device media."
            )
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val img = isGranted(context, Manifest.permission.READ_MEDIA_IMAGES)
            val vid = isGranted(context, Manifest.permission.READ_MEDIA_VIDEO)
            val aud = isGranted(context, Manifest.permission.READ_MEDIA_AUDIO)
            val full = img && vid && aud

            return StoragePermissionStatus(
                hasFullMediaAccess = full,
                hasPartialVisualAccess = false,
                hasImageAccess = img,
                hasVideoAccess = vid,
                hasAudioAccess = aud,
                requiredPermissions = getRequiredMediaPermissions().toList(),
                explanation = if (full) "Full Media Library Access Granted"
                else "Granular media permissions required for Photos, Videos, and Audio."
            )
        } else {
            val legacy = isGranted(context, Manifest.permission.READ_EXTERNAL_STORAGE)
            return StoragePermissionStatus(
                hasFullMediaAccess = legacy,
                hasPartialVisualAccess = false,
                hasImageAccess = legacy,
                hasVideoAccess = legacy,
                hasAudioAccess = legacy,
                requiredPermissions = getRequiredMediaPermissions().toList(),
                explanation = if (legacy) "Storage Access Granted"
                else "External storage read permission required."
            )
        }
    }

    private fun isGranted(context: Context, permission: String): Boolean {
        return ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED
    }
}
