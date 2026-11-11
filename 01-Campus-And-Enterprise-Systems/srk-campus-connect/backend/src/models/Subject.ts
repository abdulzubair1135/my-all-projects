import mongoose, { Document, Schema } from 'mongoose';

export interface ISubject extends Document {
  _id: mongoose.Types.ObjectId;
  name: string;
  code: string;
  departmentId: mongoose.Types.ObjectId;
  semester: number;
  credits: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

const SubjectSchema = new Schema<ISubject>(
  {
    name: { type: String, required: true, trim: true },
    code: { type: String, required: true, trim: true, uppercase: true, unique: true, index: true },
    departmentId: { type: Schema.Types.ObjectId, ref: 'Department', required: true, index: true },
    semester: { type: Number, required: true, min: 1, max: 12, index: true },
    credits: { type: Number, default: 3 },
    isActive: { type: Boolean, default: true }
  },
  {
    timestamps: true
  }
);

SubjectSchema.index({ departmentId: 1, semester: 1 });

export const Subject = mongoose.model<ISubject>('Subject', SubjectSchema);
