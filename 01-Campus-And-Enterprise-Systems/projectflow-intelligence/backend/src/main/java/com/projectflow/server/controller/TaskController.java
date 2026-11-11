package com.projectflow.server.controller;

import com.projectflow.server.dto.TaskCreateRequest;
import com.projectflow.server.dto.TaskDto;
import com.projectflow.server.dto.TaskTransitionRequest;
import com.projectflow.server.dto.TaskUpdateRequest;
import com.projectflow.server.security.SecurityUtils;
import com.projectflow.server.security.UserPrincipal;
import com.projectflow.server.service.TaskService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    @GetMapping("/projects/{projectId}/tasks")
    public ResponseEntity<List<TaskDto>> getTasks(@PathVariable UUID projectId,
                                                  @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(taskService.getTasksByProject(projectId, principal));
    }

    @GetMapping("/tasks/{id}")
    public ResponseEntity<TaskDto> getTask(@PathVariable UUID id,
                                           @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(taskService.getTask(id, principal));
    }

    @PostMapping("/tasks")
    public ResponseEntity<TaskDto> createTask(@Valid @RequestBody TaskCreateRequest request,
                                              @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        TaskDto created = taskService.createTask(request, principal);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PatchMapping("/tasks/{id}")
    public ResponseEntity<TaskDto> updateTask(@PathVariable UUID id,
                                              @RequestBody TaskUpdateRequest request,
                                              @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(taskService.updateTask(id, request, principal));
    }

    @PostMapping("/tasks/{id}/transitions")
    public ResponseEntity<TaskDto> transitionTask(@PathVariable UUID id,
                                                  @Valid @RequestBody TaskTransitionRequest request,
                                                  @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(taskService.transitionTask(id, request, principal));
    }

    @PostMapping("/tasks/{id}/dependencies")
    public ResponseEntity<Void> addDependency(@PathVariable UUID id,
                                              @RequestParam UUID predecessorId,
                                              @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        taskService.addDependency(id, predecessorId, principal);
        return ResponseEntity.status(HttpStatus.CREATED).build();
    }
}
