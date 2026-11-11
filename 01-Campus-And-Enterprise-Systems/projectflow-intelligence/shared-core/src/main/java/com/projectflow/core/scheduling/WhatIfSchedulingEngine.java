package com.projectflow.core.scheduling;

import com.projectflow.core.model.*;
import com.projectflow.core.risk.DeterministicRiskEngine;
import com.projectflow.core.validation.DependencyValidator;

import java.time.Instant;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

public class WhatIfSchedulingEngine {

    private final DeterministicRiskEngine riskEngine;

    public WhatIfSchedulingEngine() {
        this(new DeterministicRiskEngine());
    }

    public WhatIfSchedulingEngine(DeterministicRiskEngine riskEngine) {
        this.riskEngine = riskEngine;
    }

    /**
     * Evaluates a proposed What-If Schedule Scenario against current project reality.
     */
    public ScheduleComparisonResult evaluateScenario(
            Project project,
            List<Task> currentTasks,
            List<TaskDependency> dependencies,
            ScheduleScenario scenario,
            Map<UUID, WorkflowStatus> statusMap,
            Map<UUID, String> userNameMap,
            LocalDate evaluationDate,
            Instant now
    ) {
        ScheduleComparisonResult result = new ScheduleComparisonResult();

        // 1. Check graph integrity
        Set<UUID> allTaskIds = currentTasks.stream().map(Task::getId).collect(Collectors.toSet());
        if (DependencyValidator.hasCycle(allTaskIds, dependencies)) {
            result.setValid(false);
            result.setValidationMessage("Project dependency graph contains circular cycles. Scenario cannot be evaluated.");
            return result;
        }

        // 2. Clone tasks to avoid mutating live data
        Map<UUID, Task> simulated = new HashMap<>();
        for (Task t : currentTasks) {
            Task copy = new Task(t.getId(), t.getProjectId(), t.getTitle(), t.getStatusId(),
                    t.getPriority(), t.getDueDate(), t.getEstimatedHours());
            copy.setAssigneeId(t.getAssigneeId());
            copy.setArchived(t.isArchived());
            copy.setPosition(t.getPosition());
            copy.setVersion(t.getVersion());
            copy.setCompletedAt(t.getCompletedAt());
            copy.setCreatedAt(t.getCreatedAt());
            copy.setUpdatedAt(t.getUpdatedAt());
            simulated.put(copy.getId(), copy);
        }

        // 3. Apply proposed scenario changes
        if (scenario != null && scenario.getChanges() != null) {
            for (ScenarioChange change : scenario.getChanges()) {
                Task target = simulated.get(change.getTaskId());
                if (target != null) {
                    if (change.getProposedDueDate() != null) {
                        target.setDueDate(change.getProposedDueDate());
                    }
                    if (change.getProposedEstimatedHours() != null) {
                        target.setEstimatedHours(change.getProposedEstimatedHours());
                    }
                    if (change.getProposedAssigneeId() != null) {
                        target.setAssigneeId(change.getProposedAssigneeId());
                    }
                    target.setUpdatedAt(now);
                }
            }
        }

        // 4. Forward-Pass Ripple Propagation for downstream dependencies
        // Successors cannot finish before predecessors finish + successor duration
        Map<UUID, List<TaskDependency>> depsByTask = dependencies.stream()
                .collect(Collectors.groupingBy(TaskDependency::getTaskId));

        // Topological ordering for propagation
        List<UUID> topoOrder = computeTopologicalOrder(allTaskIds, dependencies);
        for (UUID taskId : topoOrder) {
            Task task = simulated.get(taskId);
            if (task == null || task.isArchived()) continue;

            List<TaskDependency> preds = depsByTask.getOrDefault(taskId, Collections.emptyList());
            LocalDate earliestPossibleStart = evaluationDate;

            for (TaskDependency dep : preds) {
                Task predTask = simulated.get(dep.getPredecessorTaskId());
                if (predTask != null && predTask.getDueDate() != null) {
                    if (predTask.getDueDate().isAfter(earliestPossibleStart)) {
                        earliestPossibleStart = predTask.getDueDate();
                    }
                }
            }

            // Estimate duration in business days (assume ~8 hrs/day, min 1 day)
            int durationDays = Math.max(1, (int) Math.ceil(task.getEstimatedHours() / 8.0));
            LocalDate requiredFinishDate = earliestPossibleStart.plusDays(durationDays);

            // If proposed or current dueDate is earlier than prerequisite allows, push forward
            if (task.getDueDate() == null || task.getDueDate().isBefore(requiredFinishDate)) {
                task.setDueDate(requiredFinishDate);
            }
        }

        // 5. Compute Completion Dates & Slippage
        LocalDate baselineFinish = currentTasks.stream()
                .filter(t -> !t.isArchived())
                .map(Task::getDueDate)
                .filter(Objects::nonNull)
                .max(LocalDate::compareTo)
                .orElse(evaluationDate);

        LocalDate scenarioFinish = simulated.values().stream()
                .filter(t -> !t.isArchived())
                .map(Task::getDueDate)
                .filter(Objects::nonNull)
                .max(LocalDate::compareTo)
                .orElse(evaluationDate);

        long delta = ChronoUnit.DAYS.between(baselineFinish, scenarioFinish);

        // 6. Compute Risks: Baseline vs Simulated
        List<RiskFinding> baselineRisks = riskEngine.evaluateProjectRisks(
                project, currentTasks, dependencies, statusMap, userNameMap, evaluationDate, now
        );

        List<RiskFinding> scenarioRisks = riskEngine.evaluateProjectRisks(
                project, new ArrayList<>(simulated.values()), dependencies, statusMap, userNameMap, evaluationDate, now
        );

        // Calculate differences in active risk counts
        Set<String> baselineRiskKeys = baselineRisks.stream()
                .map(r -> r.getRuleId() + ":" + r.getAffectedEntityId())
                .collect(Collectors.toSet());

        Set<String> scenarioRiskKeys = scenarioRisks.stream()
                .map(r -> r.getRuleId() + ":" + r.getAffectedEntityId())
                .collect(Collectors.toSet());

        int newRisks = (int) scenarioRisks.stream()
                .filter(r -> !baselineRiskKeys.contains(r.getRuleId() + ":" + r.getAffectedEntityId()))
                .count();

        int resolvedRisks = (int) baselineRisks.stream()
                .filter(r -> !scenarioRiskKeys.contains(r.getRuleId() + ":" + r.getAffectedEntityId()))
                .count();

        result.setValid(true);
        result.setValidationMessage("Scenario evaluation complete.");
        result.setBaselineFinishDate(baselineFinish);
        result.setScenarioFinishDate(scenarioFinish);
        result.setDeltaDays(delta);
        result.setSimulatedTasks(simulated);
        result.setBaselineRisks(baselineRisks);
        result.setScenarioRisks(scenarioRisks);
        result.setNewRisksCount(newRisks);
        result.setResolvedRisksCount(resolvedRisks);

        return result;
    }

    private List<UUID> computeTopologicalOrder(Set<UUID> allTaskIds, List<TaskDependency> dependencies) {
        Map<UUID, Integer> inDegree = new HashMap<>();
        Map<UUID, List<UUID>> adj = new HashMap<>();

        for (UUID id : allTaskIds) {
            inDegree.put(id, 0);
        }

        for (TaskDependency dep : dependencies) {
            if (allTaskIds.contains(dep.getTaskId()) && allTaskIds.contains(dep.getPredecessorTaskId())) {
                adj.computeIfAbsent(dep.getPredecessorTaskId(), k -> new ArrayList<>()).add(dep.getTaskId());
                inDegree.put(dep.getTaskId(), inDegree.getOrDefault(dep.getTaskId(), 0) + 1);
            }
        }

        Queue<UUID> queue = new LinkedList<>();
        for (Map.Entry<UUID, Integer> entry : inDegree.entrySet()) {
            if (entry.getValue() == 0) {
                queue.add(entry.getKey());
            }
        }

        List<UUID> order = new ArrayList<>();
        while (!queue.isEmpty()) {
            UUID node = queue.poll();
            order.add(node);
            for (UUID next : adj.getOrDefault(node, Collections.emptyList())) {
                inDegree.put(next, inDegree.get(next) - 1);
                if (inDegree.get(next) == 0) {
                    queue.add(next);
                }
            }
        }

        return order;
    }
}
