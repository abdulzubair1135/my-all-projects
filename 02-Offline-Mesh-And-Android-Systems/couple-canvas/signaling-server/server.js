const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const crypto = require('crypto');

const PORT = process.env.PORT || 8080;
const ROOM_CODE_LENGTH = 6;
const ROOM_TTL_MS = 2 * 60 * 60 * 1000; // 2 hours
const MAX_PAYLOAD_SIZE = 64 * 1024; // 64 KB limit for signaling payloads

const app = express();
app.set('trust proxy', 1);
app.use(helmet());
app.use(express.json());

// Basic rate limiting for HTTP endpoints
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { error: 'Too many requests, please try again later.' },
  validate: { xForwardedForHeader: false }
});
app.use(limiter);

const path = require('path');
const mongoose = require('mongoose');

// Mongoose Schemas & Models
const userSchema = new mongoose.Schema({
  phone: { type: String, required: true, unique: true },
  displayName: { type: String, required: true },
  userId: { type: String, required: true },
  partnerPhone: { type: String, default: null },
  partnerUserId: { type: String, default: null },
  createdAt: { type: Date, default: Date.now }
});

const directMessageSchema = new mongoose.Schema({
  id: { type: String, required: true },
  senderPhone: { type: String, required: true },
  recipientPhone: { type: String, required: true },
  text: { type: String, required: true },
  timestamp: { type: Date, default: Date.now }
});

const User = mongoose.model('User', userSchema);
const DirectMessage = mongoose.model('DirectMessage', directMessageSchema);

// In-Memory Fallback Storage if MongoDB service is offline
const memoryDb = {
  usersByPhone: new Map(),
  directMessages: []
};

let isMongoConnected = false;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/couple_canvas';

mongoose.connect(MONGO_URI, { serverSelectionTimeoutMS: 3000 })
  .then(() => {
    isMongoConnected = true;
    console.log('Connected to MongoDB database successfully!');
  })
  .catch((err) => {
    isMongoConnected = false;
    console.log('MongoDB local service not active; using persistent in-memory store.');
  });

app.use(express.static(path.join(__dirname, 'public')));

// Phone Number Auth Endpoint
app.post('/api/auth/phone-login', async (req, res) => {
  try {
    const { phone, displayName } = req.body;
    if (!phone || !phone.trim()) {
      return res.status(400).json({ error: 'Phone number is required.' });
    }

    const cleanPhone = phone.trim();
    const name = (displayName || 'Artist').trim();
    const userId = `user_${crypto.createHash('md5').update(cleanPhone).digest('hex').substring(0, 8)}`;

    let user;
    if (isMongoConnected) {
      user = await User.findOne({ phone: cleanPhone });
      if (!user) {
        user = await User.create({ phone: cleanPhone, displayName: name, userId });
      } else if (name && user.displayName !== name) {
        user.displayName = name;
        await user.save();
      }
    } else {
      user = memoryDb.usersByPhone.get(cleanPhone);
      if (!user) {
        user = { phone: cleanPhone, displayName: name, userId, partnerPhone: null };
        memoryDb.usersByPhone.set(cleanPhone, user);
      } else if (name) {
        user.displayName = name;
      }
    }

    res.status(200).json({ status: 'ok', user });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Add Partner Endpoint
app.post('/api/partner/add', async (req, res) => {
  try {
    const { userPhone, partnerPhone } = req.body;
    if (!userPhone || !partnerPhone) {
      return res.status(400).json({ error: 'Both userPhone and partnerPhone are required.' });
    }

    const cleanUserPhone = userPhone.trim();
    const cleanPartnerPhone = partnerPhone.trim();

    if (cleanUserPhone === cleanPartnerPhone) {
      return res.status(400).json({ error: 'You cannot add your own phone number as partner.' });
    }

    if (isMongoConnected) {
      const user = await User.findOne({ phone: cleanUserPhone });
      const partner = await User.findOne({ phone: cleanPartnerPhone });

      if (!user) return res.status(404).json({ error: 'User account not found.' });

      user.partnerPhone = cleanPartnerPhone;
      if (partner) user.partnerUserId = partner.userId;
      await user.save();

      if (partner) {
        partner.partnerPhone = cleanUserPhone;
        partner.partnerUserId = user.userId;
        await partner.save();
      }

      return res.status(200).json({ status: 'ok', partner: partner || { phone: cleanPartnerPhone, displayName: 'Partner' } });
    } else {
      const user = memoryDb.usersByPhone.get(cleanUserPhone);
      if (user) {
        user.partnerPhone = cleanPartnerPhone;
      }
      const partner = memoryDb.usersByPhone.get(cleanPartnerPhone);
      if (partner) {
        partner.partnerPhone = cleanUserPhone;
      }
      return res.status(200).json({ status: 'ok', partner: partner || { phone: cleanPartnerPhone, displayName: 'Partner' } });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Fetch Outside-Room Direct Messages
app.get('/api/chat/messages', async (req, res) => {
  try {
    const { phone1, phone2 } = req.query;
    if (!phone1 || !phone2) {
      return res.status(400).json({ error: 'phone1 and phone2 query parameters required.' });
    }

    if (isMongoConnected) {
      const msgs = await DirectMessage.find({
        $or: [
          { senderPhone: phone1, recipientPhone: phone2 },
          { senderPhone: phone2, recipientPhone: phone1 }
        ]
      }).sort({ timestamp: 1 }).limit(100);
      return res.status(200).json({ messages: msgs });
    } else {
      const msgs = memoryDb.directMessages.filter(
        m => (m.senderPhone === phone1 && m.recipientPhone === phone2) ||
             (m.senderPhone === phone2 && m.recipientPhone === phone1)
      );
      return res.status(200).json({ messages: msgs });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Send Outside-Room Direct Message
app.post('/api/chat/send', async (req, res) => {
  try {
    const { senderPhone, recipientPhone, text } = req.body;
    if (!senderPhone || !recipientPhone || !text || !text.trim()) {
      return res.status(400).json({ error: 'senderPhone, recipientPhone, and text are required.' });
    }

    const msgObj = {
      id: crypto.randomUUID(),
      senderPhone: senderPhone.trim(),
      recipientPhone: recipientPhone.trim(),
      text: text.trim(),
      timestamp: new Date()
    };

    if (isMongoConnected) {
      await DirectMessage.create(msgObj);
    } else {
      memoryDb.directMessages.push(msgObj);
    }

    res.status(200).json({ status: 'ok', message: msgObj });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Deep Link Route for Room Invites (/join?code=XXXXXX)
app.get('/join', (req, res) => {
  const roomCode = (req.query.code || '').trim().toUpperCase();
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>💕 Join Drawing Room - Couple Canvas</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: linear-gradient(135deg, #FFF0F5 0%, #E0F2FE 100%); color: #0F172A; display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 20px; }
        .card { background: #FFFFFF; border-radius: 24px; padding: 40px 30px; max-width: 480px; width: 100%; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.08); border: 2px solid #FFD1DC; }
        h1 { color: #FF5277; font-size: 2rem; margin-bottom: 8px; }
        .code-box { background: #FFF0F3; color: #FF5277; font-size: 2.2rem; font-weight: 800; letter-spacing: 4px; padding: 16px; border-radius: 16px; margin: 20px 0; border: 2px dashed #FF85A1; }
        .btn { display: inline-block; background: linear-gradient(135deg, #FF5277 0%, #FF758F 100%); color: #FFFFFF; text-decoration: none; font-weight: 700; font-size: 1.1rem; padding: 16px 36px; border-radius: 50px; box-shadow: 0 10px 20px rgba(255, 82, 119, 0.3); margin-bottom: 12px; }
        .btn-sub { display: inline-block; background: #38BDF8; color: #FFFFFF; text-decoration: none; font-weight: 600; font-size: 0.95rem; padding: 12px 28px; border-radius: 50px; }
      </style>
      <script>
        window.onload = function() {
          if ("${roomCode}") {
            window.location.href = "couplecanvas://join?code=${roomCode}";
          }
        };
      </script>
    </head>
    <body>
      <div class="card">
        <h1>💕 Join Drawing Room</h1>
        <p>You have been invited to draw together in real-time!</p>
        <div class="code-box">${roomCode || 'ROOM CODE'}</div>
        <a href="couplecanvas://join?code=${roomCode}" class="btn">🚀 Open App & Join Room</a>
        <br>
        <a href="/download" class="btn-sub">📥 Don't have the app? Download APK</a>
      </div>
    </body>
    </html>
  `);
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', activeRooms: rooms.size, timestamp: new Date().toISOString() });
});

// Privacy information endpoint
app.get('/privacy-info', (req, res) => {
  res.status(200).json({
    message: 'Couple Canvas Signaling Server does not permanently store artwork, drawings, or messages.',
    dataRetention: 'Short-lived in-memory WebRTC session tokens only.'
  });
});

const server = http.createServer(app);
const wss = new WebSocket.Server({ server, maxPayload: MAX_PAYLOAD_SIZE });

// In-memory room store: roomCode -> { code, created, host: ws, peer: ws }
const rooms = new Map();

// Generate cryptographically secure random alphanumeric room code
function generateRoomCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // Avoid easily confused characters like O, 0, I, 1
  let code = '';
  const bytes = crypto.randomBytes(ROOM_CODE_LENGTH);
  for (let i = 0; i < ROOM_CODE_LENGTH; i++) {
    code += chars[bytes[i] % chars.length];
  }
  return code;
}

// Clean up expired rooms periodically
setInterval(() => {
  const now = Date.now();
  for (const [code, room] of rooms.entries()) {
    if (now - room.created > ROOM_TTL_MS) {
      console.log(`Room ${code} expired and removed.`);
      notifyAndCloseRoom(room, 'ROOM_EXPIRED', 'Room timer expired.');
      rooms.delete(code);
    }
  }
}, 5 * 60 * 1000);

function notifyAndCloseRoom(room, type, reason) {
  const message = JSON.stringify({ type, reason });
  [room.host, room.peer].forEach(ws => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      try {
        ws.send(message);
      } catch (e) {
        // ignore send error
      }
    }
  });
}

wss.on('connection', (ws, req) => {
  ws.isAlive = true;
  ws.roomCode = null;
  ws.userId = null;
  ws.isHost = false;

  ws.on('pong', () => {
    ws.isAlive = true;
  });

  ws.on('message', (messageRaw) => {
    let data;
    try {
      data = JSON.parse(messageRaw.toString());
    } catch (e) {
      ws.send(JSON.stringify({ type: 'ERROR', message: 'Invalid JSON payload.' }));
      return;
    }

    if (!data.type) {
      ws.send(JSON.stringify({ type: 'ERROR', message: 'Message type is required.' }));
      return;
    }

    switch (data.type) {
      case 'CREATE_ROOM':
        handleCreateRoom(ws, data);
        break;
      case 'JOIN_ROOM':
        handleJoinRoom(ws, data);
        break;
      case 'LEAVE_ROOM':
        handleLeaveRoom(ws);
        break;
      default:
        handleSignalingRelay(ws, data);
        break;
    }
  });

  ws.on('close', () => {
    handleLeaveRoom(ws);
  });

  ws.on('error', (err) => {
    console.error('WebSocket error:', err.message);
    handleLeaveRoom(ws);
  });
});

function handleCreateRoom(ws, data) {
  if (ws.roomCode) {
    ws.send(JSON.stringify({ type: 'ERROR', message: 'Already in a room.' }));
    return;
  }

  let roomCode = generateRoomCode();
  // Ensure uniqueness
  let attempts = 0;
  while (rooms.has(roomCode) && attempts < 10) {
    roomCode = generateRoomCode();
    attempts++;
  }

  ws.userId = data.userId || `user_${crypto.randomBytes(4).toString('hex')}`;
  ws.displayName = data.payloadJson || data.displayName || 'Partner A';
  ws.roomCode = roomCode;
  ws.isHost = true;

  const room = {
    code: roomCode,
    created: Date.now(),
    host: ws,
    hostUserId: ws.userId,
    hostName: ws.displayName,
    peer: null,
    peerUserId: null,
    peerName: null
  };

  rooms.set(roomCode, room);

  console.log(`Room created: ${roomCode} by ${ws.userId}`);

  ws.send(JSON.stringify({
    type: 'ROOM_CREATED',
    roomId: roomCode,
    roomCode: roomCode,
    userId: ws.userId,
    role: 'HOST'
  }));
}

function handleJoinRoom(ws, data) {
  if (ws.roomCode) {
    ws.send(JSON.stringify({ type: 'ERROR', message: 'Already in a room.', payloadJson: 'ALREADY_IN_ROOM' }));
    return;
  }

  const roomCode = (data.roomId || data.roomCode || '').trim().toUpperCase();
  if (!roomCode) {
    ws.send(JSON.stringify({ type: 'ERROR', message: 'Room code required.', payloadJson: 'NO_ROOM_CODE' }));
    return;
  }

  const room = rooms.get(roomCode);
  if (!room) {
    ws.send(JSON.stringify({
      type: 'JOIN_FAILED',
      reason: 'ROOM_NOT_FOUND',
      payloadJson: 'ROOM_NOT_FOUND',
      message: 'Room not found or expired. Ask your partner to create a new room.'
    }));
    return;
  }

  // Check if host is still connected and alive
  if (!room.host || room.host.readyState !== WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: 'JOIN_FAILED',
      reason: 'HOST_OFFLINE',
      payloadJson: 'ROOM_NOT_FOUND',
      message: 'Room host is not online. Ask your partner to open the room again.'
    }));
    return;
  }

  if (room.peer !== null) {
    ws.send(JSON.stringify({
      type: 'JOIN_FAILED',
      reason: 'ROOM_FULL',
      payloadJson: 'ROOM_FULL',
      message: 'This room already has 2 participants.'
    }));
    return;
  }

  ws.userId = data.userId || `user_${crypto.randomBytes(4).toString('hex')}`;
  ws.displayName = data.payloadJson || data.displayName || 'Partner B';
  ws.roomCode = roomCode;
  ws.isHost = false;

  room.peer = ws;
  room.peerUserId = ws.userId;
  room.peerName = ws.displayName;

  console.log(`User ${ws.userId} (${ws.displayName}) joined room ${roomCode}`);

  // Notify joiner
  ws.send(JSON.stringify({
    type: 'ROOM_JOINED',
    roomId: roomCode,
    roomCode: roomCode,
    userId: ws.userId,
    role: 'PEER',
    partnerUserId: room.hostUserId,
    partnerName: room.hostName,
    payloadJson: room.hostName
  }));

  // Notify host that peer joined
  if (room.host && room.host.readyState === WebSocket.OPEN) {
    room.host.send(JSON.stringify({
      type: 'PARTNER_JOINED',
      roomId: roomCode,
      roomCode: roomCode,
      userId: ws.userId,
      partnerUserId: ws.userId,
      partnerName: ws.displayName,
      payloadJson: ws.displayName
    }));
  }
}

function handleSignalingRelay(ws, data) {
  if (!ws.roomCode) {
    ws.send(JSON.stringify({ type: 'ERROR', message: 'Not currently in a room.' }));
    return;
  }

  const room = rooms.get(ws.roomCode);
  if (!room) {
    ws.send(JSON.stringify({ type: 'ERROR', message: 'Room no longer exists.' }));
    return;
  }

  // Determine target socket
  const targetWs = ws.isHost ? room.peer : room.host;
  if (targetWs && targetWs.readyState === WebSocket.OPEN) {
    // Relay complete realtime message directly to partner
    targetWs.send(JSON.stringify(data));
  }
}

function handleLeaveRoom(ws) {
  if (!ws.roomCode) return;

  const roomCode = ws.roomCode;
  const room = rooms.get(roomCode);
  ws.roomCode = null;

  if (room) {
    const partnerWs = ws.isHost ? room.peer : room.host;
    if (partnerWs && partnerWs.readyState === WebSocket.OPEN) {
      partnerWs.send(JSON.stringify({
        type: 'PARTNER_DISCONNECTED',
        reason: 'Partner left the room.'
      }));
    }

    if (ws.isHost) {
      room.host = null;
    } else {
      room.peer = null;
    }

    // If both left, remove room
    if (!room.host && !room.peer) {
      rooms.delete(roomCode);
      console.log(`Room ${roomCode} deleted after all participants left.`);
    }
  }
}

// Heartbeat interval to drop broken socket connections
const heartbeatInterval = setInterval(() => {
  wss.clients.forEach(ws => {
    if (ws.isAlive === false) {
      return ws.terminate();
    }
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);

wss.on('close', () => {
  clearInterval(heartbeatInterval);
});

server.listen(PORT, () => {
  console.log(`Couple Canvas Signaling Server listening on port ${PORT}`);
});
