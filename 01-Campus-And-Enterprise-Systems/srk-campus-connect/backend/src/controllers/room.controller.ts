import { Request, Response, NextFunction } from 'express';
import { RoomService } from '../services/room.service';
import { ResponseUtil } from '../utils/response';
import { RoomStatus } from '../constants/enums';

export class RoomController {
  static async createRoom(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { roomNumber, building, capacity, departmentId, permanentQrCode } = req.body;
      if (!roomNumber || !building || !capacity) {
        ResponseUtil.error(res, 'roomNumber, building, and capacity are required', 400);
        return;
      }
      const room = await RoomService.createRoom({
        roomNumber,
        building,
        capacity: Number(capacity),
        departmentId,
        permanentQrCode
      });
      ResponseUtil.success(res, room, 'Room created successfully', 201);
    } catch (error: any) {
      next(error);
    }
  }

  static async getAllRooms(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { departmentId } = req.query;
      const rooms = await RoomService.getAllRooms(departmentId as string);
      ResponseUtil.success(res, rooms, 'Rooms retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async getRoomById(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const room = await RoomService.getRoomById(req.params.id);
      if (!room) {
        ResponseUtil.error(res, 'Room not found', 404);
        return;
      }
      ResponseUtil.success(res, room, 'Room retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async getRoomByQr(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { qrCode } = req.query;
      if (!qrCode) {
        ResponseUtil.error(res, 'qrCode query parameter is required', 400);
        return;
      }
      const room = await RoomService.getRoomByQr(qrCode as string);
      if (!room) {
        ResponseUtil.error(res, 'Invalid Room QR code', 404);
        return;
      }
      ResponseUtil.success(res, room, 'Room QR verified successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async updateRoom(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const room = await RoomService.updateRoom(req.params.id, req.body);
      if (!room) {
        ResponseUtil.error(res, 'Room not found', 404);
        return;
      }
      ResponseUtil.success(res, room, 'Room updated successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async updateRoomStatus(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { status } = req.body;
      if (!Object.values(RoomStatus).includes(status)) {
        ResponseUtil.error(res, 'Invalid room status', 400);
        return;
      }
      const room = await RoomService.updateRoomStatus(req.params.id, status);
      ResponseUtil.success(res, room, 'Room status updated successfully');
    } catch (error: any) {
      next(error);
    }
  }
}
