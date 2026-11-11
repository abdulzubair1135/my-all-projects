import mongoose, { Schema, Document } from 'mongoose';

export interface ISOSEvent extends Document {
  eventId: string;
  userId?: mongoose.Types.ObjectId;
  userName?: string;
  userPhone?: string;
  originDeviceId: string;
  type: 'TRAPPED' | 'MEDICAL' | 'FIRE' | 'FLOOD' | 'BUILDING_COLLAPSE' | 'ACCIDENT' | 'MISSING_PERSON' | 'OTHER';
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  description?: string;
  peopleCount: number;
  injuredCount: number;
  location: {
    type: 'Point';
    coordinates: [number, number]; // [longitude, latitude]
  };
  locationAccuracy?: number;
  addressText?: string;
  status: 'CREATED' | 'RECEIVED' | 'VERIFIED' | 'ASSIGNED' | 'ACCEPTED' | 'EN_ROUTE' | 'ARRIVED' | 'RESOLVED' | 'CANCELLED';
  source: 'ONLINE' | 'OFFLINE_BLE' | 'BLE_RELAY';
  hopCount: number;
  relayPath: string[];
  assignedTeamId?: mongoose.Types.ObjectId;
  assignedTeamName?: string;
  verifiedBy?: mongoose.Types.ObjectId;
  resolvedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

const SOSEventSchema: Schema = new Schema(
  {
    eventId: { type: String, required: true, unique: true, index: true },
    userId: { type: Schema.Types.ObjectId, ref: 'User' },
    userName: { type: String },
    userPhone: { type: String },
    originDeviceId: { type: String, required: true, index: true },
    type: {
      type: String,
      enum: ['TRAPPED', 'MEDICAL', 'FIRE', 'FLOOD', 'BUILDING_COLLAPSE', 'ACCIDENT', 'MISSING_PERSON', 'OTHER'],
      default: 'MEDICAL',
      index: true
    },
    severity: {
      type: String,
      enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
      default: 'HIGH',
      index: true
    },
    description: { type: String, default: '' },
    peopleCount: { type: Number, default: 1 },
    injuredCount: { type: Number, default: 0 },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], required: true }
    },
    locationAccuracy: { type: Number, default: 10 },
    addressText: { type: String },
    status: {
      type: String,
      enum: ['CREATED', 'RECEIVED', 'VERIFIED', 'ASSIGNED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED', 'RESOLVED', 'CANCELLED'],
      default: 'RECEIVED',
      index: true
    },
    source: {
      type: String,
      enum: ['ONLINE', 'OFFLINE_BLE', 'BLE_RELAY'],
      default: 'ONLINE',
      index: true
    },
    hopCount: { type: Number, default: 0 },
    relayPath: { type: [String], default: [] },
    assignedTeamId: { type: Schema.Types.ObjectId, ref: 'RescueTeam' },
    assignedTeamName: { type: String },
    verifiedBy: { type: Schema.Types.ObjectId, ref: 'User' },
    resolvedAt: { type: Date }
  },
  { timestamps: true }
);

SOSEventSchema.index({ location: '2dsphere' });
SOSEventSchema.index({ createdAt: -1 });
SOSEventSchema.index({ status: 1, severity: 1 });

export const SOSEvent = mongoose.model<ISOSEvent>('SOSEvent', SOSEventSchema);
