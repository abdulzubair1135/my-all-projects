package com.example.emergencyrecorder.settings

import android.content.Context
import android.content.SharedPreferences

class AppSettings(context: Context) {

    private val prefs: SharedPreferences =
        context.applicationContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    var isShortcutEnabled: Boolean
        get() = prefs.getBoolean(KEY_SHORTCUT_ENABLED, true)
        set(value) = prefs.edit().putBoolean(KEY_SHORTCUT_ENABLED, value).apply()

    var isScreenOffTriggerEnabled: Boolean
        get() = prefs.getBoolean(KEY_SCREEN_OFF_TRIGGER, false)
        set(value) = prefs.edit().putBoolean(KEY_SCREEN_OFF_TRIGGER, value).apply()

    var isAutoCallRecordingEnabled: Boolean
        get() = prefs.getBoolean(KEY_AUTO_CALL_RECORDING, true)
        set(value) = prefs.edit().putBoolean(KEY_AUTO_CALL_RECORDING, value).apply()

    var doublePressIntervalMs: Long
        get() = prefs.getLong(KEY_DOUBLE_PRESS_INTERVAL, DEFAULT_DOUBLE_PRESS_INTERVAL_MS)
        set(value) = prefs.edit().putLong(KEY_DOUBLE_PRESS_INTERVAL, value).apply()

    var isVibrationEnabled: Boolean
        get() = prefs.getBoolean(KEY_VIBRATION_ENABLED, true)
        set(value) = prefs.edit().putBoolean(KEY_VIBRATION_ENABLED, value).apply()

    var recordingQuality: RecordingQuality
        get() {
            val name = prefs.getString(KEY_RECORDING_QUALITY, RecordingQuality.STANDARD.name)
            return try {
                RecordingQuality.valueOf(name ?: RecordingQuality.STANDARD.name)
            } catch (e: IllegalArgumentException) {
                RecordingQuality.STANDARD
            }
        }
        set(value) = prefs.edit().putString(KEY_RECORDING_QUALITY, value.name).apply()

    var autoStopMinutes: Int
        get() = prefs.getInt(KEY_AUTO_STOP_MINUTES, 0) // 0 = disabled
        set(value) = prefs.edit().putInt(KEY_AUTO_STOP_MINUTES, value).apply()

    var callAudioSource: CallAudioSource
        get() {
            val name = prefs.getString(KEY_CALL_AUDIO_SOURCE, CallAudioSource.VOICE_RECOGNITION.name)
            return try {
                CallAudioSource.valueOf(name ?: CallAudioSource.VOICE_RECOGNITION.name)
            } catch (e: Exception) {
                CallAudioSource.VOICE_RECOGNITION
            }
        }
        set(value) = prefs.edit().putString(KEY_CALL_AUDIO_SOURCE, value.name).apply()

    var isAutoSpeakerOnCallEnabled: Boolean
        get() = prefs.getBoolean(KEY_AUTO_SPEAKER_ON_CALL, true)
        set(value) = prefs.edit().putBoolean(KEY_AUTO_SPEAKER_ON_CALL, value).apply()

    enum class CallAudioSource(val source: Int, val label: String) {
        VOICE_RECOGNITION(6, "Voice Recognition (Software - Recommended)"),
        VOICE_COMMUNICATION(7, "Voice Communication (VoIP/AEC)"),
        MIC(1, "Standard Microphone"),
        UNPROCESSED(9, "Unprocessed Audio")
    }

    enum class RecordingQuality(val bitRate: Int, val sampleRate: Int, val label: String) {
        STANDARD(bitRate = 128000, sampleRate = 44100, label = "Standard (128 kbps, 44.1 kHz)"),
        HIGH(bitRate = 256000, sampleRate = 48000, label = "High (256 kbps, 48 kHz)")
    }

    companion object {
        private const val PREFS_NAME = "emergency_recorder_prefs"
        private const val KEY_SHORTCUT_ENABLED = "key_shortcut_enabled"
        private const val KEY_SCREEN_OFF_TRIGGER = "key_screen_off_trigger"
        private const val KEY_AUTO_CALL_RECORDING = "key_auto_call_recording"
        private const val KEY_DOUBLE_PRESS_INTERVAL = "key_double_press_interval"
        private const val KEY_VIBRATION_ENABLED = "key_vibration_enabled"
        private const val KEY_RECORDING_QUALITY = "key_recording_quality"
        private const val KEY_AUTO_STOP_MINUTES = "key_auto_stop_minutes"
        private const val KEY_CALL_AUDIO_SOURCE = "key_call_audio_source"
        private const val KEY_AUTO_SPEAKER_ON_CALL = "key_auto_speaker_on_call"

        const val DEFAULT_DOUBLE_PRESS_INTERVAL_MS = 650L
        const val MIN_DOUBLE_PRESS_INTERVAL_MS = 250L
        const val MAX_DOUBLE_PRESS_INTERVAL_MS = 1000L

        @Volatile
        private var INSTANCE: AppSettings? = null

        fun getInstance(context: Context): AppSettings {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: AppSettings(context).also { INSTANCE = it }
            }
        }
    }
}
