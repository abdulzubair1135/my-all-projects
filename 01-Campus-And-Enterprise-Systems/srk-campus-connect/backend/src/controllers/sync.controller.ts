import { Request, Response, NextFunction } from 'express';
import { AttendanceService } from '../services/attendance.service';
import { ResponseUtil } from '../utils/response';

export class SyncController {
  /**
   * Ingest a batch of offline signed presence events from a client or peer gateway
   */
  static async ingestSyncEvents(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { gatewayDeviceId, events } = req.body;
      if (!events || !Array.isArray(events)) {
        ResponseUtil.error(res, 'events array is required', 400);
        return;
      }

      const result = await AttendanceService.ingestPresenceEvents(events, gatewayDeviceId);
      ResponseUtil.success(res, result, 'Batch sync completed', 200, {
        totalReceived: events.length,
        processedCount: result.processed.length,
        duplicateCount: result.duplicates.length,
        rejectedCount: result.rejected.length
      });
    } catch (error: any) {
      next(error);
    }
  }

  /**
   * Direct ingestion of a single presence event
   */
  static async ingestSingleEvent(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const event = req.body;
      if (!event || !event.eventId || !event.signature) {
        ResponseUtil.error(res, 'Valid signed presence event payload required', 400);
        return;
      }

      const result = await AttendanceService.ingestPresenceEvents([event]);
      if (result.rejected.length > 0) {
        ResponseUtil.error(res, `Event rejected: ${result.rejected[0].reason}`, 422, result.rejected[0]);
        return;
      }

      ResponseUtil.success(res, result, 'Presence event ingested successfully', 201);
    } catch (error: any) {
      next(error);
    }
  }
}
