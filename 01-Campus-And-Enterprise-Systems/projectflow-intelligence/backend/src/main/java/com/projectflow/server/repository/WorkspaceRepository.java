package com.projectflow.server.repository;

import com.projectflow.server.entity.WorkspaceEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface WorkspaceRepository extends JpaRepository<WorkspaceEntity, UUID> {
    List<WorkspaceEntity> findByOrganizationIdAndArchivedFalse(UUID organizationId);
    Optional<WorkspaceEntity> findByOrganizationIdAndSlug(UUID organizationId, String slug);
    List<WorkspaceEntity> findByArchivedFalse();
}
