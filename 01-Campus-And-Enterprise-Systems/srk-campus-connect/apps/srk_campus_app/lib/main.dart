import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/theme.dart';
import 'providers/auth_provider.dart';
import 'services/local_notification_service.dart';
import 'services/socket_service.dart';
import 'screens/auth/login_screen.dart';
import 'screens/main_shell_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await LocalNotificationService().initialize();
  SocketService().init();
  runApp(const ProviderScope(child: SRKCampusApp()));
}

class SRKCampusApp extends ConsumerStatefulWidget {
  const SRKCampusApp({super.key});

  @override
  ConsumerState<SRKCampusApp> createState() => _SRKCampusAppState();
}

class _SRKCampusAppState extends ConsumerState<SRKCampusApp> {
  @override
  void initState() {
    super.initState();
    _setupGlobalNotificationListeners();
  }

  void _setupGlobalNotificationListeners() {
    // When Principal sends urgent summon -> show native status bar notification
    SocketService().on('meeting.new', (data) {
      if (data != null) {
        LocalNotificationService().showNotification(
          title: 'URGENT: Principal Cabin Summon',
          body: '${data['callerName'] ?? 'Dr. Nirdesh Buch'} has summoned you to ${data['location'] ?? 'Principal Cabin P-01'}. Tap to respond: [BUSY / ON THE WAY]',
          isUrgent: true,
        );
      }
    });

    // When Campus Broadcast arrives -> show native announcement notification
    SocketService().on('broadcast.new', (data) {
      if (data != null) {
        LocalNotificationService().showNotification(
          title: 'CAMPUS BROADCAST',
          body: data['message'] ?? 'New institutional update posted.',
          isUrgent: false,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    return MaterialApp(
      title: 'SRK Campus Super App',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: authState.isAuthenticated ? const MainShellScreen() : const LoginScreen(),
    );
  }
}
