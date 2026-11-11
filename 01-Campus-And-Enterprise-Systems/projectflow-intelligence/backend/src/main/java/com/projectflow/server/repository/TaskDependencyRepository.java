package com.projectflow.server.repository;

import com.projectflow.server.entity.TaskDependencyEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface TaskDependencyRepository extends JpaRepository<TaskDependencyEntity, UUID> {
    List<TaskDependencyEntity> findByTaskId(UUID taskId);
    List<TaskDependencyEntity> findByPredecessorTaskId(UUID predecessorTaskId);
    Optional<TaskDependencyEntity> findByTaskIdAndPredecessorTaskId(UUID taskId, UUID predecessorTaskId);
}
