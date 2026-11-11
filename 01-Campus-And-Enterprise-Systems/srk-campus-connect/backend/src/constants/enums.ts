export enum UserRole {
  SUPER_ADMIN = 'SUPER_ADMIN',
  PRINCIPAL = 'PRINCIPAL',
  FACULTY = 'FACULTY',
  STUDENT = 'STUDENT'
}

export enum FacultyStatus {
  IN_CLASS = 'IN_CLASS', // Verified physical scan in room
  NOT_IN_CLASS_PENDING_SCAN = 'NOT_IN_CLASS_PENDING_SCAN', // Scheduled in timetable but not yet scanned room QR
  WITH_PRINCIPAL = 'WITH_PRINCIPAL', // Detected / in meeting with Principal
  AVAILABLE = 'AVAILABLE', // Available in Staff Room / Cabin
  BUSY = 'BUSY',
  MEETING = 'MEETING',
  ON_BREAK = 'ON_BREAK',
  MOBILE_DATA_OFF_BLE_ONLY = 'MOBILE_DATA_OFF_BLE_ONLY',
  DND = 'DND',
  OFFLINE = 'OFFLINE'
}

export enum RoomStatus {
  AVAILABLE = 'AVAILABLE',
  OCCUPIED = 'OCCUPIED',
  MAINTENANCE = 'MAINTENANCE'
}

export enum ClassSessionStatus {
  SCHEDULED = 'SCHEDULED',
  ACTIVE = 'ACTIVE',
  PAUSED = 'PAUSED',
  ENDED = 'ENDED',
  CANCELLED = 'CANCELLED'
}

export enum AttendanceStatus {
  PRESENT = 'PRESENT',
  UNCERTAIN = 'UNCERTAIN',
  ABSENT = 'ABSENT',
  LEAVE = 'LEAVE',
  EXCUSED = 'EXCUSED'
}

export enum PresenceState {
  HIGH_CONFIDENCE = 'HIGH_CONFIDENCE',
  PROBABLE = 'PROBABLE',
  UNCERTAIN = 'UNCERTAIN',
  NOT_DETECTED = 'NOT_DETECTED',
  UNKNOWN = 'UNKNOWN'
}

export enum PresenceSource {
  DYNAMIC_QR = 'DYNAMIC_QR',
  TEACHER_SCAN = 'TEACHER_SCAN',
  STUDENT_QR = 'STUDENT_QR',
  TIMETABLE = 'TIMETABLE',
  P2P_PROXIMITY = 'P2P_PROXIMITY',
  BLE_BEACON = 'BLE_BEACON',
  SENSOR = 'SENSOR',
  MANUAL_OVERRIDE = 'MANUAL_OVERRIDE'
}

export enum SyncEventStatus {
  PENDING = 'PENDING',
  SYNCING = 'SYNCING',
  PROCESSED = 'PROCESSED',
  DUPLICATE = 'DUPLICATE',
  INVALID_SIGNATURE = 'INVALID_SIGNATURE',
  REJECTED = 'REJECTED',
  FAILED = 'FAILED'
}

export enum MeetingRequestStatus {
  PENDING = 'PENDING',
  ACCEPTED = 'ACCEPTED',
  DECLINED = 'DECLINED',
  RESCHEDULED = 'RESCHEDULED',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED'
}

export enum LeaveRequestStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  CANCELLED = 'CANCELLED'
}

export enum DevicePlatform {
  ANDROID = 'ANDROID',
  IOS = 'IOS',
  WEB = 'WEB',
  DESKTOP = 'DESKTOP'
}

export enum MovementState {
  STATIONARY = 'STATIONARY',
  WALKING = 'WALKING',
  MOVING = 'MOVING',
  UNKNOWN = 'UNKNOWN'
}

export enum SocketEvent {
  CLASS_STARTED = 'class.started',
  CLASS_ENDED = 'class.ended',
  ATTENDANCE_UPDATED = 'attendance.updated',
  PRESENCE_UPDATED = 'presence.updated',
  FACULTY_STATUS_CHANGED = 'faculty.status.changed',
  MEETING_CREATED = 'meeting.created',
  MEETING_UPDATED = 'meeting.updated',
  ROOM_CHANGED = 'room.changed',
  TIMETABLE_UPDATED = 'timetable.updated',
  NOTIFICATION_CREATED = 'notification.created',
  SYNC_COMPLETED = 'sync.completed',
  BLE_ALERT_DISPATCHED = 'ble.alert.dispatched'
}
