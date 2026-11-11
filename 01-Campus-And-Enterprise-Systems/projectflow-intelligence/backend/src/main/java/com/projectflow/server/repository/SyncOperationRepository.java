package com.projectflow.server.repository;

import com.projectflow.server.entity.SyncOperationEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface SyncOperationRepository extends JpaRepository<SyncOperationEntity, UUID> {
    Optional<SyncOperationEntity> findByClientOperationId(String clientOperationId);
    Page<SyncOperationEntity> findByStatus(String status, Pageable pageable);
    long countByStatus(String status);
}
