package com.projectflow.android.data.local;

import androidx.lifecycle.LiveData;
import androidx.room.*;

import java.util.List;

public interface AppDao {

    @Dao
    interface WorkspaceDao {
        @Query("SELECT * FROM workspaces ORDER BY name ASC")
        LiveData<List<WorkspaceEntity>> getAllLive();

        @Query("SELECT * FROM workspaces ORDER BY name ASC")
        List<WorkspaceEntity> getAllSync();

        @Insert(onConflict = OnConflictStrategy.REPLACE)
        void insertAll(List<WorkspaceEntity> items);

        @Insert(onConflict = OnConflictStrategy.REPLACE)
        void insert(WorkspaceEntity item);
    }

    @Dao
    interface ProjectDao {
        @Query("SELECT * FROM projects WHERE workspaceId = :wsId ORDER BY name ASC")
        LiveData<List<ProjectEntity>> getByWorkspaceLive(String wsId);

        @Query("SELECT * FROM projects ORDER BY name ASC")
        LiveData<List<ProjectEntity>> getAllLive();

        @Query("SELECT * FROM projects ORDER BY name ASC")
        List<ProjectEntity> getAllSync();

        @Query("SELECT * FROM projects WHERE workspaceId = :wsId ORDER BY name ASC")
        List<ProjectEntity> getByWorkspaceSync(String wsId);

        @Insert(onConflict = OnConflictStrategy.REPLACE)
        void insertAll(List<ProjectEntity> items);

        @Insert(onConflict = OnConflictStrategy.REPLACE)
        void insert(ProjectEntity item);

        @Query("DELETE FROM projects")
        void deleteAll();
    }

    @Dao
    interface TaskDao {
        @Query("SELECT * FROM tasks WHERE projectId = :projId ORDER BY title ASC")
        LiveData<List<TaskEntity>> getByProjectLive(String projId);

        @Query("SELECT * FROM tasks WHERE projectId = :projId ORDER BY title ASC")
        List<TaskEntity> getByProjectSync(String projId);

        @Query("SELECT * FROM tasks ORDER BY title ASC")
        LiveData<List<TaskEntity>> getAllLive();

        @Insert(onConflict = OnConflictStrategy.REPLACE)
        void insertAll(List<TaskEntity> items);

        @Insert(onConflict = OnConflictStrategy.REPLACE)
        void insert(TaskEntity item);

        @Update
        void update(TaskEntity item);

        @Query("DELETE FROM tasks")
        void deleteAll();
    }

    @Dao
    interface RiskDao {
        @Query("SELECT * FROM risks WHERE projectId = :projId ORDER BY severity DESC")
        LiveData<List<RiskEntity>> getByProjectLive(String projId);

        @Query("SELECT * FROM risks ORDER BY severity DESC")
        LiveData<List<RiskEntity>> getAllLive();

        @Insert(onConflict = OnConflictStrategy.REPLACE)
        void insertAll(List<RiskEntity> items);

        @Query("DELETE FROM risks WHERE projectId = :projId")
        void deleteByProject(String projId);
    }

    @Dao
    interface SyncQueueDao {
        @Query("SELECT * FROM sync_queue WHERE status = 'PENDING' ORDER BY createdAt ASC")
        List<SyncQueueEntity> getPendingSync();

        @Insert(onConflict = OnConflictStrategy.REPLACE)
        void insert(SyncQueueEntity item);

        @Query("DELETE FROM sync_queue WHERE id = :id")
        void deleteById(String id);

        @Query("SELECT COUNT(*) FROM sync_queue WHERE status = 'PENDING'")
        LiveData<Integer> getPendingCountLive();
    }
}
