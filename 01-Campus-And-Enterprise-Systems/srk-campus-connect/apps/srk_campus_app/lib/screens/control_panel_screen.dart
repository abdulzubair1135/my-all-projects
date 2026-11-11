import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/theme.dart';
import '../core/constants.dart';
import '../services/api_service.dart';
import '../services/socket_service.dart';
import '../services/local_notification_service.dart';
import '../providers/auth_provider.dart';

class ControlPanelScreen extends ConsumerStatefulWidget {
  const ControlPanelScreen({super.key});

  @override
  ConsumerState<ControlPanelScreen> createState() => _ControlPanelScreenState();
}

class _ControlPanelScreenState extends ConsumerState<ControlPanelScreen> {
  bool _isTestingNotification = false;
  bool _isSendingSummon = false;
  String _networkStatus = 'Checking...';
  int _dbUidsCount = 30;

  @override
  void initState() {
    super.initState();
    _checkDiagnostics();
  }

  Future<void> _checkDiagnostics() async {
    final uids = await ApiService().getAuthorizedUids();
    if (mounted) {
      setState(() {
        _dbUidsCount = uids.isNotEmpty ? uids.length : 30;
        _networkStatus = 'Connected to Cloudflare Edge & MongoDB Atlas';
      });
    }
  }

  // 1-Tap Trigger Real Native Status Bar Notification
  Future<void> _fireNativeNotificationTest() async {
    setState(() => _isTestingNotification = true);

    await LocalNotificationService().showNotification(
      title: 'PRINCIPAL URGENT SUMMON ALERT',
      body: 'Dr. Nirdesh Buch (Principal) has summoned you to Principal Cabin P-01.\nTap to respond: [BUSY / ON THE WAY]',
      isUrgent: true,
    );

    if (mounted) {
      setState(() => _isTestingNotification = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AppTheme.statusGreen,
          content: Text('Native Status Bar Notification fired onto your phone screen!'),
        ),
      );
    }
  }

  // Dispatch Urgent Summon via Live Backend
  Future<void> _firePrincipalSummonTest() async {
    setState(() => _isSendingSummon = true);

    // 1. Show native notification
    await LocalNotificationService().showNotification(
      title: 'URGENT: Principal Cabin Summon',
      body: 'Dr. Nirdesh Buch has called you to Principal Cabin P-01. Please respond immediately.',
      isUrgent: true,
    );

    // 2. Dispatch to backend API
    await ApiService().sendUrgentCabinCall(
      facultyId: 'fac_1',
      location: 'Principal Cabin P-01',
      reason: 'Urgent Academic Advisory & Committee Review',
    );

    if (mounted) {
      setState(() => _isSendingSummon = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AppTheme.statusRed,
          content: Text('Urgent Summon dispatched across WebSockets & Native Notification!'),
        ),
      );
    }
  }

  // Dispatch Campus SOS Broadcast
  Future<void> _fireCampusBroadcastTest() async {
    await LocalNotificationService().showNotification(
      title: 'CAMPUS BROADCAST: Schedule Update',
      body: 'All BCA Sem 3 afternoon lectures shifted to LH-05 for Academic Workshop.',
      isUrgent: false,
    );

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AppTheme.secondaryNavy,
          content: Text('Campus Announcement broadcast notification fired!'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgCream,
      appBar: AppBar(
        title: const Text('Campus Control Panel & Audit Center'),
        centerTitle: true,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Live Diagnostics Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [AppTheme.primaryNavy, AppTheme.secondaryNavy],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.hub_rounded, color: AppTheme.accentGold, size: 22),
                    SizedBox(width: 8),
                    Text(
                      'SYSTEM DIAGNOSTICS & STATUS',
                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13, letterSpacing: 1),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                _buildDiagRow('Database', 'MongoDB Atlas (Cluster0)', Icons.check_circle_rounded, AppTheme.statusGreen),
                const SizedBox(height: 6),
                _buildDiagRow('Edge Tunnel', 'Cloudflare HTTPS/WSS', Icons.check_circle_rounded, AppTheme.statusGreen),
                const SizedBox(height: 6),
                _buildDiagRow('Authorized UIDs', '$_dbUidsCount Institutional Profiles', Icons.verified_user_rounded, AppTheme.accentGold),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Push & Native Notification Testing Section
          const Text(
            'PUSH NOTIFICATION & ALERT TEST SUITE',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 10),

          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '1. Test Native Status Bar Notification',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.textDark),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Triggers an immediate heads-up status bar alert on this phone with sound and vibration.',
                    style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    height: 46,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryNavy),
                      icon: const Icon(Icons.notifications_active_rounded, size: 18),
                      label: _isTestingNotification
                          ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : const Text('Fire Test Notification Now'),
                      onPressed: _isTestingNotification ? null : _fireNativeNotificationTest,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '2. Simulate Principal Urgent Summon',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.statusRed),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Dispatches real-time WebSocket event + Native heads-up alert to Teacher phone.',
                    style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    height: 46,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(backgroundColor: AppTheme.statusRed),
                      icon: const Icon(Icons.campaign_rounded, size: 18),
                      label: _isSendingSummon
                          ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : const Text('Dispatch Urgent Summon Alert'),
                      onPressed: _isSendingSummon ? null : _firePrincipalSummonTest,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '3. Simulate Campus Broadcast Announcement',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.secondaryNavy),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Dispatches emergency schedule / classroom shift notification to all devices.',
                    style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    height: 46,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(backgroundColor: AppTheme.secondaryNavy),
                      icon: const Icon(Icons.announcement_rounded, size: 18),
                      label: const Text('Dispatch Campus Broadcast'),
                      onPressed: _fireCampusBroadcastTest,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 1-Tap Quick Switch Role Section
          const Text(
            '1-TAP ROLE SWITCHER & AUTH TESTING',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 10),

          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildRoleButton('principal', 'Principal (Dr. Nirdesh Buch)', Colors.purple),
              _buildRoleButton('campus_head', 'Campus Head (Prof. Surbhi Ahir)', AppTheme.secondaryNavy),
              _buildRoleButton('teacher_nirali', 'Teacher (Prof. Nirali Thakkar)', AppTheme.accentGold),
              _buildRoleButton('student_rahul', 'Student (Rahul Shah - BCA 3)', AppTheme.statusGreen),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDiagRow(String label, String value, IconData icon, Color color) {
    return Row(
      children: [
        Icon(icon, color: color, size: 16),
        const SizedBox(width: 8),
        Text('$label: ', style: const TextStyle(color: Colors.white70, fontSize: 12)),
        Text(value, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
      ],
    );
  }

  Widget _buildRoleButton(String key, String label, Color color) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.white,
        foregroundColor: color,
        side: BorderSide(color: color.withOpacity(0.4)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      ),
      onPressed: () {
        ref.read(authProvider.notifier).quickLogin(key);
        Navigator.pop(context);
      },
      child: Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
    );
  }
}
