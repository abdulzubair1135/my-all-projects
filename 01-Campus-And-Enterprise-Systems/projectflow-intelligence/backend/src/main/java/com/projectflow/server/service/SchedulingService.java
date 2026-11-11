package com.projectflow.server.service;

import com.projectflow.core.model.Role;
import com.projectflow.core.model.Task;
import com.projectflow.core.model.TaskDependency;
import com.projectflow.core.model.WorkflowStatus;
import com.projectflow.core.scheduling.ScheduleComparisonResult;
import com.projectflow.core.scheduling.WhatIfSchedulingEngine;
import com.projectflow.server.dto.ScenarioCreateRequest;
import com.projectflow.server.dto.ScenarioDto;
import com.projectflow.server.entity.*;
import com.projectflow.server.exception.ConflictException;
import com.projectflow.server.exception.ForbiddenException;
import com.projectflow.server.exception.ResourceNotFoundException;
import com.projectflow.server.exception.ValidationException;
import com.projectflow.server.repository.*;
import com.projectflow.server.security.UserPrincipal;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class SchedulingService {

    private final ScheduleScenarioRepository scenarioRepository;
    private final ScenarioChangeRepository changeRepository;
    private final ProjectRepository projectRepository;
    private final TaskRepository taskRepository;
    private final TaskDependencyRepository dependencyRepository;
    private final WorkflowStatusRepository workflowStatusRepository;
    private final ProfileRepository profileRepository;
    private final WorkspaceService workspaceService;
    private final ProjectService projectService;
    private final RiskService riskService;
    private final AuditService auditService;
    private final WhatIfSchedulingEngine schedulingEngine = new WhatIfSchedulingEngine();

    public SchedulingService(ScheduleScenarioRepository scenarioRepository,
                             ScenarioChangeRepository changeRepository,
                             ProjectRepository projectRepository,
                             TaskRepository taskRepository,
                             TaskDependencyRepository dependencyRepository,
                             WorkflowStatusRepository workflowStatusRepository,
                             ProfileRepository profileRepository,
                             WorkspaceService workspaceService,
                             ProjectService projectService,
                             RiskService riskService,
                             AuditService auditService) {
        this.scenarioRepository = scenarioRepository;
        this.changeRepository = changeRepository;
        this.projectRepository = projectRepository;
        this.taskRepository = taskRepository;
        this.dependencyRepository = dependencyRepository;
        this.workflowStatusRepository = workflowStatusRepository;
        this.profileRepository = profileRepository;
        this.workspaceService = workspaceService;
        this.projectService = projectService;
        this.riskService = riskService;
        this.auditService = auditService;
    }

    @Transactional
    public ScenarioDto createScenario(UUID projectId, ScenarioCreateRequest request, UserPrincipal principal) {
        ProjectEntity project = projectRepository.findByIdAndArchivedFalse(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found: " + projectId));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        ScheduleScenarioEntity entity = new ScheduleScenarioEntity(
                project.getId(),
                request.getName(),
                request.getDescription(),
                principal.getId(),
                project.getVersion()
        );
        entity = scenarioRepository.save(entity);

        List<ScenarioChangeEntity> changeEntities = new ArrayList<>();
        if (request.getChanges() != null) {
            for (ScenarioCreateRequest.ScenarioChangeItem item : request.getChanges()) {
                ScenarioChangeEntity change = new ScenarioChangeEntity(
                        entity.getId(),
                        item.getTaskId(),
                        item.getProposedDueDate(),
                        item.getProposedEstimatedHours(),
                        item.getProposedAssigneeId()
                );
                changeEntities.add(changeRepository.save(change));
            }
        }

        auditService.record(null, project.getWorkspaceId(), principal.getId(), principal.getEmail(),
                "CREATE_SCENARIO", "SCENARIO", entity.getId(), "Created What-If scenario: " + entity.getName(), null);

        return toDto(entity, changeEntities);
    }

    @Transactional(readOnly = true)
    public ScenarioDto getScenario(UUID scenarioId, UserPrincipal principal) {
        ScheduleScenarioEntity scenario = scenarioRepository.findById(scenarioId)
                .orElseThrow(() -> new ResourceNotFoundException("Scenario not found: " + scenarioId));
        ProjectEntity project = projectRepository.findById(scenario.getProjectId())
                .orElseThrow(() -> new ResourceNotFoundException("Project not found"));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        List<ScenarioChangeEntity> changes = changeRepository.findByScenarioId(scenarioId);
        return toDto(scenario, changes);
    }

    @Transactional(readOnly = true)
    public ScheduleComparisonResult evaluateScenario(UUID scenarioId, UserPrincipal principal) {
        ScheduleScenarioEntity scenario = scenarioRepository.findById(scenarioId)
                .orElseThrow(() -> new ResourceNotFoundException("Scenario not found: " + scenarioId));
        ProjectEntity project = projectRepository.findById(scenario.getProjectId())
                .orElseThrow(() -> new ResourceNotFoundException("Project not found"));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        com.projectflow.core.model.Project coreProject = new com.projectflow.core.model.Project(
                project.getId(), project.getWorkspaceId(), project.getWorkflowId(),
                project.getName(), project.getStartDate(), project.getTargetDate()
        );

        List<TaskEntity> taskEntities = taskRepository.findByProjectIdAndArchivedFalseOrderByPositionAsc(project.getId());
        List<Task> coreTasks = taskEntities.stream().map(t -> {
            Task ct = new Task(t.getId(), t.getProjectId(), t.getTitle(), t.getStatusId(), t.getPriority(), t.getDueDate(), t.getEstimatedHours().doubleValue());
            ct.setAssigneeId(t.getAssigneeId());
            ct.setArchived(t.isArchived());
            ct.setUpdatedAt(t.getUpdatedAt());
            return ct;
        }).collect(Collectors.toList());

        List<UUID> taskIds = taskEntities.stream().map(TaskEntity::getId).toList();
        List<TaskDependency> coreDeps = dependencyRepository.findAll().stream()
                .filter(d -> taskIds.contains(d.getTaskId()) || taskIds.contains(d.getPredecessorTaskId()))
                .map(d -> new TaskDependency(d.getId(), d.getTaskId(), d.getPredecessorTaskId()))
                .collect(Collectors.toList());

        Map<UUID, WorkflowStatus> statusMap = workflowStatusRepository.findByWorkflowIdOrderByPositionAsc(project.getWorkflowId())
                .stream().collect(Collectors.toMap(
                        WorkflowStatusEntity::getId,
                        s -> new WorkflowStatus(s.getId(), s.getWorkflowId(), s.getName(), s.getColor(), s.getCategory(), s.getPosition())
                ));

        Map<UUID, String> userNames = profileRepository.findAll().stream()
                .collect(Collectors.toMap(ProfileEntity::getId, ProfileEntity::getFullName, (a, b) -> a));

        List<ScenarioChangeEntity> changeEntities = changeRepository.findByScenarioId(scenarioId);
        com.projectflow.core.model.ScheduleScenario coreScenario = new com.projectflow.core.model.ScheduleScenario(
                scenario.getId(), scenario.getProjectId(), scenario.getName(), scenario.getDescription(),
                scenario.getCreatedById(), scenario.getBaseProjectVersion()
        );
        for (ScenarioChangeEntity c : changeEntities) {
            coreScenario.getChanges().add(new com.projectflow.core.model.ScenarioChange(
                    c.getId(), c.getScenarioId(), c.getTaskId(), c.getProposedDueDate(),
                    c.getProposedEstimatedHours() != null ? c.getProposedEstimatedHours().doubleValue() : null,
                    c.getProposedAssigneeId()
            ));
        }

        return schedulingEngine.evaluateScenario(
                coreProject, coreTasks, coreDeps, coreScenario, statusMap, userNames, LocalDate.now(), Instant.now()
        );
    }

    @Transactional
    public void applyScenario(UUID scenarioId, UserPrincipal principal) {
        if (principal.getRole() == Role.VIEWER || principal.getRole() == Role.MEMBER) {
            throw new ForbiddenException("Only Managers and Administrators can apply schedule scenarios");
        }

        ScheduleScenarioEntity scenario = scenarioRepository.findById(scenarioId)
                .orElseThrow(() -> new ResourceNotFoundException("Scenario not found: " + scenarioId));
        ProjectEntity project = projectRepository.findByIdAndArchivedFalse(scenario.getProjectId())
                .orElseThrow(() -> new ResourceNotFoundException("Project not found"));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        if (scenario.isApplied()) {
            throw new ValidationException("Scenario has already been applied");
        }

        // Optimistic concurrency check: ensure project was not modified concurrently
        if (!Objects.equals(scenario.getBaseProjectVersion(), project.getVersion())) {
            throw new ConflictException("Project record has been modified since this scenario was created. Recalculate scenario before applying.");
        }

        // Run evaluation to verify validity
        ScheduleComparisonResult comparison = evaluateScenario(scenarioId, principal);
        if (!comparison.isValid()) {
            throw new ValidationException("Cannot apply invalid scenario: " + comparison.getValidationMessage());
        }

        // Apply simulated changes transactionally
        List<ScenarioChangeEntity> changes = changeRepository.findByScenarioId(scenarioId);
        for (ScenarioChangeEntity change : changes) {
            TaskEntity task = taskRepository.findById(change.getTaskId()).orElse(null);
            if (task != null && !task.isArchived()) {
                if (change.getProposedDueDate() != null) {
                    task.setDueDate(change.getProposedDueDate());
                }
                if (change.getProposedEstimatedHours() != null) {
                    task.setEstimatedHours(change.getProposedEstimatedHours());
                }
                if (change.getProposedAssigneeId() != null) {
                    task.setAssigneeId(change.getProposedAssigneeId());
                }
                taskRepository.save(task);
            }
        }

        scenario.setApplied(true);
        scenario.setAppliedAt(Instant.now());
        scenarioRepository.save(scenario);

        // Increment project version
        project.setVersion(project.getVersion() + 1);
        projectRepository.save(project);

        // Recalculate progress and risks
        projectService.recalculateProgress(project.getId());
        riskService.recalculateProjectRisks(project.getId(), principal);

        auditService.record(null, project.getWorkspaceId(), principal.getId(), principal.getEmail(),
                "APPLY_SCENARIO", "SCENARIO", scenario.getId(), "Applied What-If scenario to live project: " + scenario.getName(), null);
    }

    private ScenarioDto toDto(ScheduleScenarioEntity entity, List<ScenarioChangeEntity> changes) {
        ScenarioDto dto = new ScenarioDto();
        dto.setId(entity.getId());
        dto.setProjectId(entity.getProjectId());
        dto.setName(entity.getName());
        dto.setDescription(entity.getDescription());
        dto.setCreatedById(entity.getCreatedById());
        dto.setApplied(entity.isApplied());
        dto.setAppliedAt(entity.getAppliedAt());
        dto.setBaseProjectVersion(entity.getBaseProjectVersion());
        dto.setCreatedAt(entity.getCreatedAt());

        if (changes != null) {
            dto.setChanges(changes.stream().map(c -> {
                ScenarioCreateRequest.ScenarioChangeItem item = new ScenarioCreateRequest.ScenarioChangeItem();
                item.setTaskId(c.getTaskId());
                item.setProposedDueDate(c.getProposedDueDate());
                item.setProposedEstimatedHours(c.getProposedEstimatedHours());
                item.setProposedAssigneeId(c.getProposedAssigneeId());
                return item;
            }).collect(Collectors.toList()));
        }

        return dto;
    }
}
