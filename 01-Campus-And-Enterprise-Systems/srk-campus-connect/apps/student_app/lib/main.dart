import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'services/api_service.dart';
import 'screens/login_screen.dart';
import 'screens/qr_scanner_screen.dart';
import 'screens/student_id_qr_screen.dart';
import 'screens/timetable_screen.dart';
import 'screens/attendance_history_screen.dart';
import 'screens/leave_request_screen.dart';
import 'screens/p2p_sync_screen.dart';

void main() {
  runApp(const ProviderScope(child: StudentApp()));
}

class StudentApp extends StatefulWidget {
  const StudentApp({super.key});

  @override
  State<StudentApp> createState() => _StudentAppState();
}

class _StudentAppState extends State<StudentApp> {
  bool _isLoggedIn = false;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SRK Student Portal',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1565C0)),
        useMaterial3: true,
      ),
      home: _isLoggedIn
          ? StudentMainNavigation(onLogout: () => setState(() => _isLoggedIn = false))
          : LoginScreen(onLoginSuccess: () => setState(() => _isLoggedIn = true)),
    );
  }
}

class StudentMainNavigation extends StatefulWidget {
  final VoidCallback onLogout;
  const StudentMainNavigation({super.key, required this.onLogout});

  @override
  State<StudentMainNavigation> createState() => _StudentMainNavigationState();
}

class _StudentMainNavigationState extends State<StudentMainNavigation> {
  int _selectedIndex = 0;
  bool isOnline = true;
  int pendingSyncCount = 2;

  final List<Map<String, dynamic>> _notifications = [
    {
      'title': '⚠️ Mobile Data Offline Sync Active',
      'desc': 'Mobile data is OFF. Attendance is cryptographically signed with Ed25519 & buffering via student BLE mesh.',
      'time': 'Just now',
      'type': 'ALERT',
      'icon': Icons.bluetooth_audio,
      'color': Colors.deepOrange,
    },
    {
      'title': '🟢 Live Class: DBMS - I (BCA301)',
      'desc': 'Lecture Hall 3 (LH-3) session started by Prof. Nirali Thakkar (NT). Dynamic QR active.',
      'time': '10 min ago',
      'type': 'CLASS',
      'icon': Icons.door_front_door,
      'color': Colors.green,
    },
    {
      'title': '✅ Leave Request Approved',
      'desc': 'Your 2-day medical leave application has been approved by Prof. Nirali Thakkar. Marked as EXCUSED.',
      'time': '1 hour ago',
      'type': 'LEAVE',
      'icon': Icons.check_circle,
      'color': Colors.teal,
    },
    {
      'title': '📢 Master Timetable Update',
      'desc': 'Session 2 Data Structures Lab relocated to DBMS & C Lab with Prof. Arjunsinh Vaghela (AV).',
      'time': 'Yesterday',
      'type': 'NOTICE',
      'icon': Icons.campaign,
      'color': Colors.indigo,
    },
  ];

  @override
  void initState() {
    super.initState();
    _refreshSyncStatus();
  }

  void _refreshSyncStatus() async {
    final count = await StudentApiService().offlineQueue.getPendingCount();
    setState(() => pendingSyncCount = count);
  }

  void _showNotificationCenter() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        maxChildSize: 0.9,
        minChildSize: 0.4,
        expand: false,
        builder: (ctx, scrollController) => Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.notifications_active, color: Color(0xFF1565C0)),
                      const SizedBox(width: 8),
                      Text('Notifications (${_notifications.length})', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                    ],
                  ),
                  IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(ctx)),
                ],
              ),
              const Divider(),
              Expanded(
                child: ListView.builder(
                  controller: scrollController,
                  itemCount: _notifications.length,
                  itemBuilder: (ctx, idx) {
                    final n = _notifications[idx];
                    final col = n['color'] as Color;
                    return Card(
                      elevation: 1,
                      margin: const EdgeInsets.only(bottom: 10),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: col.withAlpha(30),
                          child: Icon(n['icon'], color: col, size: 20),
                        ),
                        title: Text(n['title'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 3),
                            Text(n['desc'], style: const TextStyle(fontSize: 11)),
                            const SizedBox(height: 4),
                            Text(n['time'], style: const TextStyle(fontSize: 10, color: Colors.blueGrey)),
                          ],
                        ),
                        isThreeLine: true,
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final user = StudentApiService().currentUser;
    final name = user?['name'] ?? 'Rahul Shah';
    final dept = user?['department'] ?? 'Bachelor of Computer Applications';
    final enroll = user?['enrollmentNumber'] ?? 'SRK2026BCA001';

    final screens = [
      _buildHomeScreen(name, dept, enroll),
      const StudentTimetableScreen(),
      const AttendanceHistoryScreen(),
      const StudentIdQrScreen(),
      const P2pSyncScreen(),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('SRK Student Portal', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
        actions: [
          // Notification Bell
          IconButton(
            icon: Badge(
              label: Text('${_notifications.length}'),
              backgroundColor: Colors.amber.shade800,
              child: const Icon(Icons.notifications_outlined),
            ),
            tooltip: 'Notifications',
            onPressed: _showNotificationCenter,
          ),
          // Offline / P2P indicator button
          GestureDetector(
            onTap: () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const P2pSyncScreen()))
                  .then((_) => _refreshSyncStatus());
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              margin: const EdgeInsets.only(right: 14),
              decoration: BoxDecoration(
                color: isOnline ? Colors.white24 : Colors.amber.shade100,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                children: [
                  Icon(
                    isOnline ? Icons.cloud_done : Icons.bluetooth_audio,
                    size: 15,
                    color: isOnline ? Colors.white : Colors.amber.shade900,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    isOnline ? 'Online' : 'BLE Mesh ($pendingSyncCount)',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: isOnline ? Colors.white : Colors.amber.shade900,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            UserAccountsDrawerHeader(
              decoration: const BoxDecoration(color: Color(0xFF1565C0)),
              accountName: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              accountEmail: Text('$enroll • $dept'),
              currentAccountPicture: CircleAvatar(
                backgroundColor: Colors.white,
                child: Text(name.isNotEmpty ? name[0] : 'S', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF1565C0))),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.home),
              title: const Text('Home Dashboard'),
              onTap: () {
                setState(() => _selectedIndex = 0);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.calendar_month),
              title: const Text('SRK Master Timetable'),
              onTap: () {
                setState(() => _selectedIndex = 1);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.fact_check),
              title: const Text('Attendance & Confidence'),
              onTap: () {
                setState(() => _selectedIndex = 2);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.qr_code_2),
              title: const Text('Digital Student ID'),
              onTap: () {
                setState(() => _selectedIndex = 3);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.sync),
              title: const Text('P2P BLE Mesh & Offline Queue'),
              onTap: () {
                setState(() => _selectedIndex = 4);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.sick),
              title: const Text('Apply for Leave'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(context, MaterialPageRoute(builder: (_) => const LeaveRequestScreen()));
              },
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.red),
              title: const Text('Logout', style: TextStyle(color: Colors.red)),
              onTap: () {
                Navigator.pop(context);
                widget.onLogout();
              },
            ),
          ],
        ),
      ),
      body: screens[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (i) => setState(() => _selectedIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.calendar_month), label: 'Schedule'),
          NavigationDestination(icon: Icon(Icons.fact_check), label: 'Attendance'),
          NavigationDestination(icon: Icon(Icons.qr_code), label: 'My ID'),
          NavigationDestination(icon: Icon(Icons.sync), label: 'Mesh Sync'),
        ],
      ),
    );
  }

  Widget _buildHomeScreen(String name, String dept, String enroll) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Welcome, $name', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                  Text('$dept • BCA Sem 3', style: const TextStyle(color: Colors.grey, fontSize: 13)),
                ],
              ),
              OutlinedButton.icon(
                onPressed: () => setState(() => isOnline = !isOnline),
                icon: Icon(isOnline ? Icons.wifi : Icons.bluetooth_audio, size: 14, color: isOnline ? Colors.green : Colors.deepOrange),
                label: Text(isOnline ? 'Online' : 'Data OFF (BLE)', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: isOnline ? Colors.green : Colors.deepOrange)),
                style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6)),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // BLE Mesh Offline Active Alert Banner
          if (!isOnline)
            Container(
              margin: const EdgeInsets.only(bottom: 16),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.amber.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.amber.shade800),
              ),
              child: Row(
                children: [
                  Icon(Icons.bluetooth_searching, color: Colors.amber.shade900, size: 24),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Mobile Data OFF • BLE Mesh Relay Active', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.amber.shade900)),
                        const Text('Attendance is signed locally with Ed25519 and relays via Priya Sharma or LH-3 Beacon.', style: TextStyle(fontSize: 11)),
                      ],
                    ),
                  ),
                ],
              ),
            ),

          // CURRENT CLASS CARD
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            color: const Color(0xFF1565C0),
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.white24,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text('SESSION 1 (08:40 - 09:40 AM)', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 11)),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.greenAccent.shade700,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text('LIVE IN LH-3', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 11)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text('DBMS - I (BCA301)', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  const Text('Lecture Hall 3 (LH-3) • Prof. Nirali Thakkar (NT)', style: TextStyle(color: Colors.white70, fontSize: 14)),
                  const Text('BCA Sem 3 (Div A) • 58 Students Enrolled', style: TextStyle(color: Colors.white70, fontSize: 13)),
                  const Divider(color: Colors.white24, height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Confidence: 96% (Verified)', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 12)),
                      ElevatedButton.icon(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => const QrScannerScreen()),
                          ).then((_) => _refreshSyncStatus());
                        },
                        icon: const Icon(Icons.qr_code_scanner, size: 18),
                        label: const Text('Scan 15s QR'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.white,
                          foregroundColor: const Color(0xFF1565C0),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 18),

          // QUICK ACTION BUTTONS
          Row(
            children: [
              Expanded(
                child: _buildQuickButton('Show My ID QR', Icons.qr_code_2, () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const StudentIdQrScreen()));
                }),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickButton('Apply Leave', Icons.sick, () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const LeaveRequestScreen()));
                }),
              ),
            ],
          ),
          const SizedBox(height: 18),

          // UPCOMING CLASS
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: const ListTile(
              leading: CircleAvatar(backgroundColor: Color(0xFFE3F2FD), child: Icon(Icons.schedule, color: Color(0xFF1565C0))),
              title: Text('NEXT: Lab: Data Structure using C (BCA302L)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
              subtitle: Text('DBMS & C Lab • 09:45 - 10:40 AM • Prof. Arjunsinh Vaghela (AV)', style: TextStyle(fontSize: 12)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickButton(String title, IconData icon, VoidCallback onTap) {
    return OutlinedButton.icon(
      onPressed: onTap,
      icon: Icon(icon, size: 18),
      label: Text(title, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}
