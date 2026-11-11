import mongoose, { Schema, Document } from 'mongoose';

export interface IResource extends Document {
  organizationId?: mongoose.Types.ObjectId;
  organizationName: string;
  type: 'FOOD' | 'WATER' | 'MEDICINE' | 'BLANKETS' | 'CLOTHING' | 'MEDICAL_KITS' | 'BOATS' | 'GENERATORS' | 'TARPAULINS';
  quantity: number;
  unit: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  availableQuantity: number;
  reservedQuantity: number;
}

const ResourceSchema: Schema = new Schema(
  {
    organizationId: { type: Schema.Types.ObjectId, ref: 'NGO' },
    organizationName: { type: String, required: true },
    type: {
      type: String,
      enum: ['FOOD', 'WATER', 'MEDICINE', 'BLANKETS', 'CLOTHING', 'MEDICAL_KITS', 'BOATS', 'GENERATORS', 'TARPAULINS'],
      required: true,
      index: true
    },
    quantity: { type: Number, required: true },
    unit: { type: String, default: 'units' },
    location: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], required: true }
    },
    availableQuantity: { type: Number, required: true },
    reservedQuantity: { type: Number, default: 0 }
  },
  { timestamps: true }
);

ResourceSchema.index({ location: '2dsphere' });

export const Resource = mongoose.model<IResource>('Resource', ResourceSchema);
