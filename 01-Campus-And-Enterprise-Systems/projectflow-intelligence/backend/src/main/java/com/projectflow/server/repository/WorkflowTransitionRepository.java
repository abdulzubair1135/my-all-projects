package com.projectflow.server.repository;

import com.projectflow.server.entity.WorkflowTransitionEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface WorkflowTransitionRepository extends JpaRepository<WorkflowTransitionEntity, UUID> {
    List<WorkflowTransitionEntity> findByWorkflowId(UUID workflowId);
    Optional<WorkflowTransitionEntity> findByWorkflowIdAndFromStatusIdAndToStatusId(UUID workflowId, UUID fromStatusId, UUID toStatusId);
}
