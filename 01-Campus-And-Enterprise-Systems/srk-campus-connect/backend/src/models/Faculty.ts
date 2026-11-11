import mongoose, { Document, Schema } from 'mongoose';
import { FacultyStatus } from '../constants/enums';

export interface IFaculty extends Document {
  _id: mongoose.Types.ObjectId;
  userId: mongoose.Types.ObjectId;
  employeeId: string;
  departmentId: mongoose.Types.ObjectId;
  designation: string;
  subjects: mongoose.Types.ObjectId[];
  currentStatus: FacultyStatus;
  statusUpdatedAt: Date;
  suggestedStatus?: FacultyStatus;
  currentLocation?: {
    roomId?: mongoose.Types.ObjectId;
    confidence: number;
    lastVerified: Date;
  };
  createdAt: Date;
  updatedAt: Date;
}

const FacultySchema = new Schema<IFaculty>(
  {
    userId: { type: Schema.Types.ObjectId, ref: 'User', required: true, unique: true, index: true },
    employeeId: { type: String, required: true, unique: true, uppercase: true, trim: true, index: true },
    departmentId: { type: Schema.Types.ObjectId, ref: 'Department', required: true, index: true },
    designation: { type: String, required: true, trim: true },
    subjects: [{ type: Schema.Types.ObjectId, ref: 'Subject' }],
    currentStatus: {
      type: String,
      enum: Object.values(FacultyStatus),
      default: FacultyStatus.AVAILABLE,
      index: true
    },
    statusUpdatedAt: { type: Date, default: Date.now },
    suggestedStatus: { type: String, enum: Object.values(FacultyStatus) },
    currentLocation: {
      roomId: { type: Schema.Types.ObjectId, ref: 'Room' },
      confidence: { type: Number, default: 0, min: 0, max: 100 },
      lastVerified: { type: Date, default: Date.now }
    }
  },
  {
    timestamps: true
  }
);

export const Faculty = mongoose.model<IFaculty>('Faculty', FacultySchema);
