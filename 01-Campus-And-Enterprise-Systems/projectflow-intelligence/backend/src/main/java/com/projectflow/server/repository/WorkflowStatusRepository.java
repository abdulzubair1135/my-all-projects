package com.projectflow.server.repository;

import com.projectflow.server.entity.WorkflowStatusEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface WorkflowStatusRepository extends JpaRepository<WorkflowStatusEntity, UUID> {
    List<WorkflowStatusEntity> findByWorkflowIdOrderByPositionAsc(UUID workflowId);
}
