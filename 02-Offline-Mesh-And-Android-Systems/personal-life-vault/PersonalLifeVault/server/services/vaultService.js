const fs = require('fs');
const { getDatabase } = require('../database/database');
const config = require('../config/config');

/**
 * Computes [startOfDayMs, startOfNextDayMs) for a given YYYY-MM-DD date in the configured timezone.
 * @param {string} dateString 'YYYY-MM-DD'
 * @param {string} timezone e.g. 'Asia/Kolkata'
 * @returns {{ startMs: number, endMs: number }}
 */
function getDateTimestampRange(dateString, timezone = config.timezone) {
  // Approximate UTC start, then adjust for timezone offset
  const [year, month, day] = dateString.split('-').map(Number);
  
  // Create a date in UTC
  const utcGuess = new Date(Date.UTC(year, month - 1, day, 0, 0, 0, 0));
  
  // Format in the target timezone to find the offset
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: timezone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });

  const parts = formatter.formatToParts(utcGuess);
  const tzHour = parseInt(parts.find(p => p.type === 'hour')?.value || '0', 10);
  const tzDay = parseInt(parts.find(p => p.type === 'day')?.value || String(day), 10);
  
  // Adjust offset
  let offsetMs = 0;
  if (tzDay === day) {
    const tzMinute = parseInt(parts.find(p => p.type === 'minute')?.value || '0', 10);
    offsetMs = (tzHour * 60 + tzMinute) * 60 * 1000;
  }

  const startMs = utcGuess.getTime() - offsetMs;
  const endMs = startMs + 24 * 60 * 60 * 1000;

  return { startMs, endMs };
}

/**
 * Retrieves all vaulted records for an exact date.
 * @param {string} dateString 'YYYY-MM-DD'
 */
function getVaultByDate(dateString) {
  const { startMs, endMs } = getDateTimestampRange(dateString);
  const db = getDatabase();

  const notifications = db.prepare(`
    SELECT id, client_event_id, device_id, app_name, title, content, timestamp, created_at
    FROM notifications
    WHERE timestamp >= ? AND timestamp < ?
    ORDER BY timestamp ASC
  `).all(startMs, endMs);

  const telecom = db.prepare(`
    SELECT id, client_event_id, device_id, type, party, body, duration, timestamp, created_at
    FROM telecom_logs
    WHERE timestamp >= ? AND timestamp < ?
    ORDER BY timestamp ASC
  `).all(startMs, endMs);

  const sensors = db.prepare(`
    SELECT id, client_event_id, device_id, type, payload_json, timestamp, created_at
    FROM sensor_logs
    WHERE timestamp >= ? AND timestamp < ?
    ORDER BY timestamp ASC
  `).all(startMs, endMs);

  const media = db.prepare(`
    SELECT id, client_event_id, device_id, original_name, file_hash, local_path, mime_type, file_size, timestamp, created_at
    FROM media_files
    WHERE timestamp >= ? AND timestamp < ?
    ORDER BY timestamp ASC
  `).all(startMs, endMs);

  return {
    date: dateString,
    timezone: config.timezone,
    timestamp_range: { start: startMs, end: endMs },
    counts: {
      notifications: notifications.length,
      telecom_logs: telecom.length,
      sensor_logs: sensors.length,
      media_files: media.length
    },
    notifications,
    telecom_logs: telecom,
    sensor_logs: sensors,
    media_files: media
  };
}

/**
 * Retrieves records across a date range.
 * @param {string} fromDate 'YYYY-MM-DD'
 * @param {string} toDate 'YYYY-MM-DD'
 */
function getVaultByRange(fromDate, toDate) {
  const { startMs } = getDateTimestampRange(fromDate);
  const { endMs } = getDateTimestampRange(toDate);
  const db = getDatabase();

  const notifications = db.prepare(`
    SELECT id, client_event_id, device_id, app_name, title, content, timestamp, created_at
    FROM notifications
    WHERE timestamp >= ? AND timestamp < ?
    ORDER BY timestamp ASC
  `).all(startMs, endMs);

  const telecom = db.prepare(`
    SELECT id, client_event_id, device_id, type, party, body, duration, timestamp, created_at
    FROM telecom_logs
    WHERE timestamp >= ? AND timestamp < ?
    ORDER BY timestamp ASC
  `).all(startMs, endMs);

  const sensors = db.prepare(`
    SELECT id, client_event_id, device_id, type, payload_json, timestamp, created_at
    FROM sensor_logs
    WHERE timestamp >= ? AND timestamp < ?
    ORDER BY timestamp ASC
  `).all(startMs, endMs);

  const media = db.prepare(`
    SELECT id, client_event_id, device_id, original_name, file_hash, local_path, mime_type, file_size, timestamp, created_at
    FROM media_files
    WHERE timestamp >= ? AND timestamp < ?
    ORDER BY timestamp ASC
  `).all(startMs, endMs);

  return {
    from: fromDate,
    to: toDate,
    timezone: config.timezone,
    counts: {
      notifications: notifications.length,
      telecom_logs: telecom.length,
      sensor_logs: sensors.length,
      media_files: media.length
    },
    notifications,
    telecom_logs: telecom,
    sensor_logs: sensors,
    media_files: media
  };
}

/**
 * Retrieves filesystem and vault storage statistics.
 */
function getStorageStats() {
  const stat = fs.statfsSync(config.storageRoot);
  const total_bytes = Number(BigInt(stat.blocks) * BigInt(stat.bsize));
  const free_bytes = Number(BigInt(stat.bavail) * BigInt(stat.bsize));
  const used_bytes = total_bytes - free_bytes;

  const db = getDatabase();
  const mediaCountRow = db.prepare('SELECT COUNT(*) as count, COALESCE(SUM(file_size), 0) as total_size FROM media_files').get();

  return {
    vault_path: config.storageRoot,
    total_bytes,
    used_bytes,
    free_bytes,
    vault_media: {
      count: mediaCountRow.count,
      total_bytes: mediaCountRow.total_size
    }
  };
}

module.exports = {
  getVaultByDate,
  getVaultByRange,
  getStorageStats
};
