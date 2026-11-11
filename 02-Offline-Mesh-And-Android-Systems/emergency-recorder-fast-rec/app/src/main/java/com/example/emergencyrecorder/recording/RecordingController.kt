package com.example.emergencyrecorder.recording

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.util.Log
import androidx.core.content.ContextCompat
import com.example.emergencyrecorder.feedback.HapticFeedbackManager
import com.example.emergencyrecorder.permissions.PermissionManager
import com.example.emergencyrecorder.storage.RecordingStorage
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

object RecordingController {

    private const val TAG = "RecordingController"

    private val _state = MutableStateFlow<RecordingState>(RecordingState.Idle)
    val state: StateFlow<RecordingState> = _state.asStateFlow()

    @Synchronized
    fun toggleRecording(context: Context) {
        val currentState = _state.value
        Log.d(TAG, "toggleRecording requested while state=$currentState")
        if (currentState.canStop) {
            requestStopRecording(context)
        } else if (currentState.canStart) {
            requestStartRecording(context)
        } else {
            Log.w(TAG, "Cannot toggle recording during transient state $currentState")
        }
    }

    @Synchronized
    fun requestStartRecording(context: Context, prefix: String = "Emergency") {
        val currentState = _state.value
        if (!currentState.canStart) {
            Log.w(TAG, "requestStartRecording ignored: current state is $currentState")
            return
        }

        // Validate audio permission
        if (!PermissionManager.hasRecordAudioPermission(context)) {
            val msg = "Cannot record: Microphone permission is missing."
            Log.e(TAG, msg)
            _state.value = RecordingState.Error(msg)
            HapticFeedbackManager(context).vibrateError()
            return
        }

        // Validate storage availability
        if (!RecordingStorage.hasSufficientStorage(context)) {
            val msg = "Cannot record: Device storage is too low."
            Log.e(TAG, msg)
            _state.value = RecordingState.Error(msg)
            HapticFeedbackManager(context).vibrateError()
            return
        }

        _state.value = RecordingState.Starting

        val serviceIntent = Intent(context, RecordingService::class.java).apply {
            action = RecordingService.ACTION_START
            putExtra(RecordingService.EXTRA_PREFIX, prefix)
        }
        try {
            ContextCompat.startForegroundService(context, serviceIntent)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start RecordingService", e)
            _state.value = RecordingState.Error("Failed to start foreground service: ${e.localizedMessage}")
            HapticFeedbackManager(context).vibrateError()
        }
    }

    @Synchronized
    fun requestStopRecording(context: Context) {
        val currentState = _state.value
        if (!currentState.canStop) {
            Log.w(TAG, "requestStopRecording ignored: current state is $currentState")
            return
        }

        _state.value = RecordingState.Stopping

        val serviceIntent = Intent(context, RecordingService::class.java).apply {
            action = RecordingService.ACTION_STOP
        }
        try {
            context.startService(serviceIntent)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to send stop action to RecordingService", e)
            _state.value = RecordingState.Idle
        }
    }

    @Synchronized
    fun notifyRecordingStarted(startTimeMs: Long, uri: Uri) {
        _state.value = RecordingState.Recording(
            startTimeMs = startTimeMs,
            outputUri = uri
        )
    }

    @Synchronized
    fun notifyRecordingStopped() {
        _state.value = RecordingState.Idle
    }

    @Synchronized
    fun notifyRecordingError(message: String) {
        _state.value = RecordingState.Error(message)
    }
}
