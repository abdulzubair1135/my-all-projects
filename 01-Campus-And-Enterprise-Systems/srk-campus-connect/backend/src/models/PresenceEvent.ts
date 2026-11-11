import mongoose, { Document, Schema } from 'mongoose';
import { PresenceSource, SyncEventStatus } from '../constants/enums';

export interface IPresenceEvent extends Document {
  _id: mongoose.Types.ObjectId;
  eventId: string;
  userId: mongoose.Types.ObjectId;
  deviceId: string;
  sessionId: string;
  source: PresenceSource;
  confidence: number;
  timestamp: Date;
  signature: string;
  gatewayDeviceId?: string;
  syncStatus: SyncEventStatus;
  payload: Record<string, any>;
  createdAt: Date;
}

const PresenceEventSchema = new Schema<IPresenceEvent>(
  {
    eventId: { type: String, required: true, unique: true, index: true },
    userId: { type: Schema.Types.ObjectId, ref: 'User', required: true, index: true },
    deviceId: { type: String, required: true, index: true },
    sessionId: { type: String, required: true, index: true },
    source: {
      type: String,
      enum: Object.values(PresenceSource),
      required: true,
      index: true
    },
    confidence: { type: Number, required: true, min: 0, max: 100 },
    timestamp: { type: Date, required: true, index: true },
    signature: { type: String, required: true },
    gatewayDeviceId: { type: String, index: true },
    syncStatus: {
      type: String,
      enum: Object.values(SyncEventStatus),
      default: SyncEventStatus.PROCESSED,
      index: true
    },
    payload: { type: Schema.Types.Mixed, default: {} }
  },
  {
    timestamps: { createdAt: true, updatedAt: false }
  }
);

PresenceEventSchema.index({ sessionId: 1, userId: 1, timestamp: -1 });

export const PresenceEvent = mongoose.model<IPresenceEvent>('PresenceEvent', PresenceEventSchema);
