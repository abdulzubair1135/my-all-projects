import 'package:dio/dio.dart';
import '../models/presence_event_model.dart';

class CampusApiClient {
  final Dio dio;
  String? accessToken;
  String? refreshToken;
  final String baseUrl;

  CampusApiClient({
    required this.baseUrl,
    this.accessToken,
    this.refreshToken,
  }) : dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 10),
          headers: {'Content-Type': 'application/json'},
        )) {
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          if (accessToken != null) {
            options.headers['Authorization'] = 'Bearer $accessToken';
          }
          return handler.next(options);
        },
        onError: (DioException error, handler) async {
          // Handle automatic 401 token refresh
          if (error.response?.statusCode == 401 && refreshToken != null) {
            final refreshed = await _refreshTokens();
            if (refreshed) {
              final originalRequest = error.requestOptions;
              originalRequest.headers['Authorization'] = 'Bearer $accessToken';
              try {
                final retryResponse = await dio.fetch(originalRequest);
                return handler.resolve(retryResponse);
              } catch (e) {
                return handler.next(error);
              }
            }
          }
          return handler.next(error);
        },
      ),
    );
  }

  Future<bool> _refreshTokens() async {
    try {
      final res = await Dio(BaseOptions(baseUrl: baseUrl)).post('/auth/refresh', data: {
        'refreshToken': refreshToken,
      });
      if (res.statusCode == 200 && res.data['success'] == true) {
        accessToken = res.data['data']['accessToken'];
        refreshToken = res.data['data']['refreshToken'];
        return true;
      }
    } catch (_) {}
    return false;
  }

  /// Batch sync presence events (directly or on behalf of nearby peers)
  Future<Map<String, dynamic>> syncEvents({
    required List<PresenceEventModel> events,
    String? gatewayDeviceId,
  }) async {
    final response = await dio.post('/sync/events', data: {
      if (gatewayDeviceId != null) 'gatewayDeviceId': gatewayDeviceId,
      'events': events.map((e) => e.toJson()).toList(),
    });
    return response.data as Map<String, dynamic>;
  }
}
