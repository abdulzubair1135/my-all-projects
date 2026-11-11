const { getDatabase, transaction } = require('../database/database');
const logger = require('../utils/logger');

/**
 * Inserts a batch of text records (notifications, telecom logs, sensor logs)
 * within an atomic SQLite transaction using client_event_id for idempotency.
 * 
 * @param {string} deviceId 
 * @param {object} batchData 
 * @returns {object} Insertion summary counts
 */
function processTextSyncBatch(deviceId, batchData) {
  const { notifications = [], telecom_logs = [], sensor_logs = [] } = batchData;
  const now = Date.now();

  return transaction((db) => {
    let notificationsInserted = 0;
    let telecomInserted = 0;
    let sensorsInserted = 0;

    // Prepared statements for batch insertions with INSERT OR IGNORE for idempotency
    const insertNotification = db.prepare(`
      INSERT OR IGNORE INTO notifications (
        client_event_id, device_id, app_name, title, content, timestamp, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    const insertTelecom = db.prepare(`
      INSERT OR IGNORE INTO telecom_logs (
        client_event_id, device_id, type, party, body, duration, timestamp, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const insertSensor = db.prepare(`
      INSERT OR IGNORE INTO sensor_logs (
        client_event_id, device_id, type, payload_json, timestamp, created_at
      ) VALUES (?, ?, ?, ?, ?, ?)
    `);

    // 1. Process Notifications
    for (const item of notifications) {
      const eventId = item.client_event_id || `notif_${item.timestamp}_${Math.random().toString(36).substring(2, 9)}`;
      const result = insertNotification.run(
        eventId,
        deviceId,
        item.app_name,
        item.title || null,
        item.content || null,
        item.timestamp,
        now
      );
      if (result.changes > 0) {
        notificationsInserted++;
      }
    }

    // 2. Process Telecom Logs
    for (const item of telecom_logs) {
      const eventId = item.client_event_id || `tel_${item.type}_${item.timestamp}_${Math.random().toString(36).substring(2, 9)}`;
      const result = insertTelecom.run(
        eventId,
        deviceId,
        item.type,
        item.party || null,
        item.body || null,
        item.duration || null,
        item.timestamp,
        now
      );
      if (result.changes > 0) {
        telecomInserted++;
      }
    }

    // 3. Process Sensor Logs
    for (const item of sensor_logs) {
      const eventId = item.client_event_id || `sens_${item.type}_${item.timestamp}_${Math.random().toString(36).substring(2, 9)}`;
      const result = insertSensor.run(
        eventId,
        deviceId,
        item.type,
        item.payload_json,
        item.timestamp,
        now
      );
      if (result.changes > 0) {
        sensorsInserted++;
      }
    }

    logger.info('SYNC', `Processed batch from ${deviceId}: ${notificationsInserted} notifs, ${telecomInserted} telecom, ${sensorsInserted} sensors`, {
      deviceId,
      notificationsInserted,
      telecomInserted,
      sensorsInserted
    });

    return {
      notifications: notificationsInserted,
      telecom_logs: telecomInserted,
      sensor_logs: sensorsInserted,
      total_received: notifications.length + telecom_logs.length + sensor_logs.length
    };
  });
}

module.exports = {
  processTextSyncBatch
};
