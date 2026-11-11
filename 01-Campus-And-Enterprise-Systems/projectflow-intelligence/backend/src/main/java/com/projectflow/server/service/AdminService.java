package com.projectflow.server.service;

import com.projectflow.core.model.Role;
import com.projectflow.server.dto.AdminOverviewDto;
import com.projectflow.server.dto.SystemHealthDto;
import com.projectflow.server.dto.UserProfileDto;
import com.projectflow.server.entity.AuditLogEntity;
import com.projectflow.server.entity.ProfileEntity;
import com.projectflow.server.exception.ResourceNotFoundException;
import com.projectflow.server.repository.*;
import com.projectflow.server.security.UserPrincipal;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.sql.DataSource;
import java.lang.management.ManagementFactory;
import java.sql.Connection;
import java.time.Instant;
import java.util.UUID;

@Service
public class AdminService {

    private final ProfileRepository profileRepository;
    private final OrganizationRepository organizationRepository;
    private final WorkspaceRepository workspaceRepository;
    private final ProjectRepository projectRepository;
    private final TaskRepository taskRepository;
    private final RiskEventRepository riskEventRepository;
    private final SyncOperationRepository syncOperationRepository;
    private final AuditLogRepository auditLogRepository;
    private final AuditService auditService;
    private final DataSource dataSource;

    @Value("${app.env:development}")
    private String appEnv;

    public AdminService(ProfileRepository profileRepository,
                        OrganizationRepository organizationRepository,
                        WorkspaceRepository workspaceRepository,
                        ProjectRepository projectRepository,
                        TaskRepository taskRepository,
                        RiskEventRepository riskEventRepository,
                        SyncOperationRepository syncOperationRepository,
                        AuditLogRepository auditLogRepository,
                        AuditService auditService,
                        DataSource dataSource) {
        this.profileRepository = profileRepository;
        this.organizationRepository = organizationRepository;
        this.workspaceRepository = workspaceRepository;
        this.projectRepository = projectRepository;
        this.taskRepository = taskRepository;
        this.riskEventRepository = riskEventRepository;
        this.syncOperationRepository = syncOperationRepository;
        this.auditLogRepository = auditLogRepository;
        this.auditService = auditService;
        this.dataSource = dataSource;
    }

    @Transactional(readOnly = true)
    public AdminOverviewDto getOverview() {
        AdminOverviewDto dto = new AdminOverviewDto();
        dto.setTotalUsers(profileRepository.count());
        dto.setActiveUsers(profileRepository.countByActiveTrue());
        dto.setTotalOrganizations(organizationRepository.count());
        dto.setTotalWorkspaces(workspaceRepository.count());
        dto.setTotalProjects(projectRepository.countByArchivedFalse());
        dto.setTotalTasks(taskRepository.countByArchivedFalse());
        dto.setCompletedTasks(taskRepository.countByArchivedFalseAndCompletedAtIsNotNull());
        dto.setActiveRisks(riskEventRepository.countByStatus("ACTIVE"));
        dto.setSyncFailures(syncOperationRepository.countByStatus("FAILED") + syncOperationRepository.countByStatus("CONFLICT"));
        dto.setSystemStatus("OPERATIONAL");
        dto.setCalculatedAt(Instant.now());
        return dto;
    }

    @Transactional(readOnly = true)
    public Page<UserProfileDto> getUsers(String query, Pageable pageable) {
        Page<ProfileEntity> page;
        if (query != null && !query.isBlank()) {
            page = profileRepository.findByFullNameContainingIgnoreCaseOrEmailContainingIgnoreCase(query, query, pageable);
        } else {
            page = profileRepository.findAll(pageable);
        }
        return page.map(p -> new UserProfileDto(
                p.getId(), p.getEmail(), p.getFullName(), p.getAvatarUrl(), p.getGlobalRole(), p.isActive(), p.getCreatedAt()
        ));
    }

    @Transactional
    public UserProfileDto updateUserRole(UUID userId, Role newRole, UserPrincipal principal) {
        ProfileEntity profile = profileRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found: " + userId));

        Role oldRole = profile.getGlobalRole();
        profile.setGlobalRole(newRole);
        profile = profileRepository.save(profile);

        auditService.record(null, null, principal.getId(), principal.getEmail(),
                "UPDATE_USER_ROLE", "USER", userId, "Changed role from " + oldRole + " to " + newRole, null);

        return new UserProfileDto(
                profile.getId(), profile.getEmail(), profile.getFullName(), profile.getAvatarUrl(),
                profile.getGlobalRole(), profile.isActive(), profile.getCreatedAt()
        );
    }

    @Transactional(readOnly = true)
    public SystemHealthDto getSystemHealth() {
        SystemHealthDto dto = new SystemHealthDto();
        dto.setStatus("UP");
        dto.setApplicationVersion("2.0.0");
        dto.setEnvironment(appEnv);
        dto.setUptimeSeconds(ManagementFactory.getRuntimeMXBean().getUptime() / 1000);

        Runtime runtime = Runtime.getRuntime();
        long totalMemory = runtime.totalMemory();
        long freeMemory = runtime.freeMemory();
        dto.setMemoryUsedMb((totalMemory - freeMemory) / (1024 * 1024));
        dto.setMaxMemoryMb(runtime.maxMemory() / (1024 * 1024));

        try (Connection conn = dataSource.getConnection()) {
            dto.setDatabaseStatus("CONNECTED");
            dto.setDatabaseType(conn.getMetaData().getDatabaseProductName());
        } catch (Exception e) {
            dto.setDatabaseStatus("DISCONNECTED");
            dto.setStatus("DEGRADED");
        }

        return dto;
    }

    @Transactional(readOnly = true)
    public Page<AuditLogEntity> getAuditLogs(Pageable pageable) {
        return auditLogRepository.findAllByOrderByTimestampDesc(pageable);
    }
}
