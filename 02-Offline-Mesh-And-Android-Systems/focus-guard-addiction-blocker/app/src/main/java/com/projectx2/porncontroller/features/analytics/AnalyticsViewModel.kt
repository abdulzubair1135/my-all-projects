package com.projectx2.porncontroller.features.analytics

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.projectx2.porncontroller.PornControllerApp
import com.projectx2.porncontroller.core.database.entities.BlockedKeyword
import com.projectx2.porncontroller.core.database.entities.DailyStatistic
import com.projectx2.porncontroller.core.database.entities.HabitStreak
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class AnalyticsUiState(
    val dailyStats: List<DailyStatistic> = emptyList(),
    val streak: HabitStreak? = null,
    val topKeywords: List<BlockedKeyword> = emptyList(),
    val totalBlockedAttempts: Int = 0,
    val totalCompletedTasks: Int = 0,
    val totalFocusMinutes: Int = 0
)

class AnalyticsViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = (application as PornControllerApp).repository

    private val _uiState = MutableStateFlow(AnalyticsUiState())
    val uiState: StateFlow<AnalyticsUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            combine(
                repo.dailyStatsFlow,
                repo.habitStreakFlow,
                repo.allKeywordsFlow
            ) { dailyStatsList, streak, allKeywords ->
                val totalBlocked = dailyStatsList.sumOf { it.blockedDomainsCount + it.blockedKeywordsCount }
                val totalTasks = dailyStatsList.sumOf { it.completedTasksCount }
                val totalFocus = dailyStatsList.sumOf { it.focusMinutesTotal }
                val topKws = allKeywords.filter { it.hitCount > 0 }.sortedByDescending { it.hitCount }.take(5)

                AnalyticsUiState(
                    dailyStats = dailyStatsList.take(7).reversed(),
                    streak = streak,
                    topKeywords = topKws,
                    totalBlockedAttempts = totalBlocked,
                    totalCompletedTasks = totalTasks,
                    totalFocusMinutes = totalFocus
                )
            }.collect {
                _uiState.value = it
            }
        }
    }
}
