package com.cyclecare.database.dao;

import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.Query;
import com.cyclecare.database.entity.SyncQueueEntity;
import java.util.List;

@Dao
public interface SyncQueueDao {
    @Query("SELECT * FROM sync_queue ORDER BY createdAt ASC")
    List<SyncQueueEntity> getPendingSyncItems();

    @Insert
    void insertSyncItem(SyncQueueEntity item);

    @Query("DELETE FROM sync_queue WHERE id = :id")
    void deleteSyncItem(int id);
}
