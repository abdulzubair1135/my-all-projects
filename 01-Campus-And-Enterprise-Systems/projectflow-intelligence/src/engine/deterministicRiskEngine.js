/**
 * Deterministic Risk Radar Engine (JavaScript)
 * Evaluates the 6 mathematical risk rules against actual project data.
 */

function evaluateProjectRisks(project, tasks, dependencies, now = new Date()) {
  if (!project) return [];
  const findings = [];
  const today = new Date(now.toISOString().split('T')[0]);

  const taskMap = new Map();
  tasks.forEach(t => taskMap.set(t.id, t));

  // Predecessors map: taskId -> list of predecessor tasks
  const predecessorsByTask = new Map();
  tasks.forEach(t => predecessorsByTask.set(t.id, []));
  dependencies.forEach(dep => {
    if (predecessorsByTask.has(dep.taskId) && taskMap.has(dep.predecessorTaskId)) {
      predecessorsByTask.get(dep.taskId).push(taskMap.get(dep.predecessorTaskId));
    }
  });

  // User workload capacity map (7-day window)
  const assigneeWorkload = new Map();

  for (const task of tasks) {
    const isCompleted = !!task.completedAt;
    const dueDate = task.dueDate ? new Date(task.dueDate.split('T')[0]) : null;

    if (!isCompleted) {
      // 1. OVERDUE_TASK
      if (dueDate && dueDate < today) {
        findings.push({
          ruleId: 'OVERDUE_TASK',
          severity: 'CRITICAL',
          affectedEntityId: task.id,
          affectedEntityName: task.title,
          explanation: `Task '${task.title}' was due on ${task.dueDate.split('T')[0]} but remains incomplete.`,
          suggestedAction: 'Expedite immediate completion, reallocate resources, or apply a What-If extension.'
        });
      }

      // 2. DEADLINE_APPROACHING
      if (dueDate && dueDate >= today) {
        const daysDiff = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
        if (daysDiff <= 2) {
          findings.push({
            ruleId: 'DEADLINE_APPROACHING',
            severity: 'HIGH',
            affectedEntityId: task.id,
            affectedEntityName: task.title,
            explanation: `Task '${task.title}' is due in ${daysDiff} day(s) on ${task.dueDate.split('T')[0]}.`,
            suggestedAction: 'Verify active execution and clear all blocking dependencies.'
          });
        }
      }

      // 3. BLOCKED_TASK
      const preds = predecessorsByTask.get(task.id) || [];
      const overduePred = preds.find(p => !p.completedAt && p.dueDate && new Date(p.dueDate.split('T')[0]) < today);
      if (overduePred) {
        findings.push({
          ruleId: 'BLOCKED_TASK',
          severity: 'HIGH',
          affectedEntityId: task.id,
          affectedEntityName: task.title,
          explanation: `Task '${task.title}' is blocked by incomplete overdue predecessor '${overduePred.title}'.`,
          suggestedAction: `Resolve blocker on predecessor '${overduePred.title}' before advancing this task.`
        });
      }

      // 4. STALLED_PROGRESS
      if (task.statusCategory === 'IN_PROGRESS' && task.updatedAt) {
        const lastUpdated = new Date(task.updatedAt);
        const stalledDays = Math.ceil((today - lastUpdated) / (1000 * 60 * 60 * 24));
        if (stalledDays >= 7) {
          findings.push({
            ruleId: 'STALLED_PROGRESS',
            severity: 'MEDIUM',
            affectedEntityId: task.id,
            affectedEntityName: task.title,
            explanation: `Task '${task.title}' has been in-progress without activity updates for ${stalledDays} days.`,
            suggestedAction: 'Check in with assignee to record progress or reassign.'
          });
        }
      }

      // 5. Accumulate workload for CAPACITY_OVERLOAD
      if (task.assigneeId) {
        const est = task.estimatedHours || 8;
        assigneeWorkload.set(task.assigneeId, (assigneeWorkload.get(task.assigneeId) || 0) + est);
      }

      // 6. PROJECT_DEADLINE_RISK
      if (project.targetDate && dueDate) {
        const projTarget = new Date(project.targetDate.split('T')[0]);
        if (dueDate > projTarget) {
          findings.push({
            ruleId: 'PROJECT_DEADLINE_RISK',
            severity: 'CRITICAL',
            affectedEntityId: task.id,
            affectedEntityName: task.title,
            explanation: `Task '${task.title}' dueDate exceeds the project target deadline of ${project.targetDate}.`,
            suggestedAction: 'Compress task duration or request formal milestone baseline amendment.'
          });
        }
      }
    }
  }

  // Evaluate Capacity Overload
  for (const [assigneeId, hours] of assigneeWorkload.entries()) {
    if (hours > 40) {
      findings.push({
        ruleId: 'CAPACITY_OVERLOAD',
        severity: 'HIGH',
        affectedEntityId: assigneeId,
        affectedEntityName: `Assignee ${assigneeId.substring(0, 8)}`,
        explanation: `Team member has ${hours} planned hours of active work in the rolling 7-day period (Threshold: 40h).`,
        suggestedAction: 'Rebalance tasks to peer contributors to prevent burnout.'
      });
    }
  }

  return findings;
}

module.exports = { evaluateProjectRisks };
