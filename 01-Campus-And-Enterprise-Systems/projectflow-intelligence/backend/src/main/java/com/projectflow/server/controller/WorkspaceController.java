package com.projectflow.server.controller;

import com.projectflow.server.dto.WorkspaceCreateRequest;
import com.projectflow.server.dto.WorkspaceDto;
import com.projectflow.server.security.SecurityUtils;
import com.projectflow.server.security.UserPrincipal;
import com.projectflow.server.service.WorkspaceService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/workspaces")
public class WorkspaceController {

    private final WorkspaceService workspaceService;

    public WorkspaceController(WorkspaceService workspaceService) {
        this.workspaceService = workspaceService;
    }

    @GetMapping
    public ResponseEntity<List<WorkspaceDto>> getWorkspaces(@AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(workspaceService.getUserWorkspaces(principal));
    }

    @GetMapping("/{id}")
    public ResponseEntity<WorkspaceDto> getWorkspace(@PathVariable UUID id, @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(workspaceService.getWorkspace(id, principal));
    }

    @PostMapping
    public ResponseEntity<WorkspaceDto> createWorkspace(@Valid @RequestBody WorkspaceCreateRequest request,
                                                        @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        WorkspaceDto created = workspaceService.createWorkspace(request, principal);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }
}
