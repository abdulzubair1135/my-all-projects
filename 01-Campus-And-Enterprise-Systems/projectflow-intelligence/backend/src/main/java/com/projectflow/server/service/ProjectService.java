package com.projectflow.server.service;

import com.projectflow.server.dto.ProjectCreateRequest;
import com.projectflow.server.dto.ProjectDto;
import com.projectflow.server.entity.ProjectEntity;
import com.projectflow.server.entity.TaskEntity;
import com.projectflow.server.entity.WorkflowEntity;
import com.projectflow.server.exception.ResourceNotFoundException;
import com.projectflow.server.exception.ValidationException;
import com.projectflow.server.repository.ProjectRepository;
import com.projectflow.server.repository.TaskRepository;
import com.projectflow.server.repository.WorkflowRepository;
import com.projectflow.server.security.UserPrincipal;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class ProjectService {

    private final ProjectRepository projectRepository;
    private final TaskRepository taskRepository;
    private final WorkflowRepository workflowRepository;
    private final WorkspaceService workspaceService;
    private final AuditService auditService;

    public ProjectService(ProjectRepository projectRepository,
                          TaskRepository taskRepository,
                          WorkflowRepository workflowRepository,
                          WorkspaceService workspaceService,
                          AuditService auditService) {
        this.projectRepository = projectRepository;
        this.taskRepository = taskRepository;
        this.workflowRepository = workflowRepository;
        this.workspaceService = workspaceService;
        this.auditService = auditService;
    }

    @Transactional(readOnly = true)
    public List<ProjectDto> getProjectsByWorkspace(UUID workspaceId, UserPrincipal principal) {
        workspaceService.validateWorkspaceAccess(workspaceId, principal);
        return projectRepository.findByWorkspaceIdAndArchivedFalse(workspaceId).stream()
                .map(this::toDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public ProjectDto getProject(UUID projectId, UserPrincipal principal) {
        ProjectEntity project = projectRepository.findByIdAndArchivedFalse(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found: " + projectId));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);
        return toDto(project);
    }

    @Transactional
    public ProjectDto createProject(ProjectCreateRequest request, UserPrincipal principal) {
        workspaceService.validateWorkspaceAccess(request.getWorkspaceId(), principal);

        if (request.getTargetDate().isBefore(request.getStartDate())) {
            throw new ValidationException("Project target date cannot precede start date");
        }

        UUID workflowId = request.getWorkflowId();
        if (workflowId == null) {
            WorkflowEntity defaultWf = workflowRepository.findByWorkspaceIdAndIsDefaultTrue(request.getWorkspaceId())
                    .orElseGet(() -> workflowRepository.findByWorkspaceId(request.getWorkspaceId()).stream().findFirst()
                            .orElseThrow(() -> new ValidationException("No workflow found for workspace " + request.getWorkspaceId())));
            workflowId = defaultWf.getId();
        }

        ProjectEntity project = new ProjectEntity(
                request.getWorkspaceId(),
                workflowId,
                request.getName(),
                request.getStartDate(),
                request.getTargetDate()
        );
        project.setDescription(request.getDescription());
        project = projectRepository.save(project);

        auditService.record(null, project.getWorkspaceId(), principal.getId(), principal.getEmail(),
                "CREATE_PROJECT", "PROJECT", project.getId(), "Project created: " + project.getName(), null);

        return toDto(project);
    }

    @Transactional
    public ProjectDto updateProject(UUID projectId, ProjectCreateRequest request, UserPrincipal principal) {
        ProjectEntity project = projectRepository.findByIdAndArchivedFalse(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found: " + projectId));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        if (request.getStartDate() != null && request.getTargetDate() != null) {
            if (request.getTargetDate().isBefore(request.getStartDate())) {
                throw new ValidationException("Project target date cannot precede start date");
            }
            project.setStartDate(request.getStartDate());
            project.setTargetDate(request.getTargetDate());
        }

        if (request.getName() != null && !request.getName().isBlank()) {
            project.setName(request.getName());
        }
        if (request.getDescription() != null) {
            project.setDescription(request.getDescription());
        }
        if (request.getWorkflowId() != null) {
            project.setWorkflowId(request.getWorkflowId());
        }

        project = projectRepository.save(project);

        auditService.record(null, project.getWorkspaceId(), principal.getId(), principal.getEmail(),
                "UPDATE_PROJECT", "PROJECT", project.getId(), "Project updated: " + project.getName(), null);

        return toDto(project);
    }

    @Transactional
    public void archiveProject(UUID projectId, UserPrincipal principal) {
        ProjectEntity project = projectRepository.findByIdAndArchivedFalse(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found: " + projectId));
        workspaceService.validateWorkspaceAccess(project.getWorkspaceId(), principal);

        project.setArchived(true);
        projectRepository.save(project);

        auditService.record(null, project.getWorkspaceId(), principal.getId(), principal.getEmail(),
                "ARCHIVE_PROJECT", "PROJECT", project.getId(), "Project archived: " + project.getName(), null);
    }

    @Transactional
    public void recalculateProgress(UUID projectId) {
        ProjectEntity project = projectRepository.findById(projectId).orElse(null);
        if (project == null || project.isArchived()) return;

        List<TaskEntity> tasks = taskRepository.findByProjectIdAndArchivedFalseOrderByPositionAsc(projectId);
        if (tasks.isEmpty()) {
            project.setProgressPercentage(BigDecimal.ZERO);
        } else {
            long completed = tasks.stream().filter(t -> t.getCompletedAt() != null).count();
            BigDecimal pct = BigDecimal.valueOf(completed)
                    .multiply(BigDecimal.valueOf(100))
                    .divide(BigDecimal.valueOf(tasks.size()), 2, RoundingMode.HALF_UP);
            project.setProgressPercentage(pct);
        }
        projectRepository.save(project);
    }

    public ProjectDto toDto(ProjectEntity entity) {
        return new ProjectDto(
                entity.getId(),
                entity.getWorkspaceId(),
                entity.getWorkflowId(),
                entity.getName(),
                entity.getDescription(),
                entity.getStartDate(),
                entity.getTargetDate(),
                entity.getStatus(),
                entity.getProgressPercentage(),
                entity.isArchived(),
                entity.getVersion(),
                entity.getCreatedAt(),
                entity.getUpdatedAt()
        );
    }
}
