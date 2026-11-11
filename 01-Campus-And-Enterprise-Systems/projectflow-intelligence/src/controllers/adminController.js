const { v4: uuidv4 } = require('uuid');
const { store, supabase } = require('../supabase');
const { recordAuditLog } = require('../middleware/auditLogger');

async function getAdminUsers(req, res) {
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
    } catch (e) {
      console.warn('[ADMIN] Profiles live sync error:', e.message);
    }
  }

  const query = (req.query.query || '').toLowerCase();
  const callerEmail = (req.userEmail || req.headers['x-user-email'] || (req.user && req.user.email) || '').toLowerCase();
  let filtered = store.users.map(u => {
    const emailKey = (u.email || '').toLowerCase();
    const lastSeen = store.activeSessions ? store.activeSessions[emailKey] : null;
    const isOnline = !!(lastSeen && (Date.now() - lastSeen < 180000)) || (!!callerEmail && callerEmail === emailKey);
    return {
      ...u,
      isOnline,
      lastSeenAt: lastSeen || (isOnline ? Date.now() : null)
    };
  });
  if (query) {
    filtered = filtered.filter(u => u.email.toLowerCase().includes(query) || (u.fullName && u.fullName.toLowerCase().includes(query)));
  }
  res.json({
    content: filtered,
    totalElements: filtered.length,
    totalPages: 1,
    size: 50,
    number: 0
  });
}

async function inviteUser(req, res) {
  const { email, fullName, role } = req.body;
  if (!email) return res.status(400).json({ error: 'Email address is required' });
  const cleanEmail = email.trim().toLowerCase();
  let existing = store.users.find(u => u.email.toLowerCase() === cleanEmail);
  if (existing) {
    return res.status(409).json({ error: 'A user with this email address already exists' });
  }
  const newUser = {
    id: uuidv4(),
    email: cleanEmail,
    fullName: fullName ? fullName.trim() : cleanEmail.split('@')[0],
    role: role || 'MEMBER',
    active: true,
    createdAt: new Date().toISOString()
  };
  store.users.push(newUser);
  if (supabase) {
    try {
      await supabase.from('profiles').upsert({
        id: newUser.id,
        email: newUser.email,
        full_name: newUser.fullName,
        global_role: newUser.role,
        active: true
      });
    } catch (e) {
      console.warn('[ADMIN] Supabase user insert warning:', e.message);
    }
  }
  recordAuditLog('USER_INVITED', 'USER', newUser.id, req.headers['x-user-email'] || 'admin@projectflow.io', { email: cleanEmail, role: newUser.role });
  res.status(201).json(newUser);
}

async function updateUserRole(req, res) {
  const user = store.users.find(u => u.id === req.params.id);
  if (!user) return res.status(404).json({ message: 'User not found' });
  const oldRole = user.role;
  if (req.body.role) user.role = req.body.role;
  if (supabase) {
    try {
      await supabase.from('profiles').update({ global_role: user.role }).eq('id', user.id);
    } catch (e) {
      console.warn('[ADMIN] Supabase role update warning:', e.message);
    }
  }
  recordAuditLog('USER_ROLE_CHANGED', 'USER', user.id, req.headers['x-user-email'] || 'admin@projectflow.io', { oldRole, newRole: user.role, email: user.email });
  res.json(user);
}

async function toggleUserStatus(req, res) {
  const user = store.users.find(u => u.id === req.params.id);
  if (!user) return res.status(404).json({ message: 'User not found' });
  user.active = req.body.active !== undefined ? !!req.body.active : !user.active;
  if (supabase) {
    try {
      await supabase.from('profiles').update({ active: user.active }).eq('id', user.id);
    } catch (e) {
      console.warn('[ADMIN] Supabase status update warning:', e.message);
    }
  }
  recordAuditLog('USER_STATUS_TOGGLED', 'USER', user.id, req.headers['x-user-email'] || 'admin@projectflow.io', { active: user.active, email: user.email });
  res.json(user);
}

function getAdminWorkspaces(req, res) {
  res.json(store.workspaces);
}

function getAdminProjects(req, res) {
  const mapped = (store.projects || []).map(p => {
    const user = p.assigneeId ? (store.users || []).find(u => u.id === p.assigneeId) : null;
    const team = p.teamId ? (store.teams || []).find(t => t.id === p.teamId || t.slug === p.teamId || (p.teamName && t.name.toLowerCase() === p.teamName.toLowerCase())) : null;
    return {
      ...p,
      assigneeName: user ? user.fullName : (p.assigneeName || null),
      assigneeEmail: user ? user.email : (p.assigneeEmail || null),
      teamName: team ? team.name : (p.teamName || null)
    };
  });
  res.json(mapped);
}

module.exports = {
  getAdminUsers,
  inviteUser,
  updateUserRole,
  toggleUserStatus,
  getAdminWorkspaces,
  getAdminProjects
};
