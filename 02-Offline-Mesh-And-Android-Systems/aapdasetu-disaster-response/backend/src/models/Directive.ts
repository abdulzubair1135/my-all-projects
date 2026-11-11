import mongoose, { Schema, Document } from 'mongoose';

export interface IDirective extends Document {
  directiveId: string;
  title: string;
  category: string;
  quantity: number;
  unit: string;
  targetZone: string;
  assignedNgoName: string;
  priority: string;
  status: string;
  instructions?: string;
  stockShortageDetails?: {
    reportedAt?: Date;
    missingItems?: string;
    requestedQuantity?: number;
    notes?: string;
  };
  govtResponse?: {
    replenishedAt?: Date;
    note?: string;
  };
  issuedAt: Date;
  fulfilledAt?: Date;
}

const DirectiveSchema = new Schema<IDirective>({
  directiveId: { type: String, required: true, unique: true },
  title: { type: String, required: true },
  category: { 
    type: String, 
    required: true,
    default: 'FOOD_SUPPLY'
  },
  quantity: { type: Number, required: true },
  unit: { type: String, required: true, default: 'units' },
  targetZone: { type: String, required: true },
  assignedNgoName: { type: String, required: true },
  priority: { type: String, default: 'HIGH' },
  status: { 
    type: String, 
    enum: ['PENDING', 'ISSUED', 'ACKNOWLEDGED', 'IN_TRANSIT', 'STOCK_SHORTAGE', 'CRITICAL_STOCK_SHORTAGE', 'FULFILLED', 'COMPLETED'],
    default: 'PENDING' 
  },
  instructions: { type: String },
  stockShortageDetails: {
    reportedAt: { type: Date },
    missingItems: { type: String },
    requestedQuantity: { type: Number },
    notes: { type: String }
  },
  govtResponse: {
    replenishedAt: { type: Date },
    note: { type: String }
  },
  issuedAt: { type: Date, default: Date.now },
  fulfilledAt: { type: Date }
}, {
  timestamps: true
});

export const Directive = mongoose.model<IDirective>('Directive', DirectiveSchema);
