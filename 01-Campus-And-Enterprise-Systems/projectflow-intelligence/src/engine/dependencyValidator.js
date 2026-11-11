/**
 * Validates Directed Acyclic Graphs (DAG) and detects circular dependencies.
 */
function hasCycle(taskIds, dependencies) {
  const adj = new Map();
  for (const id of taskIds) {
    adj.set(id, []);
  }

  for (const dep of dependencies) {
    if (adj.has(dep.predecessorTaskId)) {
      adj.get(dep.predecessorTaskId).push(dep.taskId);
    }
  }

  const visited = new Set();
  const recStack = new Set();

  function dfs(curr) {
    visited.add(curr);
    recStack.add(curr);

    const neighbors = adj.get(curr) || [];
    for (const neighbor of neighbors) {
      if (!visited.has(neighbor)) {
        if (dfs(neighbor)) return true;
      } else if (recStack.has(neighbor)) {
        return true;
      }
    }

    recStack.delete(curr);
    return false;
  }

  for (const id of taskIds) {
    if (!visited.has(id)) {
      if (dfs(id)) return true;
    }
  }

  return false;
}

module.exports = { hasCycle };
