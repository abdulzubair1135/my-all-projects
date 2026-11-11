package com.projectflow.core.risk;

import com.projectflow.core.model.*;

import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

public class DeterministicRiskEngine {

    private final int deadlineApproachingDaysThreshold;
    private final int stalledDaysThreshold;
    private final double weeklyCapacityHoursThreshold;

    public DeterministicRiskEngine() {
        this(2, 7, 40.0);
    }

    public DeterministicRiskEngine(int deadlineApproachingDaysThreshold, int stalledDaysThreshold, double weeklyCapacityHoursThreshold) {
        this.deadlineApproachingDaysThreshold = deadlineApproachingDaysThreshold;
        this.stalledDaysThreshold = stalledDaysThreshold;
        this.weeklyCapacityHoursThreshold = weeklyCapacityHoursThreshold;
    }

    public List<RiskFinding> evaluateProjectRisks(
            Project project,
            List<Task> tasks,
            List<TaskDependency> dependencies,
            Map<UUID, WorkflowStatus> statusMap,
            Map<UUID, String> userNameMap,
            LocalDate evaluationDate,
            Instant now
    ) {
        if (project == null || project.isArchived()) {
            return Collections.emptyList();
        }

        List<RiskFinding> findings = new ArrayList<>();
        Map<UUID, Task> taskMap = tasks.stream().collect(Collectors.toMap(Task::getId, t -> t, (a, b) -> a));

        // Group dependencies by successor taskId
        Map<UUID, List<TaskDependency>> depsByTask = dependencies.stream()
                .collect(Collectors.groupingBy(TaskDependency::getTaskId));

        // 1. Evaluate Task-level risks
        for (Task task : tasks) {
            if (task.isArchived()) {
                continue;
            }

            WorkflowStatus status = statusMap.get(task.getStatusId());
            boolean isTerminal = status != null && status.isTerminal();

            if (!isTerminal) {
                // A. Overdue Task
                if (task.getDueDate() != null && task.getDueDate().isBefore(evaluationDate)) {
                    long daysOverdue = ChronoUnit.DAYS.between(task.getDueDate(), evaluationDate);
                    RiskSeverity severity = (task.getPriority() == TaskPriority.CRITICAL || daysOverdue > 3)
                            ? RiskSeverity.CRITICAL : RiskSeverity.HIGH;

                    findings.add(new RiskFinding(
                            UUID.randomUUID(),
                            project.getId(),
                            RiskRuleId.OVERDUE_TASK,
                            severity,
                            "TASK",
                            task.getId(),
                            task.getTitle(),
                            String.format("Task '%s' is overdue by %d day(s). It was scheduled for %s.",
                                    task.getTitle(), daysOverdue, task.getDueDate()),
                            String.format("Due Date: %s | Current Date: %s | Status: %s | Overdue: %d days",
                                    task.getDueDate(), evaluationDate, status != null ? status.getName() : "Unknown", daysOverdue),
                            "Reschedule the task or expedite completion to prevent cascading project delays."
                    ));
                }

                // B. Deadline Approaching
                if (task.getDueDate() != null && !task.getDueDate().isBefore(evaluationDate)) {
                    long daysRemaining = ChronoUnit.DAYS.between(evaluationDate, task.getDueDate());
                    if (daysRemaining <= deadlineApproachingDaysThreshold) {
                        RiskSeverity severity = task.getPriority() == TaskPriority.CRITICAL
                                ? RiskSeverity.HIGH : RiskSeverity.MEDIUM;

                        findings.add(new RiskFinding(
                                UUID.randomUUID(),
                                project.getId(),
                                RiskRuleId.DEADLINE_APPROACHING,
                                severity,
                                "TASK",
                                task.getId(),
                                task.getTitle(),
                                String.format("Task '%s' is due in %d day(s) on %s.",
                                        task.getTitle(), daysRemaining, task.getDueDate()),
                                String.format("Due Date: %s | Remaining Days: %d | Priority: %s",
                                        task.getDueDate(), daysRemaining, task.getPriority()),
                                "Confirm assignee capacity and review blockers before the due date."
                        ));
                    }
                }

                // C. Blocked Task
                List<TaskDependency> taskDeps = depsByTask.getOrDefault(task.getId(), Collections.emptyList());
                List<String> uncompletedPreds = new ArrayList<>();
                for (TaskDependency dep : taskDeps) {
                    Task pred = taskMap.get(dep.getPredecessorTaskId());
                    if (pred != null) {
                        WorkflowStatus predStatus = statusMap.get(pred.getStatusId());
                        if (predStatus == null || !predStatus.isTerminal()) {
                            uncompletedPreds.add(String.format("'%s' (%s)",
                                    pred.getTitle(), predStatus != null ? predStatus.getName() : "Incomplete"));
                        }
                    }
                }

                if (!uncompletedPreds.isEmpty()) {
                    findings.add(new RiskFinding(
                            UUID.randomUUID(),
                            project.getId(),
                            RiskRuleId.BLOCKED_TASK,
                            RiskSeverity.HIGH,
                            "TASK",
                            task.getId(),
                            task.getTitle(),
                            String.format("Task '%s' cannot proceed because %d prerequisite task(s) are unfinished: %s.",
                                    task.getTitle(), uncompletedPreds.size(), String.join(", ", uncompletedPreds)),
                            String.format("Unfinished Predecessors: %s", String.join("; ", uncompletedPreds)),
                            "Prioritize completing predecessor tasks or revise the dependency graph."
                    ));
                }

                // D. Stalled Task
                if (status != null && status.getCategory() == StatusCategory.IN_PROGRESS && task.getUpdatedAt() != null) {
                    long daysInactive = Duration.between(task.getUpdatedAt(), now).toDays();
                    if (daysInactive >= stalledDaysThreshold) {
                        findings.add(new RiskFinding(
                                UUID.randomUUID(),
                                project.getId(),
                                RiskRuleId.STALLED_TASK,
                                RiskSeverity.MEDIUM,
                                "TASK",
                                task.getId(),
                                task.getTitle(),
                                String.format("Task '%s' has been In Progress for %d day(s) without updates.",
                                        task.getTitle(), daysInactive),
                                String.format("Last updated: %s | Days without activity: %d",
                                        task.getUpdatedAt(), daysInactive),
                                "Request a status update from the assignee or re-evaluate task scope."
                        ));
                    }
                }
            }
        }

        // E. Capacity Overload (Per Assignee)
        Map<UUID, List<Task>> activeTasksByAssignee = tasks.stream()
                .filter(t -> !t.isArchived())
                .filter(t -> {
                    WorkflowStatus st = statusMap.get(t.getStatusId());
                    return st == null || !st.isTerminal();
                })
                .filter(t -> t.getAssigneeId() != null)
                .collect(Collectors.groupingBy(Task::getAssigneeId));

        for (Map.Entry<UUID, List<Task>> entry : activeTasksByAssignee.entrySet()) {
            UUID assigneeId = entry.getKey();
            List<Task> assignedTasks = entry.getValue();
            double totalHours = assignedTasks.stream().mapToDouble(Task::getEstimatedHours).sum();

            if (totalHours > weeklyCapacityHoursThreshold) {
                String assigneeName = userNameMap != null && userNameMap.containsKey(assigneeId)
                        ? userNameMap.get(assigneeId) : assigneeId.toString();

                findings.add(new RiskFinding(
                        UUID.randomUUID(),
                        project.getId(),
                        RiskRuleId.CAPACITY_OVERLOAD,
                        RiskSeverity.HIGH,
                        "USER",
                        assigneeId,
                        assigneeName,
                        String.format("Assignee '%s' is assigned %.1f hours across %d active tasks, exceeding capacity limit (%.0fh).",
                                assigneeName, totalHours, assignedTasks.size(), weeklyCapacityHoursThreshold),
                        String.format("Total Estimated Hours: %.1f | Capacity Threshold: %.0fh | Active Task Count: %d",
                                totalHours, weeklyCapacityHoursThreshold, assignedTasks.size()),
                        "Rebalance workload by reassigning lower-priority tasks to other team members."
                ));
            }
        }

        // F. Project Deadline Risk
        if (project.getTargetDate() != null) {
            LocalDate latestTaskDueDate = tasks.stream()
                    .filter(t -> !t.isArchived())
                    .map(Task::getDueDate)
                    .filter(Objects::nonNull)
                    .max(LocalDate::compareTo)
                    .orElse(null);

            if (latestTaskDueDate != null && latestTaskDueDate.isAfter(project.getTargetDate())) {
                long delayDays = ChronoUnit.DAYS.between(project.getTargetDate(), latestTaskDueDate);
                findings.add(new RiskFinding(
                        UUID.randomUUID(),
                        project.getId(),
                        RiskRuleId.PROJECT_DEADLINE_RISK,
                        RiskSeverity.CRITICAL,
                        "PROJECT",
                        project.getId(),
                        project.getName(),
                        String.format("Project '%s' target date is %s, but scheduled tasks extend to %s (%d day(s) slippage).",
                                project.getName(), project.getTargetDate(), latestTaskDueDate, delayDays),
                        String.format("Target Date: %s | Projected Finish: %s | Slippage: %d days",
                                project.getTargetDate(), latestTaskDueDate, delayDays),
                        "Create a What-If scenario to compress the schedule or negotiate target date adjustment."
                ));
            }
        }

        return findings;
    }
}
