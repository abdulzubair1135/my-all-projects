import mongoose from 'mongoose';
import { v4 as uuidv4 } from 'uuid';
import { ClassSession, IClassSession } from '../models/ClassSession';
import { Timetable } from '../models/Timetable';
import { Room } from '../models/Room';
import { Faculty } from '../models/Faculty';
import { CryptoUtil } from '../security/crypto.util';
import { SocketManager } from '../sockets/socket.manager';
import { ClassSessionStatus, FacultyStatus, SocketEvent, UserRole } from '../constants/enums';

export class SessionService {
  /**
   * Starts a new class session with room verification and timetable authorization
   */
  static async startSession(data: {
    facultyId: string;
    timetableId?: string;
    roomId: string;
    permanentRoomQr?: string;
    subjectId?: string;
  }): Promise<IClassSession> {
    // 1. Verify Room existence
    const room = await Room.findById(data.roomId);
    if (!room) {
      throw new Error('Specified room does not exist');
    }

    // If permanentRoomQr is provided, verify it matches
    if (data.permanentRoomQr && room.permanentQrCode !== data.permanentRoomQr) {
      throw new Error('Room QR verification failed: Scanned QR does not match classroom');
    }

    // 2. Check if faculty already has an ACTIVE session
    const existingFacultySession = await ClassSession.findOne({
      facultyId: data.facultyId,
      status: ClassSessionStatus.ACTIVE
    });
    if (existingFacultySession) {
      throw new Error(`Faculty already has an active class session in progress (${existingFacultySession.sessionId})`);
    }

    // 3. Check if room already has an ACTIVE session
    const existingRoomSession = await ClassSession.findOne({
      roomId: data.roomId,
      status: ClassSessionStatus.ACTIVE
    });
    if (existingRoomSession) {
      throw new Error(`Room ${room.roomNumber} already has an active class session in progress`);
    }

    let subjectId = data.subjectId;
    let timetableId = data.timetableId;

    // If timetableId is provided, validate timetable association
    if (timetableId) {
      const timetable = await Timetable.findById(timetableId);
      if (!timetable) {
        throw new Error('Timetable slot not found');
      }
      if (timetable.facultyId.toString() !== data.facultyId) {
        throw new Error('Unauthorized: Faculty is not assigned to this timetable slot');
      }
      subjectId = timetable.subjectId.toString();
    } else if (!subjectId) {
      throw new Error('subjectId or timetableId is required to start a class');
    }

    const sessionId = uuidv4();
    const { nonce, expiresAt } = CryptoUtil.generateDynamicSessionQr(sessionId);

    const session = await ClassSession.create({
      sessionId,
      timetableId,
      facultyId: data.facultyId,
      subjectId,
      roomId: data.roomId,
      startTime: new Date(),
      status: ClassSessionStatus.ACTIVE,
      currentQrNonce: nonce,
      qrExpiresAt: expiresAt
    });

    // Update faculty live status & location
    await Faculty.findByIdAndUpdate(data.facultyId, {
      currentStatus: FacultyStatus.IN_CLASS,
      statusUpdatedAt: new Date(),
      currentLocation: {
        roomId: data.roomId,
        confidence: 100,
        lastVerified: new Date()
      }
    });

    // Populate for response & socket broadcast
    const populated = await ClassSession.findById(session._id)
      .populate('subjectId', 'name code credits')
      .populate('roomId', 'roomNumber building permanentQrCode')
      .populate({
        path: 'facultyId',
        populate: { path: 'userId', select: 'name email phone avatarUrl' }
      });

    // Realtime broadcast to session room & campus radar
    try {
      SocketManager.emitToSession(sessionId, SocketEvent.CLASS_STARTED, populated);
      SocketManager.emitToRole(UserRole.PRINCIPAL, SocketEvent.FACULTY_STATUS_CHANGED, {
        facultyId: data.facultyId,
        status: FacultyStatus.IN_CLASS,
        sessionId
      });
      SocketManager.emitToRole(UserRole.STUDENT, SocketEvent.CLASS_STARTED, populated);
    } catch (e) {}

    return populated as IClassSession;
  }

  /**
   * Generates a dynamic rolling QR token for an active session
   */
  static async getRollingSessionQr(sessionId: string, facultyId: string): Promise<{
    qrString: string;
    nonce: string;
    timestamp: number;
    expiresAt: Date;
  }> {
    const session = await ClassSession.findOne({ sessionId, facultyId, status: ClassSessionStatus.ACTIVE });
    if (!session) {
      throw new Error('Active class session not found or unauthorized');
    }

    const qrData = CryptoUtil.generateDynamicSessionQr(sessionId);

    // Update latest nonce in database
    session.currentQrNonce = qrData.nonce;
    session.qrExpiresAt = qrData.expiresAt;
    await session.save();

    return qrData;
  }

  /**
   * Ends an active class session
   */
  static async endSession(sessionId: string, facultyId: string): Promise<IClassSession | null> {
    const session = await ClassSession.findOne({ sessionId, facultyId, status: ClassSessionStatus.ACTIVE });
    if (!session) {
      throw new Error('Active class session not found or unauthorized');
    }

    session.status = ClassSessionStatus.ENDED;
    session.endedAt = new Date();
    session.endTime = new Date();
    await session.save();

    // Reset faculty status to AVAILABLE
    await Faculty.findByIdAndUpdate(facultyId, {
      currentStatus: FacultyStatus.AVAILABLE,
      statusUpdatedAt: new Date()
    });

    // Realtime broadcast
    try {
      SocketManager.emitToSession(sessionId, SocketEvent.CLASS_ENDED, { sessionId, endedAt: session.endedAt });
      SocketManager.emitToRole(UserRole.PRINCIPAL, SocketEvent.FACULTY_STATUS_CHANGED, {
        facultyId,
        status: FacultyStatus.AVAILABLE,
        sessionId
      });
    } catch (e) {}

    return session;
  }

  /**
   * Retrieves the current active class session for faculty
   */
  static async getCurrentSessionForFaculty(facultyId: string): Promise<IClassSession | null> {
    return await ClassSession.findOne({ facultyId, status: ClassSessionStatus.ACTIVE })
      .populate('subjectId', 'name code credits')
      .populate('roomId', 'roomNumber building permanentQrCode')
      .populate('timetableId');
  }

  /**
   * Retrieves the current active class session for a student's cohort
   */
  static async getCurrentSessionForStudent(params: {
    departmentId: string;
    semester: number;
    division: string;
    academicYear?: string;
  }): Promise<IClassSession | null> {
    // Find matching timetables for this student cohort
    const matchingTimetables = await Timetable.find({
      departmentId: params.departmentId,
      semester: params.semester,
      division: params.division.toUpperCase(),
      isActive: true
    }).select('_id');

    const timetableIds = matchingTimetables.map(t => t._id);

    // Find any ACTIVE session matching these timetables
    return await ClassSession.findOne({
      timetableId: { $in: timetableIds },
      status: ClassSessionStatus.ACTIVE
    })
      .populate('subjectId', 'name code credits')
      .populate('roomId', 'roomNumber building permanentQrCode')
      .populate({
        path: 'facultyId',
        populate: { path: 'userId', select: 'name email phone avatarUrl' }
      });
  }

  /**
   * Get session by sessionId
   */
  static async getSessionBySessionId(sessionId: string): Promise<IClassSession | null> {
    return await ClassSession.findOne({ sessionId })
      .populate('subjectId', 'name code credits')
      .populate('roomId', 'roomNumber building')
      .populate({
        path: 'facultyId',
        populate: { path: 'userId', select: 'name email phone' }
      });
  }
}
