import { Server as SocketIOServer, Socket } from 'socket.io';
import jwt from 'jsonwebtoken';
import { User } from '../models/User.js';

let ioInstance: SocketIOServer | null = null;

export const initSocket = (io: SocketIOServer): void => {
  ioInstance = io;

  io.use(async (socket: Socket, next) => {
    try {
      const token = socket.handshake.auth.token || socket.handshake.query.token;
      if (token) {
        const secret = process.env.JWT_SECRET || 'aapdasetu_jwt_secret_change_in_production_2026_secure';
        const decoded = jwt.verify(token as string, secret) as { id: string; role: string };
        const user = await User.findById(decoded.id);
        if (user) {
          socket.data.user = user;
          socket.data.role = user.role;
        }
      }
      next();
    } catch (err) {
      console.warn('[Socket.IO] Unauthenticated connection (guest/public view):', (err as Error).message);
      next();
    }
  });

  io.on('connection', (socket: Socket) => {
    const user = socket.data.user;
    const role = socket.data.role || 'GUEST';
    console.log(`[Socket.IO] Client connected: ${socket.id}, Role: ${role}`);

    socket.join('public');

    if (role === 'GOVERNMENT' || role === 'ADMIN' || role === 'SUPER_ADMIN') {
      socket.join('gov');
      socket.join('admin');
      socket.join('rescue');
      socket.join('hospital');
      socket.join('ngo');
    } else if (role === 'RESCUE') {
      socket.join('rescue');
    } else if (role === 'HOSPITAL') {
      socket.join('hospital');
    } else if (role === 'NGO') {
      socket.join('ngo');
    }

    if (user?._id) {
      socket.join(`user:${user._id.toString()}`);
    }

    socket.on('join_room', (roomName: string) => {
      if (roomName) {
        socket.join(roomName);
        console.log(`[Socket.IO] ${socket.id} joined room: ${roomName}`);
      }
    });

    socket.on('chat:send', (msg: any) => {
      // Broadcast emergency message to all active responders and citizens
      if (ioInstance) {
        ioInstance.emit('chat:message', {
          ...msg,
          id: msg.id || `msg-${Date.now()}`,
          timestamp: msg.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
      }
    });

    socket.on('join_device', (deviceId: string) => {
      if (deviceId) {
        socket.join(`device:${deviceId}`);
      }
    });

    socket.on('join_rescue_team', (teamId: string) => {
      if (teamId) {
        socket.join(`team:${teamId}`);
      }
    });

    socket.on('disconnect', () => {
      console.log(`[Socket.IO] Client disconnected: ${socket.id}`);
    });
  });
};

export const getIO = (): SocketIOServer => {
  if (!ioInstance) {
    throw new Error('Socket.IO not initialized');
  }
  return ioInstance;
};

export const broadcastEvent = (event: string, data: any, room?: string): void => {
  if (!ioInstance) return;
  if (room) {
    ioInstance.to(room).emit(event, data);
  } else {
    ioInstance.emit(event, data);
  }
};
