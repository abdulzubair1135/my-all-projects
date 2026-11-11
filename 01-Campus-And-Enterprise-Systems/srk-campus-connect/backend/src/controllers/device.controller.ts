import { Request, Response, NextFunction } from 'express';
import { DeviceService } from '../services/device.service';
import { ResponseUtil } from '../utils/response';
import { Device } from '../models/Device';

export class DeviceController {
  static async registerDevice(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { deviceId, platform, publicKey, pushToken, appVersion } = req.body;
      if (!deviceId || !platform || !publicKey) {
        ResponseUtil.error(res, 'deviceId, platform, and publicKey are required', 400);
        return;
      }

      if (!req.user) {
        ResponseUtil.error(res, 'Unauthorized', 401);
        return;
      }

      const device = await DeviceService.registerOrUpdateDevice(
        req.user._id,
        deviceId,
        platform,
        publicKey,
        pushToken,
        appVersion
      );

      ResponseUtil.success(res, device, 'Device registered successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async getMyDevices(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      if (!req.user) {
        ResponseUtil.error(res, 'Unauthorized', 401);
        return;
      }

      const devices = await Device.find({ userId: req.user._id });
      ResponseUtil.success(res, devices, 'User devices retrieved');
    } catch (error: any) {
      next(error);
    }
  }
}
