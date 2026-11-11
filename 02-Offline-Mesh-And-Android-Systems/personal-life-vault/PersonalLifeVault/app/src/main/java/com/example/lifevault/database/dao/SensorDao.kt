package com.example.lifevault.database.dao

import androidx.room.*
import com.example.lifevault.database.entities.SensorEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface SensorDao {

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insert(sensor: SensorEntity): Long

    @Query("SELECT * FROM local_sensors ORDER BY timestamp DESC LIMIT :limit")
    fun getRecentSensors(limit: Int = 100): Flow<List<SensorEntity>>

    @Query("SELECT COUNT(*) FROM local_sensors")
    fun getCount(): Flow<Int>
}
