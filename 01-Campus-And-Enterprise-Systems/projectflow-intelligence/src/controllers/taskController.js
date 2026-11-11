const { v4: uuidv4 } = require('uuid');
const { store, supabase, saveTaskToSupabase } = require('../supabase');
const { broadcastSystemNotification } = require('./notificationController');

function getAllTasks(req, res) {
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

  let list = store.tasks;
  if (req.query.projectId) list = list.filter(t => t.projectId === req.query.projectId);
  if (req.query.assigneeId) list = list.filter(t => t.assigneeId === req.query.assigneeId);
  if (req.query.teamId) list = list.filter(t => t.teamId === req.query.teamId);

  const mapped = list.map(t => {
    const user = t.assigneeId ? store.users.find(u => u.id === t.assigneeId) : null;
    const team = t.teamId ? (store.teams || []).find(tm => tm.id === t.teamId || tm.slug === t.teamId || (t.teamName && tm.name.toLowerCase() === t.teamName.toLowerCase())) : null;
    return {
      ...t,
      assigneeName: user ? user.fullName : (t.assigneeName || null),
      assigneeEmail: user ? user.email : (t.assigneeEmail || null),
      teamName: team ? team.name : (t.teamName || null)
    };
  });

  const isStrictClient = clientPlatform === 'android' || reqRole === 'MEMBER' || req.query.assignedOnly === 'true' || req.query.my === 'true';
  if (isStrictClient && reqEmail) {
    const filtered = mapped.filter(t => {
      const assignedToOtherUser = t.assigneeEmail && t.assigneeEmail.toLowerCase() !== reqEmail;
      const assignedToOtherTeam = t.teamName && !userTeamNames.includes(t.teamName.toLowerCase()) && !userTeamIds.includes(t.teamId);

      // If explicitly assigned to someone else, reject
      if (assignedToOtherUser) return false;
      // If explicitly assigned to another squad, reject
      if (assignedToOtherTeam) return false;

      // 1. Assigned to this user directly
      if (t.assigneeId && reqUserId && t.assigneeId === reqUserId) return true;
      if (t.assigneeEmail && t.assigneeEmail.toLowerCase() === reqEmail) return true;
      if (matchedUser && t.assigneeName && t.assigneeName.toLowerCase() === matchedUser.fullName?.toLowerCase()) return true;

      // 2. Assigned to this user's team / squad
      if ((t.teamId && userTeamIds.includes(t.teamId)) || (t.teamName && userTeamNames.includes(t.teamName.toLowerCase()))) return true;

      // 3. Unassigned / General task -> only include if creatorEmail === reqEmail
      if (!t.assigneeId && !t.assigneeEmail && !t.teamId && !t.teamName) {
        return Boolean(t.creatorEmail && t.creatorEmail.toLowerCase() === reqEmail);
      }

      return false;
    });
    return res.json(filtered);
  }

  res.json(mapped);
}

async function getProjectTasks(req, res) {
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

  if (supabase) {
    try {
      const { data: dbTasks, error } = await supabase.from('tasks').select('*').eq('project_id', req.params.id);
      if (!error && dbTasks) {
        dbTasks.forEach(dt => {
          const idx = store.tasks.findIndex(t => t.id === dt.id);
          let rawDesc = dt.description || '';
          let teamId = null, teamName = null, assigneeName = null, assigneeEmail = null;
          if (rawDesc.includes('<!--PF_TASK:')) {
            const m = rawDesc.match(/<!--PF_TASK:(.*?)-->/);
            if (m && m[1]) {
              const tokens = m[1].split(':');
              tokens.forEach(tok => {
                const eq = tok.indexOf('=');
                if (eq > 0) {
                  const k = tok.slice(0, eq);
                  const v = tok.slice(eq + 1);
                  if (k === 'teamId') teamId = v;
                  if (k === 'teamName') teamName = v;
                  if (k === 'assigneeName') assigneeName = v;
                  if (k === 'assigneeEmail') assigneeEmail = v;
                }
              });
            }
            rawDesc = rawDesc.replace(/<!--PF_TASK:[^>]*-->/g, '').trim();
          }

          const mapped = {
            id: dt.id,
            projectId: dt.project_id,
            title: dt.title,
            description: rawDesc,
            priority: dt.priority,
            statusCategory: dt.status_category,
            progressPercent: dt.progress_percent,
            completedAt: dt.completed_at,
            dueDate: dt.due_date,
            assigneeId: dt.assignee_id,
            teamId,
            teamName,
            assigneeName,
            assigneeEmail,
            createdAt: dt.created_at
          };
          if (idx >= 0) store.tasks[idx] = { ...store.tasks[idx], ...mapped };
          else store.tasks.push(mapped);
        });
      }
    } catch (e) {}
  }

  const rawList = store.tasks.filter(t => t.projectId === req.params.id);
  const mapped = rawList.map(t => {
    const user = t.assigneeId ? store.users.find(u => u.id === t.assigneeId) : null;
    const team = t.teamId ? (store.teams || []).find(tm => tm.id === t.teamId || tm.slug === t.teamId || (t.teamName && tm.name.toLowerCase() === t.teamName.toLowerCase())) : null;
    return {
      ...t,
      assigneeName: user ? user.fullName : (t.assigneeName || null),
      assigneeEmail: user ? user.email : (t.assigneeEmail || null),
      teamName: team ? team.name : (t.teamName || null)
    };
  });

  const isStrictClient = clientPlatform === 'android' || reqRole === 'MEMBER' || req.query.assignedOnly === 'true' || req.query.my === 'true';
  if (isStrictClient && reqEmail) {
    const filtered = mapped.filter(t => {
      const assignedToOtherUser = t.assigneeEmail && t.assigneeEmail.toLowerCase() !== reqEmail;
      const assignedToOtherTeam = t.teamName && !userTeamNames.includes(t.teamName.toLowerCase()) && !userTeamIds.includes(t.teamId);

      // If explicitly assigned to someone else, reject
      if (assignedToOtherUser) return false;
      // If explicitly assigned to another squad, reject
      if (assignedToOtherTeam) return false;

      // 0. Created by this user
      if (t.creatorEmail && t.creatorEmail.toLowerCase() === reqEmail) return true;

      // 1. Assigned to this user directly
      if (t.assigneeId && reqUserId && t.assigneeId === reqUserId) return true;
      if (t.assigneeEmail && t.assigneeEmail.toLowerCase() === reqEmail) return true;
      if (matchedUser && t.assigneeName && t.assigneeName.toLowerCase() === matchedUser.fullName?.toLowerCase()) return true;

      // 2. Assigned to this user's team / squad
      if ((t.teamId && userTeamIds.includes(t.teamId)) || (t.teamName && userTeamNames.includes(t.teamName.toLowerCase()))) return true;

      // 3. Unassigned / General task -> only include if creatorEmail === reqEmail
      if (!t.assigneeId && !t.assigneeEmail && !t.teamId && !t.teamName) {
        return Boolean(t.creatorEmail && t.creatorEmail.toLowerCase() === reqEmail);
      }

      return false;
    });
    return res.json(filtered);
  }

  res.json(mapped);
}

async function createTask(req, res) {
  const { title, description, priority, dueDate, assigneeId: reqAssigneeId, teamId: reqTeamId, teamName: reqTeamName, assigneeName: reqAssigneeName, assigneeEmail: reqAssigneeEmail } = req.body;
  const callerEmail = (req.headers['x-user-email'] || (req.user && req.user.email) || '').trim().toLowerCase();
  const callerUser = callerEmail ? (store.users || []).find(u => u.email?.toLowerCase() === callerEmail) : (store.users && store.users[0]);

  let assigneeId = reqAssigneeId || null;
  let assigneeEmail = reqAssigneeEmail || null;
  let assigneeName = reqAssigneeName || null;
  let teamId = reqTeamId || null;
  let teamName = reqTeamName || null;

  // Resolve user by ID or email
  let user = assigneeId ? store.users.find(u => u.id === assigneeId) : null;
  if (!user && assigneeEmail) {
    user = store.users.find(u => u.email?.toLowerCase() === assigneeEmail.toLowerCase());
  }
  if (user) {
    assigneeId = user.id;
    assigneeEmail = user.email;
    assigneeName = user.fullName;
  }

  // Resolve team
  const team = (teamId || teamName) ? (store.teams || []).find(tm => tm.id === teamId || tm.slug === teamId || (teamName && tm.name.toLowerCase() === teamName.toLowerCase())) : null;
  if (team) {
    teamId = team.id;
    teamName = team.name;
  }

  // If completely unassigned, default assign to creator so they can see and manage it
  if (!assigneeId && !assigneeEmail && !teamId && !teamName && callerUser) {
    assigneeId = callerUser.id;
    assigneeName = callerUser.fullName;
    assigneeEmail = callerUser.email;
  }

  const defaultProjectId = (store.projects && store.projects[0]) ? store.projects[0].id : '10000000-0000-0000-0000-000000000001';
  const targetProjectId = req.params.id || req.body.projectId || defaultProjectId;

  const task = {
    id: uuidv4(),
    projectId: targetProjectId,
    title: title || 'New Task',
    description: description || '',
    priority: priority || 'MEDIUM',
    statusCategory: 'TODO',
    progressPercent: 0,
    dueDate: dueDate ? dueDate.split('T')[0] : null,
    assigneeId: assigneeId || null,
    assigneeName: assigneeName || null,
    assigneeEmail: assigneeEmail || null,
    creatorEmail: callerEmail || (callerUser ? callerUser.email : 'admin@projectflow.io'),
    teamId: teamId || null,
    teamName: teamName || null,
    createdAt: new Date().toISOString()
  };
  store.tasks.push(task);
  saveTaskToSupabase(task);

  let targetUserId = null;
  let targetEmail = null;
  let targetEmails = [];

  const targetAssignee = assigneeId || assigneeEmail;
  if (targetAssignee) {
    const u = store.users.find(usr => usr.id === targetAssignee || (usr.email && usr.email.toLowerCase() === targetAssignee.toLowerCase()) || (usr.fullName && assigneeName && usr.fullName.toLowerCase() === assigneeName.toLowerCase()));
    if (u) {
      targetUserId = u.id;
      targetEmail = u.email;
      targetEmails = [u.email];
    } else if (targetAssignee.includes('@')) {
      targetEmail = targetAssignee.toLowerCase();
      targetEmails = [targetAssignee.toLowerCase()];
    }
  } else if (teamId || teamName) {
    const tm = (store.teams || []).find(t => t.id === teamId || t.slug === teamId || (teamName && t.name.toLowerCase() === teamName.toLowerCase()));
    if (tm && Array.isArray(tm.members) && tm.members.length > 0) {
      targetEmails = tm.members;
    }
  }

  const targetLabel = assigneeName || (teamName ? `Team "${teamName}"` : 'Team');
  await broadcastSystemNotification({
    title: '📋 New Task Assigned',
    message: `${targetLabel} received task: "${task.title}" (Priority: ${task.priority})`,
    type: 'TASK_ASSIGNED',
    taskId: task.id,
    targetEmail: targetEmail,
    targetEmails: targetEmails,
    userId: targetUserId,
    senderEmail: callerEmail,
    priority: task.priority === 'HIGH' ? 'HIGH' : 'NORMAL'
  });

  res.status(201).json(task);
}

async function updateTask(req, res) {
  const task = store.tasks.find(t => t.id === req.params.id);
  if (!task) return res.status(404).json({ error: 'Task not found' });
  const { title, description, priority, dueDate, assigneeId, teamId, teamName, assigneeName, statusCategory, progressPercent } = req.body;
  if (title) task.title = title;
  if (description !== undefined) task.description = description;
  if (priority) task.priority = priority;
  if (dueDate) task.dueDate = dueDate.split('T')[0];
  if (statusCategory) {
    task.statusCategory = statusCategory;
    if (statusCategory === 'DONE') {
      task.progressPercent = 100;
      task.completedAt = new Date().toISOString();
    } else if (progressPercent !== undefined) {
      task.progressPercent = progressPercent;
    }
  }

  let assigneeChanged = false;
  if (assigneeId !== undefined) {
    assigneeChanged = true;
    task.assigneeId = assigneeId || null;
    const user = assigneeId ? store.users.find(u => u.id === assigneeId) : null;
    task.assigneeName = user ? user.fullName : (assigneeName || null);
  }
  if (teamId !== undefined) {
    assigneeChanged = true;
    task.teamId = teamId || null;
    const team = teamId ? (store.teams || []).find(tm => tm.id === teamId) : null;
    task.teamName = team ? team.name : (teamName || null);
  }

  saveTaskToSupabase(task);

  if (assigneeChanged) {
    const callerEmail = (req.headers['x-user-email'] || (req.user && req.user.email) || '').trim().toLowerCase();
    const targetLabel = task.assigneeName || (task.teamName ? `Team "${task.teamName}"` : null);
    if (targetLabel) {
      let targetUserId = null;
      let targetEmail = null;
      let targetEmails = [];
      const targetAssignee = task.assigneeId || req.body.assigneeEmail;
      if (targetAssignee) {
        const u = store.users.find(usr => usr.id === targetAssignee || (usr.email && usr.email.toLowerCase() === targetAssignee.toLowerCase()) || (usr.fullName && task.assigneeName && usr.fullName.toLowerCase() === task.assigneeName.toLowerCase()));
        if (u) {
          targetUserId = u.id;
          targetEmail = u.email;
          targetEmails = [u.email];
        } else if (targetAssignee.includes('@')) {
          targetEmail = targetAssignee.toLowerCase();
          targetEmails = [targetAssignee.toLowerCase()];
        }
      } else if (task.teamId || task.teamName) {
        const tm = (store.teams || []).find(t => t.id === task.teamId || t.slug === task.teamId || (task.teamName && t.name.toLowerCase() === task.teamName.toLowerCase()));
        if (tm && Array.isArray(tm.members) && tm.members.length > 0) {
          targetEmails = tm.members;
        }
      }

      await broadcastSystemNotification({
        title: '📋 Task Assigned & Delegated',
        message: `${targetLabel} was assigned task: "${task.title}" (Priority: ${task.priority})`,
        type: 'TASK_ASSIGNED',
        taskId: task.id,
        userId: targetUserId,
        targetEmail: targetEmail,
        targetEmails: targetEmails,
        senderEmail: callerEmail,
        priority: task.priority
      });
    }
  }

  res.json(task);
}

async function updateTaskStatus(req, res) {
  const task = store.tasks.find(t => t.id === req.params.id);
  if (!task) return res.status(404).json({ error: 'Task not found' });
  if (req.body.statusCategory) {
    task.statusCategory = req.body.statusCategory;
    if (task.statusCategory === 'DONE') {
      task.progressPercent = 100;
      task.completedAt = new Date().toISOString();
    } else if (task.statusCategory === 'IN_PROGRESS') {
      task.progressPercent = req.body.progressPercent || 50;
    }
  }
  saveTaskToSupabase(task);

  await broadcastSystemNotification({
    title: task.statusCategory === 'DONE' ? '🎉 Task Completed' : 'Task Status Updated',
    message: `"${task.title}" has been updated to ${task.statusCategory}.`,
    type: 'TASK_STATUS_CHANGED',
    taskId: task.id,
    priority: task.priority
  });

  res.json(task);
}

module.exports = {
  getAllTasks,
  getProjectTasks,
  createTask,
  updateTask,
  updateTaskStatus
};
