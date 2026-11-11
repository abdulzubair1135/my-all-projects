import mongoose, { Document, Schema } from 'mongoose';
import { RoomStatus } from '../constants/enums';

export interface IRoom extends Document {
  _id: mongoose.Types.ObjectId;
  roomNumber: string;
  building: string;
  capacity: number;
  departmentId?: mongoose.Types.ObjectId;
  permanentQrCode: string;
  status: RoomStatus;
  createdAt: Date;
  updatedAt: Date;
}

const RoomSchema = new Schema<IRoom>(
  {
    roomNumber: { type: String, required: true, uppercase: true, trim: true, index: true },
    building: { type: String, required: true, trim: true },
    capacity: { type: Number, required: true, min: 1 },
    departmentId: { type: Schema.Types.ObjectId, ref: 'Department', index: true },
    permanentQrCode: { type: String, required: true, unique: true, index: true },
    status: {
      type: String,
      enum: Object.values(RoomStatus),
      default: RoomStatus.AVAILABLE,
      index: true
    }
  },
  {
    timestamps: true
  }
);

RoomSchema.index({ building: 1, roomNumber: 1 }, { unique: true });

export const Room = mongoose.model<IRoom>('Room', RoomSchema);
