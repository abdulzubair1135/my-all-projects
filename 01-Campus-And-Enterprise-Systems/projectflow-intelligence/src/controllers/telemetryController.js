const { v4: uuidv4 } = require('uuid');
const { store } = require('../supabase');

function logClientError(req, res) {
  const { severity, message, stack, source, userId, metadata } = req.body;
  const errorEntry = {
    id: uuidv4(),
    severity: severity || 'ERROR',
    message: message || 'Unknown error occurred',
    stack: stack || null,
    source: source || 'CLIENT_TELEMETRY',
    userId: userId || null,
    metadata: metadata || {},
    resolved: false,
    resolvedAt: null,
    timestamp: new Date().toISOString()
  };
  (store.errors = store.errors || []).unshift(errorEntry);
  res.status(201).json(errorEntry);
}

function getSystemErrors(req, res) {
  const severity = req.query.severity;
  const status = req.query.status;
  let list = store.errors || [];
  if (severity) list = list.filter(e => e.severity.toUpperCase() === severity.toUpperCase());
  if (status === 'open') list = list.filter(e => !e.resolved);
  if (status === 'resolved') list = list.filter(e => e.resolved);
  res.json({
    content: list,
    totalElements: list.length,
    totalPages: 1,
    size: 25,
    number: 0
  });
}

function resolveSystemError(req, res) {
  const err = (store.errors || []).find(e => e.id === req.params.id);
  if (!err) return res.status(404).json({ error: 'Error log entry not found' });
  err.resolved = true;
  err.resolvedAt = new Date().toISOString();
  res.json(err);
}

function getSystemHealth(req, res) {
  const mem = process.memoryUsage();
  res.json({
    status: 'UP',
    databaseStatus: 'Supabase PostgreSQL Cloud',
    databaseLatencyMs: 3,
    freeMemoryMb: Math.round((mem.heapTotal - mem.heapUsed) / (1024 * 1024)),
    totalMemoryMb: Math.round(mem.heapTotal / (1024 * 1024)),
    activeThreads: 1,
    schemaVersion: 'V1__supabase_tables',
    checkedAt: new Date().toISOString()
  });
}

function getAuditLogs(req, res) {
  store.auditLogs = store.auditLogs || [];
  const query = (req.query.query || '').toLowerCase();
  const actionFilter = (req.query.action || '').toUpperCase();
  const page = parseInt(req.query.page) || 0;
  const size = parseInt(req.query.size) || 25;

  let list = store.auditLogs;
  if (actionFilter && actionFilter !== 'ALL') {
    list = list.filter(l => l.action.toUpperCase().includes(actionFilter));
  }
  if (query) {
    list = list.filter(l => 
      (l.action && l.action.toLowerCase().includes(query)) ||
      (l.actorEmail && l.actorEmail.toLowerCase().includes(query)) ||
      (l.entityType && l.entityType.toLowerCase().includes(query)) ||
      (l.details && l.details.toLowerCase().includes(query))
    );
  }

  const start = page * size;
  const paginated = list.slice(start, start + size);

  res.json({
    content: paginated,
    totalElements: list.length,
    totalPages: Math.ceil(list.length / size) || 1,
    size,
    number: page
  });
}

module.exports = {
  logClientError,
  getSystemErrors,
  resolveSystemError,
  getSystemHealth,
  getAuditLogs
};
