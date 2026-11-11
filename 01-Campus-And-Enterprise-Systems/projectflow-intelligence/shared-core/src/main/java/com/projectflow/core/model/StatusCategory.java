package com.projectflow.core.model;

public enum StatusCategory {
    BACKLOG,
    TODO,
    IN_PROGRESS,
    IN_REVIEW,
    DONE,
    CANCELLED;

    public boolean isTerminal() {
        return this == DONE || this == CANCELLED;
    }
}
