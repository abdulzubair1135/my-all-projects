const { v4: uuidv4 } = require('uuid');
const { store, supabase } = require('../supabase');
const { broadcastSystemNotification } = require('./notificationController');

async function getTeamMembers(req, res) {
  const reqEmail = req.userEmail || req.headers['x-user-email'] || req.query.userEmail || (req.user && req.user.email);
  if (reqEmail) {
    store.activeSessions[reqEmail.trim().toLowerCase()] = Date.now();
  }
  if (supabase) {
    try {
      const { data: profiles, error } = await supabase.from('profiles').select('*');
      if (!error && profiles && profiles.length > 0) {
        store.users = profiles.map(p => ({
          id: p.id,
          email: p.email,
          fullName: p.full_name || (p.email ? p.email.split('@')[0] : 'Member'),
          role: p.global_role || 'MEMBER',
          active: p.active !== false,
          createdAt: p.created_at || new Date().toISOString()
        }));
      }
    } catch (e) {}
  }
  const now = Date.now();
  const callerEmail = (reqEmail || '').trim().toLowerCase();
  const team = store.users.map(u => {
    const emailKey = (u.email || '').toLowerCase();
    const lastActive = store.activeSessions ? store.activeSessions[emailKey] : 0;
    // Central System Administrator service is always online while server is operational
    const isAdminAccount = emailKey === 'admin@projectflow.io' || (u.role && u.role.toUpperCase() === 'ADMINISTRATOR');
    const isRecent = !!(lastActive && (now - lastActive < 300000));
    const isCaller = !!(callerEmail && callerEmail === emailKey);
    const isOnline = isAdminAccount || isRecent || isCaller;
    return {
      id: u.id,
      email: u.email,
      fullName: u.fullName,
      role: u.role,
      active: u.active !== false,
      isOnline: isOnline,
      lastSeen: lastActive ? new Date(lastActive).toISOString() : (isOnline ? new Date().toISOString() : null),
      assignedTasksCount: (store.tasks || []).filter(t => t.assigneeId === u.id).length
    };
  });
  res.json(team);
}

function getSquadTeams(req, res) {
  res.json(store.teams || []);
}

async function createSquadTeam(req, res) {
  const { name, description, memberCount, members, memberEmails } = req.body;
  if (!name) return res.status(400).json({ error: 'Team name is required' });
  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  const channel = slug;
  const assignedMembers = Array.isArray(members) ? members : (Array.isArray(memberEmails) ? memberEmails : []);
  const newTeam = {
    id: uuidv4(),
    name,
    slug,
    description: description || '',
    memberCount: assignedMembers.length || memberCount || 1,
    members: assignedMembers,
    channel,
    createdAt: new Date().toISOString()
  };
  (store.teams = store.teams || []).push(newTeam);

  // Auto-create team welcome message in dedicated channel
  (store.messages = store.messages || []).push({
    id: uuidv4(),
    senderId: store.users[0] ? store.users[0].id : uuidv4(),
    senderName: 'System Administrator',
    content: `🎉 Welcome to #${channel}! This dedicated discussion group was created for "${name}".`,
    channel: channel,
    reactions: { '🎉': 3, '🚀': 2 },
    createdAt: new Date().toISOString()
  });

  // Target notification only to team members if specified
  await broadcastSystemNotification({
    title: '👥 New Team & Group Created',
    message: `Team "${name}" and chat channel #${channel} are now active.`,
    type: 'TEAM_CREATED',
    channel: channel,
    targetEmails: assignedMembers,
    priority: 'HIGH'
  });

  res.status(201).json(newTeam);
}

module.exports = {
  getTeamMembers,
  getSquadTeams,
  createSquadTeam
};
