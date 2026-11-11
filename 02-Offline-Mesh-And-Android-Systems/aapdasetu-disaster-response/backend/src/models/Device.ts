import mongoose, { Schema, Document } from 'mongoose';

export interface IDevice extends Document {
  deviceId: string;
  userId?: mongoose.Types.ObjectId;
  platform: string;
  appVersion?: string;
  bleEnabled: boolean;
  internetAvailable: boolean;
  batteryLevel?: number;
  location?: {
    type: 'Point';
    coordinates: [number, number]; // [longitude, latitude]
  };
  lastSeen: Date;
}

const DeviceSchema: Schema = new Schema(
  {
    deviceId: { type: String, required: true, unique: true, index: true },
    userId: { type: Schema.Types.ObjectId, ref: 'User' },
    platform: { type: String, default: 'Android' },
    appVersion: { type: String },
    bleEnabled: { type: Boolean, default: true },
    internetAvailable: { type: Boolean, default: false },
    batteryLevel: { type: Number },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], default: [0, 0] }
    },
    lastSeen: { type: Date, default: Date.now }
  },
  { timestamps: true }
);

DeviceSchema.index({ location: '2dsphere' });

export const Device = mongoose.model<IDevice>('Device', DeviceSchema);
