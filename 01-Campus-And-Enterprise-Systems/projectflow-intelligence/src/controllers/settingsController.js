const { store } = require('../supabase');
const { recordAuditLog } = require('../middleware/auditLogger');

function getSettings(req, res) {
  res.json(store.settings);
}

function updateSettings(req, res) {
  store.settings = {
    ...store.settings,
    ...req.body,
    updatedAt: new Date().toISOString()
  };
  recordAuditLog('SETTINGS_UPDATED', 'CONFIGURATION', 'global', req.headers['x-user-email'] || 'admin@projectflow.io', req.body);
  res.json(store.settings);
}

function getReportsSummary(req, res) {
  const totalTasks = store.tasks.length;
  const completedTasks = store.tasks.filter(t => t.statusCategory === 'DONE').length;
  const inProgressTasks = store.tasks.filter(t => t.statusCategory === 'IN_PROGRESS').length;
  const todoTasks = store.tasks.filter(t => t.statusCategory === 'TODO').length;
  const overdueTasks = store.tasks.filter(t => !t.completedAt && t.dueDate && new Date(t.dueDate) < new Date()).length;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const totalProjects = store.projects.length;
  const activeProjects = store.projects.filter(p => p.status !== 'COMPLETED').length;

  res.json({
    totalTasks,
    completedTasks,
    inProgressTasks,
    todoTasks,
    overdueTasks,
    completionRate,
    totalProjects,
    activeProjects,
    statusDistribution: {
      TODO: todoTasks,
      IN_PROGRESS: inProgressTasks,
      DONE: completedTasks
    },
    generatedAt: new Date().toISOString()
  });
}

function getAdminOverview(req, res) {
  res.json({
    totalUsers: store.users.length,
    totalWorkspaces: store.workspaces.length,
    totalProjects: store.projects.length,
    totalTasks: store.tasks.length,
    activeRisksCount: store.tasks.filter(t => !t.completedAt && t.dueDate && new Date(t.dueDate) < new Date()).length,
    systemStatus: 'ONLINE (Node.js + Supabase)'
  });
}

module.exports = {
  getSettings,
  updateSettings,
  getReportsSummary,
  getAdminOverview
};
