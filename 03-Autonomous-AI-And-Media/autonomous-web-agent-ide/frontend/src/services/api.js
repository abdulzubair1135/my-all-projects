const API_BASE = '/api';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    let errorMsg = `Request failed: ${response.statusText}`;
    try {
      const data = await response.json();
      if (data.error) errorMsg = data.error;
    } catch {}
    throw new Error(errorMsg);
  }

  return response.json();
}

export const api = {
  // Health
  getHealth: () => request('/health'),

  // Projects
  getProjects: () => request('/projects'),
  createProject: (name, prompt) => request('/projects', { method: 'POST', body: JSON.stringify({ name, prompt }) }),
  getProject: (id) => request(`/projects/${id}`),
  deleteProject: (id) => request(`/projects/${id}`, { method: 'DELETE' }),

  // Agent Controls
  getAgentStatus: () => request('/agent/status'),
  startAgent: (projectId, prompt, options = {}) => request('/agent/start', {
    method: 'POST',
    body: JSON.stringify({ projectId, prompt, ...options })
  }),
  pauseAgent: () => request('/agent/pause', { method: 'POST' }),
  resumeAgent: () => request('/agent/resume', { method: 'POST' }),
  stopAgent: () => request('/agent/stop', { method: 'POST' }),
  overrideAgent: (prompt) => request('/agent/override', { method: 'POST', body: JSON.stringify({ prompt }) }),

  // Tasks & Events
  getTasks: (projectId) => request(`/agent/tasks?projectId=${encodeURIComponent(projectId)}`),
  getEvents: (projectId, limit = 100) => request(`/agent/events?projectId=${encodeURIComponent(projectId)}&limit=${limit}`),
  getReplayEvents: (sinceEventId) => request(`/events/replay?sinceEventId=${encodeURIComponent(sinceEventId || '')}`),

  // Files
  getFileTree: (projectId) => request(`/files/tree?projectId=${encodeURIComponent(projectId)}`),
  getFileContent: (projectId, path) => request(`/files/content?projectId=${encodeURIComponent(projectId)}&path=${encodeURIComponent(path)}`),
  saveFile: (projectId, path, content, expectedHash) => request('/files/save', {
    method: 'POST',
    body: JSON.stringify({ projectId, path, content, expectedHash })
  }),
  createDirectory: (projectId, path) => request('/files/mkdir', {
    method: 'POST',
    body: JSON.stringify({ projectId, path })
  }),
  deleteFile: (projectId, path) => request(`/files/delete?projectId=${encodeURIComponent(projectId)}&path=${encodeURIComponent(path)}`, {
    method: 'DELETE',
    body: JSON.stringify({ projectId, path })
  }),
  searchFiles: (projectId, q) => request(`/files/search?projectId=${encodeURIComponent(projectId)}&q=${encodeURIComponent(q)}`),

  // Processes
  getProcesses: (projectId) => request(`/processes?projectId=${encodeURIComponent(projectId || '')}`),
  runCommand: (projectId, command, name) => request('/processes/run', {
    method: 'POST',
    body: JSON.stringify({ projectId, command, name })
  }),
  stopProcess: (id) => request(`/processes/${id}/stop`, { method: 'POST' }),

  // Approvals
  getApprovals: (projectId) => request(`/approvals?projectId=${encodeURIComponent(projectId || '')}`),
  approveAction: (id, alwaysAllow = false) => request(`/approvals/${id}/approve`, {
    method: 'POST',
    body: JSON.stringify({ alwaysAllow })
  }),
  rejectAction: (id) => request(`/approvals/${id}/reject`, { method: 'POST' }),

  // Settings
  getSettings: () => request('/settings'),
  updateSettings: (settings) => request('/settings', { method: 'POST', body: JSON.stringify(settings) }),

  // QA & Snapshots
  getSnapshots: (projectId) => request(`/snapshots/${encodeURIComponent(projectId)}`),
  runVisualQA: (projectId, url) => request('/qa/inspect', {
    method: 'POST',
    body: JSON.stringify({ projectId, url })
  }),
  scaffoldTests: (projectId) => request('/tests/scaffold', {
    method: 'POST',
    body: JSON.stringify({ projectId })
  }),

  // Android ADB
  getAndroidDevices: () => request('/android/devices'),
  takeAndroidScreenshot: (projectId, serial) => request('/android/screenshot', {
    method: 'POST',
    body: JSON.stringify({ projectId, serial })
  }),

  // Templates (Section 65)
  getTemplates: () => request('/templates'),
  instantiateTemplate: (templateId, projectName) => request('/templates/instantiate', {
    method: 'POST',
    body: JSON.stringify({ templateId, projectName })
  }),

  // Checkpoints & Rollback (Sections 50 & 51)
  getCheckpoints: (projectId) => request(`/checkpoints/${encodeURIComponent(projectId)}`),
  createCheckpoint: (projectId, description, stage) => request('/checkpoints/create', {
    method: 'POST',
    body: JSON.stringify({ projectId, description, stage })
  }),
  rollbackCheckpoint: (projectId, checkpointId) => request('/checkpoints/rollback', {
    method: 'POST',
    body: JSON.stringify({ projectId, checkpointId })
  })
};
