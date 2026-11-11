package com.projectflow.server.repository;

import com.projectflow.server.entity.ProjectEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface ProjectRepository extends JpaRepository<ProjectEntity, UUID> {
    List<ProjectEntity> findByWorkspaceIdAndArchivedFalse(UUID workspaceId);
    Page<ProjectEntity> findByWorkspaceIdAndArchivedFalse(UUID workspaceId, Pageable pageable);
    Optional<ProjectEntity> findByIdAndArchivedFalse(UUID id);
    long countByArchivedFalse();
}
