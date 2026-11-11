package com.projectflow.server.repository;

import com.projectflow.server.entity.AuditLogEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface AuditLogRepository extends JpaRepository<AuditLogEntity, UUID> {
    Page<AuditLogEntity> findAllByOrderByTimestampDesc(Pageable pageable);
    Page<AuditLogEntity> findByOrganizationIdOrderByTimestampDesc(UUID organizationId, Pageable pageable);
    Page<AuditLogEntity> findByActionContainingIgnoreCaseOrActorEmailContainingIgnoreCase(String action, String actorEmail, Pageable pageable);
}
