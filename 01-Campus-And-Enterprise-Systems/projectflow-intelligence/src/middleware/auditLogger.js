const { v4: uuidv4 } = require('uuid');
const { store } = require('../supabase');

function recordAuditLog(action, entityType, entityId, actorEmail, details) {
  store.auditLogs = store.auditLogs || [];
  const log = {
    id: uuidv4(),
    actorEmail: actorEmail || 'admin@projectflow.io',
    action,
    entityType: entityType || 'SYSTEM',
    entityId: entityId || null,
    details: typeof details === 'object' ? JSON.stringify(details) : (details || ''),
    timestamp: new Date().toISOString()
  };
  store.auditLogs.unshift(log);
  if (store.auditLogs.length > 500) {
    store.auditLogs = store.auditLogs.slice(0, 500);
  }
  return log;
}

module.exports = {
  recordAuditLog
};
