package com.projectflow.core.scheduling;

import com.projectflow.core.model.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.time.LocalDate;
import java.util.*;

import static org.assertj.core.api.Assertions.assertThat;

class WhatIfSchedulingEngineTest {

    private WhatIfSchedulingEngine schedulingEngine;
    private Project project;
    private WorkflowStatus inProgressStatus;
    private WorkflowStatus doneStatus;
    private Map<UUID, WorkflowStatus> statusMap;

    @BeforeEach
    void setUp() {
        schedulingEngine = new WhatIfSchedulingEngine();
        UUID workspaceId = UUID.randomUUID();
        UUID workflowId = UUID.randomUUID();
        project = new Project(UUID.randomUUID(), workspaceId, workflowId, "Alpha Launch",
                LocalDate.of(2026, 10, 1), LocalDate.of(2026, 10, 31));

        inProgressStatus = new WorkflowStatus(UUID.randomUUID(), workflowId, "In Progress", "#B68A3A", StatusCategory.IN_PROGRESS, 1);
        doneStatus = new WorkflowStatus(UUID.randomUUID(), workflowId, "Done", "#467653", StatusCategory.DONE, 2);

        statusMap = new HashMap<>();
        statusMap.put(inProgressStatus.getId(), inProgressStatus);
        statusMap.put(doneStatus.getId(), doneStatus);
    }

    @Test
    void shouldPropagateDatesDownstreamWhenPredecessorDelayed() {
        LocalDate evaluationDate = LocalDate.of(2026, 10, 5);

        // Task 1: Due Oct 10
        Task task1 = new Task(UUID.randomUUID(), project.getId(), "API Design",
                inProgressStatus.getId(), TaskPriority.HIGH, LocalDate.of(2026, 10, 10), 16.0);

        // Task 2: Depends on Task 1, initially proposed due Oct 12
        Task task2 = new Task(UUID.randomUUID(), project.getId(), "Frontend Integration",
                inProgressStatus.getId(), TaskPriority.MEDIUM, LocalDate.of(2026, 10, 12), 24.0);

        TaskDependency dep = new TaskDependency(UUID.randomUUID(), task2.getId(), task1.getId());

        // Scenario: Delay Task 1 to Oct 20
        ScheduleScenario scenario = new ScheduleScenario(UUID.randomUUID(), project.getId(),
                "Delayed API Scenario", "Push API due to dependencies", UUID.randomUUID(), 1L);

        ScenarioChange change1 = new ScenarioChange(UUID.randomUUID(), scenario.getId(),
                task1.getId(), LocalDate.of(2026, 10, 20), null, null);
        scenario.getChanges().add(change1);

        ScheduleComparisonResult result = schedulingEngine.evaluateScenario(
                project, List.of(task1, task2), List.of(dep), scenario, statusMap, Collections.emptyMap(),
                evaluationDate, Instant.now()
        );

        assertThat(result.isValid()).isTrue();
        // Task 2 has 24 hours estimated = 3 days, so task 2 cannot finish before Oct 20 + 3 days = Oct 23!
        Task simulatedTask2 = result.getSimulatedTasks().get(task2.getId());
        assertThat(simulatedTask2.getDueDate()).isAfterOrEqualTo(LocalDate.of(2026, 10, 23));
        assertThat(result.getScenarioFinishDate()).isAfterOrEqualTo(LocalDate.of(2026, 10, 23));
    }
}
