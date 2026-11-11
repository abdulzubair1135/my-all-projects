import mongoose, { Schema, Document } from 'mongoose';

export interface IVolunteer extends Document {
  userId: mongoose.Types.ObjectId;
  name: string;
  phone: string;
  skills: string[];
  availability: 'AVAILABLE' | 'ASSIGNED' | 'BUSY' | 'OFFLINE';
  vehicle: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  status: 'ACTIVE' | 'INACTIVE';
  lastActive: Date;
}

const VolunteerSchema: Schema = new Schema(
  {
    userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    name: { type: String, required: true },
    phone: { type: String, required: true },
    skills: { type: [String], default: ['First Aid', 'Search & Rescue'] },
    availability: {
      type: String,
      enum: ['AVAILABLE', 'ASSIGNED', 'BUSY', 'OFFLINE'],
      default: 'AVAILABLE',
      index: true
    },
    vehicle: { type: String, default: 'Two-Wheeler' },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], default: [72.5714, 23.0225] }
    },
    status: { type: String, enum: ['ACTIVE', 'INACTIVE'], default: 'ACTIVE' },
    lastActive: { type: Date, default: Date.now }
  },
  { timestamps: true }
);

VolunteerSchema.index({ location: '2dsphere' });

export const Volunteer = mongoose.model<IVolunteer>('Volunteer', VolunteerSchema);
