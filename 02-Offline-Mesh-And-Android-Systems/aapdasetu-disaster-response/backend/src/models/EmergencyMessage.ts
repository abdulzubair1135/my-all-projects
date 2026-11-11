import mongoose, { Schema, Document } from 'mongoose';

export interface IEmergencyMessage extends Document {
  messageId: string;
  senderDeviceId: string;
  senderUserId?: mongoose.Types.ObjectId;
  receiverDeviceId: string;
  type: 'CHAT' | 'SOS' | 'SOS_RELAY' | 'EMERGENCY_ALERT' | 'RESCUE_MESSAGE' | 'ACK';
  content: string;
  location?: {
    type: 'Point';
    coordinates: [number, number];
  };
  timestamp: number;
  ttl: number;
  hopCount: number;
  source: 'ONLINE' | 'OFFLINE_BLE' | 'BLE_RELAY';
  status: 'PENDING' | 'DELIVERED' | 'SEEN' | 'SYNCED';
  syncedAt: Date;
}

const EmergencyMessageSchema: Schema = new Schema(
  {
    messageId: { type: String, required: true, unique: true, index: true },
    senderDeviceId: { type: String, required: true, index: true },
    senderUserId: { type: Schema.Types.ObjectId, ref: 'User' },
    receiverDeviceId: { type: String, required: true, index: true },
    type: {
      type: String,
      enum: ['CHAT', 'SOS', 'SOS_RELAY', 'EMERGENCY_ALERT', 'RESCUE_MESSAGE', 'ACK'],
      default: 'CHAT'
    },
    content: { type: String, required: true },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], default: [0, 0] }
    },
    timestamp: { type: Number, required: true },
    ttl: { type: Number, default: 5 },
    hopCount: { type: Number, default: 0 },
    source: {
      type: String,
      enum: ['ONLINE', 'OFFLINE_BLE', 'BLE_RELAY'],
      default: 'ONLINE'
    },
    status: {
      type: String,
      enum: ['PENDING', 'DELIVERED', 'SEEN', 'SYNCED'],
      default: 'DELIVERED'
    },
    syncedAt: { type: Date, default: Date.now }
  },
  { timestamps: true }
);

EmergencyMessageSchema.index({ location: '2dsphere' });

export const EmergencyMessage = mongoose.model<IEmergencyMessage>('EmergencyMessage', EmergencyMessageSchema);
