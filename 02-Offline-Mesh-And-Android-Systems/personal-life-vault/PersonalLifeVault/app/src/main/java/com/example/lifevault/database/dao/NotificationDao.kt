package com.example.lifevault.database.dao

import androidx.room.*
import com.example.lifevault.database.entities.NotificationEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface NotificationDao {

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insert(notification: NotificationEntity): Long

    @Query("SELECT * FROM local_notifications ORDER BY timestamp DESC LIMIT :limit")
    fun getRecentNotifications(limit: Int = 100): Flow<List<NotificationEntity>>

    @Query("SELECT COUNT(*) FROM local_notifications")
    fun getCount(): Flow<Int>
}
