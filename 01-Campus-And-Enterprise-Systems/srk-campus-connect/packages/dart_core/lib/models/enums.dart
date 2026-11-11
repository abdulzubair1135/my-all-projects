enum UserRole {
  superAdmin('SUPER_ADMIN'),
  principal('PRINCIPAL'),
  faculty('FACULTY'),
  student('STUDENT');

  final String value;
  const UserRole(this.value);

  static UserRole fromString(String val) {
    return UserRole.values.firstWhere(
      (e) => e.value == val,
      orElse: () => UserRole.student,
    );
  }
}

enum FacultyStatus {
  available('AVAILABLE'),
  busy('BUSY'),
  inClass('IN_CLASS'),
  meeting('MEETING'),
  onBreak('ON_BREAK'),
  dnd('DND'),
  offline('OFFLINE');

  final String value;
  const FacultyStatus(this.value);

  static FacultyStatus fromString(String val) {
    return FacultyStatus.values.firstWhere(
      (e) => e.value == val,
      orElse: () => FacultyStatus.offline,
    );
  }
}

enum PresenceSource {
  dynamicQr('DYNAMIC_QR'),
  teacherScan('TEACHER_SCAN'),
  studentQr('STUDENT_QR'),
  timetable('TIMETABLE'),
  p2pProximity('P2P_PROXIMITY'),
  sensor('SENSOR'),
  manualOverride('MANUAL_OVERRIDE');

  final String value;
  const PresenceSource(this.value);

  static PresenceSource fromString(String val) {
    return PresenceSource.values.firstWhere(
      (e) => e.value == val,
      orElse: () => PresenceSource.dynamicQr,
    );
  }
}

enum SyncStatus {
  pending('PENDING'),
  syncing('SYNCING'),
  synced('SYNCED'),
  failed('FAILED'),
  rejected('REJECTED');

  final String value;
  const SyncStatus(this.value);
}
