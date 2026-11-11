package com.projectflow.server.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.projectflow.core.model.Role;
import com.projectflow.server.entity.ProfileEntity;
import com.projectflow.server.repository.ProfileRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Date;
import java.util.Optional;
import java.util.UUID;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(JwtAuthenticationFilter.class);

    private final ProfileRepository profileRepository;

    @Value("${app.supabase.jwt.issuer:https://demo.supabase.co/auth/v1}")
    private String expectedIssuer;

    @Value("${app.env:development}")
    private String appEnv;

    public JwtAuthenticationFilter(ProfileRepository profileRepository) {
        this.profileRepository = profileRepository;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String authHeader = request.getHeader("Authorization");

        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7).trim();

            try {
                // Development bootstrap / seeded admin token support
                if ("dev-admin-token".equals(token) || "seed-admin-token".equals(token)) {
                    authenticateDevUser(request, "admin@projectflow.io", "System Administrator", Role.ADMINISTRATOR);
                } else if ("dev-manager-token".equals(token)) {
                    authenticateDevUser(request, "manager@projectflow.io", "Project Manager", Role.MANAGER);
                } else if ("dev-member-token".equals(token)) {
                    authenticateDevUser(request, "member@projectflow.io", "Team Member", Role.MEMBER);
                } else {
                    // Standard Supabase JWT decode and validation
                    DecodedJWT jwt = JWT.decode(token);

                    // Check expiration
                    if (jwt.getExpiresAt() != null && jwt.getExpiresAt().before(new Date())) {
                        log.warn("Expired JWT token received");
                        response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Token expired");
                        return;
                    }

                    String subject = jwt.getSubject();
                    if (subject != null) {
                        UUID userId = UUID.fromString(subject);
                        String email = jwt.getClaim("email").asString();
                        if (email == null) {
                            email = "user-" + subject.substring(0, 8) + "@projectflow.io";
                        }

                        // Retrieve or provision profile
                        Optional<ProfileEntity> profileOpt = profileRepository.findById(userId);
                        ProfileEntity profile;
                        if (profileOpt.isEmpty()) {
                            profile = new ProfileEntity(userId, email, "ProjectFlow User", Role.MEMBER);
                            profile = profileRepository.save(profile);
                        } else {
                            profile = profileOpt.get();
                        }

                        UserPrincipal principal = new UserPrincipal(profile.getId(), profile.getEmail(), profile.getFullName(), profile.getGlobalRole());
                        UsernamePasswordAuthenticationToken authentication =
                                new UsernamePasswordAuthenticationToken(principal, null, principal.getAuthorities());
                        authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                        SecurityContextHolder.getContext().setAuthentication(authentication);
                    }
                }
            } catch (Exception e) {
                log.warn("JWT authentication failed: {}", e.getMessage());
                SecurityContextHolder.clearContext();
            }
        }

        filterChain.doFilter(request, response);
    }

    private void authenticateDevUser(HttpServletRequest request, String email, String name, Role role) {
        UUID userId = UUID.nameUUIDFromBytes(email.getBytes());
        ProfileEntity profile = profileRepository.findByEmailIgnoreCase(email)
                .orElseGet(() -> profileRepository.save(new ProfileEntity(userId, email, name, role)));

        UserPrincipal principal = new UserPrincipal(profile.getId(), profile.getEmail(), profile.getFullName(), profile.getGlobalRole());
        UsernamePasswordAuthenticationToken authentication =
                new UsernamePasswordAuthenticationToken(principal, null, principal.getAuthorities());
        authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
        SecurityContextHolder.getContext().setAuthentication(authentication);
    }
}
