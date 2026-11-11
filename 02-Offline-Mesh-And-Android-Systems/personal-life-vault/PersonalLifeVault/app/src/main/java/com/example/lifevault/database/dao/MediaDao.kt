package com.example.lifevault.database.dao

import androidx.room.*
import com.example.lifevault.database.entities.MediaEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface MediaDao {

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insert(media: MediaEntity): Long

    @Query("SELECT * FROM local_media WHERE uri = :uri LIMIT 1")
    suspend fun getByUri(uri: String): MediaEntity?

    @Query("SELECT * FROM local_media ORDER BY timestamp DESC LIMIT :limit")
    fun getRecentMedia(limit: Int = 100): Flow<List<MediaEntity>>

    @Query("SELECT COUNT(*) FROM local_media")
    fun getCount(): Flow<Int>
}
