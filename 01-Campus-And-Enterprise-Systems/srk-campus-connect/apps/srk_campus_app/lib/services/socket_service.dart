import 'package:socket_io_client/socket_io_client.dart' as io;
import 'local_notification_service.dart';

typedef SocketCallback = void Function(dynamic data);

class SocketService {
  static final SocketService _instance = SocketService._internal();
  factory SocketService() => _instance;

  io.Socket? socket;
  bool isConnected = false;
  String? _token;
  final Map<String, List<SocketCallback>> _listeners = {};

  final List<String> _candidateSocketUrls = [
    'http://127.0.0.1:5001',
    'http://127.0.0.1:5000',
    'https://counting-criterion-identifies-implied.trycloudflare.com',
    'http://10.0.2.2:5001',
    'http://localhost:5001',
  ];

  SocketService._internal();

  void init([String? token]) {
    _token = token ?? _token;

    if (socket != null && socket!.connected) {
      if (token != null) {
        socket!.io.options?['auth'] = {'token': token};
      }
      return;
    }

    _connectToFirstAvailable(0);
  }

  void _connectToFirstAvailable(int index) {
    if (index >= _candidateSocketUrls.length) return;

    final targetUrl = _candidateSocketUrls[index];

    try {
      socket?.disconnect();
      socket?.dispose();

      socket = io.io(
        targetUrl,
        io.OptionBuilder()
            .setTransports(['websocket', 'polling'])
            .setAuth({'token': _token ?? ''})
            .enableAutoConnect()
            .enableReconnection()
            .setReconnectionAttempts(5)
            .setReconnectionDelay(1000)
            .build(),
      );

      socket!.onConnect((_) {
        isConnected = true;
        socket!.emit('join_room', {'room': 'campus_broadcast'});
        socket!.emit('join_room', {'room': 'principal_channel'});
      });

      socket!.onConnectError((err) {
        isConnected = false;
        if (index + 1 < _candidateSocketUrls.length) {
          _connectToFirstAvailable(index + 1);
        }
      });

      socket!.onDisconnect((_) {
        isConnected = false;
      });

      // Unified Notification & Summon Event Listeners
      socket!.on('urgent_summon_alert', (data) {
        _handleUrgentSummon(data);
        _notify('urgent_summon_alert', data);
      });

      socket!.on('meeting.new', (data) {
        _handleUrgentSummon(data);
        _notify('meeting.new', data);
      });

      socket!.on('campus_broadcast', (data) {
        _handleBroadcast(data);
        _notify('campus_broadcast', data);
      });

      socket!.on('campus_broadcast_message', (data) {
        _handleBroadcast(data);
        _notify('campus_broadcast_message', data);
      });

      socket!.on('broadcast.new', (data) {
        _handleBroadcast(data);
        _notify('broadcast.new', data);
      });

      socket!.on('urgent_summon_response', (data) => _notify('urgent_summon_response', data));
      socket!.on('radar.updated', (data) => _notify('radar.updated', data));
    } catch (e) {
      if (index + 1 < _candidateSocketUrls.length) {
        _connectToFirstAvailable(index + 1);
      }
    }
  }

  void _handleUrgentSummon(dynamic data) {
    if (data == null) return;
    final caller = data['callerName'] ?? 'Principal Cabin';
    final room = data['location'] ?? data['room'] ?? 'Principal Office';
    final reason = data['reason'] ?? 'Emergency Institutional Summon';

    LocalNotificationService().showNotification(
      title: 'URGENT: Principal Cabin Summon',
      body: '$caller has summoned you to $room. Reason: $reason. Tap to respond: [BUSY / ON THE WAY]',
      isUrgent: true,
      payload: 'urgent_summon',
    );
  }

  void _handleBroadcast(dynamic data) {
    if (data == null) return;
    final title = data['title'] ?? 'CAMPUS ANNOUNCEMENT';
    final message = data['message'] ?? data['body'] ?? 'New institutional notice posted.';

    LocalNotificationService().showNotification(
      title: title,
      body: message,
      isUrgent: false,
      payload: 'broadcast',
    );
  }

  void emit(String event, dynamic data) {
    if (socket != null && isConnected) {
      socket!.emit(event, data);
    }
  }

  void on(String event, SocketCallback callback) {
    if (!_listeners.containsKey(event)) {
      _listeners[event] = [];
    }
    _listeners[event]!.add(callback);
  }

  void off(String event, SocketCallback callback) {
    _listeners[event]?.remove(callback);
  }

  void _notify(String event, dynamic data) {
    if (_listeners.containsKey(event)) {
      for (final cb in List.from(_listeners[event]!)) {
        try {
          cb(data);
        } catch (_) {}
      }
    }
  }

  void disconnect() {
    socket?.disconnect();
    isConnected = false;
  }
}
