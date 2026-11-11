package com.projectflow.server.service;

import com.projectflow.server.entity.AuditLogEntity;
import com.projectflow.server.repository.AuditLogRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.UUID;

@Service
public class AuditService {

    private static final Logger log = LoggerFactory.getLogger(AuditService.class);
    private final AuditLogRepository auditLogRepository;

    public AuditService(AuditLogRepository auditLogRepository) {
        this.auditLogRepository = auditLogRepository;
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void record(UUID organizationId, UUID workspaceId, UUID actorId, String actorEmail,
                       String action, String entityType, UUID entityId, String details, String ipAddress) {
        try {
            AuditLogEntity logEntity = new AuditLogEntity(
                    organizationId, workspaceId, actorId, actorEmail,
                    action, entityType, entityId, details, ipAddress
            );
            logEntity.setTimestamp(Instant.now());
            auditLogRepository.save(logEntity);
            log.info("AUDIT [{}] {} by user {} (ID: {})", entityType, action, actorEmail, actorId);
        } catch (Exception e) {
            log.error("Failed to record audit log: {}", e.getMessage());
        }
    }
}
