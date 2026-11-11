package com.projectflow.server.controller;

import com.projectflow.server.dto.RiskFindingDto;
import com.projectflow.server.security.SecurityUtils;
import com.projectflow.server.security.UserPrincipal;
import com.projectflow.server.service.RiskService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1")
public class RiskController {

    private final RiskService riskService;

    public RiskController(RiskService riskService) {
        this.riskService = riskService;
    }

    @GetMapping("/projects/{projectId}/risks")
    public ResponseEntity<List<RiskFindingDto>> getProjectRisks(@PathVariable UUID projectId,
                                                                @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(riskService.getProjectRisks(projectId, principal));
    }

    @PostMapping("/projects/{projectId}/risks/recalculate")
    public ResponseEntity<List<RiskFindingDto>> recalculateProjectRisks(@PathVariable UUID projectId,
                                                                        @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(riskService.recalculateProjectRisks(projectId, principal));
    }
}
