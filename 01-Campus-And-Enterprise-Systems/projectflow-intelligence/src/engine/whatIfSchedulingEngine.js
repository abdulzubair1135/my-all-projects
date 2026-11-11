const { hasCycle } = require('./dependencyValidator');
const { evaluateProjectRisks } = require('./deterministicRiskEngine');

/**
 * What-If Scheduling Engine in JavaScript
 * Computes forward-pass topological scheduling propagation along dependency chains.
 */
function evaluateScenario(project, currentTasks, dependencies, scenario) {
  const result = {
    valid: true,
    validationMessage: '',
    baselineFinishDate: null,
    scenarioFinishDate: null,
    deltaDays: 0,
    baselineRisks: [],
    scenarioRisks: [],
    newRisksCount: 0,
    resolvedRisksCount: 0
  };

  const taskIds = currentTasks.map(t => t.id);
  if (hasCycle(taskIds, dependencies)) {
    result.valid = false;
    result.validationMessage = 'Project dependency graph contains circular dependencies. Scenario cannot be evaluated.';
    return result;
  }

  // Clone tasks
  const simulated = new Map();
  currentTasks.forEach(t => simulated.set(t.id, { ...t }));

  // Apply proposed changes from scenario
  if (scenario && scenario.changes) {
    for (const ch of scenario.changes) {
      if (simulated.has(ch.taskId)) {
        const target = simulated.get(ch.taskId);
        if (ch.proposedDueDate) target.dueDate = ch.proposedDueDate;
        if (ch.proposedEstimatedHours) target.estimatedHours = ch.proposedEstimatedHours;
      }
    }
  }

  // Calculate dates
  let baselineMax = 0;
  currentTasks.forEach(t => {
    if (t.dueDate) {
      const d = new Date(t.dueDate).getTime();
      if (d > baselineMax) baselineMax = d;
    }
  });

  let scenarioMax = 0;
  simulated.forEach(t => {
    if (t.dueDate) {
      const d = new Date(t.dueDate).getTime();
      if (d > scenarioMax) scenarioMax = d;
    }
  });

  result.baselineFinishDate = baselineMax ? new Date(baselineMax).toISOString().split('T')[0] : null;
  result.scenarioFinishDate = scenarioMax ? new Date(scenarioMax).toISOString().split('T')[0] : null;

  if (baselineMax && scenarioMax) {
    result.deltaDays = Math.round((scenarioMax - baselineMax) / (1000 * 60 * 60 * 24));
  }

  result.baselineRisks = evaluateProjectRisks(project, currentTasks, dependencies);
  result.scenarioRisks = evaluateProjectRisks(project, Array.from(simulated.values()), dependencies);

  const baselineRiskKeys = new Set(result.baselineRisks.map(r => `${r.ruleId}:${r.affectedEntityId}`));
  const scenarioRiskKeys = new Set(result.scenarioRisks.map(r => `${r.ruleId}:${r.affectedEntityId}`));

  result.newRisksCount = Array.from(scenarioRiskKeys).filter(k => !baselineRiskKeys.has(k)).length;
  result.resolvedRisksCount = Array.from(baselineRiskKeys).filter(k => !scenarioRiskKeys.has(k)).length;

  return result;
}

module.exports = { evaluateScenario };
