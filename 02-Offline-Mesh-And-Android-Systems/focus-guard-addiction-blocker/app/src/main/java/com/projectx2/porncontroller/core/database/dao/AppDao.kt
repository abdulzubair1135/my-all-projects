package com.projectx2.porncontroller.core.database.dao

import androidx.room.*
import com.projectx2.porncontroller.core.database.entities.*
import kotlinx.coroutines.flow.Flow

@Dao
interface UserSettingsDao {
    @Query("SELECT * FROM user_settings WHERE id = 1")
    fun getSettingsFlow(): Flow<UserSettings?>

    @Query("SELECT * FROM user_settings WHERE id = 1")
    suspend fun getSettings(): UserSettings?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun updateSettings(settings: UserSettings)
}

@Dao
interface BlockedDomainDao {
    @Query("SELECT * FROM blocked_domains ORDER BY blockedCount DESC, domain ASC")
    fun getAllDomainsFlow(): Flow<List<BlockedDomain>>

    @Query("SELECT * FROM blocked_domains WHERE isEnabled = 1")
    suspend fun getEnabledDomains(): List<BlockedDomain>

    @Query("SELECT * FROM blocked_domains WHERE domain = :domain LIMIT 1")
    suspend fun findDomain(domain: String): BlockedDomain?

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertDomain(domain: BlockedDomain): Long

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertDomains(domains: List<BlockedDomain>)

    @Update
    suspend fun updateDomain(domain: BlockedDomain)

    @Delete
    suspend fun deleteDomain(domain: BlockedDomain)

    @Query("UPDATE blocked_domains SET blockedCount = blockedCount + 1 WHERE domain = :domain")
    suspend fun incrementBlockedCount(domain: String)

    @Query("SELECT COUNT(*) FROM blocked_domains WHERE isEnabled = 1")
    fun getEnabledCountFlow(): Flow<Int>
}

@Dao
interface BlockedKeywordDao {
    @Query("SELECT * FROM blocked_keywords ORDER BY hitCount DESC, keyword ASC")
    fun getAllKeywordsFlow(): Flow<List<BlockedKeyword>>

    @Query("SELECT * FROM blocked_keywords WHERE isEnabled = 1")
    suspend fun getEnabledKeywords(): List<BlockedKeyword>

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertKeyword(keyword: BlockedKeyword): Long

    @Update
    suspend fun updateKeyword(keyword: BlockedKeyword)

    @Delete
    suspend fun deleteKeyword(keyword: BlockedKeyword)

    @Query("UPDATE blocked_keywords SET hitCount = hitCount + 1 WHERE id = :id")
    suspend fun incrementHitCount(id: Long)
}

@Dao
interface DetectionEventDao {
    @Query("SELECT * FROM detection_events ORDER BY timestamp DESC LIMIT :limit")
    fun getRecentEventsFlow(limit: Int = 100): Flow<List<DetectionEvent>>

    @Insert
    suspend fun insertEvent(event: DetectionEvent): Long

    @Query("SELECT COUNT(*) FROM detection_events WHERE timestamp >= :sinceTimestamp")
    suspend fun getEventCountSince(sinceTimestamp: Long): Int

    @Query("SELECT COUNT(*) FROM detection_events WHERE timestamp >= :sinceTimestamp")
    fun getEventCountSinceFlow(sinceTimestamp: Long): Flow<Int>

    @Query("DELETE FROM detection_events")
    suspend fun clearAll()
}

@Dao
interface TaskDao {
    @Query("SELECT * FROM tasks WHERE isEnabled = 1 ORDER BY isPhysical ASC, title ASC")
    fun getActiveTasksFlow(): Flow<List<TaskItem>>

    @Query("SELECT * FROM tasks WHERE id = :id")
    suspend fun getTaskById(id: Long): TaskItem?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTask(task: TaskItem): Long

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertTasks(tasks: List<TaskItem>)

    @Update
    suspend fun updateTask(task: TaskItem)

    @Delete
    suspend fun deleteTask(task: TaskItem)

    @Insert
    suspend fun recordTaskCompletion(history: TaskHistory): Long

    @Query("SELECT * FROM task_history ORDER BY completedAt DESC LIMIT 50")
    fun getTaskHistoryFlow(): Flow<List<TaskHistory>>

    @Query("UPDATE tasks SET completionCount = completionCount + 1 WHERE id = :taskId")
    suspend fun incrementTaskCompletionCount(taskId: Long)

    @Query("SELECT COUNT(*) FROM task_history WHERE completedAt >= :sinceTimestamp")
    fun getCompletedTaskCountSinceFlow(sinceTimestamp: Long): Flow<Int>
}

@Dao
interface FocusSessionDao {
    @Query("SELECT * FROM focus_sessions ORDER BY startedAt DESC")
    fun getAllSessionsFlow(): Flow<List<FocusSession>>

    @Insert
    suspend fun insertSession(session: FocusSession): Long

    @Query("SELECT SUM(actualMinutesCompleted) FROM focus_sessions WHERE startedAt >= :sinceTimestamp")
    fun getFocusMinutesSinceFlow(sinceTimestamp: Long): Flow<Int?>
}

@Dao
interface DailyStatisticDao {
    @Query("SELECT * FROM daily_statistics ORDER BY dateString DESC LIMIT 30")
    fun getRecentDailyStatsFlow(): Flow<List<DailyStatistic>>

    @Query("SELECT * FROM daily_statistics WHERE dateString = :dateString LIMIT 1")
    suspend fun getStatsForDate(dateString: String): DailyStatistic?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrUpdate(stats: DailyStatistic)
}

@Dao
interface HabitStreakDao {
    @Query("SELECT * FROM habit_streaks WHERE id = 1")
    fun getStreakFlow(): Flow<HabitStreak?>

    @Query("SELECT * FROM habit_streaks WHERE id = 1")
    suspend fun getStreak(): HabitStreak?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun updateStreak(streak: HabitStreak)
}
