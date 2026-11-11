import { Server as HttpServer } from 'http';
import { Server as SocketIOServer, Socket } from 'socket.io';
import { JwtUtil } from '../security/jwt.util';
import { logger } from '../utils/logger';
import { SocketEvent, UserRole } from '../constants/enums';

export class SocketManager {
  private static io: SocketIOServer | null = null;

  static initialize(httpServer: HttpServer, allowedOrigins: string[]): SocketIOServer {
    this.io = new SocketIOServer(httpServer, {
      cors: {
        origin: allowedOrigins,
        methods: ['GET', 'POST'],
        credentials: true
      },
      pingTimeout: 30000,
      pingInterval: 25000
    });

    // Authenticate socket connections with JWT or allow Dashboard Observer
    this.io.use((socket: Socket, next) => {
      const token = socket.handshake.auth?.token || socket.handshake.headers['authorization']?.replace('Bearer ', '');
      if (!token) {
        // Allow unauthenticated Dashboard and Observer connections
        (socket as any).user = {
          sub: `observer_${socket.id.substring(0, 6)}`,
          role: 'DASHBOARD_OBSERVER',
          name: 'Campus Control Panel'
        };
        return next();
      }

      try {
        const payload = JwtUtil.verifyAccessToken(token);
        (socket as any).user = payload;
        next();
      } catch (err) {
        // Fallback to dashboard observer if token invalid
        (socket as any).user = {
          sub: `observer_${socket.id.substring(0, 6)}`,
          role: 'DASHBOARD_OBSERVER',
          name: 'Campus Control Panel'
        };
        next();
      }
    });

    this.io.on('connection', (socket: Socket) => {
      const user = (socket as any).user;
      logger.info(`Socket client connected: ${socket.id}, User: ${user?.sub} (${user?.role})`);

      // Auto-join personal user room
      if (user?.sub) {
        socket.join(`user:${user.sub}`);
      }

      // Auto-join role room
      if (user?.role) {
        socket.join(`role:${user.role}`);
      }

      // Auto-join department room
      if (user?.departmentId) {
        socket.join(`department:${user.departmentId}`);
      }

      // Join campus broadcast & principal rooms
      socket.join('campus_broadcast');
      socket.join('principal_channel');

      // Join room event
      socket.on('join_room', (data: { room: string }) => {
        if (data?.room) {
          socket.join(data.room);
          logger.debug(`Socket ${socket.id} joined room: ${data.room}`);
        }
      });

      // Handle Teacher 1-Tap Quick Response (🔴 BUSY / 🟢 ON THE WAY)
      socket.on('urgent_summon_response', async (data: any) => {
        logger.info(`Teacher Summon Response received:`, data);
        
        // Import TelemetryService dynamically
        const { TelemetryService } = await import('../services/telemetry.service');
        TelemetryService.logNotification({
          type: 'TEACHER_RESPONSE',
          targetUid: data.facultyUid || data.facultyName || 'FACULTY',
          title: `Teacher Response: ${data.status}`,
          body: `Faculty ${data.facultyUid || ''} responded: ${data.status} (ETA: ${data.eta || 'N/A'})`,
          room: data.room || 'Principal Cabin',
          channel: 'SOCKET_IO',
          status: 'ACKNOWLEDGED',
          metadata: data
        });

        // Broadcast to all observers and principal cabins
        socket.to('principal_channel').emit('urgent_summon_response', data);
        socket.to('campus_broadcast').emit('urgent_summon_response', data);
        SocketManager.broadcastAll('urgent_summon_response', data);
      });

      // Handle Dispatch from Control Panel
      socket.on('urgent_summon_trigger', async (data: any) => {
        logger.info(`Urgent Summon Triggered:`, data);
        const { TelemetryService } = await import('../services/telemetry.service');
        TelemetryService.logNotification({
          type: 'URGENT_SUMMON',
          targetUid: data.targetFacultyUid,
          title: '🚨 Principal Urgent Summon',
          body: `Summoned to ${data.room}. Reason: ${data.reason}`,
          room: data.room,
          channel: 'HYBRID',
          status: 'DELIVERED',
          metadata: data
        });

        SocketManager.broadcastAll('urgent_summon_alert', data);
        SocketManager.broadcastAll('meeting.new', data);
      });

      // Handle Campus Broadcast
      socket.on('campus_broadcast', async (data: any) => {
        const { TelemetryService } = await import('../services/telemetry.service');
        TelemetryService.logNotification({
          type: 'CAMPUS_BROADCAST',
          title: data.title || 'Campus Broadcast',
          body: data.message || '',
          channel: 'HYBRID',
          status: 'DELIVERED',
          metadata: data
        });

        SocketManager.broadcastAll('campus_broadcast_message', data);
      });

      // Handle Campus Direct Messaging
      socket.on('campus_direct_message', async (data: any) => {
        logger.info(`Campus Direct Message from ${data.fromName || data.fromUid} to ${data.toUid}:`, data.message);
        
        const { TelemetryService } = await import('../services/telemetry.service');
        TelemetryService.logNotification({
          type: 'CAMPUS_BROADCAST',
          targetUid: data.toUid,
          title: `💬 Message from ${data.fromName || data.fromUid}`,
          body: data.message || '',
          channel: 'SOCKET_IO',
          status: 'DELIVERED',
          metadata: data
        });

        // Broadcast to specific recipient room and campus bus
        if (data.toUid) {
          socket.to(`user:${data.toUid}`).emit('campus_direct_message', data);
        }
        socket.to('campus_broadcast').emit('campus_direct_message', data);
        SocketManager.broadcastAll('campus_direct_message', data);
      });

      // Join class session room
      socket.on('join:session', (sessionId: string) => {
        socket.join(`session:${sessionId}`);
        logger.debug(`Socket ${socket.id} joined session:${sessionId}`);
      });

      // Leave class session room
      socket.on('leave:session', (sessionId: string) => {
        socket.leave(`session:${sessionId}`);
        logger.debug(`Socket ${socket.id} left session:${sessionId}`);
      });

      socket.on('disconnect', (reason) => {
        logger.info(`Socket client disconnected: ${socket.id} (${reason})`);
      });
    });

    return this.io;
  }

  static getIO(): SocketIOServer {
    if (!this.io) {
      throw new Error('SocketManager not initialized yet');
    }
    return this.io;
  }

  /**
   * Broadcasts to all connected clients
   */
  static broadcastAll(event: string, data: any): void {
    if (this.io) {
      this.io.emit(event, data);
    }
  }

  /**
   * Broadcasts to a specific class session room
   */
  static emitToSession(sessionId: string, event: SocketEvent, data: any): void {
    if (this.io) {
      this.io.to(`session:${sessionId}`).emit(event, data);
    }
  }

  /**
   * Broadcasts to an individual user
   */
  static emitToUser(userId: string, event: SocketEvent, data: any): void {
    if (this.io) {
      this.io.to(`user:${userId}`).emit(event, data);
    }
  }

  /**
   * Broadcasts to a role group (e.g. all Admins / Principals)
   */
  static emitToRole(role: UserRole, event: SocketEvent, data: any): void {
    if (this.io) {
      this.io.to(`role:${role}`).emit(event, data);
    }
  }
}
