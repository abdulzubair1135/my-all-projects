package com.projectflow.server.controller;

import com.projectflow.core.scheduling.ScheduleComparisonResult;
import com.projectflow.server.dto.ScenarioCreateRequest;
import com.projectflow.server.dto.ScenarioDto;
import com.projectflow.server.security.SecurityUtils;
import com.projectflow.server.security.UserPrincipal;
import com.projectflow.server.service.SchedulingService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1")
public class ScenarioController {

    private final SchedulingService schedulingService;

    public ScenarioController(SchedulingService schedulingService) {
        this.schedulingService = schedulingService;
    }

    @PostMapping("/projects/{projectId}/scenarios")
    public ResponseEntity<ScenarioDto> createScenario(@PathVariable UUID projectId,
                                                      @Valid @RequestBody ScenarioCreateRequest request,
                                                      @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        ScenarioDto created = schedulingService.createScenario(projectId, request, principal);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/scenarios/{id}")
    public ResponseEntity<ScenarioDto> getScenario(@PathVariable UUID id,
                                                   @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(schedulingService.getScenario(id, principal));
    }

    @GetMapping("/scenarios/{id}/evaluate")
    public ResponseEntity<ScheduleComparisonResult> evaluateScenario(@PathVariable UUID id,
                                                                     @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(schedulingService.evaluateScenario(id, principal));
    }

    @PostMapping("/scenarios/{id}/apply")
    public ResponseEntity<Void> applyScenario(@PathVariable UUID id,
                                              @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        schedulingService.applyScenario(id, principal);
        return ResponseEntity.ok().build();
    }
}
