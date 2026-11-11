import mongoose, { Schema, Document } from 'mongoose';

export interface IShelter extends Document {
  name: string;
  address: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  capacity: number;
  occupied: number;
  waterAvailable: boolean;
  foodAvailable: boolean;
  medicalAvailable: boolean;
  status: 'OPEN' | 'FULL' | 'CLOSED' | 'EVACUATING';
  managedBy?: string;
}

const ShelterSchema: Schema = new Schema(
  {
    name: { type: String, required: true },
    address: { type: String, required: true },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], required: true }
    },
    capacity: { type: Number, default: 500 },
    occupied: { type: Number, default: 120 },
    waterAvailable: { type: Boolean, default: true },
    foodAvailable: { type: Boolean, default: true },
    medicalAvailable: { type: Boolean, default: true },
    status: {
      type: String,
      enum: ['OPEN', 'FULL', 'CLOSED', 'EVACUATING'],
      default: 'OPEN'
    },
    managedBy: { type: String, default: 'District Disaster Management Authority' }
  },
  { timestamps: true }
);

ShelterSchema.index({ location: '2dsphere' });

export const Shelter = mongoose.model<IShelter>('Shelter', ShelterSchema);
