package com.projectflow.core.scheduling;

import com.projectflow.core.model.RiskFinding;
import com.projectflow.core.model.Task;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class ScheduleComparisonResult {
    private boolean valid;
    private String validationMessage;
    private LocalDate baselineFinishDate;
    private LocalDate scenarioFinishDate;
    private long deltaDays;
    private Map<UUID, Task> simulatedTasks;
    private List<RiskFinding> baselineRisks;
    private List<RiskFinding> scenarioRisks;
    private int newRisksCount;
    private int resolvedRisksCount;

    public ScheduleComparisonResult() {
    }

    public boolean isValid() {
        return valid;
    }

    public void setValid(boolean valid) {
        this.valid = valid;
    }

    public String getValidationMessage() {
        return validationMessage;
    }

    public void setValidationMessage(String validationMessage) {
        this.validationMessage = validationMessage;
    }

    public LocalDate getBaselineFinishDate() {
        return baselineFinishDate;
    }

    public void setBaselineFinishDate(LocalDate baselineFinishDate) {
        this.baselineFinishDate = baselineFinishDate;
    }

    public LocalDate getScenarioFinishDate() {
        return scenarioFinishDate;
    }

    public void setScenarioFinishDate(LocalDate scenarioFinishDate) {
        this.scenarioFinishDate = scenarioFinishDate;
    }

    public long getDeltaDays() {
        return deltaDays;
    }

    public void setDeltaDays(long deltaDays) {
        this.deltaDays = deltaDays;
    }

    public Map<UUID, Task> getSimulatedTasks() {
        return simulatedTasks;
    }

    public void setSimulatedTasks(Map<UUID, Task> simulatedTasks) {
        this.simulatedTasks = simulatedTasks;
    }

    public List<RiskFinding> getBaselineRisks() {
        return baselineRisks;
    }

    public void setBaselineRisks(List<RiskFinding> baselineRisks) {
        this.baselineRisks = baselineRisks;
    }

    public List<RiskFinding> getScenarioRisks() {
        return scenarioRisks;
    }

    public void setScenarioRisks(List<RiskFinding> scenarioRisks) {
        this.scenarioRisks = scenarioRisks;
    }

    public int getNewRisksCount() {
        return newRisksCount;
    }

    public void setNewRisksCount(int newRisksCount) {
        this.newRisksCount = newRisksCount;
    }

    public int getResolvedRisksCount() {
        return resolvedRisksCount;
    }

    public void setResolvedRisksCount(int resolvedRisksCount) {
        this.resolvedRisksCount = resolvedRisksCount;
    }
}
