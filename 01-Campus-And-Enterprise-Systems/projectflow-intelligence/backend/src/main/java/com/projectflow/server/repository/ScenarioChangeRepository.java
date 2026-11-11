package com.projectflow.server.repository;

import com.projectflow.server.entity.ScenarioChangeEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface ScenarioChangeRepository extends JpaRepository<ScenarioChangeEntity, UUID> {
    List<ScenarioChangeEntity> findByScenarioId(UUID scenarioId);
}
