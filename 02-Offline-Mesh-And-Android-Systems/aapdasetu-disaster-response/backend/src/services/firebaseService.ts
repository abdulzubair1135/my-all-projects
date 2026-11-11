import { initializeApp, cert, getApps } from 'firebase-admin/app';
import { getMessaging, type Message } from 'firebase-admin/messaging';
import path from 'path';
import fs from 'fs';
let isFirebaseInitialized = false;
let messagingInstance: ReturnType<typeof getMessaging> | null = null;

try {
  const serviceAccountPath = path.resolve(process.cwd(), 'serviceAccountKey.json');
  if (fs.existsSync(serviceAccountPath)) {
    const serviceAccount = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    const app = getApps().length === 0
      ? initializeApp({ credential: cert(serviceAccount) })
      : getApps()[0];
    messagingInstance = getMessaging(app);
    isFirebaseInitialized = true;
    console.log('🔥 [Firebase] Admin SDK successfully initialized with project:', serviceAccount.project_id);
  } else {
    console.warn('⚠️ [Firebase] serviceAccountKey.json not found at ' + serviceAccountPath);
  }
} catch (error: any) {
  console.error('❌ [Firebase] Initialization error:', error.message);
}

export const sendEmergencyPushNotification = async (
  title: string,
  body: string,
  dataPayload?: Record<string, string>
) => {
  if (!isFirebaseInitialized || !messagingInstance) {
    console.warn('⚠️ [Firebase] Cannot send notification: Admin SDK not initialized.');
    return { success: false, reason: 'NOT_INITIALIZED' };
  }

  try {
    const message: Message = {
      topic: 'emergency_alerts',
      notification: {
        title,
        body
      },
      data: {
        click_action: 'FLUTTER_NOTIFICATION_CLICK',
        priority: 'high',
        sound: 'siren.wav',
        ...(dataPayload || {})
      },
      android: {
        priority: 'high',
        notification: {
          channelId: 'aapdasetu_notifications',
          sound: 'siren',
          priority: 'max',
          visibility: 'public',
          defaultVibrateTimings: true
        }
      }
    };

    const response = await messagingInstance.send(message);
    console.log('🚨 [Firebase FCM] Broadcast push sent successfully:', response);
    return { success: true, response };
  } catch (error: any) {
    console.error('❌ [Firebase FCM] Error sending push notification:', error.message);
    return { success: false, error: error.message };
  }
};

export const isFirebaseActive = () => isFirebaseInitialized;
