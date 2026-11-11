package com.projectflow.server.repository;

import com.projectflow.server.entity.TaskEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface TaskRepository extends JpaRepository<TaskEntity, UUID> {
    List<TaskEntity> findByProjectIdAndArchivedFalseOrderByPositionAsc(UUID projectId);
    Page<TaskEntity> findByProjectIdAndArchivedFalse(UUID projectId, Pageable pageable);
    Optional<TaskEntity> findByIdAndArchivedFalse(UUID id);
    List<TaskEntity> findByAssigneeIdAndArchivedFalse(UUID assigneeId);
    long countByArchivedFalse();
    long countByArchivedFalseAndCompletedAtIsNotNull();
}
