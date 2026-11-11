package com.projectflow.android.data.repository;

import android.content.Context;
import androidx.lifecycle.LiveData;
import com.projectflow.android.data.local.*;
import com.projectflow.android.data.remote.ApiClient;
import com.projectflow.android.data.remote.ApiService;
import com.projectflow.android.data.remote.model.DtoModels.*;
import retrofit2.Response;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ProjectFlowRepository {
    private final Context context;
    private final AppDatabase db;
    private final ApiService api;
    private final ExecutorService executor;

    // High-performance In-Memory Enterprise Caches (Instant Tab Switching, Zero Reloads)
    private static final List<TeamMemberDto> sTeamCache = new java.util.concurrent.CopyOnWriteArrayList<>();
    private static final List<ChatGroupDto> sGroupsCache = new java.util.concurrent.CopyOnWriteArrayList<>();
    private static final Map<String, List<ChatMessageDto>> sChannelMessagesCache = new java.util.concurrent.ConcurrentHashMap<>();
    private static final List<ChatMessageDto> sAllMessagesCache = new java.util.concurrent.CopyOnWriteArrayList<>();
    private static volatile ReportSummaryDto sReportSummaryCache = null;

    public ProjectFlowRepository(Context context) {
        this.context = context.getApplicationContext();
        this.db = AppDatabase.getInstance(context);
        this.api = ApiClient.getService(context);
        this.executor = Executors.newSingleThreadExecutor();
    }

    // Workspaces
    public LiveData<List<WorkspaceEntity>> getWorkspaces() {
        refreshWorkspaces();
        return db.workspaceDao().getAllLive();
    }

    public void refreshWorkspaces() {
        executor.execute(() -> {
            try {
                Response<List<WorkspaceDto>> resp = api.getWorkspaces().execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    List<WorkspaceEntity> entities = new ArrayList<>();
                    for (WorkspaceDto dto : resp.body()) {
                        entities.add(new WorkspaceEntity(dto.id, dto.name, dto.slug, dto.description, dto.createdAt));
                    }
                    db.workspaceDao().insertAll(entities);
                }
            } catch (Exception e) {
                // Offline fallback - Room database already has the cached records
            }
        });
    }

    public void createWorkspace(String name, String slug, String description, Runnable onSuccess, Runnable onError) {
        executor.execute(() -> {
            try {
                Map<String, String> body = new HashMap<>();
                body.put("name", name);
                body.put("slug", slug);
                body.put("description", description != null ? description : "");
                Response<WorkspaceDto> resp = api.createWorkspace(body).execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    WorkspaceDto dto = resp.body();
                    db.workspaceDao().insert(new WorkspaceEntity(dto.id, dto.name, dto.slug, dto.description, dto.createdAt));
                    if (onSuccess != null) onSuccess.run();
                    return;
                }
            } catch (Exception e) {
                // Save offline
                String id = UUID.randomUUID().toString();
                db.workspaceDao().insert(new WorkspaceEntity(id, name, slug, description, new Date().toString()));
                db.syncQueueDao().insert(new SyncQueueEntity(UUID.randomUUID().toString(), "CREATE", "WORKSPACE", id, "{}", "PENDING", new Date().toString()));
                if (onSuccess != null) onSuccess.run();
                return;
            }
            if (onError != null) onError.run();
        });
    }

    // Projects
    public LiveData<List<ProjectEntity>> getProjects() {
        refreshProjects();
        return db.projectDao().getAllLive();
    }

    public void refreshProjects() {
        executor.execute(() -> {
            try {
                Response<List<ProjectDto>> resp = api.getAllProjects().execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    List<ProjectEntity> entities = new ArrayList<>();
                    for (ProjectDto dto : resp.body()) {
                        entities.add(new ProjectEntity(
                                dto.id, dto.workspaceId, dto.name, dto.code, dto.description,
                                dto.status, dto.health, dto.targetDate,
                                dto.assigneeId, dto.assigneeName, dto.assigneeEmail,
                                dto.teamId, dto.teamName
                        ));
                    }
                    db.projectDao().insertAll(entities);
                }
            } catch (Exception e) {
                // Offline mode
            }
        });
    }

    public void createProject(String workspaceId, String name, String code, String description, String assigneeId, String assigneeName, String assigneeEmail, String teamId, String teamName, Runnable onSuccess, Runnable onError) {
        executor.execute(() -> {
            try {
                Map<String, String> body = new HashMap<>();
                body.put("name", name);
                body.put("code", code);
                body.put("description", description != null ? description : "");
                if (assigneeId != null) body.put("assigneeId", assigneeId);
                if (assigneeName != null) body.put("assigneeName", assigneeName);
                if (assigneeEmail != null) body.put("assigneeEmail", assigneeEmail);
                if (teamId != null) body.put("teamId", teamId);
                if (teamName != null) body.put("teamName", teamName);
                Response<ProjectDto> resp = api.createProject(workspaceId, body).execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    ProjectDto dto = resp.body();
                    db.projectDao().insert(new ProjectEntity(
                            dto.id, dto.workspaceId, dto.name, dto.code, dto.description,
                            dto.status, dto.health, dto.targetDate,
                            dto.assigneeId, dto.assigneeName, dto.assigneeEmail,
                            dto.teamId, dto.teamName
                    ));
                    if (onSuccess != null) onSuccess.run();
                    return;
                }
            } catch (Exception e) {
                String id = UUID.randomUUID().toString();
                db.projectDao().insert(new ProjectEntity(id, workspaceId, name, code, description, "PLANNING", "ON_TRACK", null, assigneeId, assigneeName, assigneeEmail, teamId, teamName));
                db.syncQueueDao().insert(new SyncQueueEntity(UUID.randomUUID().toString(), "CREATE", "PROJECT", id, "{}", "PENDING", new Date().toString()));
                if (onSuccess != null) onSuccess.run();
                return;
            }
            if (onError != null) onError.run();
        });
    }

    public void createProject(String workspaceId, String name, String code, String description, Runnable onSuccess, Runnable onError) {
        createProject(workspaceId, name, code, description, null, null, null, null, null, onSuccess, onError);
    }

    // Tasks
    public LiveData<List<TaskEntity>> getAllTasks() {
        refreshAllTasks();
        return db.taskDao().getAllLive();
    }

    public void refreshAllTasks() {
        executor.execute(() -> {
            try {
                Response<List<TaskDto>> resp = api.getAllTasks().execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    List<TaskEntity> entities = new ArrayList<>();
                    for (TaskDto dto : resp.body()) {
                        entities.add(new TaskEntity(
                                dto.id, dto.projectId, dto.title, dto.description,
                                dto.priority, dto.statusCategory, dto.progressPercent, dto.dueDate,
                                dto.assigneeId, dto.assigneeName, dto.assigneeEmail,
                                dto.teamId, dto.teamName
                        ));
                    }
                    db.taskDao().insertAll(entities);
                }
            } catch (Exception e) {
                // Offline fallback
            }
        });
    }

    public LiveData<List<TaskEntity>> getTasks(String projectId) {
        refreshTasks(projectId);
        return db.taskDao().getByProjectLive(projectId);
    }

    public void refreshTasks(String projectId) {
        if (projectId == null) return;
        executor.execute(() -> {
            try {
                Response<List<TaskDto>> resp = api.getTasks(projectId).execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    List<TaskEntity> entities = new ArrayList<>();
                    for (TaskDto dto : resp.body()) {
                        entities.add(new TaskEntity(
                                dto.id, dto.projectId, dto.title, dto.description,
                                dto.priority, dto.statusCategory, dto.progressPercent, dto.dueDate,
                                dto.assigneeId, dto.assigneeName, dto.assigneeEmail,
                                dto.teamId, dto.teamName
                        ));
                    }
                    db.taskDao().insertAll(entities);
                }
            } catch (Exception e) {
                // Offline
            }
        });
    }

    public void createTask(String projectId, String title, String description, String priority, String dueDate, String assigneeId, String assigneeName, String assigneeEmail, String teamId, String teamName, Runnable onSuccess, Runnable onError) {
        executor.execute(() -> {
            try {
                Map<String, Object> body = new HashMap<>();
                body.put("title", title);
                body.put("description", description);
                body.put("priority", priority);
                if (dueDate != null && !dueDate.isEmpty()) {
                    body.put("dueDate", dueDate);
                }
                if (assigneeId != null && !assigneeId.isEmpty()) {
                    body.put("assigneeId", assigneeId);
                }
                if (assigneeName != null && !assigneeName.isEmpty()) {
                    body.put("assigneeName", assigneeName);
                }
                if (assigneeEmail != null && !assigneeEmail.isEmpty()) {
                    body.put("assigneeEmail", assigneeEmail);
                }
                if (teamId != null && !teamId.isEmpty()) {
                    body.put("teamId", teamId);
                }
                if (teamName != null && !teamName.isEmpty()) {
                    body.put("teamName", teamName);
                }
                Response<TaskDto> resp = api.createTask(projectId, body).execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    TaskDto dto = resp.body();
                    db.taskDao().insert(new TaskEntity(
                            dto.id, dto.projectId, dto.title, dto.description,
                            dto.priority, dto.statusCategory, dto.progressPercent, dto.dueDate,
                            dto.assigneeId, dto.assigneeName, dto.assigneeEmail,
                            dto.teamId, dto.teamName
                    ));
                    if (onSuccess != null) onSuccess.run();
                    return;
                }
            } catch (Exception e) {
                String id = UUID.randomUUID().toString();
                db.taskDao().insert(new TaskEntity(id, projectId, title, description, priority, "TODO", 0, dueDate, assigneeId, assigneeName, assigneeEmail, teamId, teamName));
                db.syncQueueDao().insert(new SyncQueueEntity(UUID.randomUUID().toString(), "CREATE", "TASK", id, "{}", "PENDING", new Date().toString()));
                if (onSuccess != null) onSuccess.run();
                return;
            }
            if (onError != null) onError.run();
        });
    }

    public void createTask(String projectId, String title, String description, String priority, String dueDate, String assigneeId, String assigneeName, String teamId, String teamName, Runnable onSuccess, Runnable onError) {
        createTask(projectId, title, description, priority, dueDate, assigneeId, assigneeName, null, teamId, teamName, onSuccess, onError);
    }

    public void createTask(String projectId, String title, String description, String priority, String dueDate, Runnable onSuccess, Runnable onError) {
        createTask(projectId, title, description, priority, dueDate, null, null, null, null, onSuccess, onError);
    }

    public void createTask(String projectId, String title, String description, String priority, Runnable onSuccess, Runnable onError) {
        createTask(projectId, title, description, priority, null, null, null, null, null, onSuccess, onError);
    }

    public void updateTaskStatus(String taskId, String statusCategory, int progressPercent, Runnable onDone) {
        executor.execute(() -> {
            try {
                Map<String, Object> body = new HashMap<>();
                body.put("statusCategory", statusCategory);
                body.put("progressPercent", progressPercent);
                api.updateTaskStatus(taskId, body).execute();
            } catch (Exception ignored) {}
            if (onDone != null) onDone.run();
        });
    }

    // Risks
    public LiveData<List<RiskEntity>> getRisks(String projectId) {
        evaluateRisks(projectId);
        return db.riskDao().getByProjectLive(projectId);
    }

    public void evaluateRisks(String projectId) {
        if (projectId == null) return;
        executor.execute(() -> {
            try {
                Response<List<RiskDto>> resp = api.evaluateRisks(projectId).execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    List<RiskEntity> entities = new ArrayList<>();
                    for (RiskDto dto : resp.body()) {
                        String rId = dto.id != null ? dto.id : UUID.randomUUID().toString();
                        entities.add(new RiskEntity(rId, projectId, dto.ruleId, dto.severity, dto.title, dto.description, dto.recommendedAction, dto.detectedAt));
                    }
                    db.riskDao().deleteByProject(projectId);
                    db.riskDao().insertAll(entities);
                }
            } catch (Exception e) {
                // Offline
            }
        });
    }

    public LiveData<Integer> getPendingSyncCount() {
        return db.syncQueueDao().getPendingCountLive();
    }

    public interface DataCallback<T> {
        void onData(T data);
        void onError(String message);
    }

    public void fetchTeam(DataCallback<List<TeamMemberDto>> callback) {
        if (!sTeamCache.isEmpty() && callback != null) {
            callback.onData(new ArrayList<>(sTeamCache));
        }
        executor.execute(() -> {
            try {
                Response<List<TeamMemberDto>> resp = api.getTeam().execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    sTeamCache.clear();
                    sTeamCache.addAll(resp.body());
                    if (callback != null) callback.onData(resp.body());
                } else {
                    if (callback != null && sTeamCache.isEmpty()) callback.onError("Failed to load team");
                }
            } catch (Exception e) {
                if (callback != null && sTeamCache.isEmpty()) callback.onError(e.getMessage());
            }
        });
    }

    public void fetchNotifications(DataCallback<List<NotificationDto>> callback) {
        executor.execute(() -> {
            try {
                Response<List<NotificationDto>> resp = api.getNotifications().execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    if (callback != null) callback.onData(resp.body());
                } else {
                    if (callback != null) callback.onError("Failed to load notifications");
                }
            } catch (Exception e) {
                if (callback != null) callback.onError(e.getMessage());
            }
        });
    }

    public void markNotificationRead(String id, Runnable onDone) {
        executor.execute(() -> {
            try {
                api.markNotificationRead(id).execute();
            } catch (Exception ignored) {}
            if (onDone != null) onDone.run();
        });
    }

    public void markAllNotificationsRead(Runnable onDone) {
        executor.execute(() -> {
            try {
                api.markAllNotificationsRead().execute();
            } catch (Exception ignored) {}
            if (onDone != null) onDone.run();
        });
    }

    public void fetchChatChannels(DataCallback<List<String>> callback) {
        executor.execute(() -> {
            try {
                Response<List<String>> resp = api.getChatChannels().execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    if (callback != null) callback.onData(resp.body());
                } else {
                    if (callback != null) callback.onError("Failed to load channels");
                }
            } catch (Exception e) {
                if (callback != null) callback.onError(e.getMessage());
            }
        });
    }

    public void fetchChatGroups(DataCallback<List<ChatGroupDto>> callback) {
        if (!sGroupsCache.isEmpty() && callback != null) {
            callback.onData(new ArrayList<>(sGroupsCache));
        }
        executor.execute(() -> {
            try {
                Response<List<ChatGroupDto>> resp = api.getChatGroups().execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    sGroupsCache.clear();
                    sGroupsCache.addAll(resp.body());
                    if (callback != null) callback.onData(resp.body());
                } else {
                    if (callback != null && sGroupsCache.isEmpty()) callback.onError("Failed to load chat groups");
                }
            } catch (Exception e) {
                if (callback != null && sGroupsCache.isEmpty()) callback.onError(e.getMessage());
            }
        });
    }

    public void createChatGroup(String name, String description, List<String> memberEmails, String creatorRole, String creatorEmail, DataCallback<ChatGroupDto> callback) {
        executor.execute(() -> {
            try {
                Map<String, Object> body = new HashMap<>();
                body.put("name", name);
                body.put("description", description != null ? description : "");
                body.put("memberEmails", memberEmails != null ? memberEmails : Collections.emptyList());
                body.put("creatorRole", creatorRole != null ? creatorRole : "MEMBER");
                body.put("creatorEmail", creatorEmail != null ? creatorEmail : "");
                Response<ChatGroupDto> resp = api.createChatGroup(body).execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    sGroupsCache.add(resp.body());
                    if (callback != null) callback.onData(resp.body());
                } else {
                    String err = "Failed to create group";
                    if (resp.code() == 403) {
                        err = "Permission denied: Only administrators can create group channels.";
                    }
                    if (callback != null) callback.onError(err);
                }
            } catch (Exception e) {
                if (callback != null) callback.onError(e.getMessage());
            }
        });
    }

    public void fetchAllChatMessages(DataCallback<List<ChatMessageDto>> callback) {
        if (!sAllMessagesCache.isEmpty() && callback != null) {
            callback.onData(new ArrayList<>(sAllMessagesCache));
        }
        executor.execute(() -> {
            try {
                Response<List<ChatMessageDto>> resp = api.getChatMessages().execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    sAllMessagesCache.clear();
                    sAllMessagesCache.addAll(resp.body());
                    if (callback != null) callback.onData(resp.body());
                } else {
                    if (callback != null && sAllMessagesCache.isEmpty()) callback.onError("Failed to load chat messages");
                }
            } catch (Exception e) {
                if (callback != null && sAllMessagesCache.isEmpty()) callback.onError(e.getMessage());
            }
        });
    }

    public void fetchChatMessages(DataCallback<List<ChatMessageDto>> callback) {
        fetchChatMessagesByChannel("general", callback);
    }

    public void fetchChatMessagesByChannel(String channel, DataCallback<List<ChatMessageDto>> callback) {
        if (channel != null && sChannelMessagesCache.containsKey(channel) && callback != null) {
            callback.onData(new ArrayList<>(sChannelMessagesCache.get(channel)));
        }
        executor.execute(() -> {
            try {
                Response<List<ChatMessageDto>> resp = api.getChatMessagesByChannel(channel).execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    if (channel != null) {
                        sChannelMessagesCache.put(channel, resp.body());
                    }
                    if (callback != null) callback.onData(resp.body());
                } else {
                    if (callback != null && (channel == null || !sChannelMessagesCache.containsKey(channel))) {
                        callback.onError("Failed to load chat messages");
                    }
                }
            } catch (Exception e) {
                if (callback != null && (channel == null || !sChannelMessagesCache.containsKey(channel))) {
                    callback.onError(e.getMessage());
                }
            }
        });
    }

    public void sendChatMessage(String content, String senderName, DataCallback<ChatMessageDto> callback) {
        sendChatMessage(content, senderName, "general", callback);
    }

    public void sendChatMessage(String content, String senderName, String channel, DataCallback<ChatMessageDto> callback) {
        android.content.SharedPreferences prefs = context.getSharedPreferences("projectflow_prefs", android.content.Context.MODE_PRIVATE);
        String email = prefs.getString("user_email", "admin@projectflow.io");
        String role = prefs.getString("user_role", "ADMINISTRATOR");
        String userId = prefs.getString("user_id", "");
        sendChatMessage(content, senderName, channel, email, role, userId, callback);
    }

    public void sendChatMessage(String content, String senderName, String channel, String senderEmail, String senderRole, String senderId, DataCallback<ChatMessageDto> callback) {
        executor.execute(() -> {
            try {
                Map<String, String> body = new HashMap<>();
                body.put("content", content);
                body.put("senderName", senderName != null ? senderName : "You");
                body.put("channel", channel != null ? channel : "general");
                if (senderEmail != null) body.put("senderEmail", senderEmail);
                if (senderRole != null) body.put("senderRole", senderRole);
                if (senderId != null) body.put("senderId", senderId);
                Response<ChatMessageDto> resp = api.sendChatMessage(body).execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    if (callback != null) callback.onData(resp.body());
                } else {
                    if (callback != null) callback.onError("Failed sending message");
                }
            } catch (Exception e) {
                if (callback != null) callback.onError(e.getMessage());
            }
        });
    }

    public void reactToMessage(String messageId, String emoji, DataCallback<ChatMessageDto> callback) {
        executor.execute(() -> {
            try {
                Map<String, String> body = new HashMap<>();
                body.put("emoji", emoji != null ? emoji : "👍");
                Response<ChatMessageDto> resp = api.reactToMessage(messageId, body).execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    if (callback != null) callback.onData(resp.body());
                } else {
                    if (callback != null) callback.onError("Failed to react to message");
                }
            } catch (Exception e) {
                if (callback != null) callback.onError(e.getMessage());
            }
        });
    }

    public void markChatMessagesSeen(String channel, Runnable onDone) {
        if (channel == null) return;
        executor.execute(() -> {
            try {
                Map<String, Object> body = new HashMap<>();
                body.put("channel", channel);
                api.markChatMessagesSeen(body).execute();
            } catch (Exception ignored) {}
            if (onDone != null) onDone.run();
        });
    }

    public void fetchTeams(DataCallback<List<TeamGroupDto>> callback) {
        executor.execute(() -> {
            try {
                Response<List<TeamGroupDto>> resp = api.getTeams().execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    if (callback != null) callback.onData(resp.body());
                } else {
                    if (callback != null) callback.onError("Failed to load teams");
                }
            } catch (Exception e) {
                if (callback != null) callback.onError(e.getMessage());
            }
        });
    }

    public void fetchReportSummary(DataCallback<ReportSummaryDto> callback) {
        if (sReportSummaryCache != null && callback != null) {
            callback.onData(sReportSummaryCache);
        }
        executor.execute(() -> {
            try {
                Response<ReportSummaryDto> resp = api.getReportSummary().execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    sReportSummaryCache = resp.body();
                    if (callback != null) callback.onData(resp.body());
                } else {
                    if (callback != null && sReportSummaryCache == null) callback.onError("Failed to fetch report summary");
                }
            } catch (Exception e) {
                if (callback != null && sReportSummaryCache == null) callback.onError(e.getMessage());
            }
        });
    }

    public void updateProfile(String fullName, DataCallback<UserDto> callback) {
        executor.execute(() -> {
            try {
                Map<String, String> body = new HashMap<>();
                body.put("fullName", fullName);
                Response<UserDto> resp = api.updateProfile(body).execute();
                if (resp.isSuccessful() && resp.body() != null) {
                    if (callback != null) callback.onData(resp.body());
                } else {
                    if (callback != null) callback.onError("Failed to update profile");
                }
            } catch (Exception e) {
                if (callback != null) callback.onError(e.getMessage());
            }
        });
    }
}
