import mongoose, { Schema, Document } from 'mongoose';
import bcrypt from 'bcryptjs';

export interface IUser extends Document {
  name: string;
  phone: string;
  email?: string;
  passwordHash?: string;
  role: 'CITIZEN' | 'VOLUNTEER' | 'RESCUE' | 'GOVERNMENT' | 'NGO' | 'HOSPITAL' | 'ADMIN' | 'SUPER_ADMIN';
  address?: string;
  city?: string;
  state?: string;
  bloodGroup?: string;
  verified: boolean;
  status: 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';
  lastLoginAt?: Date;
  comparePassword(candidatePassword: string): Promise<boolean>;
}

const UserSchema: Schema = new Schema(
  {
    name: { type: String, required: true },
    phone: { type: String, required: true, index: true },
    email: { type: String, sparse: true, index: true, lowercase: true },
    passwordHash: { type: String },
    role: {
      type: String,
      enum: ['CITIZEN', 'VOLUNTEER', 'RESCUE', 'GOVERNMENT', 'NGO', 'HOSPITAL', 'ADMIN', 'SUPER_ADMIN'],
      default: 'CITIZEN',
      index: true
    },
    address: { type: String },
    city: { type: String },
    state: { type: String },
    verified: { type: Boolean, default: false },
    status: { type: String, enum: ['ACTIVE', 'INACTIVE', 'SUSPENDED'], default: 'ACTIVE' },
    lastLoginAt: { type: Date }
  },
  { timestamps: true }
);

UserSchema.methods.comparePassword = async function (candidatePassword: string): Promise<boolean> {
  if (!this.passwordHash) return false;
  return bcrypt.compare(candidatePassword, this.passwordHash);
};

export const User = mongoose.model<IUser>('User', UserSchema);
