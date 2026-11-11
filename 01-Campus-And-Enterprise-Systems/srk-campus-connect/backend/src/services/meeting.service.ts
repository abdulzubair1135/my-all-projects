import { MeetingRequest, IMeetingRequest } from '../models/MeetingRequest';
import { Faculty } from '../models/Faculty';
import { Notification } from '../models/Notification';
import { SocketManager } from '../sockets/socket.manager';
import { FacultyStatus, MeetingRequestStatus, SocketEvent, UserRole } from '../constants/enums';

export class MeetingService {
  /**
   * Principal creates an urgent or standard meeting call for a faculty member
   */
  static async createMeetingRequest(data: {
    fromUserId: string;
    toFacultyId: string;
    type?: 'MEETING' | 'CALL' | 'URGENT_CABIN_CALL';
    priority?: 'URGENT' | 'NORMAL';
    reason: string;
    scheduledTime?: Date;
  }): Promise<IMeetingRequest> {
    const faculty = await Faculty.findById(data.toFacultyId);
    if (!faculty) {
      throw new Error('Faculty member not found');
    }

    const meeting = await MeetingRequest.create({
      fromUserId: data.fromUserId,
      toFacultyId: data.toFacultyId,
      type: data.type || 'URGENT_CABIN_CALL',
      priority: data.priority || 'URGENT',
      reason: data.reason,
      status: MeetingRequestStatus.PENDING,
      scheduledTime: data.scheduledTime
    });

    const populated = await MeetingRequest.findById(meeting._id)
      .populate('fromUserId', 'name email role')
      .populate({
        path: 'toFacultyId',
        populate: { path: 'userId', select: 'name email phone' }
      });

    // Create notification document for faculty
    const title = data.priority === 'URGENT' ? '🚨 URGENT: Principal Cabin Summon' : 'Principal Meeting Request';
    const body = `Reason: ${data.reason}`;
    await Notification.create({
      recipientId: faculty.userId,
      title,
      body,
      type: 'MEETING_REQUEST',
      payload: { meetingId: meeting._id, type: data.type, priority: data.priority }
    });

    // Realtime Socket.IO dispatch
    try {
      SocketManager.emitToUser(faculty.userId.toString(), SocketEvent.MEETING_CREATED, populated);
      SocketManager.emitToUser(faculty.userId.toString(), SocketEvent.NOTIFICATION_CREATED, { title, body, priority: 'URGENT' });
      SocketManager.broadcastAll('radar.updated', { alert: `Principal summoned ${(populated?.toFacultyId as any)?.userId?.name}` });
    } catch (e) {}

    return populated as IMeetingRequest;
  }

  /**
   * Faculty responds to meeting with 1-tap quick action (BUSY with auto class info OR ARRIVING)
   */
  static async quickRespondToMeeting(data: {
    meetingId: string;
    facultyUserId: string;
    responseType: 'BUSY' | 'ARRIVING' | 'AVAILABLE';
    autoDetails?: { roomName?: string; subjectName?: string; batchName?: string; studentsCount?: number };
    customNote?: string;
  }): Promise<IMeetingRequest | null> {
    const meeting = await MeetingRequest.findById(data.meetingId);
    if (!meeting) {
      throw new Error('Meeting request not found');
    }

    const faculty = await Faculty.findById(meeting.toFacultyId);

    let statusText: any = MeetingRequestStatus.ACCEPTED;
    let responseNote = '';

    if (data.responseType === 'BUSY') {
      statusText = 'BUSY_IN_CLASS';
      const d = data.autoDetails;
      responseNote = d?.roomName
        ? `BUSY: Currently taking lecture in ${d.roomName} (${d.subjectName || 'Class'} with ${d.batchName || 'Students'}, ${d.studentsCount || 54} present). Will report post-lecture.`
        : (data.customNote || 'BUSY: Currently conducting scheduled lecture.');
      
      if (faculty) {
        faculty.currentStatus = FacultyStatus.IN_CLASS;
        await faculty.save();
      }
    } else if (data.responseType === 'ARRIVING') {
      statusText = 'ON_THE_WAY';
      responseNote = 'ON THE WAY: Walking to Principal Cabin now (ETA ~2 mins).';
      if (faculty) {
        faculty.currentStatus = FacultyStatus.WITH_PRINCIPAL;
        await faculty.save();
      }
    } else {
      statusText = MeetingRequestStatus.ACCEPTED;
      responseNote = data.customNote || 'AVAILABLE: Present in faculty cabin.';
      if (faculty) {
        faculty.currentStatus = FacultyStatus.AVAILABLE;
        await faculty.save();
      }
    }

    meeting.status = statusText;
    meeting.responseNote = responseNote;
    meeting.autoDetails = data.autoDetails;
    await meeting.save();

    const populated = await MeetingRequest.findById(meeting._id)
      .populate('fromUserId', 'name email')
      .populate({
        path: 'toFacultyId',
        populate: { path: 'userId', select: 'name email phone' }
      });

    const facultyName = (populated?.toFacultyId as any)?.userId?.name || 'Faculty';
    const title = data.responseType === 'ARRIVING' ? `🟢 ${facultyName} is ON THE WAY` : `🔴 ${facultyName} is BUSY`;
    const body = responseNote;

    await Notification.create({
      recipientId: meeting.fromUserId,
      title,
      body,
      type: 'MEETING_RESPONSE',
      payload: { meetingId: meeting._id, status: statusText, autoDetails: data.autoDetails }
    });

    try {
      SocketManager.emitToUser(meeting.fromUserId.toString(), SocketEvent.MEETING_UPDATED, populated);
      SocketManager.emitToUser(meeting.fromUserId.toString(), SocketEvent.NOTIFICATION_CREATED, { title, body });
      SocketManager.broadcastAll('radar.updated', {
        facultyId: meeting.toFacultyId,
        facultyName,
        status: statusText,
        note: responseNote
      });
    } catch (e) {}

    return populated;
  }

  /**
   * Faculty responds to meeting request (Standard)
   */
  static async respondToMeeting(data: {
    meetingId: string;
    facultyUserId: string;
    status: MeetingRequestStatus;
    responseNote?: string;
  }): Promise<IMeetingRequest | null> {
    return this.quickRespondToMeeting({
      meetingId: data.meetingId,
      facultyUserId: data.facultyUserId,
      responseType: data.status === MeetingRequestStatus.ACCEPTED ? 'ARRIVING' : 'BUSY',
      customNote: data.responseNote
    });
  }

  /**
   * Get meeting requests for a faculty member
   */
  static async getFacultyMeetings(facultyId: string): Promise<IMeetingRequest[]> {
    return await MeetingRequest.find({ toFacultyId: facultyId })
      .populate('fromUserId', 'name email role')
      .sort({ createdAt: -1 });
  }

  /**
   * Get all meeting requests (for Principal dashboard)
   */
  static async getAllMeetings(): Promise<IMeetingRequest[]> {
    return await MeetingRequest.find()
      .populate('fromUserId', 'name email role')
      .populate({
        path: 'toFacultyId',
        populate: { path: 'userId', select: 'name email phone' }
      })
      .sort({ createdAt: -1 });
  }
}
