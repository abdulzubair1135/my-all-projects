package com.projectflow.server.entity;

import com.projectflow.core.model.RiskRuleId;
import com.projectflow.core.model.RiskSeverity;
import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "risk_events")
public class RiskEventEntity {

    @Id
    private UUID id = UUID.randomUUID();

    @Column(name = "project_id", nullable = false)
    private UUID projectId;

    @Enumerated(EnumType.STRING)
    @Column(name = "rule_id", nullable = false)
    private RiskRuleId ruleId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RiskSeverity severity;

    @Column(name = "affected_entity_type", nullable = false)
    private String affectedEntityType;

    @Column(name = "affected_entity_id", nullable = false)
    private UUID affectedEntityId;

    @Column(name = "affected_entity_name", nullable = false)
    private String affectedEntityName;

    @Column(nullable = false, length = 1000)
    private String explanation;

    @Column(name = "supporting_evidence", nullable = false, length = 1000)
    private String supportingEvidence;

    @Column(name = "suggested_action", nullable = false, length = 1000)
    private String suggestedAction;

    @Column(nullable = false)
    private String status = "ACTIVE";

    @Column(name = "detected_at", nullable = false)
    private Instant detectedAt = Instant.now();

    @Column(name = "resolved_at")
    private Instant resolvedAt;

    public RiskEventEntity() {
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getProjectId() {
        return projectId;
    }

    public void setProjectId(UUID projectId) {
        this.projectId = projectId;
    }

    public RiskRuleId getRuleId() {
        return ruleId;
    }

    public void setRuleId(RiskRuleId ruleId) {
        this.ruleId = ruleId;
    }

    public RiskSeverity getSeverity() {
        return severity;
    }

    public void setSeverity(RiskSeverity severity) {
        this.severity = severity;
    }

    public String getAffectedEntityType() {
        return affectedEntityType;
    }

    public void setAffectedEntityType(String affectedEntityType) {
        this.affectedEntityType = affectedEntityType;
    }

    public UUID getAffectedEntityId() {
        return affectedEntityId;
    }

    public void setAffectedEntityId(UUID affectedEntityId) {
        this.affectedEntityId = affectedEntityId;
    }

    public String getAffectedEntityName() {
        return affectedEntityName;
    }

    public void setAffectedEntityName(String affectedEntityName) {
        this.affectedEntityName = affectedEntityName;
    }

    public String getExplanation() {
        return explanation;
    }

    public void setExplanation(String explanation) {
        this.explanation = explanation;
    }

    public String getSupportingEvidence() {
        return supportingEvidence;
    }

    public void setSupportingEvidence(String supportingEvidence) {
        this.supportingEvidence = supportingEvidence;
    }

    public String getSuggestedAction() {
        return suggestedAction;
    }

    public void setSuggestedAction(String suggestedAction) {
        this.suggestedAction = suggestedAction;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Instant getDetectedAt() {
        return detectedAt;
    }

    public void setDetectedAt(Instant detectedAt) {
        this.detectedAt = detectedAt;
    }

    public Instant getResolvedAt() {
        return resolvedAt;
    }

    public void setResolvedAt(Instant resolvedAt) {
        this.resolvedAt = resolvedAt;
    }
}
