import mongoose, { Schema, Document } from 'mongoose';

export interface INGO extends Document {
  organizationName: string;
  registrationNumber: string;
  contact: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  verificationStatus: 'VERIFIED' | 'PENDING' | 'REJECTED';
}

const NGOSchema: Schema = new Schema(
  {
    organizationName: { type: String, required: true },
    registrationNumber: { type: String, required: true },
    contact: { type: String, required: true },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], required: true }
    },
    verificationStatus: {
      type: String,
      enum: ['VERIFIED', 'PENDING', 'REJECTED'],
      default: 'VERIFIED'
    }
  },
  { timestamps: true }
);

NGOSchema.index({ location: '2dsphere' });

export const NGO = mongoose.model<INGO>('NGO', NGOSchema);
