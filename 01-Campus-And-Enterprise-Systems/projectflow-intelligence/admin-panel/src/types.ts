export type Role = 'ADMINISTRATOR' | 'MANAGER' | 'MEMBER' | 'VIEWER' | 'OWNER';

export interface UserProfile {
  id: string;
  email: string;
  fullName: string;
  avatarUrl?: string;
  role: Role;
  active: boolean;
  isOnline?: boolean;
  lastSeenAt?: number | string | null;
  createdAt?: string;
}

export interface Workspace {
  id: string;
  organizationId?: string;
  name: string;
  slug: string;
  description?: string;
  ownerId?: string;
  archived: boolean;
  createdAt: string;
  updatedAt?: string;
}

export type ProjectStatus = 'PLANNING' | 'IN_PROGRESS' | 'ON_HOLD' | 'COMPLETED' | 'ARCHIVED';
export type ProjectHealth = 'ON_TRACK' | 'AT_RISK' | 'OFF_TRACK';

export interface Project {
  id: string;
  workspaceId: string;
  name: string;
  code: string;
  description?: string;
  status: ProjectStatus;
  health: ProjectHealth;
  assigneeId?: string | null;
  assigneeName?: string | null;
  assigneeEmail?: string | null;
  teamId?: string | null;
  teamName?: string | null;
  assignedEmails?: string[];
  startDate?: string;
  targetDate?: string;
  completedAt?: string;
  createdAt: string;
  updatedAt?: string;
}

export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface Task {
  id: string;
  projectId: string;
  workflowStatusId?: string;
  title: string;
  description?: string;
  priority: TaskPriority;
  statusCategory: string;
  assigneeId?: string;
  assigneeName?: string;
  teamId?: string;
  teamName?: string;
  creatorId?: string;
  storyPoints?: number;
  progressPercent: number;
  startDate?: string;
  dueDate?: string;
  completedAt?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  channelName?: string;
  membersCount?: number;
  createdAt?: string;
}

export type RiskSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface RiskFinding {
  id?: string;
  ruleId: string;
  severity: RiskSeverity;
  title: string;
  description: string;
  affectedTaskId?: string;
  affectedTaskTitle?: string;
  projectId: string;
  recommendedAction?: string;
  detectedAt?: string;
}

export interface AuditLog {
  id: string;
  workspaceId?: string;
  actorId?: string;
  actorEmail?: string;
  action: string;
  entityType?: string;
  entityId?: string;
  details?: string;
  ipAddress?: string;
  metadata?: string;
  timestamp: string;
}

export interface SystemHealth {
  status: 'UP' | 'DOWN' | 'DEGRADED';
  databaseStatus: string;
  databaseLatencyMs: number;
  freeMemoryMb: number;
  totalMemoryMb: number;
  activeThreads: number;
  schemaVersion: string;
  checkedAt: string;
}

export interface AdminOverview {
  totalUsers: number;
  totalWorkspaces: number;
  totalProjects: number;
  totalTasks: number;
  activeRisksCount: number;
  systemStatus: string;
}

export interface PageResponse<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  size: number;
  number: number;
}

export interface AppRelease {
  id: string;
  versionName: string;
  versionCode: number;
  releaseNotes?: string;
  channel: 'ALPHA' | 'BETA' | 'STABLE';
  artifactUrl: string;
  artifactSize: number;
  sha256Checksum: string;
  minAndroidSdk: number;
  targetAndroidSdk: number;
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED' | 'DEPRECATED';
  publishedAt?: string;
  createdAt: string;
}

export interface ErrorLogEntry {
  id: string;
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  message: string;
  stack?: string | null;
  source: string;
  userId?: string | null;
  metadata?: Record<string, any>;
  resolved: boolean;
  resolvedAt?: string | null;
  timestamp: string;
}

export interface SystemSettings {
  syncIntervalMinutes: number;
  maxBatchSize: number;
  offlineGracePeriodHours: number;
  fcmEnabled: boolean;
  fcmSenderId: string;
  organizationName: string;
  contactEmail: string;
  riskSeverityThreshold: string;
  updatedAt?: string;
}
