import mongoose, { Document, Schema } from 'mongoose';

export interface ITimetable extends Document {
  _id: mongoose.Types.ObjectId;
  departmentId: mongoose.Types.ObjectId;
  semester: number;
  division: string;
  subjectId: mongoose.Types.ObjectId;
  facultyId: mongoose.Types.ObjectId;
  roomId: mongoose.Types.ObjectId;
  dayOfWeek: number; // 1 = Monday, 7 = Sunday
  startTime: string; // e.g. "10:00"
  endTime: string;   // e.g. "11:00"
  academicYear: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

const TimetableSchema = new Schema<ITimetable>(
  {
    departmentId: { type: Schema.Types.ObjectId, ref: 'Department', required: true, index: true },
    semester: { type: Number, required: true, min: 1, max: 12, index: true },
    division: { type: String, required: true, trim: true, uppercase: true, index: true },
    subjectId: { type: Schema.Types.ObjectId, ref: 'Subject', required: true, index: true },
    facultyId: { type: Schema.Types.ObjectId, ref: 'Faculty', required: true, index: true },
    roomId: { type: Schema.Types.ObjectId, ref: 'Room', required: true, index: true },
    dayOfWeek: { type: Number, required: true, min: 1, max: 7, index: true },
    startTime: { type: String, required: true, trim: true },
    endTime: { type: String, required: true, trim: true },
    academicYear: { type: String, required: true, trim: true, index: true },
    isActive: { type: Boolean, default: true, index: true }
  },
  {
    timestamps: true
  }
);

TimetableSchema.index({ departmentId: 1, semester: 1, division: 1, dayOfWeek: 1, startTime: 1 });
TimetableSchema.index({ facultyId: 1, dayOfWeek: 1, startTime: 1 });
TimetableSchema.index({ roomId: 1, dayOfWeek: 1, startTime: 1 });

export const Timetable = mongoose.model<ITimetable>('Timetable', TimetableSchema);
