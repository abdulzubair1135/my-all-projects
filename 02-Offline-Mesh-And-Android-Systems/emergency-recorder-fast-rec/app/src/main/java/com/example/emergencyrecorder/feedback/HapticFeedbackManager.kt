package com.example.emergencyrecorder.feedback

import android.content.Context
import android.os.Build
import android.os.CombinedVibration
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import com.example.emergencyrecorder.settings.AppSettings

class HapticFeedbackManager(private val context: Context) {

    private val vibrator: Vibrator? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager
        vibratorManager?.defaultVibrator
    } else {
        @Suppress("DEPRECATION")
        context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
    }

    private val appSettings = AppSettings.getInstance(context)

    fun vibrateStart() {
        if (!appSettings.isVibrationEnabled || vibrator == null || !vibrator.hasVibrator()) return

        // Two short, crisp pulses for START: 70ms on, 70ms off, 70ms on
        val timings = longArrayOf(0, 70, 70, 70)
        val amplitudes = intArrayOf(0, 200, 0, 255)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val effect = VibrationEffect.createWaveform(timings, amplitudes, -1)
            vibrator.vibrate(effect)
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(timings, -1)
        }
    }

    fun vibrateStop() {
        if (!appSettings.isVibrationEnabled || vibrator == null || !vibrator.hasVibrator()) return

        // Single sustained pulse for STOP: 180ms
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val effect = VibrationEffect.createOneShot(180, VibrationEffect.DEFAULT_AMPLITUDE)
            vibrator.vibrate(effect)
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(180)
        }
    }

    fun vibrateError() {
        if (!appSettings.isVibrationEnabled || vibrator == null || !vibrator.hasVibrator()) return

        // Three quick sharp pulses: 50ms on, 50ms off, 50ms on, 50ms off, 50ms on
        val timings = longArrayOf(0, 50, 50, 50, 50, 50)
        val amplitudes = intArrayOf(0, 255, 0, 255, 0, 255)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val effect = VibrationEffect.createWaveform(timings, amplitudes, -1)
            vibrator.vibrate(effect)
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(timings, -1)
        }
    }
}
