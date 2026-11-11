import mongoose, { Document, Schema } from 'mongoose';

export interface IStudent extends Document {
  _id: mongoose.Types.ObjectId;
  userId: mongoose.Types.ObjectId;
  enrollmentNo: string;
  departmentId: mongoose.Types.ObjectId;
  semester: number;
  division: string;
  academicYear: string;
  status: 'ACTIVE' | 'SUSPENDED' | 'ALUMNI';
  createdAt: Date;
  updatedAt: Date;
}

const StudentSchema = new Schema<IStudent>(
  {
    userId: { type: Schema.Types.ObjectId, ref: 'User', required: true, unique: true, index: true },
    enrollmentNo: { type: String, required: true, unique: true, uppercase: true, trim: true, index: true },
    departmentId: { type: Schema.Types.ObjectId, ref: 'Department', required: true, index: true },
    semester: { type: Number, required: true, min: 1, max: 12, index: true },
    division: { type: String, required: true, trim: true, uppercase: true, index: true },
    academicYear: { type: String, required: true, trim: true, index: true },
    status: { type: String, enum: ['ACTIVE', 'SUSPENDED', 'ALUMNI'], default: 'ACTIVE', index: true }
  },
  {
    timestamps: true
  }
);

StudentSchema.index({ departmentId: 1, semester: 1, division: 1, academicYear: 1 });

export const Student = mongoose.model<IStudent>('Student', StudentSchema);
