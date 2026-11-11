package com.projectflow.android.data.remote;

import com.projectflow.android.data.remote.model.DtoModels.*;
import retrofit2.Call;
import retrofit2.http.*;

import java.util.List;
import java.util.Map;

public interface ApiService {

    @POST("auth/dev-login")
    Call<AuthResponse> devLogin(@Body Map<String, String> body);

    @POST("auth/login")
    Call<AuthResponse> login(@Body Map<String, String> body);

    @POST("auth/signup")
    Call<AuthResponse> signup(@Body Map<String, String> body);

    @POST("auth/forgot-password")
    Call<Map<String, Object>> forgotPassword(@Body Map<String, String> body);

    @POST("auth/reset-password")
    Call<Map<String, Object>> resetPassword(@Body Map<String, String> body);

    @POST("users/fcm-token")
    Call<Map<String, Object>> registerFcmToken(@Body Map<String, String> body);


    @GET("workspaces")
    Call<List<WorkspaceDto>> getWorkspaces();

    @POST("workspaces")
    Call<WorkspaceDto> createWorkspace(@Body Map<String, String> body);

    @GET("workspaces/{id}/projects")
    Call<List<ProjectDto>> getProjects(@Path("id") String workspaceId);

    @GET("projects")
    Call<List<ProjectDto>> getAllProjects();

    @POST("workspaces/{id}/projects")
    Call<ProjectDto> createProject(@Path("id") String workspaceId, @Body Map<String, String> body);

    @GET("projects/{id}/tasks")
    Call<List<TaskDto>> getTasks(@Path("id") String projectId);

    @POST("projects/{id}/tasks")
    Call<TaskDto> createTask(@Path("id") String projectId, @Body Map<String, Object> body);

    @POST("projects/{id}/risks/evaluate")
    Call<List<RiskDto>> evaluateRisks(@Path("id") String projectId);

    @GET("releases/latest")
    Call<ReleaseDto> getLatestRelease(@Query("applicationId") String applicationId);

    @Streaming
    @GET("releases/{id}/download")
    Call<okhttp3.ResponseBody> downloadRelease(@Path("id") String releaseId);

    @GET("team")
    Call<List<TeamMemberDto>> getTeam();

    @GET("teams")
    Call<List<TeamGroupDto>> getTeams();

    @POST("teams")
    Call<TeamGroupDto> createTeam(@Body Map<String, Object> body);

    @GET("tasks")
    Call<List<TaskDto>> getAllTasks();

    @PATCH("tasks/{id}/status")
    Call<TaskDto> updateTaskStatus(@Path("id") String taskId, @Body Map<String, Object> body);

    @GET("notifications")
    Call<List<NotificationDto>> getNotifications();

    @PATCH("notifications/{id}/read")
    Call<NotificationDto> markNotificationRead(@Path("id") String id);

    @POST("notifications/mark-all-read")
    Call<Map<String, Object>> markAllNotificationsRead();

    @GET("chat/channels")
    Call<List<String>> getChatChannels();

    @GET("chat/groups")
    Call<List<ChatGroupDto>> getChatGroups();

    @POST("chat/groups")
    Call<ChatGroupDto> createChatGroup(@Body Map<String, Object> body);

    @GET("chat/messages")
    Call<List<ChatMessageDto>> getChatMessages();

    @GET("chat/messages")
    Call<List<ChatMessageDto>> getChatMessagesByChannel(@Query("channel") String channel);

    @POST("chat/messages")
    Call<ChatMessageDto> sendChatMessage(@Body Map<String, String> body);

    @POST("chat/messages/seen")
    Call<Map<String, Object>> markChatMessagesSeen(@Body Map<String, Object> body);

    @POST("chat/messages/{id}/react")
    Call<ChatMessageDto> reactToMessage(@Path("id") String messageId, @Body Map<String, String> body);

    @PATCH("me/profile")
    Call<UserDto> updateProfile(@Body Map<String, String> body);

    @GET("reports/summary")
    Call<ReportSummaryDto> getReportSummary();
}
