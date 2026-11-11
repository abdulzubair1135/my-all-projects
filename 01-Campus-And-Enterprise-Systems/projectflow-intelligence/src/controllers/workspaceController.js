const { v4: uuidv4 } = require('uuid');
const { store, saveWorkspaceToSupabase, saveProjectToSupabase } = require('../supabase');
const { broadcastSystemNotification } = require('./notificationController');

function getWorkspaces(req, res) {
  res.json(store.workspaces);
}

function createWorkspace(req, res) {
  const { name, slug, description } = req.body;
  const ws = {
    id: uuidv4(),
    name: name || 'Default Workspace',
    slug: slug || 'default-ws',
    description: description || '',
    ownerId: store.users[0] ? store.users[0].id : uuidv4(),
    archived: false,
    createdAt: new Date().toISOString()
  };
  store.workspaces.push(ws);
  saveWorkspaceToSupabase(ws);
  res.status(201).json(ws);
}

function getWorkspaceProjects(req, res) {
  const reqEmail = (req.headers['x-user-email'] || req.query.userEmail || (req.user && req.user.email) || '').trim().toLowerCase();
  const reqRole = (req.headers['x-user-role'] || (req.user && req.user.role) || '').toUpperCase();
  const clientPlatform = (req.headers['x-client-platform'] || '').toLowerCase();
  const matchedUser = reqEmail ? (store.users || []).find(u => u.email?.toLowerCase() === reqEmail) : null;
  const reqUserId = req.headers['x-user-id'] || req.query.userId || (matchedUser ? matchedUser.id : (req.user && req.user.id));

  const userTeams = reqEmail
    ? (store.teams || []).filter(t => Array.isArray(t.members) && t.members.some(m => m.toLowerCase() === reqEmail))
    : [];
  const userTeamIds = userTeams.map(t => t.id);
  const userTeamNames = userTeams.map(t => t.name.toLowerCase());

  const rawList = store.projects.filter(p => !req.params.id || p.workspaceId === req.params.id);
  const mapped = rawList.map(p => {
    const user = p.assigneeId ? (store.users || []).find(u => u.id === p.assigneeId) : null;
    const team = p.teamId ? (store.teams || []).find(t => t.id === p.teamId || t.slug === p.teamId || (p.teamName && t.name.toLowerCase() === p.teamName.toLowerCase())) : null;
    const projectTasks = (store.tasks || []).filter(t => t.projectId === p.id);
    const total = projectTasks.length;
    const completed = projectTasks.filter(t => t.statusCategory === 'DONE' || t.progressPercent === 100).length;
    const progressPercent = (total > 0) ? Math.round((completed * 100) / total) : 0;
    return {
      ...p,
      progressPercent,
      assigneeName: user ? user.fullName : (p.assigneeName || null),
      assigneeEmail: user ? user.email : (p.assigneeEmail || null),
      teamName: team ? team.name : (p.teamName || null)
    };
  });

  const isStrictClient = clientPlatform === 'android' || reqRole === 'MEMBER' || req.query.assignedOnly === 'true' || req.query.my === 'true';
  if (isStrictClient && reqEmail) {
    const filtered = mapped.filter(p => {
      const assignedToOtherUser = p.assigneeEmail && p.assigneeEmail.toLowerCase() !== reqEmail;
      const assignedToOtherTeam = p.teamName && !userTeamNames.includes(p.teamName.toLowerCase()) && !userTeamIds.includes(p.teamId);

      // If explicitly assigned to someone else, reject
      if (assignedToOtherUser) return false;
      // If explicitly assigned to another team, reject
      if (assignedToOtherTeam) return false;

      // 0. Created by this user
      if (p.creatorEmail && p.creatorEmail.toLowerCase() === reqEmail) return true;

      // 1. Assigned to this user directly
      if (p.assigneeId && reqUserId && p.assigneeId === reqUserId) return true;
      if (p.assigneeEmail && p.assigneeEmail.toLowerCase() === reqEmail) return true;
      if (Array.isArray(p.assignedEmails) && p.assignedEmails.some(e => e.toLowerCase() === reqEmail)) return true;
      if (matchedUser && p.assigneeName && p.assigneeName.toLowerCase() === matchedUser.fullName?.toLowerCase()) return true;

      // 2. Assigned to this user's team / squad
      if ((p.teamId && userTeamIds.includes(p.teamId)) || (p.teamName && userTeamNames.includes(p.teamName.toLowerCase()))) return true;

      // 3. Unassigned / General project -> only include if creatorEmail === reqEmail
      if (!p.assigneeId && !p.assigneeEmail && !p.teamId && !p.teamName) {
        return Boolean(p.creatorEmail && p.creatorEmail.toLowerCase() === reqEmail);
      }

      return false;
    });
    return res.json(filtered);
  }

  res.json(mapped);
}

async function createWorkspaceProject(req, res) {
  const { name, code, description, assigneeId, assigneeName, assigneeEmail, teamId, teamName, status, targetDate } = req.body;
  const callerEmail = (req.headers['x-user-email'] || (req.user && req.user.email) || '').trim().toLowerCase();
  const callerUser = callerEmail ? (store.users || []).find(u => u.email?.toLowerCase() === callerEmail) : (store.users && store.users[0]);

  const defaultWsId = (store.workspaces && store.workspaces[0]) ? store.workspaces[0].id : '00000000-0000-0000-0000-000000000001';
  const targetWsId = req.params.id || req.body.workspaceId || defaultWsId;

  const project = {
    id: uuidv4(),
    workspaceId: targetWsId,
    name: name || 'New Project',
    code: code || 'PRJ-' + Math.floor(100 + Math.random() * 900),
    description: description || '',
    status: status || 'PLANNING',
    health: 'ON_TRACK',
    assigneeId: null,
    assigneeName: null,
    assigneeEmail: null,
    creatorEmail: callerEmail || (callerUser ? callerUser.email : 'admin@projectflow.io'),
    teamId: null,
    teamName: null,
    assignedEmails: [],
    startDate: new Date().toISOString().split('T')[0],
    targetDate: targetDate || new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
    createdAt: new Date().toISOString()
  };

  const targetAssignee = assigneeId || assigneeEmail;
  if (targetAssignee && targetAssignee !== 'UNASSIGNED') {
    const u = (store.users || []).find(usr => usr.id === targetAssignee || (usr.email && usr.email.toLowerCase() === targetAssignee.toLowerCase()));
    if (u) {
      project.assigneeId = u.id;
      project.assigneeName = u.fullName;
      project.assigneeEmail = u.email;
      project.assignedEmails = [u.email];
    } else {
      project.assigneeId = assigneeId || null;
      project.assigneeName = assigneeName || null;
      project.assigneeEmail = assigneeEmail || null;
    }
  }

  const targetTeam = teamId || teamName;
  if (targetTeam && targetTeam !== 'UNASSIGNED') {
    const tm = (store.teams || []).find(t => t.id === targetTeam || t.slug === targetTeam || (teamName && t.name.toLowerCase() === teamName.toLowerCase()));
    if (tm) {
      project.teamId = tm.id;
      project.teamName = tm.name;
      if (Array.isArray(tm.members)) {
        project.assignedEmails = tm.members;
      }
    } else {
      project.teamId = teamId || null;
      project.teamName = teamName || null;
    }
  }

  // If completely unassigned, default assign to the creator so they can see and manage it
  if (!project.assigneeId && !project.assigneeEmail && !project.teamId && !project.teamName && callerUser) {
    project.assigneeId = callerUser.id;
    project.assigneeName = callerUser.fullName;
    project.assigneeEmail = callerUser.email;
    project.assignedEmails = [callerUser.email];
  }

  store.projects.push(project);
  saveProjectToSupabase(project);

  const targetLabel = project.assigneeName || (project.teamName ? `Team "${project.teamName}"` : null);

  if (targetLabel) {
    await broadcastSystemNotification({
      title: '📂 Project Assigned',
      message: `${targetLabel} was assigned project: "${project.name}" (${project.code})`,
      type: 'PROJECT_ASSIGNED',
      targetEmail: project.assigneeEmail,
      targetEmails: project.assignedEmails || [],
      userId: project.assigneeId,
      senderEmail: callerEmail,
      priority: 'HIGH'
    });
  } else {
    await broadcastSystemNotification({
      title: '🚀 New Project Created',
      message: `Project "${project.name}" (${project.code}) was created by Administrator.`,
      type: 'PROJECT_CREATED',
      priority: 'HIGH'
    });
  }

  res.status(201).json(project);
}

module.exports = {
  getWorkspaces,
  createWorkspace,
  getWorkspaceProjects,
  createWorkspaceProject
};
