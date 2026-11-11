package com.projectflow.server.repository;

import com.projectflow.server.entity.RiskEventEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface RiskEventRepository extends JpaRepository<RiskEventEntity, UUID> {
    List<RiskEventEntity> findByProjectIdAndStatus(UUID projectId, String status);
    List<RiskEventEntity> findByProjectId(UUID projectId);
    Page<RiskEventEntity> findByStatus(String status, Pageable pageable);
    long countByStatus(String status);
}
