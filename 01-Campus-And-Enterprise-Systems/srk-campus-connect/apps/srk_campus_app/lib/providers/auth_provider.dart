import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../services/socket_service.dart';
import '../core/constants.dart';

class AuthUser {
  final String id;
  final String? uid;
  final String name;
  final String email;
  final String role; // 'PRINCIPAL', 'CAMPUS_HEAD', 'ADMIN', 'FACULTY', 'STUDENT'
  final String? department;
  final String? designation;
  final String? cabin;
  final String? rollNo;
  final String? token;

  AuthUser({
    required this.id,
    this.uid,
    required this.name,
    required this.email,
    required this.role,
    this.department,
    this.designation,
    this.cabin,
    this.rollNo,
    this.token,
  });

  bool get isPrincipal => role == 'PRINCIPAL' || role == 'CAMPUS_HEAD' || role == 'ADMIN';
  bool get isTeacher => role == 'FACULTY';
  bool get isStudent => role == 'STUDENT';
}

class AuthState {
  final bool isAuthenticated;
  final bool isLoading;
  final AuthUser? user;
  final String? errorMessage;
  final String? successMessage;

  AuthState({
    this.isAuthenticated = false,
    this.isLoading = false,
    this.user,
    this.errorMessage,
    this.successMessage,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    bool? isLoading,
    AuthUser? user,
    String? errorMessage,
    String? successMessage,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isLoading: isLoading ?? this.isLoading,
      user: user ?? this.user,
      errorMessage: errorMessage,
      successMessage: successMessage,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState());

  // Quick 1-Tap Login
  Future<void> quickLogin(String accountKey) async {
    final account = AppConstants.quickAccounts[accountKey];
    if (account == null) return;

    state = state.copyWith(isLoading: true, errorMessage: null, successMessage: null);

    final res = await ApiService().login(account['email']!, account['password']!);
    String? token;
    String id = 'srk_${accountKey}_id';

    if (res['success'] == true && res['data'] != null) {
      final data = res['data'];
      token = data['tokens']?['accessToken'] ?? data['token'];
      if (data['user'] != null && data['user']['id'] != null) {
        id = data['user']['id'];
      }
    }

    final user = AuthUser(
      id: id,
      uid: account['uid'] ?? 'SRK-${account['role']}-01',
      name: account['name']!,
      email: account['email']!,
      role: account['role']!,
      department: account['dept'],
      designation: account['title'],
      cabin: account['cabin'],
      rollNo: account['rollNo'],
      token: token ?? 'demo_token_srk',
    );

    ApiService().setAuthToken(user.token);
    SocketService().init(user.token!);

    state = state.copyWith(
      isAuthenticated: true,
      isLoading: false,
      user: user,
    );
  }

  // Login via UID or Email
  Future<bool> login(String identifier, String password) async {
    state = state.copyWith(isLoading: true, errorMessage: null, successMessage: null);

    final res = await ApiService().login(identifier.trim(), password.trim());
    if (res['success'] == true && res['data'] != null) {
      final data = res['data'];
      final u = data['user'] ?? {};
      final token = data['tokens']?['accessToken'] ?? data['token'] ?? 'jwt_token';

      final user = AuthUser(
        id: u['id'] ?? u['_id'] ?? 'user_1',
        uid: u['uid'] ?? identifier.toUpperCase(),
        name: u['name'] ?? identifier.split('@')[0],
        email: u['email'] ?? identifier,
        role: u['role'] ?? 'FACULTY',
        department: u['department'] ?? 'SRK Campus',
        designation: u['designation'],
        cabin: u['cabinNumber'] ?? u['cabin'],
        rollNo: u['rollNumber'] ?? u['rollNo'],
        token: token,
      );

      ApiService().setAuthToken(token);
      SocketService().init(token);

      state = state.copyWith(
        isAuthenticated: true,
        isLoading: false,
        user: user,
      );
      return true;
    } else {
      state = state.copyWith(
        isLoading: false,
        errorMessage: res['message'] ?? 'Invalid UID/Email or password',
      );
      return false;
    }
  }

  // Sign Up with Campus UID & OTP Verification
  Future<bool> signupWithUid({
    required String uid,
    required String email,
    String? phone,
    required String password,
    required String otp,
  }) async {
    state = state.copyWith(isLoading: true, errorMessage: null, successMessage: null);

    final res = await ApiService().signupWithUid(
      uid: uid,
      email: email,
      phone: phone,
      password: password,
      otp: otp,
    );

    if (res['success'] == true && res['data'] != null) {
      final data = res['data'];
      final u = data['user'] ?? {};
      final token = data['tokens']?['accessToken'] ?? data['token'] ?? 'jwt_token';

      final user = AuthUser(
        id: u['id'] ?? u['_id'] ?? 'user_new',
        uid: u['uid'] ?? uid,
        name: u['name'] ?? 'Faculty / Student',
        email: u['email'] ?? email,
        role: u['role'] ?? 'FACULTY',
        department: u['department'] ?? 'SRK Campus',
        designation: u['designation'],
        cabin: u['cabinNumber'],
        rollNo: u['rollNumber'],
        token: token,
      );

      ApiService().setAuthToken(token);
      SocketService().init(token);

      state = state.copyWith(
        isAuthenticated: true,
        isLoading: false,
        user: user,
        successMessage: 'Account activated successfully!',
      );
      return true;
    } else {
      state = state.copyWith(
        isLoading: false,
        errorMessage: res['message'] ?? 'Verification or registration failed',
      );
      return false;
    }
  }

  void logout() {
    ApiService().setAuthToken(null);
    SocketService().disconnect();
    state = AuthState();
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});
