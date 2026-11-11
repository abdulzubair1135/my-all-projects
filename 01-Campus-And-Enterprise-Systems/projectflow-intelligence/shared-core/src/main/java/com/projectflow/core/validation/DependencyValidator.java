package com.projectflow.core.validation;

import com.projectflow.core.model.TaskDependency;

import java.util.*;

public class DependencyValidator {

    /**
     * Validates whether adding a proposed dependency (taskId depends on predecessorTaskId)
     * would introduce a circular dependency cycle.
     *
     * @param existingDependencies list of currently active dependencies
     * @param taskId the successor task ID
     * @param predecessorTaskId the prerequisite predecessor task ID
     * @return true if safe to add, false if a cycle would be introduced or invalid
     */
    public static boolean wouldCreateCycle(List<TaskDependency> existingDependencies, UUID taskId, UUID predecessorTaskId) {
        if (taskId == null || predecessorTaskId == null) {
            return true; // invalid
        }
        if (taskId.equals(predecessorTaskId)) {
            return true; // self-dependency is a cycle
        }

        // Build adjacency graph: predecessor -> successors
        Map<UUID, List<UUID>> adj = new HashMap<>();
        for (TaskDependency dep : existingDependencies) {
            adj.computeIfAbsent(dep.getPredecessorTaskId(), k -> new ArrayList<>()).add(dep.getTaskId());
        }

        // Add proposed edge: predecessorTaskId -> taskId
        adj.computeIfAbsent(predecessorTaskId, k -> new ArrayList<>()).add(taskId);

        // Check if there is a path from taskId back to predecessorTaskId (which would complete a cycle)
        Set<UUID> visited = new HashSet<>();
        Queue<UUID> queue = new LinkedList<>();
        queue.add(taskId);
        visited.add(taskId);

        while (!queue.isEmpty()) {
            UUID current = queue.poll();
            if (current.equals(predecessorTaskId)) {
                return true; // Cycle detected!
            }
            List<UUID> successors = adj.getOrDefault(current, Collections.emptyList());
            for (UUID next : successors) {
                if (!visited.contains(next)) {
                    visited.add(next);
                    queue.add(next);
                }
            }
        }

        return false;
    }

    /**
     * Detects if the entire graph currently has any cycles using Kahn's topological sort.
     */
    public static boolean hasCycle(Set<UUID> allTaskIds, List<TaskDependency> dependencies) {
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

        int visitedCount = 0;
        while (!queue.isEmpty()) {
            UUID node = queue.poll();
            visitedCount++;
            for (UUID next : adj.getOrDefault(node, Collections.emptyList())) {
                inDegree.put(next, inDegree.get(next) - 1);
                if (inDegree.get(next) == 0) {
                    queue.add(next);
                }
            }
        }

        return visitedCount != allTaskIds.size();
    }
}
