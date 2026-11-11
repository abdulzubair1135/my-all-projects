package com.projectx2.porncontroller.features.dashboard

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.projectx2.porncontroller.PornControllerApp
import com.projectx2.porncontroller.core.database.entities.DailyStatistic
import com.projectx2.porncontroller.core.database.entities.HabitStreak
import com.projectx2.porncontroller.core.database.entities.UserSettings
import com.projectx2.porncontroller.services.AccessibilityMonitorService
import com.projectx2.porncontroller.services.LocalVpnService
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

data class DashboardUiState(
    val settings: UserSettings? = null,
    val streak: HabitStreak? = null,
    val todayStats: DailyStatistic? = null,
    val isVpnRunning: Boolean = false,
    val isAccessibilityRunning: Boolean = false,
    val activeDomainCount: Int = 0
)

data class DbData(
    val settings: UserSettings?,
    val streak: HabitStreak?,
    val dailyStats: List<DailyStatistic>,
    val domainCount: Int
)

class DashboardViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = (application as PornControllerApp).repository
    private val context = application.applicationContext

    private val _uiState = MutableStateFlow(DashboardUiState())
    val uiState: StateFlow<DashboardUiState> = _uiState.asStateFlow()

    init {
        val todayStr = SimpleDateFormat("yyyy-MM-dd", Locale.ROOT).format(Date())

        val dbDataFlow = combine(
            repo.settingsFlow,
            repo.habitStreakFlow,
            repo.dailyStatsFlow,
            repo.enabledDomainCountFlow
        ) { settings, streak, dailyStats, domainCount ->
            DbData(settings, streak, dailyStats, domainCount)
        }

        val serviceFlow = combine(
            LocalVpnService.isRunningFlow,
            AccessibilityMonitorService.isRunningFlow
        ) { vpnRunning, accRunning ->
            val isAccActive = accRunning || AccessibilityMonitorService.isAccessibilityEnabledInSystem(context)
            Pair(vpnRunning || LocalVpnService.isRunning, isAccActive)
        }

        viewModelScope.launch {
            combine(dbDataFlow, serviceFlow) { dbData, (vpnRunning, accRunning) ->
                val todayStat = dbData.dailyStats.find { it.dateString == todayStr }
                DashboardUiState(
                    settings = dbData.settings,
                    streak = dbData.streak,
                    todayStats = todayStat,
                    isVpnRunning = vpnRunning,
                    isAccessibilityRunning = accRunning,
                    activeDomainCount = dbData.domainCount
                )
            }.collect { newState ->
                _uiState.value = newState
            }
        }
    }

    fun toggleDomainProtection(enabled: Boolean) {
        viewModelScope.launch {
            val current = _uiState.value.settings ?: return@launch
            repo.updateSettings(current.copy(isDomainProtectionEnabled = enabled))
            refreshServiceStates()
        }
    }

    fun toggleKeywordMonitoring(enabled: Boolean) {
        viewModelScope.launch {
            val current = _uiState.value.settings ?: return@launch
            repo.updateSettings(current.copy(isKeywordMonitoringEnabled = enabled))
            refreshServiceStates()
        }
    }

    fun refreshServiceStates() {
        val isAccActive = AccessibilityMonitorService.isRunning || 
            AccessibilityMonitorService.isAccessibilityEnabledInSystem(context)
        _uiState.update {
            it.copy(
                isVpnRunning = LocalVpnService.isRunning,
                isAccessibilityRunning = isAccActive
            )
        }
    }
}
