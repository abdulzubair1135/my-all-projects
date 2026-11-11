import mongoose from 'mongoose';
import { Timetable, ITimetable } from '../models/Timetable';
import { Room } from '../models/Room';
import { Faculty } from '../models/Faculty';
import { Notification } from '../models/Notification';
import { Student } from '../models/Student';
import { SocketManager } from '../sockets/socket.manager';
import { SocketEvent, UserRole } from '../constants/enums';

export interface TimetableSlotInput {
  departmentId: string;
  semester: number;
  division: string;
  subjectId: string;
  facultyId: string;
  roomId: string;
  dayOfWeek: number; // 1 = Monday, 7 = Sunday
  startTime: string; // "10:00"
  endTime: string;   // "11:00"
  academicYear: string;
}

export class TimetableService {
  /**
   * Helper to convert "HH:MM" to minutes from midnight for overlap checking
   */
  static timeToMinutes(timeStr: string): number {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
  }

  /**
   * Validates if two time intervals overlap
   */
  static isOverlapping(startA: string, endA: string, startB: string, endB: string): boolean {
    const aStart = this.timeToMinutes(startA);
    const aEnd = this.timeToMinutes(endA);
    const bStart = this.timeToMinutes(startB);
    const bEnd = this.timeToMinutes(endB);

    return Math.max(aStart, bStart) < Math.min(aEnd, bEnd);
  }

  /**
   * Checks for schedule conflicts across Room, Faculty, and Division
   */
  static async checkConflicts(
    data: TimetableSlotInput,
    excludeId?: string
  ): Promise<{ hasConflict: boolean; reason?: string }> {
    // 1. Check Room Collision
    const roomSlots = await Timetable.find({
      roomId: data.roomId,
      dayOfWeek: data.dayOfWeek,
      isActive: true,
      ...(excludeId ? { _id: { $ne: excludeId } } : {})
    }).populate('subjectId', 'name code');

    for (const slot of roomSlots) {
      if (this.isOverlapping(data.startTime, data.endTime, slot.startTime, slot.endTime)) {
        return {
          hasConflict: true,
          reason: `Room collision: Room is already booked from ${slot.startTime} to ${slot.endTime}`
        };
      }
    }

    // 2. Check Faculty Collision
    const facultySlots = await Timetable.find({
      facultyId: data.facultyId,
      dayOfWeek: data.dayOfWeek,
      isActive: true,
      ...(excludeId ? { _id: { $ne: excludeId } } : {})
    }).populate('roomId', 'roomNumber');

    for (const slot of facultySlots) {
      if (this.isOverlapping(data.startTime, data.endTime, slot.startTime, slot.endTime)) {
        return {
          hasConflict: true,
          reason: `Faculty collision: Faculty is already assigned to another class from ${slot.startTime} to ${slot.endTime}`
        };
      }
    }

    // 3. Check Division Collision
    const divisionSlots = await Timetable.find({
      departmentId: data.departmentId,
      semester: data.semester,
      division: data.division.toUpperCase(),
      academicYear: data.academicYear,
      dayOfWeek: data.dayOfWeek,
      isActive: true,
      ...(excludeId ? { _id: { $ne: excludeId } } : {})
    }).populate('subjectId', 'name code');

    for (const slot of divisionSlots) {
      if (this.isOverlapping(data.startTime, data.endTime, slot.startTime, slot.endTime)) {
        return {
          hasConflict: true,
          reason: `Division collision: Division ${data.division} already has class scheduled from ${slot.startTime} to ${slot.endTime}`
        };
      }
    }

    return { hasConflict: false };
  }

  /**
   * Create a new timetable entry
   */
  static async createSlot(data: TimetableSlotInput): Promise<ITimetable> {
    const conflictCheck = await this.checkConflicts(data);
    if (conflictCheck.hasConflict) {
      throw new Error(conflictCheck.reason);
    }

    const slot = await Timetable.create({
      ...data,
      division: data.division.toUpperCase(),
      isActive: true
    });

    // Notify connected clients
    try {
      SocketManager.emitToRole(UserRole.STUDENT, SocketEvent.TIMETABLE_UPDATED, { slotId: slot._id });
      SocketManager.emitToRole(UserRole.FACULTY, SocketEvent.TIMETABLE_UPDATED, { slotId: slot._id });
    } catch (e) {}

    return slot;
  }

  /**
   * Update or reschedule a timetable entry with automated notification dispatch
   */
  static async updateSlot(id: string, updateData: Partial<TimetableSlotInput>): Promise<ITimetable | null> {
    const existing = await Timetable.findById(id);
    if (!existing) {
      throw new Error('Timetable slot not found');
    }

    const mergedData: TimetableSlotInput = {
      departmentId: (updateData.departmentId || existing.departmentId).toString(),
      semester: updateData.semester || existing.semester,
      division: (updateData.division || existing.division).toUpperCase(),
      subjectId: (updateData.subjectId || existing.subjectId).toString(),
      facultyId: (updateData.facultyId || existing.facultyId).toString(),
      roomId: (updateData.roomId || existing.roomId).toString(),
      dayOfWeek: updateData.dayOfWeek || existing.dayOfWeek,
      startTime: updateData.startTime || existing.startTime,
      endTime: updateData.endTime || existing.endTime,
      academicYear: updateData.academicYear || existing.academicYear
    };

    const conflictCheck = await this.checkConflicts(mergedData, id);
    if (conflictCheck.hasConflict) {
      throw new Error(conflictCheck.reason);
    }

    const isRoomChanged = updateData.roomId && updateData.roomId !== existing.roomId.toString();
    const isTimeChanged = (updateData.startTime && updateData.startTime !== existing.startTime) ||
                          (updateData.endTime && updateData.endTime !== existing.endTime);

    const updated = await Timetable.findByIdAndUpdate(id, mergedData, { new: true })
      .populate('subjectId', 'name code')
      .populate('roomId', 'roomNumber building')
      .populate('facultyId', 'userId designation');

    // Dispatch notifications if room or time changed
    if (isRoomChanged || isTimeChanged) {
      const subjectName = (updated?.subjectId as any)?.name || 'Class';
      const newRoomNo = (updated?.roomId as any)?.roomNumber || 'New Room';
      const notificationTitle = isRoomChanged ? 'Class Room Changed' : 'Class Rescheduled';
      const notificationBody = `${subjectName} has been moved to ${newRoomNo} (${updated?.startTime} - ${updated?.endTime}).`;

      // Find affected faculty user
      const faculty = await Faculty.findById(mergedData.facultyId);
      if (faculty?.userId) {
        await Notification.create({
          recipientId: faculty.userId,
          title: notificationTitle,
          body: notificationBody,
          type: 'TIMETABLE_RESCHEDULED',
          payload: { slotId: id, roomId: mergedData.roomId }
        });
        try {
          SocketManager.emitToUser(faculty.userId.toString(), SocketEvent.NOTIFICATION_CREATED, { title: notificationTitle, body: notificationBody });
        } catch (e) {}
      }

      // Find affected division students
      const students = await Student.find({
        departmentId: mergedData.departmentId,
        semester: mergedData.semester,
        division: mergedData.division,
        academicYear: mergedData.academicYear,
        status: 'ACTIVE'
      });

      for (const student of students) {
        await Notification.create({
          recipientId: student.userId,
          title: notificationTitle,
          body: notificationBody,
          type: 'TIMETABLE_RESCHEDULED',
          payload: { slotId: id, roomId: mergedData.roomId }
        });
        try {
          SocketManager.emitToUser(student.userId.toString(), SocketEvent.NOTIFICATION_CREATED, { title: notificationTitle, body: notificationBody });
        } catch (e) {}
      }
    }

    return updated;
  }

  /**
   * Get student timetable by student profile params
   */
  static async getStudentTimetable(params: {
    departmentId: string;
    semester: number;
    division: string;
    academicYear?: string;
    dayOfWeek?: number;
  }): Promise<ITimetable[]> {
    const query: any = {
      departmentId: params.departmentId,
      semester: params.semester,
      division: params.division.toUpperCase(),
      isActive: true
    };

    if (params.academicYear) query.academicYear = params.academicYear;
    if (params.dayOfWeek) query.dayOfWeek = params.dayOfWeek;

    return await Timetable.find(query)
      .populate('subjectId', 'name code credits')
      .populate('roomId', 'roomNumber building permanentQrCode capacity')
      .populate({
        path: 'facultyId',
        populate: { path: 'userId', select: 'name email phone avatarUrl' }
      })
      .sort({ dayOfWeek: 1, startTime: 1 });
  }

  /**
   * Get faculty timetable by facultyId
   */
  static async getFacultyTimetable(facultyId: string, dayOfWeek?: number): Promise<ITimetable[]> {
    const query: any = {
      facultyId,
      isActive: true
    };
    if (dayOfWeek) query.dayOfWeek = dayOfWeek;

    return await Timetable.find(query)
      .populate('subjectId', 'name code credits')
      .populate('roomId', 'roomNumber building permanentQrCode capacity')
      .populate('departmentId', 'name code')
      .sort({ dayOfWeek: 1, startTime: 1 });
  }

  /**
   * Master admin timetable query with multi-filtering
   */
  static async getMasterTimetable(filter: {
    departmentId?: string;
    semester?: number;
    division?: string;
    facultyId?: string;
    roomId?: string;
    dayOfWeek?: number;
  } = {}): Promise<ITimetable[]> {
    const query: any = { isActive: true };
    if (filter.departmentId) query.departmentId = filter.departmentId;
    if (filter.semester) query.semester = filter.semester;
    if (filter.division) query.division = filter.division.toUpperCase();
    if (filter.facultyId) query.facultyId = filter.facultyId;
    if (filter.roomId) query.roomId = filter.roomId;
    if (filter.dayOfWeek) query.dayOfWeek = filter.dayOfWeek;

    return await Timetable.find(query)
      .populate('subjectId', 'name code')
      .populate('roomId', 'roomNumber building')
      .populate('departmentId', 'name code')
      .populate({
        path: 'facultyId',
        populate: { path: 'userId', select: 'name email' }
      })
      .sort({ dayOfWeek: 1, startTime: 1 });
  }

  /**
   * Delete / Deactivate a timetable slot
   */
  static async deleteSlot(id: string): Promise<ITimetable | null> {
    return await Timetable.findByIdAndUpdate(id, { isActive: false }, { new: true });
  }
}
