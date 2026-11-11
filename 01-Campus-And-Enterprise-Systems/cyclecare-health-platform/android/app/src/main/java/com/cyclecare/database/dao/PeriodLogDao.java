package com.cyclecare.database.dao;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;

import com.cyclecare.database.entity.PeriodLogEntity;
import java.util.List;

@Dao
public interface PeriodLogDao {
    @Query("SELECT * FROM local_period_logs ORDER BY startDate DESC")
    LiveData<List<PeriodLogEntity>> getAllPeriodLogs();

    @Query("SELECT * FROM local_period_logs ORDER BY startDate DESC")
    List<PeriodLogEntity> getAllPeriodLogsSync();

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertPeriodLog(PeriodLogEntity log);

    @Query("DELETE FROM local_period_logs WHERE id = :logId")
    void deletePeriodLog(String logId);

    @Query("DELETE FROM local_period_logs")
    void clearAll();
}
