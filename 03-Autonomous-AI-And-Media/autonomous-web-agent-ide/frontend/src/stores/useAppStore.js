import { create } from 'zustand';
import { api } from '../services/api';
import { wsClient } from '../services/websocket';

export const useAppStore = create((set, get) => ({
  // Health & Connection
  isConnected: false,
  health: {
    backend: false,
    agentBridge: { status: 'IDLE' },
    browser: true,
    llm: true,
    workspace: true
  },

  // Projects
  projects: [],
  activeProject: null,

  // Tasks & Graph
  tasks: [],
  dependencies: [],

  // Files & Editor
  fileTree: [],
  openTabs: [],
  activeTab: null,

  // Terminal & Processes
  terminalLogs: [],
  processes: [],

  // Agent State
  agentStatus: 'IDLE',
  approvalMode: 'SAFE',
  activeRunId: null,
  pendingApprovals: [],
  qualityScore: 100,
  scoreDelta: 0,
  activeRole: 'Multi-Agent Team',
  previewUrl: 'http://localhost:5174',
  previewPort: 5174,

  // UI Modals & Panels
  isCommandPaletteOpen: false,
  isFileSearchOpen: false,
  isTemplateGalleryOpen: false,
  isProjectWizardOpen: false,
  activeSidebarTab: 'tasks', // 'tasks', 'files', 'processes', 'qa', 'evolution'

  // Actions
  setConnectionStatus: (connected) => set({ isConnected: connected }),
  setSidebarTab: (tab) => set({ activeSidebarTab: tab }),
  setCommandPaletteOpen: (open) => set({ isCommandPaletteOpen: open }),
  setFileSearchOpen: (open) => set({ isFileSearchOpen: open }),
  setTemplateGalleryOpen: (open) => set({ isTemplateGalleryOpen: open }),
  setProjectWizardOpen: (open) => set({ isProjectWizardOpen: open }),

  fetchHealth: async () => {
    try {
      const data = await api.getHealth();
      set({
        health: {
          backend: true,
          agentBridge: data.agentBridge || { status: 'IDLE' },
          browser: true,
          llm: true,
          workspace: true
        }
      });
    } catch {
      set((state) => ({ health: { ...state.health, backend: false } }));
    }
  },

  loadProjects: async () => {
    try {
      const list = await api.getProjects();
      set({ projects: list });
      if (list.length > 0 && !get().activeProject) {
        get().selectProject(list[0].id);
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
    }
  },

  createProject: async (name, prompt) => {
    const project = await api.createProject(name, prompt);
    set((state) => ({ projects: [project, ...state.projects] }));
    await get().selectProject(project.id);
    return project;
  },

  selectProject: async (projectId) => {
    try {
      const project = await api.getProject(projectId);
      set({ activeProject: project });
      await Promise.all([
        get().refreshFileTree(),
        get().refreshTasks(),
        get().refreshProcesses(),
        get().refreshApprovals()
      ]);
    } catch (err) {
      console.error('Failed to select project:', err);
    }
  },

  refreshFileTree: async () => {
    const { activeProject } = get();
    if (!activeProject) return;
    try {
      const tree = await api.getFileTree(activeProject.id);
      set({ fileTree: tree });
    } catch (err) {
      console.error('Failed to load file tree:', err);
    }
  },

  openFile: async (rawFilePath) => {
    if (!rawFilePath) return;
    const filePath = rawFilePath.replace(/\\/g, '/');

    let { activeProject, openTabs, projects } = get();
    if (!activeProject) {
      if (projects && projects.length > 0) {
        activeProject = projects[0];
        set({ activeProject });
      } else {
        try {
          const list = await api.getProjects();
          if (list && list.length > 0) {
            activeProject = list[0];
            set({ projects: list, activeProject });
          }
        } catch {}
      }
    }

    // Check if already open
    const existing = openTabs.find((t) => t.path.replace(/\\/g, '/') === filePath);
    if (existing) {
      set({ activeTab: existing.path });
      return;
    }

    const name = filePath.split('/').pop() || filePath;
    const optimisticTab = {
      path: filePath,
      name,
      content: '// Loading file content...',
      hash: '',
      isDirty: false,
      isLoading: true
    };

    // Immediately open tab for responsive instant feedback
    set({
      openTabs: [...openTabs, optimisticTab],
      activeTab: filePath
    });

    try {
      const projId = activeProject ? (activeProject.id || activeProject.name) : 'school';
      const fileData = await api.getFileContent(projId, filePath);
      set((state) => ({
        openTabs: state.openTabs.map((t) =>
          t.path === filePath
            ? { ...t, content: fileData.content, originalContent: fileData.content, hash: fileData.hash, isLoading: false }
            : t
        )
      }));
    } catch (err) {
      console.error('Failed to open file:', err);
      set((state) => ({
        openTabs: state.openTabs.map((t) =>
          t.path === filePath
            ? { ...t, content: `// Error loading file: ${err.message}\n// Path: ${filePath}`, isLoading: false }
            : t
        )
      }));
    }
  },

  closeTab: (filePath) => {
    const { openTabs, activeTab } = get();
    const newTabs = openTabs.filter((t) => t.path !== filePath);
    let newActive = activeTab;
    if (activeTab === filePath) {
      newActive = newTabs.length > 0 ? newTabs[newTabs.length - 1].path : null;
    }
    set({ openTabs: newTabs, activeTab: newActive });
  },

  updateTabContent: (filePath, newContent) => {
    const { openTabs } = get();
    set({
      openTabs: openTabs.map((tab) =>
        tab.path === filePath ? { ...tab, content: newContent, isDirty: true } : tab
      )
    });
  },

  saveCurrentFile: async () => {
    const { activeProject, openTabs, activeTab } = get();
    if (!activeProject || !activeTab) return;

    const tab = openTabs.find((t) => t.path === activeTab);
    if (!tab) return;

    try {
      const saved = await api.saveFile(activeProject.id, tab.path, tab.content, tab.hash);
      set({
        openTabs: openTabs.map((t) =>
          t.path === activeTab ? { ...t, hash: saved.hash, originalContent: tab.content, isDirty: false } : t
        )
      });
      get().refreshFileTree();
    } catch (err) {
      alert(`Save error: ${err.message}`);
    }
  },

  refreshTasks: async () => {
    const { activeProject } = get();
    if (!activeProject) return;
    try {
      const data = await api.getTasks(activeProject.id);
      set({ tasks: data.tasks || [], dependencies: data.dependencies || [] });
    } catch (err) {
      console.error('Failed to load tasks:', err);
    }
  },

  refreshProcesses: async () => {
    const { activeProject } = get();
    if (!activeProject) return;
    try {
      const list = await api.getProcesses(activeProject.id);
      set({ processes: list });
    } catch (err) {
      console.error('Failed to load processes:', err);
    }
  },

  refreshApprovals: async () => {
    const { activeProject } = get();
    if (!activeProject) return;
    try {
      const list = await api.getApprovals(activeProject.id);
      set({ pendingApprovals: list });
    } catch (err) {
      console.error('Failed to load approvals:', err);
    }
  },

  selectedProvider: (() => {
    try {
      return localStorage.getItem('agent_selected_provider') || 'deepseek_web';
    } catch {
      return 'deepseek_web';
    }
  })(),
  setProvider: (prov) => {
    try {
      localStorage.setItem('agent_selected_provider', prov);
    } catch {}
    set({ selectedProvider: prov });
  },

  startAgent: async (prompt, options = {}) => {
    let { activeProject, approvalMode, selectedProvider, projects, createProject, selectProject } = get();
    const { imagePaths = [], zipFile = null } = options;

    if (!activeProject) {
      if (projects && projects.length > 0) {
        await selectProject(projects[0].id);
        activeProject = get().activeProject;
      } else {
        const projectName = prompt.slice(0, 20).replace(/[^a-zA-Z0-9]/g, '_').toLowerCase() || 'my_app';
        activeProject = await createProject(projectName, prompt);
      }
    }
    if (!activeProject) return;

    try {
      set({ agentStatus: 'RUNNING', terminalLogs: [] });
      const res = await api.startAgent(activeProject.id, prompt, {
        approvalMode,
        provider: selectedProvider || 'deepseek_web',
        imagePaths,
        zipFile,
      });
      set({ activeRunId: res.runId });
    } catch (err) {
      set({ agentStatus: 'FAILED' });
      alert(`Start failed: ${err.message}`);
    }
  },

  pauseAgent: async () => {
    await api.pauseAgent();
    set({ agentStatus: 'PAUSED' });
  },

  resumeAgent: async () => {
    await api.resumeAgent();
    set({ agentStatus: 'RUNNING' });
  },

  stopAgent: async () => {
    await api.stopAgent();
    set({ agentStatus: 'STOPPED' });
  },

  overrideAgent: async (prompt) => {
    await api.overrideAgent(prompt);
  },

  handleApproval: async (approvalId, allow, always = false) => {
    try {
      if (allow) {
        await api.approveAction(approvalId, always);
      } else {
        await api.rejectAction(approvalId);
      }
      set((state) => ({
        pendingApprovals: state.pendingApprovals.filter((a) => a.id !== approvalId)
      }));
    } catch (err) {
      alert(`Approval error: ${err.message}`);
    }
  },

  appendTerminalLog: (log) => {
    set((state) => ({
      terminalLogs: [...state.terminalLogs.slice(-1000), log]
    }));
  },

  clearTerminal: () => {
    set({ terminalLogs: [] });
  },

  _wsListenersInitialized: false,

  initWebSocketListeners: () => {
    if (get()._wsListenersInitialized) return;
    set({ _wsListenersInitialized: true });

    wsClient.on('connection.state', ({ connected }) => {
      get().setConnectionStatus(connected);
      if (connected) get().fetchHealth();
    });

    wsClient.on('command.output', (data) => {
      const payload = data.payload || data;
      get().appendTerminalLog(payload);
    });

    wsClient.on('task.created', () => get().refreshTasks());
    wsClient.on('task.started', () => get().refreshTasks());
    wsClient.on('task.completed', () => get().refreshTasks());
    wsClient.on('task.failed', () => get().refreshTasks());

    wsClient.on('file.created', () => get().refreshFileTree());
    wsClient.on('file.modified', (data) => {
      const payload = data.payload || data;
      get().refreshFileTree();
      // If the modified file is open in editor and NOT dirty, reload it
      const { openTabs, activeProject } = get();
      const openTab = openTabs.find((t) => t.path === payload.path);
      if (openTab && !openTab.isDirty && activeProject) {
        api.getFileContent(activeProject.id, payload.path).then((fileData) => {
          set((state) => ({
            openTabs: state.openTabs.map((t) =>
              t.path === payload.path ? { ...t, content: fileData.content, hash: fileData.hash } : t
            )
          }));
        });
      }
    });
    wsClient.on('file.deleted', () => get().refreshFileTree());

    wsClient.on('process.started', () => get().refreshProcesses());
    wsClient.on('process.stopped', () => get().refreshProcesses());
    wsClient.on('process.crashed', () => get().refreshProcesses());

    wsClient.on('approval.required', () => get().refreshApprovals());
    wsClient.on('approval.granted', () => get().refreshApprovals());
    wsClient.on('approval.rejected', () => get().refreshApprovals());

    wsClient.on('agent.started', () => set({ agentStatus: 'RUNNING' }));
    wsClient.on('agent.paused', () => set({ agentStatus: 'PAUSED' }));
    wsClient.on('agent.resumed', () => set({ agentStatus: 'RUNNING' }));
    wsClient.on('agent.stopped', () => set({ agentStatus: 'STOPPED' }));
    wsClient.on('agent.completed', () => set({ agentStatus: 'COMPLETED' }));
    wsClient.on('agent.error', () => set({ agentStatus: 'FAILED' }));

    wsClient.on('score.updated', (data) => {
      const p = data.payload || data;
      set({ qualityScore: p.score, scoreDelta: p.delta });
    });
    wsClient.on('agent.role.started', (data) => {
      const p = data.payload || data;
      set({ activeRole: p.role });
    });
    wsClient.on('preview.open', (data) => {
      const p = data.payload || data;
      if (p.url) {
        set({ previewUrl: p.url, previewPort: p.port || 5174 });
      }
    });

    // Autonomous Web-Agent IDE: Mission events
    wsClient.on('mission.created', (data) => {
      const p = data.payload || data;
      set({ currentMission: p });
    });

    wsClient.on('project.inspected', (data) => {
      const p = data.payload || data;
      set({ projectInfo: p });
    });

    wsClient.on('artifact.created', (data) => {
      const p = data.payload || data;
      set((state) => ({
        artifacts: [...(state.artifacts || []), p],
      }));
    });

    // File tree changed (after ZIP import)
    wsClient.on('file.tree.changed', () => get().refreshFileTree());

    wsClient.connect();
  }
}));
