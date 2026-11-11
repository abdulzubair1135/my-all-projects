package com.projectflow.core.model;

import java.time.Instant;
import java.util.UUID;

public class RiskFinding {
    private UUID id;
    private UUID projectId;
    private RiskRuleId ruleId;
    private RiskSeverity severity;
    private String affectedEntityType;
    private UUID affectedEntityId;
    private String affectedEntityName;
    private String explanation;
    private String supportingEvidence;
    private Instant detectedAt;
    private String status; // ACTIVE, RESOLVED, ACKNOWLEDGED
    private String suggestedAction;
    private Instant resolvedAt;

    public RiskFinding() {
    }

    public RiskFinding(UUID id, UUID projectId, RiskRuleId ruleId, RiskSeverity severity,
                       String affectedEntityType, UUID affectedEntityId, String affectedEntityName,
                       String explanation, String supportingEvidence, String suggestedAction) {
        this.id = id;
        this.projectId = projectId;
        this.ruleId = ruleId;
        this.severity = severity;
        this.affectedEntityType = affectedEntityType;
        this.affectedEntityId = affectedEntityId;
        this.affectedEntityName = affectedEntityName;
        this.explanation = explanation;
        this.supportingEvidence = supportingEvidence;
        this.suggestedAction = suggestedAction;
        this.detectedAt = Instant.now();
        this.status = "ACTIVE";
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

    public Instant getDetectedAt() {
        return detectedAt;
    }

    public void setDetectedAt(Instant detectedAt) {
        this.detectedAt = detectedAt;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getSuggestedAction() {
        return suggestedAction;
    }

    public void setSuggestedAction(String suggestedAction) {
        this.suggestedAction = suggestedAction;
    }

    public Instant getResolvedAt() {
        return resolvedAt;
    }

    public void setResolvedAt(Instant resolvedAt) {
        this.resolvedAt = resolvedAt;
    }
}
