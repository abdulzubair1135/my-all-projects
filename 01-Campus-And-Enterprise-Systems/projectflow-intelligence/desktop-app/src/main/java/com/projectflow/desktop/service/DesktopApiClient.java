package com.projectflow.desktop.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.projectflow.core.model.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.util.*;

public class DesktopApiClient {
    private static final Logger log = LoggerFactory.getLogger(DesktopApiClient.class);

    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    private final LocalStorageService localStorage;
    private String baseUrl;
    private String authToken;

    public DesktopApiClient(LocalStorageService localStorage) {
        this.localStorage = localStorage;
        this.baseUrl = localStorage.getSetting("api_base_url", "http://localhost:8080/api/v1");
        this.authToken = localStorage.getSetting("auth_token", "dev-manager-token");

        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(3))
                .build();

        this.objectMapper = new ObjectMapper();
        this.objectMapper.registerModule(new JavaTimeModule());
        this.objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    }

    public boolean isServerReachable() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/me"))
                    .header("Authorization", "Bearer " + authToken)
                    .timeout(Duration.ofSeconds(2))
                    .GET()
                    .build();
            HttpResponse<String> resp = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            return resp.statusCode() == 200;
        } catch (Exception e) {
            return false;
        }
    }

    public List<Workspace> getWorkspaces() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/workspaces"))
                    .header("Authorization", "Bearer " + authToken)
                    .timeout(Duration.ofSeconds(4))
                    .GET()
                    .build();
            HttpResponse<String> resp = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() == 200) {
                List<Workspace> list = objectMapper.readValue(resp.body(), new TypeReference<List<Workspace>>() {});
                cacheWorkspaces(list);
                return list;
            }
        } catch (Exception e) {
            log.warn("Failed fetching workspaces from server, falling back to local SQLite cache: {}", e.getMessage());
        }
        return getCachedWorkspaces();
    }

    public Workspace createWorkspace(String name, String slug, String description) throws Exception {
        Map<String, String> body = Map.of(
                "name", name,
                "slug", slug,
                "description", description != null ? description : ""
        );
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/workspaces"))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + authToken)
                .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(body)))
                .build();
        HttpResponse<String> resp = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() >= 200 && resp.statusCode() < 300) {
            Workspace ws = objectMapper.readValue(resp.body(), Workspace.class);
            cacheWorkspaces(List.of(ws));
            return ws;
        }
        throw new IOException("Server returned " + resp.statusCode() + ": " + resp.body());
    }

    public List<Project> getProjects(UUID workspaceId) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/workspaces/" + workspaceId + "/projects"))
                    .header("Authorization", "Bearer " + authToken)
                    .timeout(Duration.ofSeconds(4))
                    .GET()
                    .build();
            HttpResponse<String> resp = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() == 200) {
                List<Project> list = objectMapper.readValue(resp.body(), new TypeReference<List<Project>>() {});
                cacheProjects(workspaceId, list);
                return list;
            }
        } catch (Exception e) {
            log.warn("Failed fetching projects from server, falling back to local SQLite: {}", e.getMessage());
        }
        return getCachedProjects(workspaceId);
    }

    public Project createProject(UUID workspaceId, String name, String code, String description) throws Exception {
        Map<String, String> body = Map.of(
                "name", name,
                "code", code,
                "description", description != null ? description : ""
        );
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/workspaces/" + workspaceId + "/projects"))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + authToken)
                .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(body)))
                .build();
        HttpResponse<String> resp = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() >= 200 && resp.statusCode() < 300) {
            Project p = objectMapper.readValue(resp.body(), Project.class);
            cacheProjects(workspaceId, List.of(p));
            return p;
        }
        throw new IOException("Failed creating project: " + resp.body());
    }

    public List<Task> getTasks(UUID projectId) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/projects/" + projectId + "/tasks"))
                    .header("Authorization", "Bearer " + authToken)
                    .timeout(Duration.ofSeconds(4))
                    .GET()
                    .build();
            HttpResponse<String> resp = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() == 200) {
                List<Task> list = objectMapper.readValue(resp.body(), new TypeReference<List<Task>>() {});
                cacheTasks(projectId, list);
                return list;
            }
        } catch (Exception e) {
            log.warn("Failed fetching tasks from server, falling back to local SQLite: {}", e.getMessage());
        }
        return getCachedTasks(projectId);
    }

    public Task createTask(UUID projectId, String title, String description, TaskPriority priority, LocalDate dueDate) throws Exception {
        Map<String, Object> body = new HashMap<>();
        body.put("title", title);
        body.put("description", description);
        body.put("priority", priority.name());
        if (dueDate != null) {
            body.put("dueDate", dueDate.toString());
        }

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/projects/" + projectId + "/tasks"))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + authToken)
                .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(body)))
                .build();
        HttpResponse<String> resp = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() >= 200 && resp.statusCode() < 300) {
            Task t = objectMapper.readValue(resp.body(), Task.class);
            cacheTasks(projectId, List.of(t));
            return t;
        }
        throw new IOException("Failed creating task: " + resp.body());
    }

    public List<RiskFinding> evaluateRisks(UUID projectId) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/projects/" + projectId + "/risks/evaluate"))
                    .header("Authorization", "Bearer " + authToken)
                    .POST(HttpRequest.BodyPublishers.noBody())
                    .build();
            HttpResponse<String> resp = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() == 200) {
                return objectMapper.readValue(resp.body(), new TypeReference<List<RiskFinding>>() {});
            }
        } catch (Exception e) {
            log.warn("Online risk evaluation failed: {}", e.getMessage());
        }
        return Collections.emptyList();
    }

    // Local SQLite Caching Implementations
    private void cacheWorkspaces(List<Workspace> list) {
        String sql = "INSERT INTO local_workspaces(id, name, slug, description, created_at) VALUES(?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET name = excluded.name, slug = excluded.slug, description = excluded.description";
        try (Connection conn = localStorage.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            for (Workspace ws : list) {
                ps.setString(1, ws.getId().toString());
                ps.setString(2, ws.getName());
                ps.setString(3, ws.getSlug());
                ps.setString(4, ws.getDescription());
                ps.setString(5, ws.getCreatedAt() != null ? ws.getCreatedAt().toString() : Instant.now().toString());
                ps.addBatch();
            }
            ps.executeBatch();
        } catch (Exception e) {
            log.error("Failed caching workspaces", e);
        }
    }

    private List<Workspace> getCachedWorkspaces() {
        List<Workspace> res = new ArrayList<>();
        String sql = "SELECT id, name, slug, description, created_at FROM local_workspaces";
        try (Connection conn = localStorage.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                Workspace ws = new Workspace();
                ws.setId(UUID.fromString(rs.getString("id")));
                ws.setName(rs.getString("name"));
                ws.setSlug(rs.getString("slug"));
                ws.setDescription(rs.getString("description"));
                res.add(ws);
            }
        } catch (Exception e) {
            log.error("Failed querying cached workspaces", e);
        }
        return res;
    }

    private void cacheProjects(UUID workspaceId, List<Project> list) {
        String sql = "INSERT INTO local_projects(id, workspace_id, name, code, description, status, health, target_date, created_at) " +
                "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET name = excluded.name, status = excluded.status";
        try (Connection conn = localStorage.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            for (Project p : list) {
                ps.setString(1, p.getId().toString());
                ps.setString(2, workspaceId.toString());
                ps.setString(3, p.getName());
                ps.setString(4, p.getName().substring(0, Math.min(3, p.getName().length())).toUpperCase());
                ps.setString(5, p.getDescription());
                ps.setString(6, p.getStatus() != null ? p.getStatus() : "ACTIVE");
                ps.setString(7, "ON_TRACK");
                ps.setString(8, p.getTargetDate() != null ? p.getTargetDate().toString() : null);
                ps.setString(9, p.getCreatedAt() != null ? p.getCreatedAt().toString() : Instant.now().toString());
                ps.addBatch();
            }
            ps.executeBatch();
        } catch (Exception e) {
            log.error("Failed caching projects", e);
        }
    }

    private List<Project> getCachedProjects(UUID workspaceId) {
        List<Project> res = new ArrayList<>();
        String sql = "SELECT id, name, description, status, target_date FROM local_projects WHERE workspace_id = ?";
        try (Connection conn = localStorage.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, workspaceId.toString());
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    Project p = new Project();
                    p.setId(UUID.fromString(rs.getString("id")));
                    p.setWorkspaceId(workspaceId);
                    p.setName(rs.getString("name"));
                    p.setDescription(rs.getString("description"));
                    p.setStatus(rs.getString("status"));
                    String targetDateStr = rs.getString("target_date");
                    if (targetDateStr != null) {
                        p.setTargetDate(LocalDate.parse(targetDateStr));
                    }
                    res.add(p);
                }
            }
        } catch (Exception e) {
            log.error("Failed querying cached projects", e);
        }
        return res;
    }

    private void cacheTasks(UUID projectId, List<Task> list) {
        String sql = "INSERT INTO local_tasks(id, project_id, title, description, priority, status_category, progress_percent, due_date, created_at) " +
                "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET title = excluded.title, priority = excluded.priority";
        try (Connection conn = localStorage.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            for (Task t : list) {
                ps.setString(1, t.getId().toString());
                ps.setString(2, projectId.toString());
                ps.setString(3, t.getTitle());
                ps.setString(4, t.getDescription());
                ps.setString(5, t.getPriority() != null ? t.getPriority().name() : "MEDIUM");
                ps.setString(6, t.getCompletedAt() != null ? "DONE" : "IN_PROGRESS");
                ps.setInt(7, t.getCompletedAt() != null ? 100 : 0);
                ps.setString(8, t.getDueDate() != null ? t.getDueDate().toString() : null);
                ps.setString(9, t.getCreatedAt() != null ? t.getCreatedAt().toString() : Instant.now().toString());
                ps.addBatch();
            }
            ps.executeBatch();
        } catch (Exception e) {
            log.error("Failed caching tasks", e);
        }
    }

    private List<Task> getCachedTasks(UUID projectId) {
        List<Task> res = new ArrayList<>();
        String sql = "SELECT id, title, description, priority, due_date FROM local_tasks WHERE project_id = ?";
        try (Connection conn = localStorage.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, projectId.toString());
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    Task t = new Task();
                    t.setId(UUID.fromString(rs.getString("id")));
                    t.setProjectId(projectId);
                    t.setTitle(rs.getString("title"));
                    t.setDescription(rs.getString("description"));
                    t.setPriority(TaskPriority.valueOf(rs.getString("priority")));
                    String due = rs.getString("due_date");
                    if (due != null) {
                        t.setDueDate(LocalDate.parse(due));
                    }
                    res.add(t);
                }
            }
        } catch (Exception e) {
            log.error("Failed querying cached tasks", e);
        }
        return res;
    }
}
