import mongoose, { Schema, Document } from 'mongoose';

export interface IIncident extends Document {
  title: string;
  description: string;
  type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  radiusKm: number;
  status: 'OPEN' | 'IN_PROGRESS' | 'CONTAINED' | 'RESOLVED';
  createdBy?: mongoose.Types.ObjectId;
  verifiedBy?: mongoose.Types.ObjectId;
}

const IncidentSchema: Schema = new Schema(
  {
    title: { type: String, required: true },
    description: { type: String, required: true },
    type: { type: String, required: true, index: true },
    severity: {
      type: String,
      enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
      default: 'HIGH'
    },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], required: true }
    },
    radiusKm: { type: Number, default: 5 },
    status: {
      type: String,
      enum: ['OPEN', 'IN_PROGRESS', 'CONTAINED', 'RESOLVED'],
      default: 'OPEN',
      index: true
    },
    createdBy: { type: Schema.Types.ObjectId, ref: 'User' },
    verifiedBy: { type: Schema.Types.ObjectId, ref: 'User' }
  },
  { timestamps: true }
);

IncidentSchema.index({ location: '2dsphere' });

export const Incident = mongoose.model<IIncident>('Incident', IncidentSchema);
