const { v4: uuidv4 } = require('uuid');
const { db } = require('../database/db');
const { broadcast } = require('../websocket/ws');

const MAX_REPLAY_BUFFER = 500;
const replayBuffer = [];

const insertEventStmt = db.prepare(`
  INSERT INTO agent_events (event_id, project_id, run_id, event_type, payload, timestamp)
  VALUES (?, ?, ?, ?, ?, ?)
`);

class EventBus {
  emit(eventType, payload = {}, projectId = null, runId = null) {
    const eventId = uuidv4();
    const timestamp = new Date().toISOString();

    const eventRecord = {
      event_id: eventId,
      project_id: projectId,
      run_id: runId,
      event_type: eventType,
      payload: typeof payload === 'object' ? payload : { data: payload },
      timestamp
    };

    // Store in database
    try {
      insertEventStmt.run(
        eventId,
        projectId,
        runId,
        eventType,
        JSON.stringify(eventRecord.payload),
        timestamp
      );
    } catch (err) {
      console.error('Error persisting event to DB:', err);
    }

    // Maintain in-memory circular replay buffer
    replayBuffer.push(eventRecord);
    if (replayBuffer.length > MAX_REPLAY_BUFFER) {
      replayBuffer.shift();
    }

    // Broadcast over WebSocket (maps both event_type and event field for convenience)
    broadcast({
      event: eventType,
      ...eventRecord
    });

    return eventRecord;
  }

  getReplayEvents(sinceEventId = null, limit = 100) {
    if (!sinceEventId) {
      return replayBuffer.slice(-limit);
    }
    const idx = replayBuffer.findIndex(e => e.event_id === sinceEventId);
    if (idx === -1) {
      return replayBuffer.slice(-limit);
    }
    return replayBuffer.slice(idx + 1, idx + 1 + limit);
  }
}

const eventBus = new EventBus();
module.exports = eventBus;
