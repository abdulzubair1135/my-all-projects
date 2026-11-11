const { v4: uuidv4 } = require('uuid');
const { store, supabase } = require('../supabase');
const { recordAuditLog } = require('../middleware/auditLogger');

// FCM Push Tokens Store
store.fcmTokens = store.fcmTokens || [];
store.pushLogs = store.pushLogs || [];

// Broadcast Push Notification Dispatcher
async function dispatchPushNotification(title, message, extraData = {}) {
  console.log(`[PUSH] Dispatching to ${store.fcmTokens.length} mobile devices: "${title}" - "${message}"`);
  const record = {
    id: uuidv4(),
    title,
    message,
    recipients: store.fcmTokens.length,
    timestamp: new Date().toISOString()
  };
  (store.pushLogs = store.pushLogs || []).unshift(record);
}

// Universal Enterprise Real-time Notification Engine
async function broadcastSystemNotification({
  title,
  message,
  type = 'SYSTEM',
  taskId = null,
  channel = null,
  senderName = null,
  senderId = null,
  senderEmail = null,
  priority = 'NORMAL',
  userId = null,
  targetEmail = null,
  targetEmails = []
}) {
  const normTargetEmails = Array.isArray(targetEmails) ? targetEmails.map(e => (e || '').toLowerCase()).filter(Boolean) : [];
  if (targetEmail && !normTargetEmails.includes(targetEmail.toLowerCase())) {
    normTargetEmails.push(targetEmail.toLowerCase());
  }
  
  // Resolve userId if not set but targetEmail is known
  let resolvedUserId = userId;
  if (!resolvedUserId && normTargetEmails.length === 1) {
    const matched = (store.users || []).find(u => u.email?.toLowerCase() === normTargetEmails[0]);
    if (matched) resolvedUserId = matched.id;
  }

  const notif = {
    id: uuidv4(),
    title: title || 'Workspace Alert',
    message: message || 'New enterprise update',
    type: type || 'SYSTEM',
    taskId: taskId || null,
    channel: channel || null,
    senderName: senderName || null,
    senderId: senderId || null,
    senderEmail: senderEmail || null,
    priority: priority || 'NORMAL',
    userId: resolvedUserId || null,
    targetEmail: targetEmail || (normTargetEmails.length === 1 ? normTargetEmails[0] : null),
    targetEmails: normTargetEmails,
    read: false,
    createdAt: new Date().toISOString()
  };

  (store.notifications = store.notifications || []).unshift(notif);
  if (store.notifications.length > 200) {
    store.notifications = store.notifications.slice(0, 200);
  }

  // Encode channel, taskId, senderName, targets into message metadata for Supabase persistence
  const metaParts = [];
  if (channel) metaParts.push(`ch=${channel}`);
  if (taskId) metaParts.push(`task=${taskId}`);
  if (senderName) metaParts.push(`sender=${senderName}`);
  if (senderEmail) metaParts.push(`senderEmail=${senderEmail}`);
  if (notif.targetEmail) metaParts.push(`targetEmail=${notif.targetEmail}`);
  if (normTargetEmails.length > 0) metaParts.push(`targetEmails=${normTargetEmails.join(',')}`);

  const metaTag = metaParts.length > 0 ? ` <!--PF:${metaParts.join(':')}-->` : '';
  const supabaseMessage = (notif.message || '') + metaTag;

  if (supabase) {
    try {
      await supabase.from('notifications').upsert({
        id: notif.id,
        title: notif.title,
        message: supabaseMessage,
        type: notif.type,
        user_id: notif.userId || null,
        read: false,
        created_at: notif.createdAt
      });
    } catch (e) {
      console.warn('[NOTIF] Supabase sync warning:', e.message);
    }
  }

  await dispatchPushNotification(notif.title, notif.message, {
    type: notif.type,
    taskId: notif.taskId,
    channel: notif.channel,
    priority: notif.priority,
    targetEmails: normTargetEmails,
    targetEmail: notif.targetEmail,
    userId: notif.userId
  });

  return notif;
}

// Handler: FCM Token Registration
function registerFcmToken(req, res) {
  const { fcmToken, email } = req.body;
  if (fcmToken) {
    const existing = store.fcmTokens.find(t => t.token === fcmToken);
    if (!existing) {
      store.fcmTokens.push({ token: fcmToken, email: email || null, registeredAt: new Date().toISOString() });
      console.log('[FCM] Registered new mobile push token:', fcmToken.substring(0, 20) + '...');
    }
  }
  res.json({ success: true, count: store.fcmTokens.length });
}

// Handler: Targeted Push
async function sendPush(req, res) {
  const { title, message, taskId, priority, type } = req.body;
  const notif = await broadcastSystemNotification({
    title: title || 'Workspace Alert',
    message: message || 'You have a new update in ProjectFlow.',
    type: type || 'PUSH_ALERT',
    taskId: taskId || null,
    priority: priority || 'HIGH'
  });
  res.json({ success: true, notification: notif, deliveredDevices: store.fcmTokens.length });
}

// Handler: Broadcast Send
async function handleBroadcastSend(req, res) {
  const { title, body, message, type } = req.body;
  const alertTitle = title || 'ProjectFlow Broadcast Alert';
  const alertBody = body || message || 'New enterprise announcement';
  await broadcastSystemNotification({
    title: alertTitle,
    message: alertBody,
    type: type || 'BROADCAST',
    priority: 'HIGH'
  });
  recordAuditLog('BROADCAST_SENT', 'NOTIFICATION', null, req.headers['x-user-email'] || 'admin@projectflow.io', { title: alertTitle, recipientsCount: store.fcmTokens.length });
  res.json({
    success: true,
    message: `Dispatched to ${store.fcmTokens.length} active mobile subscribers`,
    recipientsCount: store.fcmTokens.length,
    timestamp: new Date().toISOString()
  });
}

// Handler: Broadcast History
function getBroadcastHistory(req, res) {
  res.json(store.pushLogs || []);
}

// Handler: Get Notifications with Channel & Metadata Extraction
async function getNotifications(req, res) {
  if (supabase) {
    try {
      const { data: dbNotifs, error } = await supabase
        .from('notifications')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(60);
      if (!error && dbNotifs && dbNotifs.length > 0) {
        dbNotifs.forEach(dn => {
          const idx = (store.notifications || []).findIndex(n => n.id === dn.id);
          let rawMsg = dn.message || '';
          let ch = null;
          let tId = null;
          let sName = null;
          let sEmail = null;
          let tEmail = null;
          let tEmails = [];

          if (rawMsg.includes('<!--PF:')) {
            const m = rawMsg.match(/<!--PF:(.*?)-->/);
            if (m && m[1]) {
              const tokens = m[1].split(':');
              tokens.forEach(tok => {
                const eqIdx = tok.indexOf('=');
                if (eqIdx > 0) {
                  const k = tok.slice(0, eqIdx);
                  const v = tok.slice(eqIdx + 1);
                  if (k === 'ch') ch = v || null;
                  if (k === 'task') tId = v || null;
                  if (k === 'sender') sName = v || null;
                  if (k === 'senderEmail') sEmail = v || null;
                  if (k === 'targetEmail') tEmail = v || null;
                  if (k === 'targetEmails') tEmails = v ? v.split(',').filter(Boolean) : [];
                }
              });
            }
            rawMsg = rawMsg.replace(/<!--PF:[^>]*-->/, '').trim();
          }

          if (idx >= 0) {
            store.notifications[idx].read = !!dn.read;
            if (!store.notifications[idx].channel && ch) store.notifications[idx].channel = ch;
            if (!store.notifications[idx].taskId && tId) store.notifications[idx].taskId = tId;
            if (!store.notifications[idx].senderName && sName) store.notifications[idx].senderName = sName;
            if (!store.notifications[idx].senderEmail && sEmail) store.notifications[idx].senderEmail = sEmail;
            if (!store.notifications[idx].targetEmail && tEmail) store.notifications[idx].targetEmail = tEmail;
            if ((!store.notifications[idx].targetEmails || store.notifications[idx].targetEmails.length === 0) && tEmails.length > 0) store.notifications[idx].targetEmails = tEmails;
          } else {
            (store.notifications = store.notifications || []).push({
              id: dn.id,
              title: dn.title,
              message: rawMsg,
              type: dn.type || 'SYSTEM',
              taskId: tId,
              channel: ch,
              senderName: sName,
              senderEmail: sEmail,
              targetEmail: tEmail,
              targetEmails: tEmails,
              userId: dn.user_id || null,
              read: !!dn.read,
              createdAt: dn.created_at
            });
          }
        });
        store.notifications.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
      }
    } catch (e) {
      console.warn('[NOTIF] Supabase fetch error:', e.message);
    }
  }

  // Return clean messages without metadata tags
  const cleaned = (store.notifications || []).map(n => {
    let msg = n.message || '';
    if (msg.includes('<!--PF:')) {
      msg = msg.replace(/<!--PF:[^>]*-->/, '').trim();
    }
    return {
      ...n,
      message: msg
    };
  });

  const reqEmail = (req.headers['x-user-email'] || req.query.userEmail || (req.user && req.user.email) || '').trim().toLowerCase();
  const matchedUser = reqEmail ? (store.users || []).find(u => u.email?.toLowerCase() === reqEmail) : null;
  const reqUserId = req.headers['x-user-id'] || req.query.userId || (matchedUser ? matchedUser.id : (req.user && req.user.id));

  if (!reqEmail) {
    return res.json(cleaned);
  }

  const userSlug = reqEmail.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();

  // Find teams the user is member of
  const userTeamIds = (store.teams || [])
    .filter(t => Array.isArray(t.members) && t.members.some(m => m.toLowerCase() === reqEmail))
    .map(t => t.id);

  const filtered = cleaned.filter(n => {
    // 1. Never notify user about their own initiated actions/messages
    if (n.senderEmail && n.senderEmail.toLowerCase() === reqEmail) return false;
    if (n.senderId && reqUserId && n.senderId === reqUserId) return false;

    // 2. Direct Messages (dm_...): MUST contain user's own email slug
    if (n.channel && n.channel.startsWith('dm_')) {
      return n.channel.includes(userSlug);
    }

    // 3. Group Messages (group_...): If group has members list, user must be a member
    if (n.channel && n.channel.startsWith('group_')) {
      const grp = (store.chatGroups || []).find(g => g.channel === n.channel);
      if (grp && Array.isArray(grp.members) && grp.members.length > 0) {
        return grp.members.some(m => m.toLowerCase() === reqEmail);
      }
      return true;
    }

    // 4. Team Chat Channels: user must be in team
    if (n.channel && n.channel !== 'general') {
      const tm = (store.teams || []).find(t => t.channel === n.channel || t.slug === n.channel);
      if (tm && Array.isArray(tm.members) && tm.members.length > 0) {
        return tm.members.some(m => m.toLowerCase() === reqEmail);
      }
    }

    // 5. Targeted Notifications (by userId, targetEmail, targetEmails)
    if (n.userId && reqUserId && n.userId === reqUserId) return true;
    if (n.targetEmail && n.targetEmail.toLowerCase() === reqEmail) return true;
    if (Array.isArray(n.targetEmails) && n.targetEmails.length > 0) {
      return n.targetEmails.some(e => e.toLowerCase() === reqEmail);
    }

    // 6. Task Assigned: check if assigned to this user or their team
    if (n.type === 'TASK_ASSIGNED' || n.taskId) {
      if (n.targetEmail && n.targetEmail.toLowerCase() === reqEmail) return true;
      if (Array.isArray(n.targetEmails) && n.targetEmails.some(e => e.toLowerCase() === reqEmail)) return true;
      if (n.userId && reqUserId && n.userId === reqUserId) return true;

      const task = (store.tasks || []).find(t => t.id === n.taskId);
      if (task) {
        if (task.assigneeId && reqUserId && task.assigneeId === reqUserId) return true;
        if (task.assigneeName && matchedUser && task.assigneeName.toLowerCase() === matchedUser.fullName?.toLowerCase()) return true;
        if (task.teamId && userTeamIds.includes(task.teamId)) return true;
      }
      return false;
    }

    // 7. General Broadcast alerts
    if (n.type === 'BROADCAST') return true;

    // 8. If notification is strictly targeted to another user
    if (n.userId && reqUserId && n.userId !== reqUserId) return false;
    if (n.targetEmail && n.targetEmail.toLowerCase() !== reqEmail) return false;
    if (Array.isArray(n.targetEmails) && n.targetEmails.length > 0 && !n.targetEmails.some(e => e.toLowerCase() === reqEmail)) return false;

    // Unassigned system updates (only if not a DM / not a task assigned to someone else)
    return !n.userId && (!n.targetEmails || n.targetEmails.length === 0);
  });

  res.json(filtered);
}

// Handler: Mark Single Read
function markNotificationRead(req, res) {
  const notif = (store.notifications || []).find(n => n.id === req.params.id);
  if (notif) notif.read = true;
  res.json(notif || { success: true });
}

// Handler: Mark All Read
function markAllRead(req, res) {
  (store.notifications || []).forEach(n => { n.read = true; });
  res.json({ success: true, count: (store.notifications || []).length });
}

module.exports = {
  dispatchPushNotification,
  broadcastSystemNotification,
  registerFcmToken,
  sendPush,
  handleBroadcastSend,
  getBroadcastHistory,
  getNotifications,
  markNotificationRead,
  markAllRead
};
