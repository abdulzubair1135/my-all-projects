const { WebSocketServer } = require('ws');

let wss = null;
const clients = new Set();
const subscriptions = new Map(); // ws -> Set(channels)

function initWebSocketServer(server, onClientMessage) {
  wss = new WebSocketServer({ server, path: '/ws' });

  wss.on('connection', (ws, req) => {
    clients.add(ws);
    subscriptions.set(ws, new Set(['all']));

    // Ping interval for connection health
    ws.isAlive = true;
    ws.on('pong', () => {
      ws.isAlive = true;
    });

    ws.on('message', (message) => {
      try {
        const parsed = JSON.parse(message.toString());
        
        if (parsed.type === 'subscribe') {
          const subs = subscriptions.get(ws) || new Set();
          if (Array.isArray(parsed.channels)) {
            parsed.channels.forEach(ch => subs.add(ch));
          } else if (parsed.channel) {
            subs.add(parsed.channel);
          }
          subscriptions.set(ws, subs);
        } else if (parsed.type === 'unsubscribe') {
          const subs = subscriptions.get(ws) || new Set();
          if (Array.isArray(parsed.channels)) {
            parsed.channels.forEach(ch => subs.delete(ch));
          } else if (parsed.channel) {
            subs.delete(parsed.channel);
          }
          subscriptions.set(ws, subs);
        } else if (onClientMessage) {
          onClientMessage(ws, parsed);
        }
      } catch (err) {
        console.error('Error handling WebSocket message:', err);
      }
    });

    ws.on('close', () => {
      clients.delete(ws);
      subscriptions.delete(ws);
    });

    ws.on('error', (err) => {
      console.error('WebSocket client error:', err);
    });

    // Send initial connected event
    ws.send(JSON.stringify({
      event: 'connection.ready',
      timestamp: new Date().toISOString(),
      payload: { message: 'Connected to Autonomous Web-Agent IDE WebSocket server' }
    }));
  });

  const interval = setInterval(() => {
    wss.clients.forEach((ws) => {
      if (!ws.isAlive) return ws.terminate();
      ws.isAlive = false;
      ws.ping();
    });
  }, 30000);

  wss.on('close', () => {
    clearInterval(interval);
  });

  return wss;
}

function broadcast(eventData, channel = 'all') {
  const payloadStr = JSON.stringify(eventData);
  clients.forEach((ws) => {
    if (ws.readyState === ws.OPEN) {
      const subs = subscriptions.get(ws);
      if (subs && (subs.has('all') || subs.has(channel) || subs.has(eventData.event_type) || subs.has(eventData.event))) {
        ws.send(payloadStr);
      }
    }
  });
}

module.exports = {
  initWebSocketServer,
  broadcast,
  getClients: () => clients
};
