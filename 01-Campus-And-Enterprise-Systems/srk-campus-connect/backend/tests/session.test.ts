import { SessionService } from '../src/services/session.service';
import { ClassSession } from '../src/models/ClassSession';
import { Room } from '../src/models/Room';
import { Timetable } from '../src/models/Timetable';
import { Faculty } from '../src/models/Faculty';
import { ClassSessionStatus, FacultyStatus } from '../src/constants/enums';

describe('Phase 4: Class Session Engine & Dynamic Rolling QR Tests', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should start a new class session after validating room and timetable', async () => {
    // 1. Mock Room
    jest.spyOn(Room, 'findById').mockResolvedValue({
      _id: 'room204',
      roomNumber: '204',
      building: 'Building A',
      permanentQrCode: 'CAMPUS_ROOM_V1:BUILDING_A-204'
    } as any);

    // 2. Mock No Existing Active Sessions
    jest.spyOn(ClassSession, 'findOne').mockResolvedValue(null as any);

    // 3. Mock Timetable
    jest.spyOn(Timetable, 'findById').mockResolvedValue({
      _id: 'tt_dbms',
      facultyId: 'fac_arjun',
      subjectId: 'sub_dbms'
    } as any);

    // 4. Mock Faculty status update
    jest.spyOn(Faculty, 'findByIdAndUpdate').mockResolvedValue({} as any);

    // 5. Mock ClassSession creation & population
    jest.spyOn(ClassSession, 'create').mockImplementation((data: any) => Promise.resolve({
      _id: 'session_obj_id',
      ...data
    }) as any);

    jest.spyOn(ClassSession, 'findById').mockReturnValue({
      populate: jest.fn().mockReturnThis()
    } as any);

    const session = await SessionService.startSession({
      facultyId: 'fac_arjun',
      timetableId: 'tt_dbms',
      roomId: 'room204',
      permanentRoomQr: 'CAMPUS_ROOM_V1:BUILDING_A-204'
    });

    expect(session).toBeDefined();
  });

  it('should reject session start if room permanent QR does not match', async () => {
    jest.spyOn(Room, 'findById').mockResolvedValue({
      _id: 'room204',
      roomNumber: '204',
      permanentQrCode: 'CAMPUS_ROOM_V1:BUILDING_A-204'
    } as any);

    await expect(
      SessionService.startSession({
        facultyId: 'fac_arjun',
        roomId: 'room204',
        permanentRoomQr: 'CAMPUS_ROOM_V1:WRONG_ROOM_QR'
      })
    ).rejects.toThrow('Room QR verification failed');
  });

  it('should generate rolling dynamic QR for an active session', async () => {
    const mockSession = {
      sessionId: 'sess-12345',
      facultyId: 'fac_arjun',
      status: ClassSessionStatus.ACTIVE,
      save: jest.fn().mockResolvedValue(true)
    };

    jest.spyOn(ClassSession, 'findOne').mockResolvedValue(mockSession as any);

    const qrResult = await SessionService.getRollingSessionQr('sess-12345', 'fac_arjun');

    expect(qrResult.qrString).toContain('CAMPUS_SESSION_V1:sess-12345:');
    expect(qrResult.nonce).toBeDefined();
    expect(qrResult.expiresAt).toBeDefined();
    expect(mockSession.save).toHaveBeenCalled();
  });

  it('should end session and return faculty status to AVAILABLE', async () => {
    const mockSession = {
      sessionId: 'sess-12345',
      facultyId: 'fac_arjun',
      status: ClassSessionStatus.ACTIVE,
      save: jest.fn().mockResolvedValue(true)
    };

    jest.spyOn(ClassSession, 'findOne').mockResolvedValue(mockSession as any);
    const facultySpy = jest.spyOn(Faculty, 'findByIdAndUpdate').mockResolvedValue({} as any);

    const ended = await SessionService.endSession('sess-12345', 'fac_arjun');

    expect(ended?.status).toBe(ClassSessionStatus.ENDED);
    expect(mockSession.save).toHaveBeenCalled();
    expect(facultySpy).toHaveBeenCalledWith('fac_arjun', expect.objectContaining({
      currentStatus: FacultyStatus.AVAILABLE
    }));
  });
});
