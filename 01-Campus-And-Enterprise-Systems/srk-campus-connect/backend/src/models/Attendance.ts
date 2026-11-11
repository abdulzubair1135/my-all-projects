import mongoose, { Document, Schema } from 'mongoose';
import { AttendanceStatus, PresenceSource } from '../constants/enums';

export interface IAttendance extends Document {
  _id: mongoose.Types.ObjectId;
  sessionId: string;
  studentId: mongoose.Types.ObjectId;
  status: AttendanceStatus;
  confidence: number;
  sources: PresenceSource[];
  checkInTime?: Date;
  checkOutTime?: Date;
  verifiedBy?: mongoose.Types.ObjectId;
  isManualOverride: boolean;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

const AttendanceSchema = new Schema<IAttendance>(
  {
    sessionId: { type: String, required: true, index: true },
    studentId: { type: Schema.Types.ObjectId, ref: 'Student', required: true, index: true },
    status: {
      type: String,
      enum: Object.values(AttendanceStatus),
      default: AttendanceStatus.ABSENT,
      index: true
    },
    confidence: { type: Number, default: 0, min: 0, max: 100 },
    sources: [{ type: String, enum: Object.values(PresenceSource) }],
    checkInTime: { type: Date },
    checkOutTime: { type: Date },
    verifiedBy: { type: Schema.Types.ObjectId, ref: 'Faculty' },
    isManualOverride: { type: Boolean, default: false },
    notes: { type: String }
  },
  {
    timestamps: true
  }
);

AttendanceSchema.index({ sessionId: 1, studentId: 1 }, { unique: true });
AttendanceSchema.index({ studentId: 1, status: 1 });

export const Attendance = mongoose.model<IAttendance>('Attendance', AttendanceSchema);
