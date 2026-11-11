package com.projectflow.server.controller;

import com.projectflow.server.dto.ProjectCreateRequest;
import com.projectflow.server.dto.ProjectDto;
import com.projectflow.server.security.SecurityUtils;
import com.projectflow.server.security.UserPrincipal;
import com.projectflow.server.service.ProjectService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/projects")
public class ProjectController {

    private final ProjectService projectService;

    public ProjectController(ProjectService projectService) {
        this.projectService = projectService;
    }

    @GetMapping
    public ResponseEntity<List<ProjectDto>> getProjects(@RequestParam UUID workspaceId,
                                                        @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(projectService.getProjectsByWorkspace(workspaceId, principal));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProjectDto> getProject(@PathVariable UUID id,
                                                 @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(projectService.getProject(id, principal));
    }

    @PostMapping
    public ResponseEntity<ProjectDto> createProject(@Valid @RequestBody ProjectCreateRequest request,
                                                    @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        ProjectDto created = projectService.createProject(request, principal);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PatchMapping("/{id}")
    public ResponseEntity<ProjectDto> updateProject(@PathVariable UUID id,
                                                    @RequestBody ProjectCreateRequest request,
                                                    @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(projectService.updateProject(id, request, principal));
    }

    @PostMapping("/{id}/archive")
    public ResponseEntity<Void> archiveProject(@PathVariable UUID id,
                                               @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        projectService.archiveProject(id, principal);
        return ResponseEntity.noContent().build();
    }
}
