import { Device, IDevice } from '../models/Device';
import { DevicePlatform } from '../constants/enums';

export class DeviceService {
  static async registerOrUpdateDevice(
    userId: string,
    deviceId: string,
    platform: DevicePlatform,
    publicKey: string,
    pushToken?: string,
    appVersion?: string
  ): Promise<IDevice> {
    const existing = await Device.findOne({ deviceId });

    if (existing) {
      existing.userId = userId as any;
      existing.platform = platform;
      existing.publicKey = publicKey;
      if (pushToken) existing.pushToken = pushToken;
      if (appVersion) existing.appVersion = appVersion;
      existing.lastSeen = new Date();
      existing.lastSync = new Date();
      return await existing.save();
    }

    return await Device.create({
      userId,
      deviceId,
      platform,
      publicKey,
      pushToken,
      appVersion,
      lastSeen: new Date(),
      lastSync: new Date(),
      isTrusted: true
    });
  }

  static async getDevicePublicKey(deviceId: string): Promise<string | null> {
    const device = await Device.findOne({ deviceId, isTrusted: true });
    return device ? device.publicKey : null;
  }

  static async updateLastSeen(deviceId: string): Promise<void> {
    await Device.updateOne({ deviceId }, { lastSeen: new Date() });
  }
}
