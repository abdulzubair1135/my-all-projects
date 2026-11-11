package com.projectflow.server.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.projectflow.server.dto.SyncBatchRequest;
import com.projectflow.server.dto.SyncBatchResponse;
import com.projectflow.server.entity.SyncOperationEntity;
import com.projectflow.server.entity.TaskEntity;
import com.projectflow.server.repository.SyncOperationRepository;
import com.projectflow.server.repository.TaskRepository;
import com.projectflow.server.security.UserPrincipal;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Service
public class SyncService {

    private static final Logger log = LoggerFactory.getLogger(SyncService.class);

    private final SyncOperationRepository syncOperationRepository;
    private final TaskRepository taskRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public SyncService(SyncOperationRepository syncOperationRepository, TaskRepository taskRepository) {
        this.syncOperationRepository = syncOperationRepository;
        this.taskRepository = taskRepository;
    }

    @Transactional
    public SyncBatchResponse processBatch(SyncBatchRequest request, UserPrincipal principal) {
        List<SyncBatchResponse.SyncResultItem> results = new ArrayList<>();

        if (request == null || request.getOperations() == null) {
            return new SyncBatchResponse(results);
        }

        for (SyncBatchRequest.SyncItem op : request.getOperations()) {
            // 1. Idempotency check
            Optional<SyncOperationEntity> existingOp = syncOperationRepository.findByClientOperationId(op.getClientOperationId());
            if (existingOp.isPresent()) {
                log.info("Duplicate sync operation ignored: {}", op.getClientOperationId());
                results.add(new SyncBatchResponse.SyncResultItem(
                        op.getClientOperationId(),
                        "DUPLICATE_IGNORED",
                        existingOp.get().getBaseVersion(),
                        "Operation already processed."
                ));
                continue;
            }

            SyncOperationEntity record = new SyncOperationEntity(
                    op.getClientOperationId(),
                    op.getEntityType(),
                    op.getEntityId(),
                    op.getOperationType(),
                    op.getPayloadJson(),
                    op.getBaseVersion(),
                    op.getClientCreatedAt()
            );

            // 2. Process by entity type
            if ("TASK".equalsIgnoreCase(op.getEntityType())) {
                processTaskSync(op, record, results);
            } else {
                record.setStatus("UNSUPPORTED_ENTITY");
                record.setProcessedAt(Instant.now());
                syncOperationRepository.save(record);
                results.add(new SyncBatchResponse.SyncResultItem(
                        op.getClientOperationId(),
                        "FAILED",
                        null,
                        "Unsupported entity type: " + op.getEntityType()
                ));
            }
        }

        return new SyncBatchResponse(results);
    }

    private void processTaskSync(SyncBatchRequest.SyncItem op, SyncOperationEntity record,
                                 List<SyncBatchResponse.SyncResultItem> results) {
        Optional<TaskEntity> taskOpt = taskRepository.findById(op.getEntityId());

        if (taskOpt.isEmpty()) {
            record.setStatus("NOT_FOUND");
            record.setProcessedAt(Instant.now());
            syncOperationRepository.save(record);
            results.add(new SyncBatchResponse.SyncResultItem(
                    op.getClientOperationId(),
                    "FAILED",
                    null,
                    "Task not found: " + op.getEntityId()
            ));
            return;
        }

        TaskEntity task = taskOpt.get();

        // Version Conflict Detection: If server version has advanced beyond client base version
        if (task.getVersion() > op.getBaseVersion()) {
            record.setStatus("CONFLICT");
            record.setErrorMessage("Server version (" + task.getVersion() + ") is newer than client base (" + op.getBaseVersion() + ")");
            record.setProcessedAt(Instant.now());
            syncOperationRepository.save(record);

            results.add(new SyncBatchResponse.SyncResultItem(
                    op.getClientOperationId(),
                    "CONFLICT",
                    task.getVersion(),
                    record.getErrorMessage()
            ));
            return;
        }

        try {
            // Apply updates from payload
            if (op.getPayloadJson() != null && !op.getPayloadJson().isBlank()) {
                var jsonNode = objectMapper.readTree(op.getPayloadJson());
                if (jsonNode.has("title")) {
                    task.setTitle(jsonNode.get("title").asText());
                }
                if (jsonNode.has("description")) {
                    task.setDescription(jsonNode.get("description").asText());
                }
            }

            task = taskRepository.save(task);

            record.setStatus("SYNCED");
            record.setProcessedAt(Instant.now());
            syncOperationRepository.save(record);

            results.add(new SyncBatchResponse.SyncResultItem(
                    op.getClientOperationId(),
                    "SYNCED",
                    task.getVersion(),
                    "Synchronized successfully."
            ));
        } catch (Exception e) {
            record.setStatus("FAILED");
            record.setErrorMessage(e.getMessage());
            record.setProcessedAt(Instant.now());
            syncOperationRepository.save(record);

            results.add(new SyncBatchResponse.SyncResultItem(
                    op.getClientOperationId(),
                    "FAILED",
                    task.getVersion(),
                    "Error applying sync: " + e.getMessage()
            ));
        }
    }
}
