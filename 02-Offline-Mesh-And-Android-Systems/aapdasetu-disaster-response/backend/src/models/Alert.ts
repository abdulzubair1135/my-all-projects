import mongoose, { Schema, Document } from 'mongoose';

export interface IAlert extends Document {
  title: string;
  message: string;
  type: string;
  severity: string;
  location?: {
    type: 'Point';
    coordinates: [number, number];
  };
  radiusKm?: number;
  source: string;
  createdBy?: mongoose.Types.ObjectId;
  expiresAt: Date;
  active: boolean;
}

const AlertSchema: Schema = new Schema(
  {
    title: { type: String, required: true },
    message: { type: String, required: true },
    type: {
      type: String,
      default: 'GENERAL',
      index: true
    },
    severity: {
      type: String,
      default: 'WARNING',
      index: true
    },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], default: [72.5714, 23.0225] }
    },
    radiusKm: { type: Number, default: 25 },
    source: {
      type: String,
      default: 'GOVERNMENT'
    },
    createdBy: { type: Schema.Types.ObjectId, ref: 'User' },
    expiresAt: { type: Date, required: true, index: true },
    active: { type: Boolean, default: true, index: true }
  },
  { timestamps: true }
);

AlertSchema.index({ location: '2dsphere' });

export const Alert = mongoose.model<IAlert>('Alert', AlertSchema);
