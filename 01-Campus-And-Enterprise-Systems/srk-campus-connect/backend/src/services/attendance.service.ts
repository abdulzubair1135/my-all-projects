import mongoose from 'mongoose';
import crypto from 'crypto';
import { Attendance, IAttendance } from '../models/Attendance';
import { PresenceEvent, IPresenceEvent } from '../models/PresenceEvent';
import { ClassSession } from '../models/ClassSession';
import { Student } from '../models/Student';
import { Device } from '../models/Device';
import { CryptoUtil } from '../security/crypto.util';
import { envConfig } from '../config/env.config';
import { SocketManager } from '../sockets/socket.manager';
import {
  AttendanceStatus,
  ClassSessionStatus,
  PresenceSource,
  SyncEventStatus,
  SocketEvent
} from '../constants/enums';

export interface SignedEventDto {
  eventId: string;
  userId: string;
  deviceId: string;
  sessionId: string;
  source: PresenceSource;
  timestamp: number;
  payload: {
    qrNonce?: string;
    qrTimestamp?: number;
    qrString?: string;
    dwellMinutes?: number;
    movementState?: string;
    rssi?: number;
    peerDeviceIds?: string[];
  };
  signature: string;
}

export interface SyncBatchResult {
  processed: string[];
  duplicates: string[];
  rejected: { eventId: string; reason: string }[];
}

export class AttendanceService {
  /**
   * Generates a cryptographically signed identity QR string for a student
   * Format: CAMPUS_STUDENT_V1:{studentId}:{enrollmentNo}:{timestamp}:{hmac}
   */
  static generateStudentIdentityQr(studentId: string, enrollmentNo: string): { qrString: string; expiresAt: Date } {
    const timestamp = Date.now();
    const expiresAt = new Date(timestamp + 300 * 1000); // 5 minutes valid
    const messageToSign = `${studentId}:${enrollmentNo.toUpperCase()}:${timestamp}`;
    const hmac = crypto
      .createHmac('sha256', envConfig.qrHmacSecret)
      .update(messageToSign)
      .digest('hex');

    const qrString = `CAMPUS_STUDENT_V1:${studentId}:${enrollmentNo.toUpperCase()}:${timestamp}:${hmac}`;
    return { qrString, expiresAt };
  }

  /**
   * Validates a student identity QR token scanned by faculty
   */
  static validateStudentIdentityQr(qrString: string): { isValid: boolean; studentId?: string; enrollmentNo?: string; error?: string } {
    try {
      const parts = qrString.split(':');
      if (parts.length !== 5 || parts[0] !== 'CAMPUS_STUDENT_V1') {
        return { isValid: false, error: 'Invalid Student QR format' };
      }

      const [, studentId, enrollmentNo, timestampStr, signature] = parts;
      const timestamp = parseInt(timestampStr, 10);
      if (isNaN(timestamp)) {
        return { isValid: false, error: 'Invalid timestamp in QR' };
      }

      // 5 min expiry window
      if (Date.now() - timestamp > 300 * 1000) {
        return { isValid: false, error: 'Student Identity QR has expired' };
      }

      const messageToSign = `${studentId}:${enrollmentNo}:${timestampStr}`;
      const expectedHmac = crypto
        .createHmac('sha256', envConfig.qrHmacSecret)
        .update(messageToSign)
        .digest('hex');

      if (expectedHmac !== signature) {
        return { isValid: false, error: 'Cryptographic signature mismatch in Student QR' };
      }

      return { isValid: true, studentId, enrollmentNo };
    } catch (err: any) {
      return { isValid: false, error: err.message || 'Validation error' };
    }
  }

  /**
   * Verifies an Ed25519 signed presence event
   */
  static async verifyEventSignature(event: SignedEventDto): Promise<{ isValid: boolean; reason?: string }> {
    const device = await Device.findOne({ deviceId: event.deviceId, isTrusted: true });
    if (!device) {
      return { isValid: false, reason: `Unregistered or untrusted device: ${event.deviceId}` };
    }

    // Verify user owns device
    if (device.userId.toString() !== event.userId) {
      return { isValid: false, reason: 'Device registration does not match event user' };
    }

    // Canonical representation of event data signed by client
    const canonicalPayload = JSON.stringify({
      eventId: event.eventId,
      userId: event.userId,
      deviceId: event.deviceId,
      sessionId: event.sessionId,
      source: event.source,
      timestamp: event.timestamp,
      payload: event.payload
    });

    const isSigValid = CryptoUtil.verifySignature(canonicalPayload, event.signature, device.publicKey);
    if (!isSigValid) {
      return { isValid: false, reason: 'Ed25519 digital signature verification failed' };
    }

    return { isValid: true };
  }

  /**
   * Ingests a single signed presence event or batch of offline events (Idempotent)
   */
  static async ingestPresenceEvents(
    events: SignedEventDto[],
    gatewayDeviceId?: string
  ): Promise<SyncBatchResult> {
    const result: SyncBatchResult = {
      processed: [],
      duplicates: [],
      rejected: []
    };

    for (const event of events) {
      try {
        // 1. Idempotency Check: check if eventId already exists
        const existing = await PresenceEvent.findOne({ eventId: event.eventId });
        if (existing) {
          result.duplicates.push(event.eventId);
          continue;
        }

        // 2. Validate Session
        const session = await ClassSession.findOne({ sessionId: event.sessionId });
        if (!session || (session.status !== ClassSessionStatus.ACTIVE && session.status !== ClassSessionStatus.ENDED)) {
          result.rejected.push({ eventId: event.eventId, reason: 'Invalid or non-existent class session' });
          continue;
        }

        // 3. Find Student Profile
        const student = await Student.findOne({ userId: event.userId });
        if (!student) {
          result.rejected.push({ eventId: event.eventId, reason: 'Student profile not found for user' });
          continue;
        }

        // 4. Validate Ed25519 Digital Signature
        const sigCheck = await this.verifyEventSignature(event);
        if (!sigCheck.isValid) {
          result.rejected.push({ eventId: event.eventId, reason: sigCheck.reason || 'Invalid signature' });
          continue;
        }

        // 5. If Dynamic QR source, validate rolling QR signature
        if (event.source === PresenceSource.DYNAMIC_QR && event.payload.qrString) {
          const qrCheck = CryptoUtil.validateDynamicSessionQr(event.payload.qrString);
          if (!qrCheck.isValid || qrCheck.sessionId !== event.sessionId) {
            result.rejected.push({ eventId: event.eventId, reason: qrCheck.error || 'Invalid dynamic QR token' });
            continue;
          }
        }

        // 6. Calculate Event Confidence Contribution
        let eventConfidence = 30; // base QR weight
        if (event.source === PresenceSource.TEACHER_SCAN) eventConfidence = 35;
        if (event.source === PresenceSource.P2P_PROXIMITY) eventConfidence = 15;

        // 7. Store Immutable Presence Event
        await PresenceEvent.create({
          eventId: event.eventId,
          userId: event.userId,
          deviceId: event.deviceId,
          sessionId: event.sessionId,
          source: event.source,
          confidence: eventConfidence,
          timestamp: new Date(event.timestamp),
          signature: event.signature,
          gatewayDeviceId,
          syncStatus: SyncEventStatus.PROCESSED,
          payload: event.payload
        });

        // 8. Materialize / Update Attendance Record
        await this.materializeAttendance(session.sessionId, student._id.toString(), event.source, event.timestamp);

        result.processed.push(event.eventId);
      } catch (err: any) {
        result.rejected.push({ eventId: event.eventId, reason: err.message || 'Processing error' });
      }
    }

    return result;
  }

  /**
   * Materializes presence events into consolidated Attendance records
   */
  static async materializeAttendance(
    sessionId: string,
    studentId: string,
    source: PresenceSource,
    eventTimestamp: number
  ): Promise<IAttendance> {
    const existing = await Attendance.findOne({ sessionId, studentId });

    if (existing) {
      if (!existing.sources.includes(source)) {
        existing.sources.push(source);
      }
      // Increment confidence with multiple corroborating sources
      const newConfidence = Math.min(100, existing.confidence + 25);
      existing.confidence = newConfidence;
      if (newConfidence >= 50 && existing.status !== AttendanceStatus.PRESENT) {
        existing.status = AttendanceStatus.PRESENT;
      }
      if (!existing.checkInTime) {
        existing.checkInTime = new Date(eventTimestamp);
      }
      existing.checkOutTime = new Date(eventTimestamp);
      await existing.save();

      // Broadcast update
      try {
        SocketManager.emitToSession(sessionId, SocketEvent.ATTENDANCE_UPDATED, existing);
      } catch (e) {}

      return existing;
    }

    const attendance = await Attendance.create({
      sessionId,
      studentId,
      status: AttendanceStatus.PRESENT,
      confidence: 75,
      sources: [source],
      checkInTime: new Date(eventTimestamp),
      checkOutTime: new Date(eventTimestamp),
      isManualOverride: false
    });

    try {
      SocketManager.emitToSession(sessionId, SocketEvent.ATTENDANCE_UPDATED, attendance);
    } catch (e) {}

    return attendance;
  }

  /**
   * Manual Attendance Override by Faculty or Administrator
   */
  static async manualOverride(data: {
    sessionId: string;
    studentId: string;
    status: AttendanceStatus;
    verifiedBy: string;
    notes?: string;
  }): Promise<IAttendance> {
    const session = await ClassSession.findOne({ sessionId: data.sessionId });
    if (!session) {
      throw new Error('Class session not found');
    }

    const updated = await Attendance.findOneAndUpdate(
      { sessionId: data.sessionId, studentId: data.studentId },
      {
        sessionId: data.sessionId,
        studentId: data.studentId,
        status: data.status,
        confidence: data.status === AttendanceStatus.PRESENT ? 100 : 0,
        sources: [PresenceSource.MANUAL_OVERRIDE],
        verifiedBy: data.verifiedBy,
        isManualOverride: true,
        notes: data.notes,
        checkInTime: data.status === AttendanceStatus.PRESENT ? new Date() : undefined
      },
      { upsert: true, new: true, runValidators: true }
    ).populate({
      path: 'studentId',
      populate: { path: 'userId', select: 'name email' }
    });

    try {
      SocketManager.emitToSession(data.sessionId, SocketEvent.ATTENDANCE_UPDATED, updated);
    } catch (e) {}

    return updated;
  }

  /**
   * Faculty scanning Student Identity QR directly
   */
  static async verifyStudentByQr(sessionId: string, studentQrString: string, facultyId: string): Promise<IAttendance> {
    const qrResult = this.validateStudentIdentityQr(studentQrString);
    if (!qrResult.isValid || !qrResult.studentId) {
      throw new Error(qrResult.error || 'Invalid student QR');
    }

    const student = await Student.findById(qrResult.studentId);
    if (!student) {
      throw new Error('Student not enrolled in system');
    }

    return await this.materializeAttendance(
      sessionId,
      student._id.toString(),
      PresenceSource.TEACHER_SCAN,
      Date.now()
    );
  }

  /**
   * Get live attendance list for a session
   */
  static async getSessionAttendance(sessionId: string): Promise<IAttendance[]> {
    return await Attendance.find({ sessionId })
      .populate({
        path: 'studentId',
        populate: { path: 'userId', select: 'name email phone avatarUrl' }
      })
      .populate('verifiedBy', 'userId designation');
  }

  /**
   * Get student's overall attendance history & percentage summary
   */
  static async getStudentAttendanceHistory(studentId: string): Promise<{
    summary: { overallPercentage: number; totalClasses: number; attendedClasses: number };
    records: IAttendance[];
  }> {
    const records = await Attendance.find({ studentId })
      .populate({
        path: 'sessionId',
        select: 'subjectId roomId startTime endTime status'
      })
      .sort({ createdAt: -1 });

    const totalClasses = records.length;
    const attendedClasses = records.filter(r => r.status === AttendanceStatus.PRESENT).length;
    const overallPercentage = totalClasses > 0 ? Math.round((attendedClasses / totalClasses) * 100) : 0;

    return {
      summary: {
        overallPercentage,
        totalClasses,
        attendedClasses
      },
      records
    };
  }
}
