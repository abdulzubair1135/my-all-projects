import { AdminOverview, AppRelease, AuditLog, ErrorLogEntry, PageResponse, Project, RiskFinding, SystemHealth, SystemSettings, Task, Team, UserProfile, Workspace } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('projectflow_token') || 'dev-admin-token';
  const email = localStorage.getItem('projectflow_user_email') || 'admin@projectflow.io';
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    'x-user-email': email
  };
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    if (res.status === 401) {
      // Unauthenticated
      console.warn('API returned 401 Unauthorized');
    }
    const errBody = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(errBody.error || errBody.message || `API error ${res.status}`);
  }
  if (res.status === 204) {
    return {} as T;
  }
  return res.json();
}

export const api = {
  // Auth
  async login(email: string, password?: string) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password: password || 'ProjectFlow@2026' })
    });
    return handleResponse<{ token: string; user: UserProfile }>(res);
  },

  async devLogin(email: string) {
    const res = await fetch(`${API_BASE}/auth/dev-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    return handleResponse<{ token: string; user: UserProfile }>(res);
  },

  async forgotPassword(email: string) {
    const res = await fetch(`${API_BASE}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    return handleResponse<{ success: boolean; message: string; otp: string }>(res);
  },

  async resetPassword(email: string, otp: string, newPassword: string) {
    const res = await fetch(`${API_BASE}/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, otp, newPassword })
    });
    return handleResponse<{ success: boolean; message: string }>(res);
  },


  async getCurrentUser() {
    const res = await fetch(`${API_BASE}/me`, {
      headers: getAuthHeaders()
    });
    return handleResponse<UserProfile>(res);
  },

  // Admin Overview & Health
  async getAdminOverview() {
    const res = await fetch(`${API_BASE}/admin/overview`, {
      headers: getAuthHeaders()
    });
    return handleResponse<AdminOverview>(res);
  },

  async getSystemHealth() {
    const res = await fetch(`${API_BASE}/admin/system/health`, {
      headers: getAuthHeaders()
    });
    return handleResponse<SystemHealth>(res);
  },

  async getAuditEvents(page = 0, size = 25, query = '', action = '') {
    const q = query ? `&query=${encodeURIComponent(query)}` : '';
    const a = action && action !== 'ALL' ? `&action=${encodeURIComponent(action)}` : '';
    const res = await fetch(`${API_BASE}/admin/audit-events?page=${page}&size=${size}${q}${a}`, {
      headers: getAuthHeaders()
    });
    return handleResponse<PageResponse<AuditLog>>(res);
  },

  // Users
  async getUsers(query = '', page = 0, size = 50) {
    const q = query ? `&query=${encodeURIComponent(query)}` : '';
    const res = await fetch(`${API_BASE}/admin/users?page=${page}&size=${size}${q}`, {
      headers: getAuthHeaders()
    });
    return handleResponse<PageResponse<UserProfile>>(res);
  },

  async createUser(data: { email: string; fullName: string; role: string }) {
    const res = await fetch(`${API_BASE}/admin/users`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<UserProfile>(res);
  },

  async updateUserRole(userId: string, role: string) {
    const res = await fetch(`${API_BASE}/admin/users/${userId}/role`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ role })
    });
    return handleResponse<UserProfile>(res);
  },

  async updateUserStatus(userId: string, active?: boolean) {
    const res = await fetch(`${API_BASE}/admin/users/${userId}/status`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(active !== undefined ? { active } : {})
    });
    return handleResponse<UserProfile>(res);
  },

  // System Settings
  async getSettings() {
    const res = await fetch(`${API_BASE}/admin/settings`, {
      headers: getAuthHeaders()
    });
    return handleResponse<SystemSettings>(res);
  },

  async updateSettings(data: Partial<SystemSettings>) {
    const res = await fetch(`${API_BASE}/admin/settings`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<SystemSettings>(res);
  },

  // Workspaces
  async getWorkspaces() {
    const res = await fetch(`${API_BASE}/admin/workspaces`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Workspace[]>(res);
  },

  async createWorkspace(data: { name: string; slug: string; description?: string }) {
    const res = await fetch(`${API_BASE}/workspaces`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<Workspace>(res);
  },

  // Projects
  async getProjects() {
    const res = await fetch(`${API_BASE}/admin/projects`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Project[]>(res);
  },

  async getWorkspaceProjects(workspaceId: string) {
    const res = await fetch(`${API_BASE}/workspaces/${workspaceId}/projects`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Project[]>(res);
  },

  async createProject(workspaceId: string, data: { name: string; code: string; description?: string; assigneeId?: string | null; assigneeName?: string | null; assigneeEmail?: string | null; teamId?: string | null; teamName?: string | null; targetDate?: string }) {
    const res = await fetch(`${API_BASE}/workspaces/${workspaceId}/projects`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<Project>(res);
  },

  async updateProject(projectId: string, data: Partial<Project>) {
    const res = await fetch(`${API_BASE}/projects/${projectId}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<Project>(res);
  },

  // Tasks
  async getProjectTasks(projectId: string) {
    const res = await fetch(`${API_BASE}/projects/${projectId}/tasks`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Task[]>(res);
  },

  async getAllTasks() {
    const res = await fetch(`${API_BASE}/tasks`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Task[]>(res);
  },

  async createTask(projectId: string, data: {
    title: string;
    description?: string;
    priority?: string;
    dueDate?: string;
    assigneeId?: string;
    assigneeName?: string;
    teamId?: string;
    teamName?: string;
  }) {
    const res = await fetch(`${API_BASE}/projects/${projectId}/tasks`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<Task>(res);
  },

  async updateTaskStatus(taskId: string, statusCategory: string, progressPercent?: number) {
    const res = await fetch(`${API_BASE}/tasks/${taskId}/status`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ statusCategory, progressPercent })
    });
    return handleResponse<Task>(res);
  },

  async updateTask(taskId: string, data: Partial<Task>) {
    const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<Task>(res);
  },

  // Teams & Squads
  async getTeams() {
    const res = await fetch(`${API_BASE}/teams`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Team[]>(res);
  },

  async createTeam(data: { name: string; description?: string }) {
    const res = await fetch(`${API_BASE}/teams`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<Team>(res);
  },

  // Risks
  async getProjectRisks(projectId: string) {
    const res = await fetch(`${API_BASE}/projects/${projectId}/risks`, {
      headers: getAuthHeaders()
    });
    return handleResponse<RiskFinding[]>(res);
  },

  async evaluateRisks(projectId: string) {
    const res = await fetch(`${API_BASE}/projects/${projectId}/risks/evaluate`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return handleResponse<RiskFinding[]>(res);
  },

  // App Releases & APK Distribution
  async getReleases() {
    const res = await fetch(`${API_BASE}/admin/releases`, {
      headers: getAuthHeaders()
    });
    return handleResponse<AppRelease[]>(res);
  },

  async createRelease(data: Partial<AppRelease>) {
    const res = await fetch(`${API_BASE}/admin/releases`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<AppRelease>(res);
  },

  async publishRelease(id: string) {
    const res = await fetch(`${API_BASE}/admin/releases/${id}/publish`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return handleResponse<AppRelease>(res);
  },

  async unpublishRelease(id: string) {
    const res = await fetch(`${API_BASE}/admin/releases/${id}/unpublish`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return handleResponse<AppRelease>(res);
  },

  getDownloadUrl(id: string) {
    return `${API_BASE}/releases/${id}/download`;
  },

  // Error Telemetry & Diagnostics
  async getSystemErrors(severity?: string, status?: string) {
    let query = '';
    const params: string[] = [];
    if (severity) params.push(`severity=${encodeURIComponent(severity)}`);
    if (status) params.push(`status=${encodeURIComponent(status)}`);
    if (params.length > 0) query = `?${params.join('&')}`;

    const res = await fetch(`${API_BASE}/admin/system/errors${query}`, {
      headers: getAuthHeaders()
    });
    return handleResponse<PageResponse<ErrorLogEntry>>(res);
  },

  async reportError(data: { severity?: string; message: string; stack?: string; source?: string; metadata?: any }) {
    const res = await fetch(`${API_BASE}/telemetry/errors`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<ErrorLogEntry>(res);
  },

  async resolveError(id: string) {
    const res = await fetch(`${API_BASE}/admin/system/errors/${id}/resolve`, {
      method: 'PATCH',
      headers: getAuthHeaders()
    });
    return handleResponse<ErrorLogEntry>(res);
  },

  // Chat & Real-Time Discussions
  async getChatMessages(channel?: string) {
    const q = channel ? `?channel=${encodeURIComponent(channel)}` : '';
    const res = await fetch(`${API_BASE}/chat/messages${q}`, {
      headers: getAuthHeaders()
    });
    return handleResponse<any[]>(res);
  },

  async sendChatMessage(data: { channel: string; content: string; messageType?: string; senderName?: string; senderEmail?: string; senderRole?: string }) {
    const res = await fetch(`${API_BASE}/chat/messages`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<any>(res);
  },

  async getChatGroups() {
    const res = await fetch(`${API_BASE}/chat/groups`, {
      headers: getAuthHeaders()
    });
    return handleResponse<any[]>(res);
  },

  async createChatGroup(data: { name: string; description?: string; channel: string; members?: string[] }) {
    const res = await fetch(`${API_BASE}/chat/groups`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<any>(res);
  },

  // FCM Push Notifications & Broadcasts
  async sendBroadcastNotification(data: { title: string; body: string; type?: string }) {
    const res = await fetch(`${API_BASE}/fcm/broadcast`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<{ success: boolean; message: string; results?: any }>(res);
  },

  async getTeamMembers() {
    const res = await fetch(`${API_BASE}/team`, {
      headers: getAuthHeaders()
    });
    return handleResponse<any[]>(res);
  },

  async sendHeartbeat(email?: string) {
    const userEmail = email || localStorage.getItem('projectflow_user_email') || 'admin@projectflow.io';
    const res = await fetch(`${API_BASE}/users/heartbeat`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ email: userEmail })
    });
    return handleResponse<{ success: boolean; online: boolean }>(res);
  }
};
