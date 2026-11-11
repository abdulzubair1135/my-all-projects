import { SocketManager } from '../sockets/socket.manager';
import { logger } from '../utils/logger';

export interface AuthTelemetryEvent {
  id: string;
  type: 'LOGIN' | 'SIGNUP' | 'OTP_REQUEST';
  uid?: string;
  name?: string;
  role?: string;
  email?: string;
  ip?: string;
  userAgent?: string;
  status: 'SUCCESS' | 'FAILED';
  error?: string;
  timestamp: string;
}

export interface ApiRequestTelemetryEvent {
  id: string;
  method: string;
  url: string;
  status: number;
  durationMs: number;
  ip?: string;
  userAgent?: string;
  timestamp: string;
  error?: string;
}

export interface NotificationTelemetryEvent {
  id: string;
  type: 'FCM_PUSH' | 'URGENT_SUMMON' | 'CAMPUS_BROADCAST' | 'TEACHER_RESPONSE';
  targetUid?: string;
  title: string;
  body: string;
  room?: string;
  channel: 'FCM_PUSH' | 'SOCKET_IO' | 'HYBRID';
  status: 'DELIVERED' | 'DISPATCHED' | 'FAILED' | 'ACKNOWLEDGED';
  error?: string;
  timestamp: string;
  metadata?: any;
}

export interface ErrorTelemetryEvent {
  id: string;
  message: string;
  stack?: string;
  endpoint?: string;
  method?: string;
  ip?: string;
  timestamp: string;
}

export class TelemetryService {
  private static readonly MAX_BUFFER = 250;

  private static authEvents: AuthTelemetryEvent[] = [];
  private static apiRequests: ApiRequestTelemetryEvent[] = [];
  private static notifications: NotificationTelemetryEvent[] = [];
  private static errors: ErrorTelemetryEvent[] = [];

  private static metrics = {
    totalLogins: 0,
    totalSignups: 0,
    totalRequests: 0,
    totalErrors: 0,
    totalNotifications: 0,
    serverStartTime: new Date().toISOString()
  };

  /**
   * Logs an authentication event (Login, Signup, OTP)
   */
  static logAuth(event: Omit<AuthTelemetryEvent, 'id' | 'timestamp'>): void {
    const fullEvent: AuthTelemetryEvent = {
      ...event,
      id: `AUTH_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
      timestamp: new Date().toISOString()
    };

    if (event.type === 'LOGIN' && event.status === 'SUCCESS') this.metrics.totalLogins++;
    if (event.type === 'SIGNUP' && event.status === 'SUCCESS') this.metrics.totalSignups++;

    this.authEvents.unshift(fullEvent);
    if (this.authEvents.length > this.MAX_BUFFER) this.authEvents.pop();

    try {
      SocketManager.broadcastAll('telemetry_auth', fullEvent);
    } catch (e) {
      // safe fallback
    }
  }

  /**
   * Logs an incoming API HTTP request
   */
  static logApiRequest(event: Omit<ApiRequestTelemetryEvent, 'id' | 'timestamp'>): void {
    const fullEvent: ApiRequestTelemetryEvent = {
      ...event,
      id: `REQ_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
      timestamp: new Date().toISOString()
    };

    this.metrics.totalRequests++;

    this.apiRequests.unshift(fullEvent);
    if (this.apiRequests.length > this.MAX_BUFFER) this.apiRequests.pop();

    try {
      SocketManager.broadcastAll('telemetry_api', fullEvent);
    } catch (e) {}
  }

  /**
   * Logs a notification or urgent summon delivery
   */
  static logNotification(event: Omit<NotificationTelemetryEvent, 'id' | 'timestamp'>): void {
    const fullEvent: NotificationTelemetryEvent = {
      ...event,
      id: `NOTIF_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
      timestamp: new Date().toISOString()
    };

    this.metrics.totalNotifications++;

    this.notifications.unshift(fullEvent);
    if (this.notifications.length > this.MAX_BUFFER) this.notifications.pop();

    try {
      SocketManager.broadcastAll('telemetry_notification', fullEvent);
    } catch (e) {}
  }

  /**
   * Logs an unhandled error or API exception
   */
  static logError(event: Omit<ErrorTelemetryEvent, 'id' | 'timestamp'>): void {
    const fullEvent: ErrorTelemetryEvent = {
      ...event,
      id: `ERR_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
      timestamp: new Date().toISOString()
    };

    this.metrics.totalErrors++;

    this.errors.unshift(fullEvent);
    if (this.errors.length > this.MAX_BUFFER) this.errors.pop();

    try {
      SocketManager.broadcastAll('telemetry_error', fullEvent);
    } catch (e) {}
  }

  /**
   * Returns comprehensive snapshot for Web Control Panel
   */
  static getDashboardSnapshot(): any {
    return {
      metrics: {
        ...this.metrics,
        uptimeSeconds: Math.floor(process.uptime()),
        memoryUsageMb: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
        activeBufferCounts: {
          auth: this.authEvents.length,
          apiRequests: this.apiRequests.length,
          notifications: this.notifications.length,
          errors: this.errors.length
        }
      },
      recentAuth: this.authEvents.slice(0, 50),
      recentRequests: this.apiRequests.slice(0, 50),
      recentNotifications: this.notifications.slice(0, 50),
      recentErrors: this.errors.slice(0, 50)
    };
  }
}
