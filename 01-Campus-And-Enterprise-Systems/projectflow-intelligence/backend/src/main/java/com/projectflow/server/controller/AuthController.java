package com.projectflow.server.controller;

import com.projectflow.core.model.Role;
import com.projectflow.server.dto.AuthRequest;
import com.projectflow.server.dto.AuthResponse;
import com.projectflow.server.dto.UserProfileDto;
import com.projectflow.server.entity.ProfileEntity;
import com.projectflow.server.repository.ProfileRepository;
import com.projectflow.server.security.SecurityUtils;
import com.projectflow.server.security.UserPrincipal;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1")
public class AuthController {

    private final ProfileRepository profileRepository;

    public AuthController(ProfileRepository profileRepository) {
        this.profileRepository = profileRepository;
    }

    @GetMapping("/me")
    public ResponseEntity<UserProfileDto> getCurrentUser(@AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) {
            principal = SecurityUtils.getCurrentUser();
        }
        UserProfileDto dto = new UserProfileDto(
                principal.getId(),
                principal.getEmail(),
                principal.getFullName(),
                null,
                principal.getRole(),
                true,
                null
        );
        return ResponseEntity.ok(dto);
    }

    @PostMapping("/auth/dev-login")
    public ResponseEntity<AuthResponse> devLogin(@RequestBody AuthRequest request) {
        String targetEmail = (request.getEmail() != null && !request.getEmail().isBlank())
                ? request.getEmail() : "admin@projectflow.io";

        Role role = Role.MEMBER;
        String token = "dev-member-token";
        String name = "Team Member";

        if (targetEmail.contains("admin")) {
            role = Role.ADMINISTRATOR;
            token = "dev-admin-token";
            name = "System Administrator";
        } else if (targetEmail.contains("manager")) {
            role = Role.MANAGER;
            token = "dev-manager-token";
            name = "Project Manager";
        }

        final String userEmail = targetEmail;
        final String userName = name;
        final Role userRole = role;

        UUID userId = UUID.nameUUIDFromBytes(userEmail.getBytes());
        ProfileEntity profile = profileRepository.findByEmailIgnoreCase(userEmail)
                .orElseGet(() -> profileRepository.save(new ProfileEntity(userId, userEmail, userName, userRole)));

        UserProfileDto userDto = new UserProfileDto(
                profile.getId(), profile.getEmail(), profile.getFullName(), profile.getAvatarUrl(),
                profile.getGlobalRole(), profile.isActive(), profile.getCreatedAt()
        );

        return ResponseEntity.ok(new AuthResponse(token, userDto));
    }
}
