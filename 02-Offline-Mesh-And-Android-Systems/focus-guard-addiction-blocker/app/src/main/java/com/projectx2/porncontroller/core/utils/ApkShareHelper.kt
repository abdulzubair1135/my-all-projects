package com.projectx2.porncontroller.core.utils

import android.content.Context
import android.content.Intent
import android.widget.Toast
import androidx.core.content.FileProvider
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream

object ApkShareHelper {

    fun shareAppApk(context: Context) {
        try {
            val appInfo = context.applicationInfo
            val sourceApk = File(appInfo.sourceDir)
            if (!sourceApk.exists()) {
                Toast.makeText(context, "APK source not found on device", Toast.LENGTH_SHORT).show()
                return
            }

            // Copy to shared_apk cache with clean user-friendly filename
            val destDir = File(context.cacheDir, "shared_apk")
            if (!destDir.exists()) destDir.mkdirs()
            val destApk = File(destDir, "PRN_Controller_by_projectX2.apk")

            FileInputStream(sourceApk).use { input ->
                FileOutputStream(destApk).use { output ->
                    input.copyTo(output)
                }
            }

            val apkUri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                destApk
            )

            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                type = "application/vnd.android.package-archive"
                putExtra(Intent.EXTRA_STREAM, apkUri)
                putExtra(
                    Intent.EXTRA_TEXT,
                    "P.RN Controller (made by projectX²)\nOffline Digital Addiction Prevention & Self-Control Android App."
                )
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }

            val chooser = Intent.createChooser(shareIntent, "Share P.RN Controller APK via:")
            chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(chooser)
        } catch (e: Exception) {
            Toast.makeText(context, "Failed to share APK: ${e.localizedMessage}", Toast.LENGTH_LONG).show()
        }
    }
}
