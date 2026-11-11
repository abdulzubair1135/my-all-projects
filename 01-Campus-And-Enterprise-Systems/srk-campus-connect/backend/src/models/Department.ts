import mongoose, { Document, Schema } from 'mongoose';

export interface IDepartment extends Document {
  _id: mongoose.Types.ObjectId;
  name: string;
  code: string;
  hodId?: mongoose.Types.ObjectId;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

const DepartmentSchema = new Schema<IDepartment>(
  {
    name: { type: String, required: true, trim: true, unique: true },
    code: { type: String, required: true, trim: true, uppercase: true, unique: true, index: true },
    hodId: { type: Schema.Types.ObjectId, ref: 'Faculty' },
    isActive: { type: Boolean, default: true }
  },
  {
    timestamps: true
  }
);

export const Department = mongoose.model<IDepartment>('Department', DepartmentSchema);
