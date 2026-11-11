package com.projectflow.server.controller;

import com.projectflow.core.model.Role;
import com.projectflow.server.dto.AdminOverviewDto;
import com.projectflow.server.dto.ProjectDto;
import com.projectflow.server.dto.SystemHealthDto;
import com.projectflow.server.dto.UserProfileDto;
import com.projectflow.server.dto.WorkspaceDto;
import com.projectflow.server.entity.AuditLogEntity;
import com.projectflow.server.repository.ProjectRepository;
import com.projectflow.server.repository.WorkspaceRepository;
import com.projectflow.server.security.SecurityUtils;
import com.projectflow.server.security.UserPrincipal;
import com.projectflow.server.service.AdminService;
import com.projectflow.server.service.ProjectService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/admin")
@PreAuthorize("hasAnyRole('ADMINISTRATOR', 'OWNER')")
public class AdminController {

    private final AdminService adminService;
    private final WorkspaceRepository workspaceRepository;
    private final ProjectRepository projectRepository;
    private final ProjectService projectService;

    public AdminController(AdminService adminService,
                           WorkspaceRepository workspaceRepository,
                           ProjectRepository projectRepository,
                           ProjectService projectService) {
        this.adminService = adminService;
        this.workspaceRepository = workspaceRepository;
        this.projectRepository = projectRepository;
        this.projectService = projectService;
    }

    @GetMapping("/overview")
    public ResponseEntity<AdminOverviewDto> getOverview() {
        return ResponseEntity.ok(adminService.getOverview());
    }

    @GetMapping("/users")
    public ResponseEntity<Page<UserProfileDto>> getUsers(@RequestParam(required = false) String query,
                                                         @PageableDefault(size = 20) Pageable pageable) {
        return ResponseEntity.ok(adminService.getUsers(query, pageable));
    }

    @PatchMapping("/users/{id}/role")
    public ResponseEntity<UserProfileDto> updateUserRole(@PathVariable UUID id,
                                                         @RequestBody Map<String, String> body,
                                                         @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        Role newRole = Role.valueOf(body.get("role").toUpperCase());
        return ResponseEntity.ok(adminService.updateUserRole(id, newRole, principal));
    }

    @GetMapping("/workspaces")
    public ResponseEntity<List<WorkspaceDto>> getWorkspaces() {
        return ResponseEntity.ok(workspaceRepository.findAll().stream()
                .map(w -> new WorkspaceDto(w.getId(), w.getOrganizationId(), w.getName(), w.getSlug(), w.getDescription(), w.getOwnerId(), w.isArchived(), w.getCreatedAt(), w.getUpdatedAt()))
                .collect(Collectors.toList()));
    }

    @GetMapping("/projects")
    public ResponseEntity<List<ProjectDto>> getProjects() {
        return ResponseEntity.ok(projectRepository.findAll().stream()
                .map(projectService::toDto)
                .collect(Collectors.toList()));
    }

    @GetMapping("/system/health")
    public ResponseEntity<SystemHealthDto> getSystemHealth() {
        return ResponseEntity.ok(adminService.getSystemHealth());
    }

    @GetMapping("/audit-events")
    public ResponseEntity<Page<AuditLogEntity>> getAuditEvents(@PageableDefault(size = 25) Pageable pageable) {
        return ResponseEntity.ok(adminService.getAuditLogs(pageable));
    }
}
