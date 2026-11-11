package com.example.lifevault.database.dao

import androidx.room.*
import com.example.lifevault.database.entities.TelecomEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface TelecomDao {

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insert(telecom: TelecomEntity): Long

    @Query("SELECT * FROM local_telecom ORDER BY timestamp DESC LIMIT :limit")
    fun getRecentTelecom(limit: Int = 100): Flow<List<TelecomEntity>>

    @Query("SELECT COUNT(*) FROM local_telecom")
    fun getCount(): Flow<Int>
}
