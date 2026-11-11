package com.projectflow.server.controller;

import com.projectflow.server.dto.WorkflowDto;
import com.projectflow.server.dto.WorkflowStatusDto;
import com.projectflow.server.dto.WorkflowTransitionDto;
import com.projectflow.server.entity.WorkflowEntity;
import com.projectflow.server.exception.ResourceNotFoundException;
import com.projectflow.server.repository.WorkflowRepository;
import com.projectflow.server.repository.WorkflowStatusRepository;
import com.projectflow.server.repository.WorkflowTransitionRepository;
import com.projectflow.server.security.SecurityUtils;
import com.projectflow.server.security.UserPrincipal;
import com.projectflow.server.service.WorkspaceService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/workflows")
public class WorkflowController {

    private final WorkflowRepository workflowRepository;
    private final WorkflowStatusRepository workflowStatusRepository;
    private final WorkflowTransitionRepository workflowTransitionRepository;
    private final WorkspaceService workspaceService;

    public WorkflowController(WorkflowRepository workflowRepository,
                              WorkflowStatusRepository workflowStatusRepository,
                              WorkflowTransitionRepository workflowTransitionRepository,
                              WorkspaceService workspaceService) {
        this.workflowRepository = workflowRepository;
        this.workflowStatusRepository = workflowStatusRepository;
        this.workflowTransitionRepository = workflowTransitionRepository;
        this.workspaceService = workspaceService;
    }

    @GetMapping
    public ResponseEntity<List<WorkflowDto>> getWorkflows(@RequestParam UUID workspaceId,
                                                          @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        workspaceService.validateWorkspaceAccess(workspaceId, principal);

        List<WorkflowDto> workflows = workflowRepository.findByWorkspaceId(workspaceId).stream()
                .map(this::populateDto)
                .collect(Collectors.toList());

        return ResponseEntity.ok(workflows);
    }

    @GetMapping("/{id}")
    public ResponseEntity<WorkflowDto> getWorkflow(@PathVariable UUID id,
                                                   @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        WorkflowEntity workflow = workflowRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Workflow not found: " + id));
        workspaceService.validateWorkspaceAccess(workflow.getWorkspaceId(), principal);

        return ResponseEntity.ok(populateDto(workflow));
    }

    private WorkflowDto populateDto(WorkflowEntity entity) {
        WorkflowDto dto = new WorkflowDto();
        dto.setId(entity.getId());
        dto.setWorkspaceId(entity.getWorkspaceId());
        dto.setName(entity.getName());
        dto.setDescription(entity.getDescription());
        dto.setDefault(entity.isDefault());
        dto.setCreatedAt(entity.getCreatedAt());

        dto.setStatuses(workflowStatusRepository.findByWorkflowIdOrderByPositionAsc(entity.getId()).stream()
                .map(s -> new WorkflowStatusDto(s.getId(), s.getWorkflowId(), s.getName(), s.getColor(), s.getCategory(), s.getPosition()))
                .collect(Collectors.toList()));

        dto.setTransitions(workflowTransitionRepository.findByWorkflowId(entity.getId()).stream()
                .map(t -> new WorkflowTransitionDto(t.getId(), t.getWorkflowId(), t.getFromStatusId(), t.getToStatusId(), t.getName()))
                .collect(Collectors.toList()));

        return dto;
    }
}
