import { Room, IRoom } from '../models/Room';
import { RoomStatus } from '../constants/enums';

export class RoomService {
  static async createRoom(data: {
    roomNumber: string;
    building: string;
    capacity: number;
    departmentId?: string;
    permanentQrCode?: string;
  }): Promise<IRoom> {
    const existing = await Room.findOne({
      building: data.building,
      roomNumber: data.roomNumber.toUpperCase()
    });
    if (existing) {
      throw new Error(`Room ${data.roomNumber} in ${data.building} already exists`);
    }

    const permanentQrCode = data.permanentQrCode || `CAMPUS_ROOM_V1:${data.building.toUpperCase()}-${data.roomNumber.toUpperCase()}`;

    return await Room.create({
      roomNumber: data.roomNumber.toUpperCase(),
      building: data.building,
      capacity: data.capacity,
      departmentId: data.departmentId,
      permanentQrCode,
      status: RoomStatus.AVAILABLE
    });
  }

  static async getAllRooms(departmentId?: string): Promise<IRoom[]> {
    const query: any = {};
    if (departmentId) query.departmentId = departmentId;
    return await Room.find(query).populate('departmentId', 'name code');
  }

  static async getRoomById(id: string): Promise<IRoom | null> {
    return await Room.findById(id).populate('departmentId');
  }

  static async getRoomByQr(qrCode: string): Promise<IRoom | null> {
    return await Room.findOne({ permanentQrCode: qrCode });
  }

  static async updateRoom(id: string, updateData: Partial<IRoom>): Promise<IRoom | null> {
    if (updateData.roomNumber) {
      updateData.roomNumber = updateData.roomNumber.toUpperCase();
    }
    return await Room.findByIdAndUpdate(id, updateData, { new: true, runValidators: true });
  }

  static async updateRoomStatus(id: string, status: RoomStatus): Promise<IRoom | null> {
    return await Room.findByIdAndUpdate(id, { status }, { new: true });
  }
}
