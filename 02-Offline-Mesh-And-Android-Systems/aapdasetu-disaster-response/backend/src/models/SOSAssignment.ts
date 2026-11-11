import mongoose, { Schema, Document } from 'mongoose';

export interface ISOSAssignment extends Document {
  sosId: mongoose.Types.ObjectId;
  eventId: string;
  rescueTeamId: mongoose.Types.ObjectId;
  assignedBy?: mongoose.Types.ObjectId;
  assignedAt: Date;
  acceptedAt?: Date;
  enRouteAt?: Date;
  arrivedAt?: Date;
  resolvedAt?: Date;
  status: 'ASSIGNED' | 'ACCEPTED' | 'EN_ROUTE' | 'ARRIVED' | 'RESOLVED' | 'CANCELLED';
  notes?: string;
}

const SOSAssignmentSchema: Schema = new Schema(
  {
    sosId: { type: Schema.Types.ObjectId, ref: 'SOSEvent', required: true, index: true },
    eventId: { type: String, required: true },
    rescueTeamId: { type: Schema.Types.ObjectId, ref: 'RescueTeam', required: true, index: true },
    assignedBy: { type: Schema.Types.ObjectId, ref: 'User' },
    assignedAt: { type: Date, default: Date.now },
    acceptedAt: { type: Date },
    enRouteAt: { type: Date },
    arrivedAt: { type: Date },
    resolvedAt: { type: Date },
    status: {
      type: String,
      enum: ['ASSIGNED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED', 'RESOLVED', 'CANCELLED'],
      default: 'ASSIGNED',
      index: true
    },
    notes: { type: String }
  },
  { timestamps: true }
);

export const SOSAssignment = mongoose.model<ISOSAssignment>('SOSAssignment', SOSAssignmentSchema);
