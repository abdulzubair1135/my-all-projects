package com.projectflow.core.risk;

import com.projectflow.core.model.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.time.LocalDate;
import java.util.*;

import static org.assertj.core.api.Assertions.assertThat;

class DeterministicRiskEngineTest {

    private DeterministicRiskEngine riskEngine;
    private Project project;
    private Map<UUID, WorkflowStatus> statusMap;
    private WorkflowStatus todoStatus;
    private WorkflowStatus inProgressStatus;
    private WorkflowStatus doneStatus;

    @BeforeEach
    void setUp() {
        riskEngine = new DeterministicRiskEngine(2, 7, 40.0);
        UUID workspaceId = UUID.randomUUID();
        UUID workflowId = UUID.randomUUID();
        project = new Project(UUID.randomUUID(), workspaceId, workflowId, "Project Flow Alpha",
                LocalDate.of(2026, 10, 1), LocalDate.of(2026, 10, 20));

        todoStatus = new WorkflowStatus(UUID.randomUUID(), workflowId, "To Do", "#78866B", StatusCategory.TODO, 1);
        inProgressStatus = new WorkflowStatus(UUID.randomUUID(), workflowId, "In Progress", "#B68A3A", StatusCategory.IN_PROGRESS, 2);
        doneStatus = new WorkflowStatus(UUID.randomUUID(), workflowId, "Done", "#467653", StatusCategory.DONE, 3);

        statusMap = new HashMap<>();
        statusMap.put(todoStatus.getId(), todoStatus);
        statusMap.put(inProgressStatus.getId(), inProgressStatus);
        statusMap.put(doneStatus.getId(), doneStatus);
    }

    @Test
    void shouldDetectOverdueTask() {
        LocalDate evaluationDate = LocalDate.of(2026, 10, 15);
        Task overdueTask = new Task(UUID.randomUUID(), project.getId(), "Database Setup",
                todoStatus.getId(), TaskPriority.HIGH, LocalDate.of(2026, 10, 10), 8.0);

        List<RiskFinding> findings = riskEngine.evaluateProjectRisks(
                project, List.of(overdueTask), Collections.emptyList(), statusMap, Collections.emptyMap(),
                evaluationDate, Instant.now()
        );

        assertThat(findings).hasSize(1);
        RiskFinding finding = findings.get(0);
        assertThat(finding.getRuleId()).isEqualTo(RiskRuleId.OVERDUE_TASK);
        assertThat(finding.getAffectedEntityId()).isEqualTo(overdueTask.getId());
        assertThat(finding.getSeverity()).isEqualTo(RiskSeverity.CRITICAL); // > 3 days overdue
    }

    @Test
    void shouldNotFlagCompletedTaskAsOverdue() {
        LocalDate evaluationDate = LocalDate.of(2026, 10, 15);
        Task completedTask = new Task(UUID.randomUUID(), project.getId(), "Database Setup Done",
                doneStatus.getId(), TaskPriority.HIGH, LocalDate.of(2026, 10, 10), 8.0);

        List<RiskFinding> findings = riskEngine.evaluateProjectRisks(
                project, List.of(completedTask), Collections.emptyList(), statusMap, Collections.emptyMap(),
                evaluationDate, Instant.now()
        );

        assertThat(findings).isEmpty();
    }

    @Test
    void shouldDetectBlockedTaskWhenPredecessorIncomplete() {
        LocalDate evaluationDate = LocalDate.of(2026, 10, 10);
        Task taskA = new Task(UUID.randomUUID(), project.getId(), "Database Schema",
                todoStatus.getId(), TaskPriority.MEDIUM, LocalDate.of(2026, 10, 12), 16.0);
        Task taskB = new Task(UUID.randomUUID(), project.getId(), "Backend API",
                todoStatus.getId(), TaskPriority.HIGH, LocalDate.of(2026, 10, 16), 24.0);

        TaskDependency dep = new TaskDependency(UUID.randomUUID(), taskB.getId(), taskA.getId());

        List<RiskFinding> findings = riskEngine.evaluateProjectRisks(
                project, List.of(taskA, taskB), List.of(dep), statusMap, Collections.emptyMap(),
                evaluationDate, Instant.now()
        );

        Optional<RiskFinding> blockedFinding = findings.stream()
                .filter(f -> f.getRuleId() == RiskRuleId.BLOCKED_TASK)
                .findFirst();

        assertThat(blockedFinding).isPresent();
        assertThat(blockedFinding.get().getAffectedEntityId()).isEqualTo(taskB.getId());
    }

    @Test
    void shouldDetectProjectDeadlineSlippage() {
        LocalDate evaluationDate = LocalDate.of(2026, 10, 10);
        // Project target date is 2026-10-20
        Task lateTask = new Task(UUID.randomUUID(), project.getId(), "Deployment & Testing",
                todoStatus.getId(), TaskPriority.CRITICAL, LocalDate.of(2026, 10, 25), 40.0);

        List<RiskFinding> findings = riskEngine.evaluateProjectRisks(
                project, List.of(lateTask), Collections.emptyList(), statusMap, Collections.emptyMap(),
                evaluationDate, Instant.now()
        );

        Optional<RiskFinding> projectRisk = findings.stream()
                .filter(f -> f.getRuleId() == RiskRuleId.PROJECT_DEADLINE_RISK)
                .findFirst();

        assertThat(projectRisk).isPresent();
        assertThat(projectRisk.get().getSeverity()).isEqualTo(RiskSeverity.CRITICAL);
    }
}
