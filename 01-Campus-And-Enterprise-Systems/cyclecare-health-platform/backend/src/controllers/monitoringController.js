const pool = require('../config/db');

// Ingest error from Android, Web, or Backend
const reportError = async (req, res) => {
  try {
    const {
      source = 'ANDROID',
      severity = 'ERROR',
      message,
      stack = null,
      route = null,
      method = null,
      user_id = req.user ? req.user.id : null,
      status_code = null,
      device_info = null,
      metadata = null
    } = req.body;

    if (!message) {
      return res.status(400).json({ success: false, message: 'Error message is required' });
    }

    const query = `
      INSERT INTO app_error_logs 
        (source, severity, message, stack, route, method, user_id, status_code, device_info, metadata)
      VALUES 
        ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      RETURNING id, created_at;
    `;

    const values = [
      source.toUpperCase(),
      severity.toUpperCase(),
      message,
      stack,
      route,
      method,
      user_id,
      status_code ? parseInt(status_code, 10) : null,
      device_info ? JSON.stringify(device_info) : null,
      metadata ? JSON.stringify(metadata) : null
    ];

    const result = await pool.query(query, values);

    return res.status(201).json({
      success: true,
      message: 'Error logged successfully',
      incident_id: result.rows[0].id
    });
  } catch (err) {
    console.error('[Monitoring Ingestion Error]', err);
    return res.status(500).json({ success: false, message: 'Failed to record error log' });
  }
};

// Retrieve error logs for Admin Control Panel
const getAdminErrors = async (req, res) => {
  try {
    const { severity, source, resolved, limit = 50, offset = 0 } = req.query;

    const conditions = [];
    const values = [];
    let paramIndex = 1;

    if (severity) {
      conditions.push(`severity = $${paramIndex++}`);
      values.push(severity.toUpperCase());
    }

    if (source) {
      conditions.push(`source = $${paramIndex++}`);
      values.push(source.toUpperCase());
    }

    if (resolved !== undefined) {
      conditions.push(`resolved = $${paramIndex++}`);
      values.push(resolved === 'true' || resolved === true);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    const sql = `
      SELECT 
        id, source, severity, message, stack, route, method, user_id,
        status_code, resolved, device_info, metadata, created_at, resolved_at
      FROM app_error_logs
      ${whereClause}
      ORDER BY created_at DESC
      LIMIT $${paramIndex++} OFFSET $${paramIndex++};
    `;

    values.push(parseInt(limit, 10), parseInt(offset, 10));

    const result = await pool.query(sql, values);

    // Also get count
    const countSql = `SELECT COUNT(*) as total FROM app_error_logs ${whereClause};`;
    const countResult = await pool.query(countSql, values.slice(0, conditions.length));
    const total = parseInt(countResult.rows[0].total, 10);

    return res.json({
      success: true,
      total,
      errors: result.rows
    });
  } catch (err) {
    console.error('[Admin Errors Fetch Error]', err);
    return res.status(500).json({ success: false, message: 'Failed to retrieve error logs' });
  }
};

// Error incident summary stats for admin header
const getErrorStats = async (req, res) => {
  try {
    const statsSql = `
      SELECT
        COUNT(*) as total_errors,
        COUNT(*) FILTER (WHERE resolved = false) as unresolved_errors,
        COUNT(*) FILTER (WHERE severity = 'CRITICAL' AND resolved = false) as critical_unresolved,
        COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') as errors_last_24h
      FROM app_error_logs;
    `;
    const result = await pool.query(statsSql);
    const row = result.rows[0] || {};

    return res.json({
      success: true,
      stats: {
        total: parseInt(row.total_errors || 0, 10),
        unresolved: parseInt(row.unresolved_errors || 0, 10),
        critical: parseInt(row.critical_unresolved || 0, 10),
        last_24h: parseInt(row.errors_last_24h || 0, 10)
      }
    });
  } catch (err) {
    console.error('[Error Stats Fetch Error]', err);
    return res.status(500).json({ success: false, message: 'Failed to retrieve error stats' });
  }
};

// Resolve an error incident
const resolveError = async (req, res) => {
  try {
    const { id } = req.params;

    const query = `
      UPDATE app_error_logs
      SET resolved = true, resolved_at = NOW()
      WHERE id = $1
      RETURNING id, resolved, resolved_at;
    `;

    const result = await pool.query(query, [id]);

    if (result.rowCount === 0) {
      return res.status(404).json({ success: false, message: 'Error log not found' });
    }

    return res.json({
      success: true,
      message: 'Incident marked as resolved',
      incident: result.rows[0]
    });
  } catch (err) {
    console.error('[Resolve Error Handler]', err);
    return res.status(500).json({ success: false, message: 'Failed to resolve error incident' });
  }
};

// Register FCM Device Push Token
const registerDeviceToken = async (req, res) => {
  try {
    const userId = req.user ? req.user.id : null;
    const { token, platform = 'ANDROID', device_model = null, os_version = null } = req.body;

    if (!token) {
      return res.status(400).json({ success: false, message: 'Push token is required' });
    }

    if (!userId) {
      return res.status(401).json({ success: false, message: 'Authentication required' });
    }

    const query = `
      INSERT INTO device_tokens (user_id, token, platform, device_model, os_version, is_active, updated_at)
      VALUES ($1, $2, $3, $4, $5, true, NOW())
      ON CONFLICT (user_id, token) 
      DO UPDATE SET is_active = true, updated_at = NOW(), device_model = EXCLUDED.device_model, os_version = EXCLUDED.os_version
      RETURNING id;
    `;

    const result = await pool.query(query, [userId, token, platform.toUpperCase(), device_model, os_version]);

    return res.json({
      success: true,
      message: 'Device token registered successfully',
      id: result.rows[0].id
    });
  } catch (err) {
    console.error('[Register Token Error]', err);
    return res.status(500).json({ success: false, message: 'Failed to register device token' });
  }
};

module.exports = {
  reportError,
  getAdminErrors,
  getErrorStats,
  resolveError,
  registerDeviceToken
};
