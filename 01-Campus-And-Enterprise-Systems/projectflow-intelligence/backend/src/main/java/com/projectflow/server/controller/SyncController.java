package com.projectflow.server.controller;

import com.projectflow.server.dto.SyncBatchRequest;
import com.projectflow.server.dto.SyncBatchResponse;
import com.projectflow.server.security.SecurityUtils;
import com.projectflow.server.security.UserPrincipal;
import com.projectflow.server.service.SyncService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/sync")
public class SyncController {

    private final SyncService syncService;

    public SyncController(SyncService syncService) {
        this.syncService = syncService;
    }

    @PostMapping("/operations")
    public ResponseEntity<SyncBatchResponse> syncOperations(@RequestBody SyncBatchRequest request,
                                                            @AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) principal = SecurityUtils.getCurrentUser();
        return ResponseEntity.ok(syncService.processBatch(request, principal));
    }
}
