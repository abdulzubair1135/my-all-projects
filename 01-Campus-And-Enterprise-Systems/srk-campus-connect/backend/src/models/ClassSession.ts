import mongoose, { Document, Schema } from 'mongoose';
import { ClassSessionStatus } from '../constants/enums';

export interface IClassSession extends Document {
  _id: mongoose.Types.ObjectId;
  sessionId: string;
  timetableId?: mongoose.Types.ObjectId;
  facultyId: mongoose.Types.ObjectId;
  subjectId: mongoose.Types.ObjectId;
  roomId: mongoose.Types.ObjectId;
  startTime: Date;
  endTime?: Date;
  status: ClassSessionStatus;
  currentQrNonce?: string;
  qrExpiresAt?: Date;
  createdAt: Date;
  endedAt?: Date;
}

const ClassSessionSchema = new Schema<IClassSession>(
  {
    sessionId: { type: String, required: true, unique: true, index: true },
    timetableId: { type: Schema.Types.ObjectId, ref: 'Timetable', index: true },
    facultyId: { type: Schema.Types.ObjectId, ref: 'Faculty', required: true, index: true },
    subjectId: { type: Schema.Types.ObjectId, ref: 'Subject', required: true, index: true },
    roomId: { type: Schema.Types.ObjectId, ref: 'Room', required: true, index: true },
    startTime: { type: Date, default: Date.now, index: true },
    endTime: { type: Date },
    status: {
      type: String,
      enum: Object.values(ClassSessionStatus),
      default: ClassSessionStatus.ACTIVE,
      index: true
    },
    currentQrNonce: { type: String },
    qrExpiresAt: { type: Date },
    endedAt: { type: Date }
  },
  {
    timestamps: true
  }
);

ClassSessionSchema.index({ facultyId: 1, status: 1 });
ClassSessionSchema.index({ roomId: 1, status: 1 });

export const ClassSession = mongoose.model<IClassSession>('ClassSession', ClassSessionSchema);
