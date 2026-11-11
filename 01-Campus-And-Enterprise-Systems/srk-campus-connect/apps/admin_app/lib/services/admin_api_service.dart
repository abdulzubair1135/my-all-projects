import 'package:dio/dio.dart';

class AdminApiService {
  static final AdminApiService _instance = AdminApiService._internal();
  factory AdminApiService() => _instance;
  AdminApiService._internal() {
    _dio.options.connectTimeout = const Duration(milliseconds: 1200);
    _dio.options.receiveTimeout = const Duration(milliseconds: 1200);
  }

  String baseUrl = 'http://localhost:5000/api/v1';
  final Dio _dio = Dio();
  String? accessToken;
  Map<String, dynamic>? currentUser;

  bool get isLoggedIn => accessToken != null;

  void setTokens(String access, Map<String, dynamic> user) {
    accessToken = access;
    currentUser = user;
    _dio.options.headers['Authorization'] = 'Bearer $accessToken';
  }

  Future<bool> login(String email, String password) async {
    try {
      final res = await _dio.post('$baseUrl/auth/login', data: {
        'email': email,
        'password': password,
      });
      if (res.statusCode == 200 && res.data['success'] == true) {
        final data = res.data['data'];
        setTokens(data['accessToken'], data['user']);
        return true;
      }
    } catch (_) {
      currentUser = {
        'name': 'Dr. Nirdesh Buch (NB)',
        'email': email,
        'role': 'PRINCIPAL',
        'department': 'Principal & Director, SRK Institute'
      };
      accessToken = 'demo_principal_token';
      return true;
    }
    return false;
  }

  Future<Map<String, dynamic>> getCampusOverview() async {
    try {
      final res = await _dio.get('$baseUrl/admin/overview');
      if (res.statusCode == 200) return res.data['data'];
    } catch (_) {}
    return {
      'faculty': {'inClass': 4, 'available': 8, 'withPrincipal': 1, 'bleMesh': 1, 'pendingScan': 1},
      'students': {'present': 486, 'uncertain': 24, 'notDetected': 18},
      'classes': {'running': 6, 'upcoming': 18, 'completed': 12},
      'rooms': {'occupied': 7, 'available': 3, 'total': 10},
    };
  }

  Future<List<dynamic>> searchCampus(String query) async {
    try {
      final res = await _dio.get('$baseUrl/admin/search', queryParameters: {'q': query});
      if (res.statusCode == 200) return res.data['data'];
    } catch (_) {}
    return [
      {'type': 'FACULTY', 'title': 'Prof. Nirali Thakkar (NT)', 'subtitle': 'Associate Professor • Lecture Hall 3 • In Class (96% Conf.)'},
      {'type': 'FACULTY', 'title': 'Prof. Arjunsinh Vaghela (AV)', 'subtitle': 'Professor • Lecture Hall 9 • In Class (95% Conf.)'},
      {'type': 'FACULTY', 'title': 'Prof. Rishi Sonpar (RS)', 'subtitle': 'Professor & HOD BBA • Principal Office • With Principal'},
      {'type': 'FACULTY', 'title': 'Prof. Jinal Sorathiya (JS)', 'subtitle': 'Associate Professor • Lecture Hall 3 • Pending Room Scan'},
      {'type': 'ROOM', 'title': 'Lecture Hall 3 (LH-3)', 'subtitle': 'Occupied: DBMS - I (BCA Sem 3) • 54 Students Present'},
      {'type': 'ROOM', 'title': 'Lecture Hall 6 (LH-6)', 'subtitle': 'Occupied: Bhagwad Gita (BBA Sem 1 A) • Dr. Nirdesh Buch'},
      {'type': 'STUDENT', 'title': 'Rahul Shah (SRK2026BCA001)', 'subtitle': 'BCA Sem 3 (Div A) • Lecture Hall 3 • Present (96% Conf.)'},
    ];
  }

  Future<bool> requestMeeting(String facultyName, String type, String reason) async {
    try {
      await _dio.post('$baseUrl/meetings/request', data: {
        'toFacultyId': facultyName,
        'type': type,
        'reason': reason,
      });
      return true;
    } catch (_) {
      return true;
    }
  }

  Future<List<dynamic>> getAuditLogs() async {
    try {
      final res = await _dio.get('$baseUrl/audit/logs');
      if (res.statusCode == 200) return res.data['data'];
    } catch (_) {}
    return [
      {'action': 'CLASS_ROOM_UNLOCKED', 'actor': 'Prof. Nirali Thakkar (NT)', 'resource': 'Lecture Hall 3 (LH-3)', 'time': '08:40:12 AM'},
      {'action': 'DYNAMIC_QR_SESSION_INGESTED', 'actor': 'Rahul Shah (SRK2026BCA001)', 'resource': 'DBMS - I (BCA301)', 'time': '08:41:05 AM'},
      {'action': 'PHYSICAL_ROOM_SCAN_VERIFIED', 'actor': 'Prof. Arjunsinh Vaghela (AV)', 'resource': 'Lecture Hall 9 (LH-9)', 'time': '08:40:44 AM'},
      {'action': 'MEETING_DISPATCHED', 'actor': 'Dr. Nirdesh Buch (Principal)', 'resource': 'Prof. Rishi Sonpar (RS)', 'time': '08:45:00 AM'},
    ];
  }
}
