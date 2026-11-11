import mongoose, { Document, Schema } from 'mongoose';
import { MeetingRequestStatus } from '../constants/enums';

export interface IMeetingRequest extends Document {
  _id: mongoose.Types.ObjectId;
  fromUserId: mongoose.Types.ObjectId;
  toFacultyId: mongoose.Types.ObjectId;
  type: 'MEETING' | 'CALL' | 'URGENT_CABIN_CALL';
  priority: 'URGENT' | 'NORMAL';
  reason: string;
  status: MeetingRequestStatus | 'BUSY_IN_CLASS' | 'ON_THE_WAY';
  scheduledTime?: Date;
  responseNote?: string;
  autoDetails?: Record<string, any>;
  transitEta?: string;
  createdAt: Date;
  updatedAt: Date;
}

const MeetingRequestSchema = new Schema<IMeetingRequest>(
  {
    fromUserId: { type: Schema.Types.ObjectId, ref: 'User', required: true, index: true },
    toFacultyId: { type: Schema.Types.ObjectId, ref: 'Faculty', required: true, index: true },
    type: { type: String, enum: ['MEETING', 'CALL', 'URGENT_CABIN_CALL'], default: 'URGENT_CABIN_CALL' },
    priority: { type: String, enum: ['URGENT', 'NORMAL'], default: 'URGENT' },
    reason: { type: String, required: true, trim: true },
    status: {
      type: String,
      default: MeetingRequestStatus.PENDING,
      index: true
    },
    scheduledTime: { type: Date },
    responseNote: { type: String, trim: true },
    autoDetails: { type: Schema.Types.Mixed },
    transitEta: { type: String, default: '2 mins' }
  },
  {
    timestamps: true
  }
);

export const MeetingRequest = mongoose.model<IMeetingRequest>('MeetingRequest', MeetingRequestSchema);
