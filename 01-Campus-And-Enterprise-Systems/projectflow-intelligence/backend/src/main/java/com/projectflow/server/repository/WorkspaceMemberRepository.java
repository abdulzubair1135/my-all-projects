package com.projectflow.server.repository;

import com.projectflow.server.entity.WorkspaceMemberEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface WorkspaceMemberRepository extends JpaRepository<WorkspaceMemberEntity, UUID> {
    Optional<WorkspaceMemberEntity> findByWorkspaceIdAndUserId(UUID workspaceId, UUID userId);
    List<WorkspaceMemberEntity> findByWorkspaceId(UUID workspaceId);
    List<WorkspaceMemberEntity> findByUserId(UUID userId);
}
