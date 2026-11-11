import { AttendanceService, SignedEventDto } from '../src/services/attendance.service';
import { CryptoUtil } from '../src/security/crypto.util';
import { PresenceEvent } from '../src/models/PresenceEvent';
import { ClassSession } from '../src/models/ClassSession';
import { Student } from '../src/models/Student';
import { Device } from '../src/models/Device';
import { Attendance } from '../src/models/Attendance';
import { AttendanceStatus, ClassSessionStatus, PresenceSource } from '../src/constants/enums';

describe('Phase 5 & 6: Attendance Engine & Offline Idempotent Sync Tests', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should generate and validate student identity QR code', () => {
    const studentId = 'stud_rahul_123';
    const enrollmentNo = 'EN2026COMP001';

    const qrResult = AttendanceService.generateStudentIdentityQr(studentId, enrollmentNo);
    expect(qrResult.qrString).toContain('CAMPUS_STUDENT_V1:stud_rahul_123:EN2026COMP001:');

    const validation = AttendanceService.validateStudentIdentityQr(qrResult.qrString);
    expect(validation.isValid).toBe(true);
    expect(validation.studentId).toBe(studentId);
    expect(validation.enrollmentNo).toBe(enrollmentNo);

    // Tampering test
    const tampered = qrResult.qrString.slice(0, -3) + 'abc';
    const tamperedVal = AttendanceService.validateStudentIdentityQr(tampered);
    expect(tamperedVal.isValid).toBe(false);
  });

  it('should ingest valid signed offline presence event and materialize attendance', async () => {
    const keyPair = CryptoUtil.generateEd25519KeyPair();
    const eventId = 'evt_offline_999';
    const userId = 'usr_rahul';
    const deviceId = 'dev_android_rahul';
    const sessionId = 'sess_dbms_100';

    const dynamicQr = CryptoUtil.generateDynamicSessionQr(sessionId);

    const eventData = {
      eventId,
      userId,
      deviceId,
      sessionId,
      source: PresenceSource.DYNAMIC_QR,
      timestamp: Date.now(),
      payload: {
        qrString: dynamicQr.qrString,
        qrNonce: dynamicQr.nonce,
        dwellMinutes: 15,
        movementState: 'STATIONARY'
      }
    };

    const signature = CryptoUtil.signMessage(JSON.stringify(eventData), keyPair.secretKey);

    const signedEvent: SignedEventDto = {
      ...eventData,
      signature
    };

    // Mocks
    jest.spyOn(PresenceEvent, 'findOne').mockResolvedValue(null as any);
    jest.spyOn(ClassSession, 'findOne').mockResolvedValue({
      sessionId,
      status: ClassSessionStatus.ACTIVE
    } as any);
    jest.spyOn(Student, 'findOne').mockResolvedValue({
      _id: 'stud_rahul_id',
      userId
    } as any);
    jest.spyOn(Device, 'findOne').mockResolvedValue({
      deviceId,
      userId,
      publicKey: keyPair.publicKey,
      isTrusted: true
    } as any);
    jest.spyOn(PresenceEvent, 'create').mockResolvedValue({} as any);
    jest.spyOn(Attendance, 'findOne').mockResolvedValue(null as any);
    jest.spyOn(Attendance, 'create').mockResolvedValue({
      sessionId,
      studentId: 'stud_rahul_id',
      status: AttendanceStatus.PRESENT,
      confidence: 75
    } as any);

    const result = await AttendanceService.ingestPresenceEvents([signedEvent], 'gateway_peer_device');

    expect(result.processed).toContain(eventId);
    expect(result.duplicates.length).toBe(0);
    expect(result.rejected.length).toBe(0);
  });

  it('should identify duplicate presence events idempotently without throwing', async () => {
    const duplicateEvent: SignedEventDto = {
      eventId: 'evt_duplicate_123',
      userId: 'usr_rahul',
      deviceId: 'dev_android_rahul',
      sessionId: 'sess_dbms_100',
      source: PresenceSource.DYNAMIC_QR,
      timestamp: Date.now(),
      payload: {},
      signature: 'sig123'
    };

    // Mock that event already exists in DB
    jest.spyOn(PresenceEvent, 'findOne').mockResolvedValue({
      eventId: 'evt_duplicate_123'
    } as any);

    const result = await AttendanceService.ingestPresenceEvents([duplicateEvent]);

    expect(result.duplicates).toContain('evt_duplicate_123');
    expect(result.processed.length).toBe(0);
    expect(result.rejected.length).toBe(0);
  });
});
