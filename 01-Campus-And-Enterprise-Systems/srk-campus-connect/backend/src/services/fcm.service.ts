import { initializeApp, cert, getApps, App } from 'firebase-admin/app';
import { getMessaging, Message } from 'firebase-admin/messaging';
import { logger } from '../utils/logger';

import { TelemetryService } from './telemetry.service';

export class FCMService {
  private static app: App | null = null;
  private static isInitialized = false;

  static initialize() {
    if (this.isInitialized) return;

    try {
      if (process.env.FIREBASE_SERVICE_ACCOUNT) {
        const serviceAccount = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT);
        if (getApps().length === 0) {
          this.app = initializeApp({
            credential: cert(serviceAccount)
          });
        } else {
          this.app = getApps()[0];
        }
        this.isInitialized = true;
        logger.info('Firebase Admin SDK initialized successfully.');
      } else {
        logger.info('Firebase Admin running in mock/direct mode (set FIREBASE_SERVICE_ACCOUNT for live cloud FCM).');
      }
    } catch (error) {
      logger.warn('Failed to initialize Firebase Admin SDK. Fallback mode active:', error);
    }
  }

  // Send High Priority Urgent Summon to Teacher's Phone via FCM
  static async sendUrgentSummonNotification(params: {
    deviceToken?: string;
    facultyName: string;
    targetUid?: string;
    callerName: string;
    location: string;
    meetingId: string;
    reason: string;
  }): Promise<boolean> {
    const { deviceToken, facultyName, targetUid, callerName, location, meetingId, reason } = params;

    logger.info(`[FCM Push] Dispatched Urgent Summon to ${facultyName} (${location})`);

    TelemetryService.logNotification({
      type: 'URGENT_SUMMON',
      targetUid: targetUid || facultyName,
      title: '🚨 URGENT: Principal Cabin Summon',
      body: `${callerName} summoned you to ${location}. Reason: ${reason}`,
      room: location,
      channel: 'HYBRID',
      status: 'DELIVERED',
      metadata: { meetingId, callerName }
    });

    if (this.isInitialized && this.app && deviceToken && deviceToken.length > 10) {
      try {
        const message: Message = {
          token: deviceToken,
          notification: {
            title: '🚨 URGENT: Principal Cabin Summon',
            body: `${callerName} has summoned you to ${location}. Reason: ${reason}`
          },
          data: {
            type: 'URGENT_CABIN_CALL',
            meetingId,
            caller: callerName,
            location,
            reason
          },
          android: {
            priority: 'high',
            notification: {
              channelId: 'srk_urgent_summon_channel',
              sound: 'default',
              color: '#EF4444'
            }
          }
        };
        await getMessaging(this.app).send(message);
        return true;
      } catch (err) {
        logger.error('Error sending FCM push message:', err);
      }
    }
    return true;
  }

  // Send Broadcast / Campus Announcement Notification via FCM
  static async sendCampusBroadcast(params: {
    title: string;
    message: string;
    priority: 'HIGH' | 'EMERGENCY' | 'NORMAL';
    topic?: string;
  }): Promise<boolean> {
    const { title, message, priority, topic = 'campus_all' } = params;

    logger.info(`[FCM Push] Dispatched Campus Broadcast: "${title}" to topic ${topic}`);

    if (this.isInitialized && this.app) {
      try {
        await getMessaging(this.app).send({
          topic,
          notification: {
            title: `📢 ${title}`,
            body: message
          },
          data: {
            type: 'CAMPUS_BROADCAST',
            priority
          }
        });
        return true;
      } catch (err) {
        logger.error('Error sending topic broadcast:', err);
      }
    }
    return true;
  }
}
