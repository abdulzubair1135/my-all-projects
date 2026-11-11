package com.projectflow.server.repository;

import com.projectflow.server.entity.WorkflowEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface WorkflowRepository extends JpaRepository<WorkflowEntity, UUID> {
    List<WorkflowEntity> findByWorkspaceId(UUID workspaceId);
    Optional<WorkflowEntity> findByWorkspaceIdAndIsDefaultTrue(UUID workspaceId);
}
