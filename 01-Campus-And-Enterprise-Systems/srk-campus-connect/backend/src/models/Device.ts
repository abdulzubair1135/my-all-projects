import mongoose, { Document, Schema } from 'mongoose';
import { DevicePlatform } from '../constants/enums';

export interface IDevice extends Document {
  _id: mongoose.Types.ObjectId;
  userId: mongoose.Types.ObjectId;
  deviceId: string;
  platform: DevicePlatform;
  publicKey: string; // Base64 or Hex encoded Ed25519 public key
  pushToken?: string;
  lastSeen: Date;
  lastSync: Date;
  appVersion?: string;
  isTrusted: boolean;
  createdAt: Date;
  updatedAt: Date;
}

const DeviceSchema = new Schema<IDevice>(
  {
    userId: { type: Schema.Types.ObjectId, ref: 'User', required: true, index: true },
    deviceId: { type: String, required: true, unique: true, index: true },
    platform: {
      type: String,
      enum: Object.values(DevicePlatform),
      required: true
    },
    publicKey: { type: String, required: true },
    pushToken: { type: String },
    lastSeen: { type: Date, default: Date.now },
    lastSync: { type: Date, default: Date.now },
    appVersion: { type: String },
    isTrusted: { type: Boolean, default: true }
  },
  {
    timestamps: true
  }
);

export const Device = mongoose.model<IDevice>('Device', DeviceSchema);
