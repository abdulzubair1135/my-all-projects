package com.projectx2.porncontroller.features.focus

import android.app.Application
import android.content.Context
import android.content.Intent
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.projectx2.porncontroller.PornControllerApp
import com.projectx2.porncontroller.core.database.entities.FocusSession
import com.projectx2.porncontroller.services.FocusService
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class FocusUiState(
    val sessions: List<FocusSession> = emptyList(),
    val isRunning: Boolean = false,
    val isPaused: Boolean = false,
    val remainingSeconds: Int = 0,
    val selectedMinutes: Int = 25
)

class FocusViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = (application as PornControllerApp).repository
    private val context: Context = application.applicationContext

    private val _selectedMinutes = MutableStateFlow(25)
    private val _uiState = MutableStateFlow(FocusUiState())
    val uiState: StateFlow<FocusUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            combine(
                repo.focusSessionsFlow,
                FocusService.isRunningFlow,
                FocusService.isPausedFlow,
                FocusService.remainingSecondsFlow,
                _selectedMinutes
            ) { sessions, isRunning, isPaused, remaining, selectedMin ->
                FocusUiState(
                    sessions = sessions,
                    isRunning = isRunning,
                    isPaused = isPaused,
                    remainingSeconds = remaining,
                    selectedMinutes = selectedMin
                )
            }.collect {
                _uiState.value = it
            }
        }
    }

    fun selectPreset(minutes: Int) {
        _selectedMinutes.value = minutes
    }

    fun startFocusSession(minutes: Int = _selectedMinutes.value) {
        val intent = Intent(context, FocusService::class.java).apply {
            action = FocusService.ACTION_START
            putExtra(FocusService.EXTRA_DURATION_MINUTES, minutes)
        }
        context.startService(intent)
    }

    fun pauseFocusSession() {
        val intent = Intent(context, FocusService::class.java).apply {
            action = FocusService.ACTION_PAUSE
        }
        context.startService(intent)
    }

    fun resumeFocusSession() {
        val intent = Intent(context, FocusService::class.java).apply {
            action = FocusService.ACTION_RESUME
        }
        context.startService(intent)
    }

    fun stopFocusSession() {
        val intent = Intent(context, FocusService::class.java).apply {
            action = FocusService.ACTION_STOP
        }
        context.startService(intent)
    }
}
