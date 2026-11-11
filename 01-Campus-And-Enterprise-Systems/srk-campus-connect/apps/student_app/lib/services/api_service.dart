import 'package:campus_dart_core/campus_dart_core.dart';
import 'package:dio/dio.dart';

class StudentApiService {
  static final StudentApiService _instance = StudentApiService._internal();
  factory StudentApiService() => _instance;
  StudentApiService._internal() {
    _dio.options.connectTimeout = const Duration(milliseconds: 1200);
    _dio.options.receiveTimeout = const Duration(milliseconds: 1200);
  }

  String baseUrl = 'http://localhost:5000/api/v1';
  final Dio _dio = Dio();
  String? accessToken;
  String? refreshToken;
  Map<String, dynamic>? currentUser;

  final InMemoryOfflineQueue offlineQueue = InMemoryOfflineQueue();

  bool get isLoggedIn => accessToken != null;

  void setTokens(String access, String refresh, Map<String, dynamic> user) {
    accessToken = access;
    refreshToken = refresh;
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
        setTokens(data['accessToken'], data['refreshToken'], data['user']);
        return true;
      }
    } catch (_) {
      // Offline fallback demo mode for SRK Institute
      currentUser = {
        'name': 'Rahul Shah',
        'email': email,
        'role': 'STUDENT',
        'enrollmentNumber': 'SRK2026BCA001',
        'department': 'Bachelor of Computer Applications',
        'program': 'BCA Sem 3',
        'room': 'Lecture Hall 3',
        'semester': 3,
        'division': 'A'
      };
      accessToken = 'demo_access_token';
      return true;
    }
    return false;
  }

  Future<Map<String, dynamic>> getCurrentClass() async {
    return {
      'sessionId': 'sess_dbms_301',
      'subject': 'DBMS - I (BCA301)',
      'faculty': 'Prof. Nirali Thakkar (NT)',
      'room': 'Lecture Hall 3',
      'startTime': '08:40 AM',
      'endTime': '09:40 AM',
      'session': 'Session 1',
      'status': 'ACTIVE',
      'teacherStatus': 'IN_CLASS (Teaching - LH 3)',
      'confidence': 96,
    };
  }

  // Real SRK Master Timetable Data mapped to Lecture Halls 1-10
  Map<String, List<Map<String, dynamic>>> getSRKTimetable(String selectedProgram, String day) {
    final Map<String, Map<String, List<Map<String, dynamic>>>> masterData = {
      'BCA Sem 3 (LH-3)': {
        'Monday': [
          {'session': 'Session 1 (08:40 - 09:40 AM)', 'subject': 'DBMS - I', 'code': 'BCA301', 'faculty': 'Prof. Nirali Thakkar (NT)', 'room': 'Lecture Hall 3'},
          {'session': 'Session 2 (09:45 - 10:40 AM)', 'subject': 'Lab: Data Structure using C', 'code': 'BCA302L', 'faculty': 'Prof. Arjunsinh Vaghela (AV)', 'room': 'DBMS & C Lab'},
          {'session': 'Session 3 (11:30 - 12:25 PM)', 'subject': 'Indian Thinkers', 'code': 'BCA303', 'faculty': 'Prof. Rishi Joshi (RJ)', 'room': 'Lecture Hall 3'},
          {'session': 'Session 4 (12:30 - 01:25 PM)', 'subject': 'Understanding OOP with Python', 'code': 'BCA304', 'faculty': 'Prof. Prakash Lambha (PL)', 'room': 'Lecture Hall 3'},
        ],
        'Tuesday': [
          {'session': 'Session 1 (08:40 - 09:40 AM)', 'subject': 'CBNT (JS) / Cyber Security (NT)', 'code': 'BCA305', 'faculty': 'Prof. Jinal Sorathiya (JS) / Prof. Nirali Thakkar (NT)', 'room': 'Lecture Hall 3'},
          {'session': 'Session 2 (09:45 - 10:40 AM)', 'subject': 'Indian Thinkers', 'code': 'BCA303', 'faculty': 'Prof. Rishi Joshi (RJ)', 'room': 'Lecture Hall 3'},
          {'session': 'Session 3 (11:30 - 12:25 PM)', 'subject': 'Lab: DBMS - I', 'code': 'BCA301L', 'faculty': 'Prof. Nirali Thakkar (NT)', 'room': 'DBMS & C Lab'},
          {'session': 'Session 4 (12:30 - 01:25 PM)', 'subject': 'Lab: OOP with Python', 'code': 'BCA304L', 'faculty': 'Prof. Prakash Lambha (PL)', 'room': 'Python & App Lab'},
        ],
      },
      'BCA Sem 1 (LH-5)': {
        'Monday': [
          {'session': 'Session 1 (08:40 - 09:40 AM)', 'subject': 'Statistics', 'code': 'BCA101', 'faculty': 'Prof. Jinal Sorathiya (JS)', 'room': 'Lecture Hall 5'},
          {'session': 'Session 2 (09:45 - 10:40 AM)', 'subject': 'Web Designing using HTML/CSS/JS', 'code': 'BCA102', 'faculty': 'Prof. Nirali Thakkar (NT)', 'room': 'Lecture Hall 5'},
          {'session': 'Session 3 (11:30 - 12:25 PM)', 'subject': 'Digital Electronics', 'code': 'BCA103', 'faculty': 'Prof. Prakash Lambha (PL)', 'room': 'Lecture Hall 5'},
          {'session': 'Session 4 (12:30 - 01:25 PM)', 'subject': 'Bhagavad Gita & Life Management', 'code': 'BCA104', 'faculty': 'Dr. Nirdesh Buch (NB - Principal)', 'room': 'Lecture Hall 5'},
        ]
      },
      'BCA Sem 5 (LH-9)': {
        'Monday': [
          {'session': 'Session 1 (08:40 - 09:40 AM)', 'subject': 'Advanced DBMS', 'code': 'BCA501', 'faculty': 'Prof. Arjunsinh Vaghela (AV)', 'room': 'Lecture Hall 9'},
          {'session': 'Session 2 (09:45 - 10:40 AM)', 'subject': 'Operational Research', 'code': 'BCA502', 'faculty': 'Prof. Jinal Sorathiya (JS)', 'room': 'Lecture Hall 9'},
          {'session': 'Session 3 (11:30 - 12:25 PM)', 'subject': 'Software Engineering', 'code': 'BCA503', 'faculty': 'Prof. Nirali Thakkar (NT)', 'room': 'Lecture Hall 9'},
          {'session': 'Session 4 (12:30 - 01:25 PM)', 'subject': 'Understanding Operating Systems', 'code': 'BCA504', 'faculty': 'Prof. Arjunsinh Vaghela (AV)', 'room': 'Lecture Hall 9'},
        ]
      },
      'BBA Sem 1 Class I (LH-6)': {
        'Monday': [
          {'session': 'Session 1 (08:40 - 09:40 AM)', 'subject': 'Introduction to Bhagwad Gita', 'code': 'BBA101', 'faculty': 'Dr. Nirdesh Buch (NB - Principal)', 'room': 'Lecture Hall 6'},
          {'session': 'Session 2 (09:45 - 10:40 AM)', 'subject': 'Fundamentals of Management', 'code': 'BBA102', 'faculty': 'Prof. Rishi Sonpar (RS)', 'room': 'Lecture Hall 6'},
          {'session': 'Session 3 (11:30 - 12:25 PM)', 'subject': 'E-Commerce & Digital Solutions', 'code': 'BBA103', 'faculty': 'Prof. Mayur Meghani (MM)', 'room': 'Lecture Hall 6'},
          {'session': 'Session 4 (12:30 - 01:25 PM)', 'subject': 'Economics-1', 'code': 'BBA104', 'faculty': 'Prof. Chandni Thacker (CT)', 'room': 'Lecture Hall 6'},
        ]
      },
      'BBA Sem 1 Class II (LH-7)': {
        'Monday': [
          {'session': 'Session 1 (08:40 - 09:40 AM)', 'subject': 'Business Organization & Structure', 'code': 'BBA105', 'faculty': 'Prof. Abhishek Abhani (AA)', 'room': 'Lecture Hall 7'},
          {'session': 'Session 2 (09:45 - 10:40 AM)', 'subject': 'E-Commerce & Digital Solutions', 'code': 'BBA103', 'faculty': 'Prof. Mayur Meghani (MM)', 'room': 'Lecture Hall 7'},
          {'session': 'Session 3 (11:30 - 12:25 PM)', 'subject': 'Business Statistics/Ecology', 'code': 'BBA106', 'faculty': 'Prof. Jinal Sorathiya (JS)', 'room': 'Lecture Hall 7'},
          {'session': 'Session 4 (12:30 - 01:25 PM)', 'subject': 'Fundamentals of Management', 'code': 'BBA102', 'faculty': 'Prof. Rishi Sonpar (RS)', 'room': 'Lecture Hall 7'},
        ]
      },
      'BBA Sem 3 (LH-1)': {
        'Monday': [
          {'session': 'Session 1 (08:40 - 09:40 AM)', 'subject': 'Consumer Behaviour', 'code': 'BBA301', 'faculty': 'Prof. Stephen Sober (SS)', 'room': 'Lecture Hall 1'},
          {'session': 'Session 2 (09:45 - 10:40 AM)', 'subject': 'Humanities', 'code': 'BBA302', 'faculty': 'Prof. Abhishek Abhani (AA)', 'room': 'Lecture Hall 1'},
          {'session': 'Session 3 (11:30 - 12:25 PM)', 'subject': 'HRM-1', 'code': 'BBA303', 'faculty': 'Prof. Rishi Sonpar (RS)', 'room': 'Lecture Hall 1'},
          {'session': 'Session 4 (12:30 - 01:25 PM)', 'subject': 'Practical English - III', 'code': 'BBA304', 'faculty': 'Prof. Rishi Joshi (RJ)', 'room': 'Lecture Hall 1'},
        ]
      },
      'BBA Sem 5 (LH-2)': {
        'Monday': [
          {'session': 'Session 1 (08:40 - 09:40 AM)', 'subject': 'Mercantile Law', 'code': 'BBA501', 'faculty': 'Prof. Rishi Sonpar (RS)', 'room': 'Lecture Hall 2'},
          {'session': 'Session 2 (09:45 - 10:40 AM)', 'subject': 'Direct Tax', 'code': 'BBA502', 'faculty': 'Prof. Chandni Thacker (CT)', 'room': 'Lecture Hall 2'},
          {'session': 'Session 3 (11:30 - 12:25 PM)', 'subject': 'Business Environment - 2', 'code': 'BBA503', 'faculty': 'Dr. Nirdesh Buch (NB - Principal)', 'room': 'Lecture Hall 2'},
          {'session': 'Session 4 (12:30 - 01:25 PM)', 'subject': 'CM & OD', 'code': 'BBA504', 'faculty': 'Prof. Stephen Sober (SS)', 'room': 'Lecture Hall 2'},
        ]
      },
    };

    return masterData[selectedProgram] ?? masterData['BCA Sem 3 (LH-3)']!;
  }

  Future<Map<String, dynamic>> submitLeave(String reason, DateTime from, DateTime to) async {
    return {'success': true, 'message': 'Leave application submitted to SRK Faculty'};
  }

  Future<bool> recordPresenceQr(String qrPayload) async {
    final now = DateTime.now().millisecondsSinceEpoch;
    final event = PresenceEventModel(
      eventId: 'evt_$now',
      userId: currentUser?['enrollmentNumber'] ?? 'SRK2026BCA001',
      deviceId: 'dev_phone_rahul',
      sessionId: 'sess_dbms_301',
      source: PresenceSource.dynamicQr,
      confidence: 0.96,
      timestamp: now,
      payload: {'qrToken': qrPayload},
      signature: 'ed25519_signed_hash_valid',
    );

    await offlineQueue.enqueue(event);
    return true;
  }
}
