package com.example.lifevault.database.dao

import androidx.room.*
import com.example.lifevault.database.entities.SyncQueueEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface SyncQueueDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun enqueue(item: SyncQueueEntity): Long

    @Query("SELECT * FROM sync_queue WHERE syncStatus = 'PENDING' AND dataType != 'MEDIA' ORDER BY createdAt ASC LIMIT :limit")
    suspend fun getPendingTextBatch(limit: Int = 100): List<SyncQueueEntity>

    @Query("SELECT * FROM sync_queue WHERE syncStatus = 'PENDING' AND dataType = 'MEDIA' ORDER BY createdAt DESC LIMIT :limit")
    suspend fun getPendingMediaBatch(limit: Int = 10): List<SyncQueueEntity>

    @Query("UPDATE sync_queue SET syncStatus = :status, lastError = :error WHERE id = :id")
    suspend fun updateStatus(id: Long, status: String, error: String? = null)

    @Query("UPDATE sync_queue SET syncStatus = 'FAILED', retryCount = retryCount + 1, lastError = :error WHERE id = :id")
    suspend fun markFailed(id: Long, error: String)

    @Query("UPDATE sync_queue SET syncStatus = 'PENDING', retryCount = retryCount + 1, lastError = :error WHERE id = :id")
    suspend fun markRetry(id: Long, error: String)

    @Query("SELECT COUNT(*) FROM sync_queue WHERE syncStatus = 'PENDING'")
    fun getPendingCountFlow(): Flow<Int>

    @Query("SELECT COUNT(*) FROM sync_queue WHERE syncStatus = 'PENDING' AND dataType != 'MEDIA'")
    fun getPendingTextCountFlow(): Flow<Int>

    @Query("SELECT COUNT(*) FROM sync_queue WHERE syncStatus = 'PENDING' AND dataType = 'MEDIA'")
    fun getPendingMediaCountFlow(): Flow<Int>

    @Query("SELECT COUNT(*) FROM sync_queue WHERE syncStatus = 'SYNCED'")
    fun getSyncedCountFlow(): Flow<Int>

    @Query("SELECT COUNT(*) FROM sync_queue WHERE syncStatus = 'FAILED'")
    fun getFailedCountFlow(): Flow<Int>

    @Query("DELETE FROM sync_queue WHERE syncStatus = 'SYNCED' AND createdAt < :timestampBefore")
    suspend fun cleanOldSynced(timestampBefore: Long)
}
