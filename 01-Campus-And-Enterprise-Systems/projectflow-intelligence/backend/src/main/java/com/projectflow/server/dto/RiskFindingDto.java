package com.projectflow.server.dto;

import com.projectflow.core.model.RiskRuleId;
import com.projectflow.core.model.RiskSeverity;
import java.time.Instant;
import java.util.UUID;

public class RiskFindingDto {
    private UUID id;
    private UUID projectId;
    private RiskRuleId ruleId;
    private String ruleName;
    private RiskSeverity severity;
    private String affectedEntityType;
    private UUID affectedEntityId;
    private String affectedEntityName;
    private String explanation;
    private String supportingEvidence;
    private String suggestedAction;
    private String status;
    private Instant detectedAt;

    public RiskFindingDto() {
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

    public String getRuleName() {
        return ruleName;
    }

    public void setRuleName(String ruleName) {
        this.ruleName = ruleName;
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
}
