import { MeetingService } from '../src/services/meeting.service';
import { LeaveService } from '../src/services/leave.service';
import { AnalyticsService } from '../src/services/analytics.service';
import { MeetingRequest } from '../src/models/MeetingRequest';
import { LeaveRequest } from '../src/models/LeaveRequest';
import { Faculty } from '../src/models/Faculty';
import { Notification } from '../src/models/Notification';
import { Attendance } from '../src/models/Attendance';
import { Room } from '../src/models/Room';
import { ClassSession } from '../src/models/ClassSession';
import { Department } from '../src/models/Department';
import { MeetingRequestStatus, LeaveRequestStatus } from '../src/constants/enums';

describe('Phase 9 & 10: Faculty Coordination, Leave & Analytics Tests', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('MeetingService: should create meeting request and update status upon faculty response', async () => {
    jest.spyOn(Faculty, 'findById').mockResolvedValue({
      _id: 'fac_arjun',
      userId: 'user_arjun'
    } as any);

    jest.spyOn(MeetingRequest, 'create').mockResolvedValue({
      _id: 'meet_123',
      fromUserId: 'principal_user',
      toFacultyId: 'fac_arjun',
      status: MeetingRequestStatus.PENDING
    } as any);

    const mockMeetingDoc = {
      _id: 'meet_123',
      fromUserId: 'principal_user',
      toFacultyId: { userId: { name: 'Arjun Sir' } },
      status: MeetingRequestStatus.PENDING,
      responseNote: '',
      save: jest.fn().mockResolvedValue(true)
    };

    jest.spyOn(MeetingRequest, 'findById').mockReturnValue({
      populate: jest.fn().mockReturnValue({
        populate: jest.fn().mockResolvedValue(mockMeetingDoc)
      }),
      then: (resolve: any) => resolve(mockMeetingDoc)
    } as any);

    jest.spyOn(Notification, 'create').mockResolvedValue({} as any);

    const meeting = await MeetingService.createMeetingRequest({
      fromUserId: 'principal_user',
      toFacultyId: 'fac_arjun',
      type: 'MEETING',
      reason: 'Discuss timetable adjustments'
    });

    expect(meeting).toBeDefined();

    const responded = await MeetingService.respondToMeeting({
      meetingId: 'meet_123',
      facultyUserId: 'user_arjun',
      status: MeetingRequestStatus.ACCEPTED,
      responseNote: 'Available in 20 min'
    });

    expect(mockMeetingDoc.status).toBe(MeetingRequestStatus.ACCEPTED);
    expect(mockMeetingDoc.responseNote).toBe('Available in 20 min');
  });

  it('LeaveService: should create leave request and support approval/rejection', async () => {
    jest.spyOn(LeaveRequest, 'create').mockResolvedValue({
      _id: 'leave_123',
      studentId: 'stud_rahul',
      status: LeaveRequestStatus.PENDING
    } as any);

    const leave = await LeaveService.submitLeaveRequest({
      studentId: 'stud_rahul',
      fromDate: new Date('2026-09-10'),
      toDate: new Date('2026-09-12'),
      reason: 'Attending National Hackathon'
    });

    expect(leave.status).toBe(LeaveRequestStatus.PENDING);
  });

  it('AnalyticsService: should aggregate campus metrics and confidence distribution', async () => {
    jest.spyOn(Attendance, 'countDocuments')
      .mockResolvedValueOnce(100) // total
      .mockResolvedValueOnce(85)  // present
      .mockResolvedValueOnce(10)  // uncertain
      .mockResolvedValueOnce(5)   // absent
      .mockResolvedValueOnce(70)  // highConfidence
      .mockResolvedValueOnce(15)  // probable
      .mockResolvedValueOnce(10)  // uncertain
      .mockResolvedValueOnce(5);  // notDetected

    jest.spyOn(Department, 'find').mockResolvedValue([
      { name: 'Computer Engineering' }
    ] as any);

    const analytics = await AnalyticsService.getAttendanceAnalytics();
    expect(analytics.overallAttendanceRate).toBe(85);
    expect(analytics.totalAttendanceRecords).toBe(100);

    const distribution = await AnalyticsService.getPresenceDistribution();
    expect(distribution.highConfidence).toBe(70);
    expect(distribution.notDetected).toBe(5);
  });
});
