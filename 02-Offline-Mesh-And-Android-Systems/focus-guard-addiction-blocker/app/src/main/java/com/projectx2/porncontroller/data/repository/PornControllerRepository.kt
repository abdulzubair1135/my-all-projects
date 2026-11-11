package com.projectx2.porncontroller.data.repository

import com.projectx2.porncontroller.core.database.AppDatabase
import com.projectx2.porncontroller.core.database.entities.*
import com.projectx2.porncontroller.core.preferences.PreferenceManager
import kotlinx.coroutines.flow.Flow
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class PornControllerRepository(
    private val database: AppDatabase,
    private val preferenceManager: PreferenceManager
) {
    // User Settings
    val settingsFlow: Flow<UserSettings?> = database.userSettingsDao().getSettingsFlow()
    suspend fun getSettings(): UserSettings? = database.userSettingsDao().getSettings()
    suspend fun updateSettings(settings: UserSettings) = database.userSettingsDao().updateSettings(settings)

    // Blocked Domains
    val allDomainsFlow: Flow<List<BlockedDomain>> = database.blockedDomainDao().getAllDomainsFlow()
    val enabledDomainCountFlow: Flow<Int> = database.blockedDomainDao().getEnabledCountFlow()
    suspend fun getEnabledDomains(): List<BlockedDomain> = database.blockedDomainDao().getEnabledDomains()
    suspend fun insertDomain(domain: BlockedDomain): Long = database.blockedDomainDao().insertDomain(domain)
    suspend fun insertDomains(domains: List<BlockedDomain>) = database.blockedDomainDao().insertDomains(domains)
    suspend fun updateDomain(domain: BlockedDomain) = database.blockedDomainDao().updateDomain(domain)
    suspend fun deleteDomain(domain: BlockedDomain) = database.blockedDomainDao().deleteDomain(domain)
    suspend fun recordDomainBlocked(domain: String) {
        database.blockedDomainDao().incrementBlockedCount(domain)
        database.detectionEventDao().insertEvent(
            DetectionEvent(
                type = "DOMAIN",
                triggerSource = domain,
                actionTaken = "BLOCKED"
            )
        )
        updateDailyStats(blockedDomain = true)
    }

    // Blocked Keywords
    val allKeywordsFlow: Flow<List<BlockedKeyword>> = database.blockedKeywordDao().getAllKeywordsFlow()
    suspend fun getEnabledKeywords(): List<BlockedKeyword> = database.blockedKeywordDao().getEnabledKeywords()
    suspend fun insertKeyword(keyword: BlockedKeyword): Long = database.blockedKeywordDao().insertKeyword(keyword)
    suspend fun updateKeyword(keyword: BlockedKeyword) = database.blockedKeywordDao().updateKeyword(keyword)
    suspend fun deleteKeyword(keyword: BlockedKeyword) = database.blockedKeywordDao().deleteKeyword(keyword)
    suspend fun recordKeywordDetected(id: Long, keyword: String, appPackage: String?) {
        database.blockedKeywordDao().incrementHitCount(id)
        database.detectionEventDao().insertEvent(
            DetectionEvent(
                type = "KEYWORD",
                triggerSource = keyword,
                appPackage = appPackage,
                actionTaken = "INTERVENTION"
            )
        )
        updateDailyStats(blockedKeyword = true)
    }

    // Detection Events & History
    val recentEventsFlow: Flow<List<DetectionEvent>> = database.detectionEventDao().getRecentEventsFlow()
    suspend fun clearHistory() = database.detectionEventDao().clearAll()

    // Tasks & Replacement Engine
    val activeTasksFlow: Flow<List<TaskItem>> = database.taskDao().getActiveTasksFlow()
    val taskHistoryFlow: Flow<List<TaskHistory>> = database.taskDao().getTaskHistoryFlow()
    suspend fun getTaskById(id: Long): TaskItem? = database.taskDao().getTaskById(id)
    suspend fun insertTask(task: TaskItem): Long = database.taskDao().insertTask(task)
    suspend fun updateTask(task: TaskItem) = database.taskDao().updateTask(task)
    suspend fun deleteTask(task: TaskItem) = database.taskDao().deleteTask(task)
    suspend fun recordTaskCompletion(taskId: Long, title: String, durationSec: Int) {
        database.taskDao().incrementTaskCompletionCount(taskId)
        database.taskDao().recordTaskCompletion(
            TaskHistory(
                taskId = taskId,
                taskTitle = title,
                durationSeconds = durationSec,
                wasCompleted = true
            )
        )
        updateDailyStats(taskCompleted = true)
    }

    // Focus Sessions
    val focusSessionsFlow: Flow<List<FocusSession>> = database.focusSessionDao().getAllSessionsFlow()
    suspend fun recordFocusSession(targetMin: Int, actualMin: Int, startedAt: Long, successful: Boolean) {
        database.focusSessionDao().insertSession(
            FocusSession(
                targetMinutes = targetMin,
                actualMinutesCompleted = actualMin,
                startedAt = startedAt,
                wasSuccessful = successful
            )
        )
        updateDailyStats(focusMinutes = actualMin)
    }

    // Habit Streaks
    val habitStreakFlow: Flow<HabitStreak?> = database.habitStreakDao().getStreakFlow()
    suspend fun updateHabitStreak(streak: HabitStreak) = database.habitStreakDao().updateStreak(streak)

    // Daily Statistics
    val dailyStatsFlow: Flow<List<DailyStatistic>> = database.dailyStatisticDao().getRecentDailyStatsFlow()

    private fun getTodayDateString(): String {
        return SimpleDateFormat("yyyy-MM-dd", Locale.ROOT).format(Date())
    }

    private suspend fun updateDailyStats(
        blockedDomain: Boolean = false,
        blockedKeyword: Boolean = false,
        taskCompleted: Boolean = false,
        focusMinutes: Int = 0
    ) {
        val today = getTodayDateString()
        val current = database.dailyStatisticDao().getStatsForDate(today) ?: DailyStatistic(dateString = today)
        val updated = current.copy(
            blockedDomainsCount = current.blockedDomainsCount + (if (blockedDomain) 1 else 0),
            blockedKeywordsCount = current.blockedKeywordsCount + (if (blockedKeyword) 1 else 0),
            completedTasksCount = current.completedTasksCount + (if (taskCompleted) 1 else 0),
            focusMinutesTotal = current.focusMinutesTotal + focusMinutes
        )
        database.dailyStatisticDao().insertOrUpdate(updated)
    }

    // Data wipe
    suspend fun wipeAllUserData() {
        database.detectionEventDao().clearAll()
        database.clearAllTables()
    }
}
