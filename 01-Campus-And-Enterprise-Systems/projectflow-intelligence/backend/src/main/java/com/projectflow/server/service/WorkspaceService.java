package com.projectflow.server.service;

import com.projectflow.core.model.Role;
import com.projectflow.core.model.StatusCategory;
import com.projectflow.server.dto.WorkspaceCreateRequest;
import com.projectflow.server.dto.WorkspaceDto;
import com.projectflow.server.entity.*;
import com.projectflow.server.exception.ForbiddenException;
import com.projectflow.server.exception.ResourceNotFoundException;
import com.projectflow.server.repository.*;
import com.projectflow.server.security.UserPrincipal;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class WorkspaceService {

    private final WorkspaceRepository workspaceRepository;
    private final WorkspaceMemberRepository workspaceMemberRepository;
    private final OrganizationRepository organizationRepository;
    private final WorkflowRepository workflowRepository;
    private final WorkflowStatusRepository workflowStatusRepository;
    private final WorkflowTransitionRepository workflowTransitionRepository;
    private final AuditService auditService;

    public WorkspaceService(WorkspaceRepository workspaceRepository,
                            WorkspaceMemberRepository workspaceMemberRepository,
                            OrganizationRepository organizationRepository,
                            WorkflowRepository workflowRepository,
                            WorkflowStatusRepository workflowStatusRepository,
                            WorkflowTransitionRepository workflowTransitionRepository,
                            AuditService auditService) {
        this.workspaceRepository = workspaceRepository;
        this.workspaceMemberRepository = workspaceMemberRepository;
        this.organizationRepository = organizationRepository;
        this.workflowRepository = workflowRepository;
        this.workflowStatusRepository = workflowStatusRepository;
        this.workflowTransitionRepository = workflowTransitionRepository;
        this.auditService = auditService;
    }

    @Transactional(readOnly = true)
    public List<WorkspaceDto> getUserWorkspaces(UserPrincipal principal) {
        if (principal.getRole() == Role.ADMINISTRATOR || principal.getRole() == Role.OWNER) {
            return workspaceRepository.findByArchivedFalse().stream()
                    .map(this::toDto)
                    .collect(Collectors.toList());
        }

        List<WorkspaceMemberEntity> memberships = workspaceMemberRepository.findByUserId(principal.getId());
        List<UUID> workspaceIds = memberships.stream().map(WorkspaceMemberEntity::getWorkspaceId).toList();
        return workspaceRepository.findAllById(workspaceIds).stream()
                .filter(w -> !w.isArchived())
                .map(this::toDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public WorkspaceDto getWorkspace(UUID workspaceId, UserPrincipal principal) {
        validateWorkspaceAccess(workspaceId, principal);
        WorkspaceEntity entity = workspaceRepository.findById(workspaceId)
                .filter(w -> !w.isArchived())
                .orElseThrow(() -> new ResourceNotFoundException("Workspace not found: " + workspaceId));
        return toDto(entity);
    }

    @Transactional
    public WorkspaceDto createWorkspace(WorkspaceCreateRequest request, UserPrincipal principal) {
        UUID orgId = request.getOrganizationId();
        if (orgId == null) {
            // Find or create default organization
            OrganizationEntity defaultOrg = organizationRepository.findAll().stream().findFirst()
                    .orElseGet(() -> organizationRepository.save(new OrganizationEntity("Default Organization", "default-org", principal.getId())));
            orgId = defaultOrg.getId();
        }

        String slug = request.getSlug();
        if (slug == null || slug.isBlank()) {
            slug = request.getName().toLowerCase().replaceAll("[^a-z0-9]+", "-") + "-" + System.currentTimeMillis() % 10000;
        }

        WorkspaceEntity workspace = new WorkspaceEntity(orgId, request.getName(), slug, principal.getId());
        workspace.setDescription(request.getDescription());
        workspace = workspaceRepository.save(workspace);

        // Add creator as OWNER member of workspace
        WorkspaceMemberEntity member = new WorkspaceMemberEntity(workspace.getId(), principal.getId(), Role.OWNER);
        workspaceMemberRepository.save(member);

        // Provision default workflow for the workspace
        WorkflowEntity defaultWf = new WorkflowEntity(workspace.getId(), "Standard Agile Workflow", true);
        defaultWf = workflowRepository.save(defaultWf);

        WorkflowStatusEntity backlog = workflowStatusRepository.save(new WorkflowStatusEntity(defaultWf.getId(), "Backlog", "#73766D", StatusCategory.BACKLOG, 1));
        WorkflowStatusEntity todo = workflowStatusRepository.save(new WorkflowStatusEntity(defaultWf.getId(), "To Do", "#78866B", StatusCategory.TODO, 2));
        WorkflowStatusEntity inProgress = workflowStatusRepository.save(new WorkflowStatusEntity(defaultWf.getId(), "In Progress", "#B68A3A", StatusCategory.IN_PROGRESS, 3));
        WorkflowStatusEntity review = workflowStatusRepository.save(new WorkflowStatusEntity(defaultWf.getId(), "In Review", "#56664C", StatusCategory.IN_REVIEW, 4));
        WorkflowStatusEntity done = workflowStatusRepository.save(new WorkflowStatusEntity(defaultWf.getId(), "Done", "#467653", StatusCategory.DONE, 5));

        // Configure default transitions
        workflowTransitionRepository.save(new WorkflowTransitionEntity(defaultWf.getId(), backlog.getId(), todo.getId(), "Move to To-Do"));
        workflowTransitionRepository.save(new WorkflowTransitionEntity(defaultWf.getId(), todo.getId(), inProgress.getId(), "Start Work"));
        workflowTransitionRepository.save(new WorkflowTransitionEntity(defaultWf.getId(), inProgress.getId(), review.getId(), "Submit for Review"));
        workflowTransitionRepository.save(new WorkflowTransitionEntity(defaultWf.getId(), review.getId(), inProgress.getId(), "Request Revisions"));
        workflowTransitionRepository.save(new WorkflowTransitionEntity(defaultWf.getId(), review.getId(), done.getId(), "Approve & Complete"));

        auditService.record(orgId, workspace.getId(), principal.getId(), principal.getEmail(),
                "CREATE_WORKSPACE", "WORKSPACE", workspace.getId(), "Workspace created: " + workspace.getName(), null);

        return toDto(workspace);
    }

    public void validateWorkspaceAccess(UUID workspaceId, UserPrincipal principal) {
        if (principal.getRole() == Role.ADMINISTRATOR || principal.getRole() == Role.OWNER) {
            return;
        }
        boolean isMember = workspaceMemberRepository.findByWorkspaceIdAndUserId(workspaceId, principal.getId()).isPresent();
        if (!isMember) {
            throw new ForbiddenException("Access denied: You are not a member of workspace " + workspaceId);
        }
    }

    private WorkspaceDto toDto(WorkspaceEntity entity) {
        return new WorkspaceDto(
                entity.getId(),
                entity.getOrganizationId(),
                entity.getName(),
                entity.getSlug(),
                entity.getDescription(),
                entity.getOwnerId(),
                entity.isArchived(),
                entity.getCreatedAt(),
                entity.getUpdatedAt()
        );
    }
}
