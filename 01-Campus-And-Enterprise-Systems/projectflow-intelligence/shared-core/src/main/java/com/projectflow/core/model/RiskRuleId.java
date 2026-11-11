package com.projectflow.core.model;

public enum RiskRuleId {
    OVERDUE_TASK("Overdue Task"),
    DEADLINE_APPROACHING("Deadline Approaching"),
    BLOCKED_TASK("Blocked by Dependencies"),
    STALLED_TASK("Stalled Progress"),
    CAPACITY_OVERLOAD("Capacity Overload"),
    PROJECT_DEADLINE_RISK("Project Target Date Slippage");

    private final String displayName;

    RiskRuleId(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }
}
