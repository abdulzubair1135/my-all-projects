import mongoose, { Schema, Document } from 'mongoose';

export interface ISOSRelay extends Document {
  eventId: string;
  originDeviceId: string;
  relayDeviceId: string;
  fromDeviceId: string;
  toDeviceId?: string;
  hopCount: number;
  receivedAt: Date;
  forwardedAt?: Date;
  networkAvailable: boolean;
  uploadedToServer: boolean;
}

const SOSRelaySchema: Schema = new Schema(
  {
    eventId: { type: String, required: true, index: true },
    originDeviceId: { type: String, required: true },
    relayDeviceId: { type: String, required: true, index: true },
    fromDeviceId: { type: String, required: true },
    toDeviceId: { type: String },
    hopCount: { type: Number, default: 1 },
    receivedAt: { type: Date, default: Date.now },
    forwardedAt: { type: Date },
    networkAvailable: { type: Boolean, default: false },
    uploadedToServer: { type: Boolean, default: true }
  },
  { timestamps: true }
);

export const SOSRelay = mongoose.model<ISOSRelay>('SOSRelay', SOSRelaySchema);
