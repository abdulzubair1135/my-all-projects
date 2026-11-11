import mongoose, { Schema, Document } from 'mongoose';

export interface ICitizenReport extends Document {
  userId?: mongoose.Types.ObjectId;
  userName?: string;
  userPhone?: string;
  type: 'FLOOD' | 'FIRE' | 'BLOCKED_ROAD' | 'COLLAPSED_BUILDING' | 'MISSING_PERSON' | 'DANGEROUS_AREA' | 'DAMAGED_INFRASTRUCTURE' | 'MEDICAL_EMERGENCY' | 'OTHER';
  description: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  images?: string[];
  mediaUrl?: string;
  addressText?: string;
  verificationStatus: 'SUBMITTED' | 'UNDER_REVIEW' | 'VERIFIED' | 'REJECTED' | 'ACTION_TAKEN';
  verifiedBy?: mongoose.Types.ObjectId;
  verifiedAt?: Date;
}

const CitizenReportSchema: Schema = new Schema(
  {
    userId: { type: Schema.Types.ObjectId, ref: 'User' },
    userName: { type: String },
    userPhone: { type: String },
    type: {
      type: String,
      enum: ['FLOOD', 'FIRE', 'BLOCKED_ROAD', 'COLLAPSED_BUILDING', 'MISSING_PERSON', 'DANGEROUS_AREA', 'DAMAGED_INFRASTRUCTURE', 'MEDICAL_EMERGENCY', 'OTHER'],
      required: true
    },
    description: { type: String, required: true },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], required: true }
    },
    addressText: { type: String },
    images: { type: [String], default: [] },
    mediaUrl: { type: String },
    verificationStatus: {
      type: String,
      enum: ['SUBMITTED', 'UNDER_REVIEW', 'VERIFIED', 'REJECTED', 'ACTION_TAKEN'],
      default: 'SUBMITTED',
      index: true
    },
    verifiedBy: { type: Schema.Types.ObjectId, ref: 'User' },
    verifiedAt: { type: Date }
  },
  { timestamps: true }
);

CitizenReportSchema.index({ location: '2dsphere' });

export const CitizenReport = mongoose.model<ICitizenReport>('CitizenReport', CitizenReportSchema);
