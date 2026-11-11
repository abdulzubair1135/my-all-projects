import { TimetableService } from '../src/services/timetable.service';
import { Timetable } from '../src/models/Timetable';

describe('Phase 3: Timetable Engine & Conflict Detection Tests', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should accurately calculate time intervals and detect overlaps', () => {
    expect(TimetableService.timeToMinutes('10:00')).toBe(600);
    expect(TimetableService.timeToMinutes('11:30')).toBe(690);

    // Overlapping cases
    expect(TimetableService.isOverlapping('10:00', '11:00', '10:30', '11:30')).toBe(true);
    expect(TimetableService.isOverlapping('10:00', '11:00', '09:30', '10:30')).toBe(true);
    expect(TimetableService.isOverlapping('10:00', '11:00', '10:00', '11:00')).toBe(true);

    // Non-overlapping contiguous cases
    expect(TimetableService.isOverlapping('10:00', '11:00', '11:00', '12:00')).toBe(false);
    expect(TimetableService.isOverlapping('10:00', '11:00', '12:00', '13:00')).toBe(false);
  });

  it('should reject slot creation if room collision is detected', async () => {
    // Mock room has existing booking
    jest.spyOn(Timetable, 'find').mockReturnValue({
      populate: jest.fn().mockResolvedValue([
        {
          _id: 'slot_existing',
          startTime: '10:00',
          endTime: '11:00',
          subjectId: { name: 'DBMS', code: 'CS401' }
        }
      ])
    } as any);

    const conflict = await TimetableService.checkConflicts({
      departmentId: 'dept1',
      semester: 4,
      division: 'A',
      subjectId: 'sub2',
      facultyId: 'fac2',
      roomId: 'room204',
      dayOfWeek: 1,
      startTime: '10:15',
      endTime: '11:15',
      academicYear: '2025-2026'
    });

    expect(conflict.hasConflict).toBe(true);
    expect(conflict.reason).toContain('Room collision');
  });

  it('should allow slot creation when there are no collisions', async () => {
    jest.spyOn(Timetable, 'find').mockReturnValue({
      populate: jest.fn().mockResolvedValue([])
    } as any);

    const conflict = await TimetableService.checkConflicts({
      departmentId: 'dept1',
      semester: 4,
      division: 'A',
      subjectId: 'sub2',
      facultyId: 'fac2',
      roomId: 'room204',
      dayOfWeek: 1,
      startTime: '14:00',
      endTime: '15:00',
      academicYear: '2025-2026'
    });

    expect(conflict.hasConflict).toBe(false);
  });
});
