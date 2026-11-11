package com.projectflow.server.service;

import com.projectflow.core.model.RiskFinding;
import com.projectflow.core.model.Task;
import com.projectflow.core.model.TaskDependency;
import com.projectflow.core.model.WorkflowStatus;
import com.projectflow.core.risk.DeterministicRiskEngine;
import com.projectflow.server.dto.RiskFindingDto;
import com.projectflow.server.entity.*;
import com.projectflow.server.exception.ResourceNotFoundException;
import com.projectflow.server.repository.*;
import com.projectflow.server.security.UserPrincipal;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class RiskService {

    private final RiskEventRepository riskEventRepository;
    private final ProjectRepository projectRepository;
    private final TaskRepository taskRepository;
    private final TaskDependencyRepository taskDependencyRepository;
    private final WorkflowStatusRepository workflowStatusRepository;
    private final ProfileRepository profileRepository;
    private final WorkspaceService workspaceService;
    private final DeterministicRiskEngine riskEngine = new DeterministicRiskEngine();

    public RiskService(RiskEventRepository riskEventRepository,
                       ProjectRepository projectRepository,
                       TaskRepository taskRepository,
                       TaskDependencyRepository taskDependencyRepository,
                       WorkflowStatusRepository workflowStatusRepository,
                       ProfileRepository profileRepository,
                       WorkspaceService workspaceService) {
        this.riskEventRepository = riskEventRepository;
        this.projectRepository = projectRepository;
        this.taskRepository = taskRepository;
        this.taskDependencyRepository = taskDependencyRepository;
        this.workflowStatusRepository = workflowStatusRepository;
        this.profileRepository = profileRepository;
        this.workspaceService = workspaceService;
    }

    @Transactional(readOnly = true)
    public List<RiskFindingDto> getProjectRisks(UUID projectId, UserPrincipal principal) {
        ProjectEntity project = projectRepository.findByIdAndArchivedFalse(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found: " + projectId));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        return riskEventRepository.findByProjectId(projectId).stream()
                .map(this::toDto)
                .collect(Collectors.toList());
    }

    @Transactional
    public List<RiskFindingDto> recalculateProjectRisks(UUID projectId, UserPrincipal principal) {
        ProjectEntity projectEntity = projectRepository.findByIdAndArchivedFalse(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found: " + projectId));
        workspaceService.validateWorkspaceAccess(projectEntity.getWorkspaceId(), principal);

        com.projectflow.core.model.Project coreProject = new com.projectflow.core.model.Project(
                projectEntity.getId(),
                projectEntity.getWorkspaceId(),
                projectEntity.getWorkflowId(),
                projectEntity.getName(),
                projectEntity.getStartDate(),
                projectEntity.getTargetDate()
        );

        List<TaskEntity> taskEntities = taskRepository.findByProjectIdAndArchivedFalseOrderByPositionAsc(projectId);
        List<Task> coreTasks = taskEntities.stream().map(t -> {
            Task ct = new Task(t.getId(), t.getProjectId(), t.getTitle(), t.getStatusId(), t.getPriority(), t.getDueDate(), t.getEstimatedHours().doubleValue());
            ct.setAssigneeId(t.getAssigneeId());
            ct.setArchived(t.isArchived());
            ct.setUpdatedAt(t.getUpdatedAt());
            return ct;
        }).collect(Collectors.toList());

        List<UUID> taskIds = taskEntities.stream().map(TaskEntity::getId).toList();
        List<TaskDependencyEntity> depEntities = taskDependencyRepository.findAll().stream()
                .filter(d -> taskIds.contains(d.getTaskId()) || taskIds.contains(d.getPredecessorTaskId()))
                .toList();

        List<TaskDependency> coreDeps = depEntities.stream()
                .map(d -> new TaskDependency(d.getId(), d.getTaskId(), d.getPredecessorTaskId()))
                .collect(Collectors.toList());

        Map<UUID, WorkflowStatus> statusMap = workflowStatusRepository.findByWorkflowIdOrderByPositionAsc(projectEntity.getWorkflowId())
                .stream().collect(Collectors.toMap(
                        WorkflowStatusEntity::getId,
                        s -> new WorkflowStatus(s.getId(), s.getWorkflowId(), s.getName(), s.getColor(), s.getCategory(), s.getPosition())
                ));

        Map<UUID, String> userNames = profileRepository.findAll().stream()
                .collect(Collectors.toMap(ProfileEntity::getId, ProfileEntity::getFullName, (a, b) -> a));

        List<RiskFinding> computedFindings = riskEngine.evaluateProjectRisks(
                coreProject, coreTasks, coreDeps, statusMap, userNames, LocalDate.now(), Instant.now()
        );

        // Synchronize with database: avoid creating duplicates, resolve old ones
        List<RiskEventEntity> existingEvents = riskEventRepository.findByProjectId(projectId);
        Map<String, RiskEventEntity> existingByRuleAndEntity = existingEvents.stream()
                .collect(Collectors.toMap(e -> e.getRuleId() + ":" + e.getAffectedEntityId(), e -> e, (a, b) -> a));

        Set<String> computedKeys = new HashSet<>();
        for (RiskFinding f : computedFindings) {
            String key = f.getRuleId() + ":" + f.getAffectedEntityId();
            computedKeys.add(key);

            RiskEventEntity existing = existingByRuleAndEntity.get(key);
            if (existing != null) {
                // Update existing active event
                existing.setSeverity(f.getSeverity());
                existing.setExplanation(f.getExplanation());
                existing.setSupportingEvidence(f.getSupportingEvidence());
                existing.setSuggestedAction(f.getSuggestedAction());
                existing.setStatus("ACTIVE");
                existing.setResolvedAt(null);
                riskEventRepository.save(existing);
            } else {
                // Create new event
                RiskEventEntity newEntity = new RiskEventEntity();
                newEntity.setProjectId(projectId);
                newEntity.setRuleId(f.getRuleId());
                newEntity.setSeverity(f.getSeverity());
                newEntity.setAffectedEntityType(f.getAffectedEntityType());
                newEntity.setAffectedEntityId(f.getAffectedEntityId());
                newEntity.setAffectedEntityName(f.getAffectedEntityName());
                newEntity.setExplanation(f.getExplanation());
                newEntity.setSupportingEvidence(f.getSupportingEvidence());
                newEntity.setSuggestedAction(f.getSuggestedAction());
                newEntity.setStatus("ACTIVE");
                newEntity.setDetectedAt(Instant.now());
                riskEventRepository.save(newEntity);
            }
        }

        // Auto-resolve findings whose conditions no longer exist
        for (RiskEventEntity existing : existingEvents) {
            String key = existing.getRuleId() + ":" + existing.getAffectedEntityId();
            if (!computedKeys.contains(key) && "ACTIVE".equals(existing.getStatus())) {
                existing.setStatus("RESOLVED");
                existing.setResolvedAt(Instant.now());
                riskEventRepository.save(existing);
            }
        }

        return riskEventRepository.findByProjectId(projectId).stream()
                .map(this::toDto)
                .collect(Collectors.toList());
    }

    private RiskFindingDto toDto(RiskEventEntity entity) {
        RiskFindingDto dto = new RiskFindingDto();
        dto.setId(entity.getId());
        dto.setProjectId(entity.getProjectId());
        dto.setRuleId(entity.getRuleId());
        dto.setRuleName(entity.getRuleId().getDisplayName());
        dto.setSeverity(entity.getSeverity());
        dto.setAffectedEntityType(entity.getAffectedEntityType());
        dto.setAffectedEntityId(entity.getAffectedEntityId());
        dto.setAffectedEntityName(entity.getAffectedEntityName());
        dto.setExplanation(entity.getExplanation());
        dto.setSupportingEvidence(entity.getSupportingEvidence());
        dto.setSuggestedAction(entity.getSuggestedAction());
        dto.setStatus(entity.getStatus());
        dto.setDetectedAt(entity.getDetectedAt());
        return dto;
    }
}
