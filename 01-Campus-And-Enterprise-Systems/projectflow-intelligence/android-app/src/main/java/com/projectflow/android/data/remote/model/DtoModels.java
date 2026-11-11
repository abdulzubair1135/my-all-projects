package com.projectflow.android.data.remote.model;

import java.util.List;

public class DtoModels {

    public static class WorkspaceDto {
        public String id;
        public String name;
        public String slug;
        public String description;
        public String createdAt;
    }

    public static class ProjectDto {
        public String id;
        public String workspaceId;
        public String name;
        public String code;
        public String description;
        public String status;
        public String health;
        public String targetDate;
        public String assigneeId;
        public String assigneeName;
        public String assigneeEmail;
        public String teamId;
        public String teamName;
    }

    public static class TaskDto {
        public String id;
        public String projectId;
        public String title;
        public String description;
        public String priority;
        public String statusCategory;
        public int progressPercent;
        public String dueDate;
        public String assigneeId;
        public String assigneeName;
        public String assigneeEmail;
        public String teamId;
        public String teamName;
    }

    public static class RiskDto {
        public String id;
        public String ruleId;
        public String severity;
        public String title;
        public String description;
        public String recommendedAction;
        public String detectedAt;
    }

    public static class UserDto {
        public String id;
        public String email;
        public String fullName;
        public String role;
        public boolean active;
    }

    public static class AuthResponse {
        public String token;
        public UserDto user;
    }

    public static class ReleaseDto {
        public String id;
        public String applicationId;
        public String versionName;
        public long versionCode;
        public String artifactFilename;
        public String downloadUrl;
        public long fileSizeBytes;
        public String sha256Checksum;
        public String releaseChannel;
        public String releaseNotes;
        public String status;
        public String publishedAt;
    }

    public static class TeamMemberDto {
        public String id;
        public String email;
        public String fullName;
        public String role;
        public boolean active;
        public boolean isOnline;
        public String lastSeen;
        public int assignedTasksCount;
    }

    public static class TeamGroupDto {
        public String id;
        public String name;
        public String slug;
        public String description;
        public int memberCount;
        public String channel;
        public String createdAt;
    }

    public static class NotificationDto {
        public String id;
        public String title;
        public String message;
        public String type;
        public String taskId;
        public String projectId;
        public String priority;
        public String channel;
        public String senderName;
        public String senderEmail;
        public String userId;
        public String targetEmail;
        public List<String> targetEmails;
        public boolean read;
        public String createdAt;
    }

    public static class ChatMessageDto {
        public String id;
        public String senderId;
        public String senderName;
        public String senderEmail;
        public String senderRole;
        public String content;
        public String channel;
        public java.util.Map<String, Integer> reactions;
        public boolean seen;
        public List<String> seenBy;
        public String seenAt;
        public String status;
        public String createdAt;
    }

    public static class ReportSummaryDto {
        public int totalTasks;
        public int completedTasks;
        public int inProgressTasks;
        public int todoTasks;
        public int overdueTasks;
        public int completionRate;
        public int totalProjects;
        public int activeProjects;
        public java.util.Map<String, Integer> statusDistribution;
        public String generatedAt;
    }

    public static class ChatGroupDto {
        public String id;
        public String name;
        public String channel;
        public String description;
        public List<String> members;
        public String createdBy;
        public String createdAt;
    }
}
