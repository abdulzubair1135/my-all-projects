import mongoose, { Schema, Document } from 'mongoose';

export interface IResourceRequest extends Document {
  requestedBy: string;
  requesterRole: string;
  resourceType: string;
  quantity: number;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'PENDING' | 'APPROVED' | 'DISPATCHED' | 'FULFILLED' | 'REJECTED';
}

const ResourceRequestSchema: Schema = new Schema(
  {
    requestedBy: { type: String, required: true },
    requesterRole: { type: String, default: 'SHELTER_MANAGER' },
    resourceType: { type: String, required: true },
    quantity: { type: Number, required: true },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], required: true }
    },
    priority: {
      type: String,
      enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
      default: 'HIGH'
    },
    status: {
      type: String,
      enum: ['PENDING', 'APPROVED', 'DISPATCHED', 'FULFILLED', 'REJECTED'],
      default: 'PENDING',
      index: true
    }
  },
  { timestamps: true }
);

ResourceRequestSchema.index({ location: '2dsphere' });

export const ResourceRequest = mongoose.model<IResourceRequest>('ResourceRequest', ResourceRequestSchema);
