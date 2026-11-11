import { PresenceEvent } from '../models/PresenceEvent';
import { Attendance } from '../models/Attendance';
import { ClassSession } from '../models/ClassSession';
import { Timetable } from '../models/Timetable';
import { Student } from '../models/Student';
import { PresenceSource, PresenceState, AttendanceStatus, MovementState } from '../constants/enums';

export interface PresenceEvidence {
  hasValidDynamicQr: boolean;
  hasTeacherScan: boolean;
  isTimetableEnrolled: boolean;
  dwellPingsCount: number;
  totalSessionMinutes: number;
  peerProximityCount: number;
  movementState?: MovementState;
}

export interface PresenceEvaluationResult {
  confidenceScore: number;
  presenceState: PresenceState;
  stateLabel: string;
  evidenceBreakdown: {
    qrScore: number;
    teacherScore: number;
    timetableScore: number;
    dwellScore: number;
    p2pScore: number;
    movementScore: number;
  };
  scheduleMismatch?: {
    isMismatch: boolean;
    expectedRoom?: string;
    detectedRoom?: string;
  };
}

export class PresenceEngine {
  // Configurable Weights
  static readonly WEIGHT_DYNAMIC_QR = 30;
  static readonly WEIGHT_TEACHER_SCAN = 25;
  static readonly WEIGHT_TIMETABLE_MATCH = 15;
  static readonly WEIGHT_DWELL_TIME = 15;
  static readonly WEIGHT_P2P_PROXIMITY = 10;
  static readonly WEIGHT_MOVEMENT_SENSOR = 5;

  /**
   * Evaluates presence evidence and computes normalized confidence score (0 - 100)
   */
  static calculateConfidence(evidence: PresenceEvidence): PresenceEvaluationResult {
    let qrScore = 0;
    let teacherScore = 0;
    let timetableScore = 0;
    let dwellScore = 0;
    let p2pScore = 0;
    let movementScore = 0;

    // 1. Dynamic QR Verification
    if (evidence.hasValidDynamicQr) {
      qrScore = this.WEIGHT_DYNAMIC_QR;
    }

    // 2. Teacher Direct Verification
    if (evidence.hasTeacherScan) {
      teacherScore = this.WEIGHT_TEACHER_SCAN;
    }

    // 3. Timetable Enrollment Match
    if (evidence.isTimetableEnrolled) {
      timetableScore = this.WEIGHT_TIMETABLE_MATCH;
    }

    // 4. Dwell Time Ratio (Periodic pings over session duration)
    if (evidence.totalSessionMinutes > 0 && evidence.dwellPingsCount > 0) {
      const expectedPings = Math.max(1, Math.floor(evidence.totalSessionMinutes / 10));
      const dwellRatio = Math.min(1.0, evidence.dwellPingsCount / expectedPings);
      dwellScore = Math.round(dwellRatio * this.WEIGHT_DWELL_TIME);
    }

    // 5. Peer P2P Proximity (Seen by 3+ peers)
    if (evidence.peerProximityCount >= 3) {
      p2pScore = this.WEIGHT_P2P_PROXIMITY;
    } else if (evidence.peerProximityCount > 0) {
      p2pScore = Math.round((evidence.peerProximityCount / 3) * this.WEIGHT_P2P_PROXIMITY);
    }

    // 6. Movement Sensor
    if (evidence.movementState === MovementState.STATIONARY) {
      movementScore = this.WEIGHT_MOVEMENT_SENSOR;
    } else if (evidence.movementState === MovementState.WALKING) {
      movementScore = Math.round(this.WEIGHT_MOVEMENT_SENSOR * 0.5);
    }

    const totalScore = Math.min(100, qrScore + teacherScore + timetableScore + dwellScore + p2pScore + movementScore);

    // Strict non-accusatory presence state labeling
    let presenceState: PresenceState;
    let stateLabel: string;

    if (totalScore >= 80) {
      presenceState = PresenceState.HIGH_CONFIDENCE;
      stateLabel = 'Present in scheduled classroom';
    } else if (totalScore >= 50) {
      presenceState = PresenceState.PROBABLE;
      stateLabel = 'Probable presence (verification in progress)';
    } else if (totalScore >= 20) {
      presenceState = PresenceState.UNCERTAIN;
      stateLabel = 'Presence could not be definitively verified';
    } else {
      presenceState = PresenceState.NOT_DETECTED;
      stateLabel = 'Not detected in scheduled classroom';
    }

    return {
      confidenceScore: totalScore,
      presenceState,
      stateLabel,
      evidenceBreakdown: {
        qrScore,
        teacherScore,
        timetableScore,
        dwellScore,
        p2pScore,
        movementScore
      }
    };
  }

  /**
   * Evaluates student presence for a specific session by aggregating raw event stream
   */
  static async evaluateStudentSessionPresence(sessionId: string, studentId: string): Promise<PresenceEvaluationResult> {
    const student = await Student.findById(studentId);
    if (!student) {
      throw new Error('Student not found');
    }

    const session = await ClassSession.findOne({ sessionId })
      .populate('timetableId')
      .populate('roomId');

    if (!session) {
      throw new Error('Class session not found');
    }

    const events = await PresenceEvent.find({
      sessionId,
      userId: student.userId
    }).sort({ timestamp: 1 });

    const hasValidDynamicQr = events.some(e => e.source === PresenceSource.DYNAMIC_QR);
    const hasTeacherScan = events.some(e => e.source === PresenceSource.TEACHER_SCAN);
    
    // Timetable cohort match check
    let isTimetableEnrolled = false;
    if (session.timetableId) {
      const timetable = session.timetableId as any;
      isTimetableEnrolled =
        timetable.departmentId.toString() === student.departmentId.toString() &&
        timetable.semester === student.semester &&
        timetable.division === student.division;
    }

    const sessionStart = session.startTime ? session.startTime.getTime() : Date.now();
    const sessionEnd = session.endTime ? session.endTime.getTime() : Date.now();
    const totalSessionMinutes = Math.max(1, Math.round((sessionEnd - sessionStart) / (1000 * 60)));

    const dwellPingsCount = events.length;
    const peerProximityCount = events.filter(e => e.source === PresenceSource.P2P_PROXIMITY).length;
    const latestEventWithMovement = events.slice().reverse().find(e => e.payload?.movementState);
    const movementState = (latestEventWithMovement?.payload?.movementState as MovementState) || MovementState.STATIONARY;

    return this.calculateConfidence({
      hasValidDynamicQr,
      hasTeacherScan,
      isTimetableEnrolled,
      dwellPingsCount,
      totalSessionMinutes,
      peerProximityCount,
      movementState
    });
  }

  /**
   * Schedule mismatch analyzer
   */
  static checkScheduleMismatch(
    expectedRoomNumber: string,
    detectedRoomNumber: string,
    confidence: number
  ): { isMismatch: boolean; alert?: string } {
    if (expectedRoomNumber.toUpperCase() !== detectedRoomNumber.toUpperCase() && confidence >= 50) {
      return {
        isMismatch: true,
        alert: `Schedule Mismatch: Expected in Room ${expectedRoomNumber}, presence detected in Room ${detectedRoomNumber} (${confidence}% confidence).`
      };
    }
    return { isMismatch: false };
  }
}
