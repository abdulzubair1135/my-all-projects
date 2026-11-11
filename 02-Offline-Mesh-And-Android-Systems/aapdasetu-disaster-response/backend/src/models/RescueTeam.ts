import mongoose, { Schema, Document } from 'mongoose';

export interface IRescueTeam extends Document {
  name: string;
  contactNumber: string;
  organizationId?: string;
  teamType: 'NDRF' | 'SDRF' | 'FIRE_RESCUE' | 'MEDICAL_EMS' | 'POLICE' | 'CIVIL_DEFENSE' | 'VOLUNTEER_GROUP';
  membersCount: number;
  vehicle: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  status: 'AVAILABLE' | 'ASSIGNED' | 'EN_ROUTE' | 'ON_SCENE' | 'OFFLINE';
  currentAssignment?: mongoose.Types.ObjectId;
  lastSeen: Date;
}

const RescueTeamSchema: Schema = new Schema(
  {
    name: { type: String, required: true },
    contactNumber: { type: String, required: true },
    organizationId: { type: String },
    teamType: {
      type: String,
      enum: ['NDRF', 'SDRF', 'FIRE_RESCUE', 'MEDICAL_EMS', 'POLICE', 'CIVIL_DEFENSE', 'VOLUNTEER_GROUP'],
      default: 'NDRF'
    },
    membersCount: { type: Number, default: 4 },
    vehicle: { type: String, default: 'Rescue Van' },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], default: [72.5714, 23.0225] }
    },
    status: {
      type: String,
      enum: ['AVAILABLE', 'ASSIGNED', 'EN_ROUTE', 'ON_SCENE', 'OFFLINE'],
      default: 'AVAILABLE',
      index: true
    },
    currentAssignment: { type: Schema.Types.ObjectId, ref: 'SOSEvent' },
    lastSeen: { type: Date, default: Date.now }
  },
  { timestamps: true }
);

RescueTeamSchema.index({ location: '2dsphere' });

export const RescueTeam = mongoose.model<IRescueTeam>('RescueTeam', RescueTeamSchema);
