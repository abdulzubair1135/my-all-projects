package com.projectflow.core.validation;

import com.projectflow.core.model.TaskDependency;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

class DependencyValidatorTest {

    @Test
    void shouldDetectDirectCycle() {
        UUID taskA = UUID.randomUUID();
        UUID taskB = UUID.randomUUID();

        // Existing: A -> B (B depends on A)
        List<TaskDependency> deps = List.of(new TaskDependency(UUID.randomUUID(), taskB, taskA));

        // Proposed: B -> A (A depends on B)
        boolean createsCycle = DependencyValidator.wouldCreateCycle(deps, taskA, taskB);
        assertThat(createsCycle).isTrue();
    }

    @Test
    void shouldDetectTransitiveCycle() {
        UUID taskA = UUID.randomUUID();
        UUID taskB = UUID.randomUUID();
        UUID taskC = UUID.randomUUID();

        // A -> B (B depends on A)
        // B -> C (C depends on B)
        List<TaskDependency> deps = List.of(
                new TaskDependency(UUID.randomUUID(), taskB, taskA),
                new TaskDependency(UUID.randomUUID(), taskC, taskB)
        );

        // Proposed: C -> A (A depends on C) => Cycle!
        boolean createsCycle = DependencyValidator.wouldCreateCycle(deps, taskA, taskC);
        assertThat(createsCycle).isTrue();
    }

    @Test
    void shouldAllowAcyclicDependency() {
        UUID taskA = UUID.randomUUID();
        UUID taskB = UUID.randomUUID();
        UUID taskC = UUID.randomUUID();

        // A -> B
        List<TaskDependency> deps = new ArrayList<>(List.of(
                new TaskDependency(UUID.randomUUID(), taskB, taskA)
        ));

        // Proposed: B -> C (C depends on B) => Clean DAG
        boolean createsCycle = DependencyValidator.wouldCreateCycle(deps, taskC, taskB);
        assertThat(createsCycle).isFalse();
    }

    @Test
    void shouldRejectSelfDependency() {
        UUID taskA = UUID.randomUUID();
        boolean createsCycle = DependencyValidator.wouldCreateCycle(List.of(), taskA, taskA);
        assertThat(createsCycle).isTrue();
    }

    @Test
    void shouldDetectCycleInEntireGraph() {
        UUID taskA = UUID.randomUUID();
        UUID taskB = UUID.randomUUID();

        List<TaskDependency> cyclicDeps = List.of(
                new TaskDependency(UUID.randomUUID(), taskB, taskA),
                new TaskDependency(UUID.randomUUID(), taskA, taskB)
        );

        assertThat(DependencyValidator.hasCycle(Set.of(taskA, taskB), cyclicDeps)).isTrue();
    }
}
