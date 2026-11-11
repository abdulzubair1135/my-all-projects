package com.projectflow.server.service;

import com.projectflow.core.model.TaskDependency;
import com.projectflow.core.validation.DependencyValidator;
import com.projectflow.core.validation.WorkflowValidator;
import com.projectflow.server.dto.TaskCreateRequest;
import com.projectflow.server.dto.TaskDto;
import com.projectflow.server.dto.TaskTransitionRequest;
import com.projectflow.server.dto.TaskUpdateRequest;
import com.projectflow.server.entity.*;
import com.projectflow.server.exception.ResourceNotFoundException;
import com.projectflow.server.exception.ValidationException;
import com.projectflow.server.repository.*;
import com.projectflow.server.security.UserPrincipal;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class TaskService {

    private final TaskRepository taskRepository;
    private final ProjectRepository projectRepository;
    private final WorkflowRepository workflowRepository;
    private final WorkflowStatusRepository workflowStatusRepository;
    private final WorkflowTransitionRepository workflowTransitionRepository;
    private final TaskDependencyRepository taskDependencyRepository;
    private final ProfileRepository profileRepository;
    private final WorkspaceService workspaceService;
    private final ProjectService projectService;
    private final AuditService auditService;

    public TaskService(TaskRepository taskRepository,
                       ProjectRepository projectRepository,
                       WorkflowRepository workflowRepository,
                       WorkflowStatusRepository workflowStatusRepository,
                       WorkflowTransitionRepository workflowTransitionRepository,
                       TaskDependencyRepository taskDependencyRepository,
                       ProfileRepository profileRepository,
                       WorkspaceService workspaceService,
                       ProjectService projectService,
                       AuditService auditService) {
        this.taskRepository = taskRepository;
        this.projectRepository = projectRepository;
        this.workflowRepository = workflowRepository;
        this.workflowStatusRepository = workflowStatusRepository;
        this.workflowTransitionRepository = workflowTransitionRepository;
        this.taskDependencyRepository = taskDependencyRepository;
        this.profileRepository = profileRepository;
        this.workspaceService = workspaceService;
        this.projectService = projectService;
        this.auditService = auditService;
    }

    @Transactional(readOnly = true)
    public List<TaskDto> getTasksByProject(UUID projectId, UserPrincipal principal) {
        ProjectEntity project = projectRepository.findByIdAndArchivedFalse(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found: " + projectId));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        Map<UUID, WorkflowStatusEntity> statusMap = workflowStatusRepository.findByWorkflowIdOrderByPositionAsc(project.getWorkflowId())
                .stream().collect(Collectors.toMap(WorkflowStatusEntity::getId, s -> s));

        Map<UUID, String> profileNames = profileRepository.findAll().stream()
                .collect(Collectors.toMap(ProfileEntity::getId, ProfileEntity::getFullName, (a, b) -> a));

        return taskRepository.findByProjectIdAndArchivedFalseOrderByPositionAsc(projectId).stream()
                .map(t -> toDto(t, statusMap.get(t.getStatusId()), profileNames.get(t.getAssigneeId())))
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public TaskDto getTask(UUID taskId, UserPrincipal principal) {
        TaskEntity task = taskRepository.findByIdAndArchivedFalse(taskId)
                .orElseThrow(() -> new ResourceNotFoundException("Task not found: " + taskId));
        ProjectEntity project = projectRepository.findById(task.getProjectId())
                .orElseThrow(() -> new ResourceNotFoundException("Project not found: " + task.getProjectId()));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        WorkflowStatusEntity status = workflowStatusRepository.findById(task.getStatusId()).orElse(null);
        String assigneeName = task.getAssigneeId() != null
                ? profileRepository.findById(task.getAssigneeId()).map(ProfileEntity::getFullName).orElse(null)
                : null;

        return toDto(task, status, assigneeName);
    }

    @Transactional
    public TaskDto createTask(TaskCreateRequest request, UserPrincipal principal) {
        ProjectEntity project = projectRepository.findByIdAndArchivedFalse(request.getProjectId())
                .orElseThrow(() -> new ResourceNotFoundException("Project not found: " + request.getProjectId()));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        // Determine or validate status
        UUID finalStatusId;
        if (request.getStatusId() == null) {
            WorkflowStatusEntity firstStatus = workflowStatusRepository.findByWorkflowIdOrderByPositionAsc(project.getWorkflowId()).stream()
                    .findFirst()
                    .orElseThrow(() -> new ValidationException("No statuses configured for workflow " + project.getWorkflowId()));
            finalStatusId = firstStatus.getId();
        } else {
            UUID requestedStatusId = request.getStatusId();
            WorkflowStatusEntity targetStatus = workflowStatusRepository.findById(requestedStatusId)
                    .orElseThrow(() -> new ValidationException("Status not found: " + requestedStatusId));
            if (!targetStatus.getWorkflowId().equals(project.getWorkflowId())) {
                throw new ValidationException("Status does not belong to project's workflow");
            }
            finalStatusId = requestedStatusId;
        }

        TaskEntity task = new TaskEntity(
                project.getId(),
                request.getTitle(),
                finalStatusId,
                request.getPriority(),
                request.getDueDate(),
                request.getEstimatedHours() != null ? request.getEstimatedHours() : BigDecimal.ZERO
        );
        task.setDescription(request.getDescription());
        task.setAssigneeId(request.getAssigneeId());

        task = taskRepository.save(task);
        projectService.recalculateProgress(project.getId());

        auditService.record(null, project.getWorkspaceId(), principal.getId(), principal.getEmail(),
                "CREATE_TASK", "TASK", task.getId(), "Task created: " + task.getTitle(), null);

        WorkflowStatusEntity status = workflowStatusRepository.findById(task.getStatusId()).orElse(null);
        String assigneeName = task.getAssigneeId() != null
                ? profileRepository.findById(task.getAssigneeId()).map(ProfileEntity::getFullName).orElse(null)
                : null;

        return toDto(task, status, assigneeName);
    }

    @Transactional
    public TaskDto updateTask(UUID taskId, TaskUpdateRequest request, UserPrincipal principal) {
        TaskEntity task = taskRepository.findByIdAndArchivedFalse(taskId)
                .orElseThrow(() -> new ResourceNotFoundException("Task not found: " + taskId));
        ProjectEntity project = projectRepository.findById(task.getProjectId())
                .orElseThrow(() -> new ResourceNotFoundException("Project not found"));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        if (request.getTitle() != null && !request.getTitle().isBlank()) {
            task.setTitle(request.getTitle());
        }
        if (request.getDescription() != null) {
            task.setDescription(request.getDescription());
        }
        if (request.getAssigneeId() != null) {
            task.setAssigneeId(request.getAssigneeId());
        }
        if (request.getPriority() != null) {
            task.setPriority(request.getPriority());
        }
        if (request.getDueDate() != null) {
            task.setDueDate(request.getDueDate());
        }
        if (request.getEstimatedHours() != null) {
            task.setEstimatedHours(request.getEstimatedHours());
        }
        if (request.getPosition() != null) {
            task.setPosition(request.getPosition());
        }
        if (request.getArchived() != null) {
            task.setArchived(request.getArchived());
        }

        task = taskRepository.save(task);

        WorkflowStatusEntity status = workflowStatusRepository.findById(task.getStatusId()).orElse(null);
        String assigneeName = task.getAssigneeId() != null
                ? profileRepository.findById(task.getAssigneeId()).map(ProfileEntity::getFullName).orElse(null)
                : null;

        return toDto(task, status, assigneeName);
    }

    @Transactional
    public TaskDto transitionTask(UUID taskId, TaskTransitionRequest request, UserPrincipal principal) {
        TaskEntity task = taskRepository.findByIdAndArchivedFalse(taskId)
                .orElseThrow(() -> new ResourceNotFoundException("Task not found: " + taskId));
        ProjectEntity project = projectRepository.findById(task.getProjectId())
                .orElseThrow(() -> new ResourceNotFoundException("Project not found"));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        UUID targetStatusId = request.getTargetStatusId();
        WorkflowStatusEntity targetStatus = workflowStatusRepository.findById(targetStatusId)
                .orElseThrow(() -> new ValidationException("Target status not found: " + targetStatusId));

        if (!targetStatus.getWorkflowId().equals(project.getWorkflowId())) {
            throw new ValidationException("Target status does not belong to project's workflow");
        }

        // Validate allowed transition
        boolean transitionAllowed = workflowTransitionRepository
                .findByWorkflowIdAndFromStatusIdAndToStatusId(project.getWorkflowId(), task.getStatusId(), targetStatusId)
                .isPresent() || task.getStatusId().equals(targetStatusId);

        if (!transitionAllowed) {
            throw new ValidationException(String.format("Invalid workflow transition from '%s' to '%s'",
                    task.getStatusId(), targetStatus.getName()));
        }

        task.setStatusId(targetStatusId);
        if (targetStatus.getCategory().isTerminal()) {
            task.setCompletedAt(Instant.now());
        } else {
            task.setCompletedAt(null);
        }

        task = taskRepository.save(task);
        projectService.recalculateProgress(project.getId());

        auditService.record(null, project.getWorkspaceId(), principal.getId(), principal.getEmail(),
                "TRANSITION_TASK", "TASK", task.getId(), "Transitioned task to " + targetStatus.getName(), null);

        String assigneeName = task.getAssigneeId() != null
                ? profileRepository.findById(task.getAssigneeId()).map(ProfileEntity::getFullName).orElse(null)
                : null;

        return toDto(task, targetStatus, assigneeName);
    }

    @Transactional
    public void addDependency(UUID taskId, UUID predecessorTaskId, UserPrincipal principal) {
        if (taskId.equals(predecessorTaskId)) {
            throw new ValidationException("A task cannot depend on itself");
        }

        TaskEntity task = taskRepository.findByIdAndArchivedFalse(taskId)
                .orElseThrow(() -> new ResourceNotFoundException("Task not found: " + taskId));
        TaskEntity pred = taskRepository.findByIdAndArchivedFalse(predecessorTaskId)
                .orElseThrow(() -> new ResourceNotFoundException("Predecessor task not found: " + predecessorTaskId));

        if (!task.getProjectId().equals(pred.getProjectId())) {
            throw new ValidationException("Dependencies can only be created between tasks in the same project");
        }

        ProjectEntity project = projectRepository.findById(task.getProjectId()).orElseThrow();
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        // Check cycle
        List<TaskDependencyEntity> existing = taskDependencyRepository.findAll();
        List<TaskDependency> coreDeps = existing.stream()
                .map(e -> new TaskDependency(e.getId(), e.getTaskId(), e.getPredecessorTaskId()))
                .collect(Collectors.toList());

        if (DependencyValidator.wouldCreateCycle(coreDeps, taskId, predecessorTaskId)) {
            throw new ValidationException("Cannot add dependency: Would create a circular dependency cycle");
        }

        Optional<TaskDependencyEntity> existingDep = taskDependencyRepository.findByTaskIdAndPredecessorTaskId(taskId, predecessorTaskId);
        if (existingDep.isEmpty()) {
            taskDependencyRepository.save(new TaskDependencyEntity(taskId, predecessorTaskId));
            auditService.record(null, project.getWorkspaceId(), principal.getId(), principal.getEmail(),
                    "ADD_DEPENDENCY", "TASK", taskId, "Added dependency on predecessor " + predecessorTaskId, null);
        }
    }

    public TaskDto toDto(TaskEntity entity, WorkflowStatusEntity status, String assigneeName) {
        TaskDto dto = new TaskDto();
        dto.setId(entity.getId());
        dto.setProjectId(entity.getProjectId());
        dto.setTitle(entity.getTitle());
        dto.setDescription(entity.getDescription());
        dto.setAssigneeId(entity.getAssigneeId());
        dto.setAssigneeName(assigneeName);
        dto.setPriority(entity.getPriority());
        dto.setStatusId(entity.getStatusId());
        if (status != null) {
            dto.setStatusName(status.getName());
            dto.setStatusColor(status.getColor());
        }
        dto.setDueDate(entity.getDueDate());
        dto.setEstimatedHours(entity.getEstimatedHours());
        dto.setPosition(entity.getPosition());
        dto.setArchived(entity.isArchived());
        dto.setVersion(entity.getVersion());
        dto.setCompletedAt(entity.getCompletedAt());
        dto.setCreatedAt(entity.getCreatedAt());
        dto.setUpdatedAt(entity.getUpdatedAt());
        return dto;
    }
}
