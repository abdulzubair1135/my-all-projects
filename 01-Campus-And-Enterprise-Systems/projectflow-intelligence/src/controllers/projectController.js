const { store, saveProjectToSupabase } = require('../supabase');
const { broadcastSystemNotification } = require('./notificationController');

function getAllProjects(req, res) {
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

  const mapped = (store.projects || []).map(p => {
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

async function updateProject(req, res) {
  const project = store.projects.find(p => p.id === req.params.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });
  const { name, description, status, health, targetDate, assigneeId, assigneeName, assigneeEmail, teamId, teamName } = req.body;
  if (name) project.name = name;
  if (description !== undefined) project.description = description;
  if (status) project.status = status;
  if (health) project.health = health;
  if (targetDate) project.targetDate = targetDate;

  let assignmentChanged = false;
  if (assigneeId !== undefined || assigneeEmail !== undefined) {
    assignmentChanged = true;
    const targetAssignee = assigneeId || assigneeEmail;
    if (!targetAssignee || targetAssignee === 'UNASSIGNED') {
      project.assigneeId = null;
      project.assigneeName = null;
      project.assigneeEmail = null;
      project.assignedEmails = [];
    } else {
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
  }

  if (teamId !== undefined || teamName !== undefined) {
    assignmentChanged = true;
    const targetTeam = teamId || teamName;
    if (!targetTeam || targetTeam === 'UNASSIGNED') {
      project.teamId = null;
      project.teamName = null;
    } else {
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
  }

  project.updatedAt = new Date().toISOString();
  saveProjectToSupabase(project);

  if (assignmentChanged) {
    const callerEmail = (req.headers['x-user-email'] || (req.user && req.user.email) || '').trim().toLowerCase();
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
    }
  } else {
    await broadcastSystemNotification({
      title: '📊 Project Updated',
      message: `Project "${project.name}" status: ${project.status || 'ACTIVE'}, health: ${project.health || 'ON_TRACK'}`,
      type: 'PROJECT_UPDATED',
      priority: 'NORMAL'
    });
  }

  res.json(project);
}

module.exports = {
  getAllProjects,
  updateProject
};
