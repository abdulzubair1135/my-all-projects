import mongoose, { Schema, Document } from 'mongoose';

export interface IHospital extends Document {
  name: string;
  phone: string;
  address: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  emergencyStatus: 'NORMAL' | 'HIGH_ALERT' | 'OVERWHELMED' | 'DIVERTING';
  totalBeds: number;
  availableBeds: number;
  icuBeds: number;
  availableICUBeds: number;
  ambulances: number;
  availableAmbulances: number;
  bloodAvailability: {
    aPos: number;
    aNeg: number;
    bPos: number;
    bNeg: number;
    abPos: number;
    abNeg: number;
    oPos: number;
    oNeg: number;
  };
  updatedBy?: mongoose.Types.ObjectId;
}

const HospitalSchema: Schema = new Schema(
  {
    name: { type: String, required: true },
    phone: { type: String, required: true },
    address: { type: String, required: true },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], required: true }
    },
    emergencyStatus: {
      type: String,
      enum: ['NORMAL', 'HIGH_ALERT', 'OVERWHELMED', 'DIVERTING'],
      default: 'NORMAL'
    },
    totalBeds: { type: Number, default: 100 },
    availableBeds: { type: Number, default: 25 },
    icuBeds: { type: Number, default: 20 },
    availableICUBeds: { type: Number, default: 5 },
    ambulances: { type: Number, default: 6 },
    availableAmbulances: { type: Number, default: 2 },
    bloodAvailability: {
      aPos: { type: Number, default: 10 },
      aNeg: { type: Number, default: 4 },
      bPos: { type: Number, default: 12 },
      bNeg: { type: Number, default: 3 },
      abPos: { type: Number, default: 5 },
      abNeg: { type: Number, default: 2 },
      oPos: { type: Number, default: 15 },
      oNeg: { type: Number, default: 6 }
    },
    updatedBy: { type: Schema.Types.ObjectId, ref: 'User' }
  },
  { timestamps: true }
);

HospitalSchema.index({ location: '2dsphere' });

export const Hospital = mongoose.model<IHospital>('Hospital', HospitalSchema);
