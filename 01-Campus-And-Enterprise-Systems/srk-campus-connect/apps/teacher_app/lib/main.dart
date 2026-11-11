import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'services/teacher_api_service.dart';
import 'screens/teacher_login_screen.dart';
import 'screens/rolling_qr_display_screen.dart';
import 'screens/room_unlock_scanner_screen.dart';
import 'screens/student_scanner_roster_screen.dart';
import 'screens/principal_requests_screen.dart';
import 'screens/teacher_timetable_screen.dart';
import 'screens/leave_approvals_screen.dart';

void main() {
  runApp(const ProviderScope(child: TeacherApp()));
}

class TeacherApp extends StatefulWidget {
  const TeacherApp({super.key});

  @override
  State<TeacherApp> createState() => _TeacherAppState();
}

class _TeacherAppState extends State<TeacherApp> {
  bool _isLoggedIn = false;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SRK Faculty Portal',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF00897B)),
        useMaterial3: true,
      ),
      home: _isLoggedIn
          ? TeacherMainNavigation(onLogout: () => setState(() => _isLoggedIn = false))
          : TeacherLoginScreen(onLoginSuccess: () => setState(() => _isLoggedIn = true)),
    );
  }
}

class TeacherMainNavigation extends StatefulWidget {
  final VoidCallback onLogout;
  const TeacherMainNavigation({super.key, required this.onLogout});

  @override
  State<TeacherMainNavigation> createState() => _TeacherMainNavigationState();
}

class _TeacherMainNavigationState extends State<TeacherMainNavigation> {
  int _selectedIndex = 0;
  String currentStatus = 'IN_CLASS (Teaching - Lecture Hall 3)';
  bool isMobileDataOff = true;

  final List<Map<String, dynamic>> _teacherNotifications = [
    {
      'title': '⚠️ Mobile Data is OFF: BLE Mesh Active',
      'desc': 'Mobile data is disconnected. BLE Mesh daemon is broadcasting presence and buffering student attendance locally.',
      'time': 'Just now',
      'type': 'ALERT',
      'icon': Icons.bluetooth_audio,
      'color': Colors.deepOrange,
    },
    {
      'title': '📩 Meeting from Principal Dr. Nirdesh Buch',
      'desc': 'Subject: NAAC Timetable Verification & Student Attendance Compliance in Principal Cabin.',
      'time': '15 min ago',
      'type': 'PRINCIPAL',
      'icon': Icons.person_pin,
      'color': Colors.purple,
    },
    {
      'title': '📝 2 Student Leaves Pending',
      'desc': 'Rahul Shah (Medical) & Priya Sharma (Hackathon) submitted leave applications for review.',
      'time': '30 min ago',
      'type': 'LEAVE',
      'icon': Icons.event_busy,
      'color': Colors.teal,
    },
    {
      'title': '🟢 Room Verified: Lecture Hall 3 (LH-3)',
      'desc': 'Physical room sticker QR scanned and verified. Dynamic 15s session unlocked.',
      'time': '08:40 AM',
      'type': 'ROOM',
      'icon': Icons.door_front_door,
      'color': Colors.green,
    },
  ];

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
                      const Icon(Icons.notifications_active, color: Color(0xFF00897B)),
                      const SizedBox(width: 8),
                      Text('Faculty Notifications (${_teacherNotifications.length})', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                    ],
                  ),
                  IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(ctx)),
                ],
              ),
              const Divider(),
              Expanded(
                child: ListView.builder(
                  controller: scrollController,
                  itemCount: _teacherNotifications.length,
                  itemBuilder: (ctx, idx) {
                    final n = _teacherNotifications[idx];
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
    final user = TeacherApiService().currentUser;
    final name = user?['name'] ?? 'Prof. Nirali Thakkar (NT)';
    final dept = user?['department'] ?? 'Bachelor of Computer Applications';
    final desig = user?['designation'] ?? 'Associate Professor';

    final screens = [
      _buildHomeScreen(name, dept, desig),
      const TeacherTimetableScreen(),
      const StudentScannerRosterScreen(),
      const PrincipalRequestsScreen(),
      const LeaveApprovalsScreen(),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('SRK Faculty Portal', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF00897B),
        foregroundColor: Colors.white,
        actions: [
          // Notification Bell with Badge
          IconButton(
            icon: Badge(
              label: Text('${_teacherNotifications.length}'),
              backgroundColor: Colors.amber.shade800,
              child: const Icon(Icons.notifications_outlined),
            ),
            tooltip: 'Notifications',
            onPressed: _showNotificationCenter,
          ),
          PopupMenuButton<String>(
            initialValue: currentStatus,
            onSelected: (val) {
              setState(() => currentStatus = val);
              TeacherApiService().updateStatus(val);
            },
            itemBuilder: (ctx) => const [
              PopupMenuItem(value: 'IN_CLASS (Teaching - Lecture Hall 3)', child: Text('🟢 In Class (Teaching - LH 3 Verified)')),
              PopupMenuItem(value: 'NOT_IN_CLASS (Pending QR Scan)', child: Text('🟡 Not in Class (Pending Scan)')),
              PopupMenuItem(value: 'WITH_PRINCIPAL (Cabin / Meeting)', child: Text('🟣 With Principal (Dr. Nirdesh Buch)')),
              PopupMenuItem(value: 'IN_CABIN (Available)', child: Text('🔵 Available in Cabin')),
              PopupMenuItem(value: 'ON_RECESS (Break)', child: Text('☕ On Recess / Break')),
            ],
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              margin: const EdgeInsets.only(right: 14),
              decoration: BoxDecoration(
                color: Colors.white24,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                children: [
                  const Icon(Icons.location_on, size: 14, color: Colors.white),
                  const SizedBox(width: 4),
                  Text(
                    currentStatus.contains('IN_CLASS') ? 'Teaching (LH-3)' : (currentStatus.contains('PRINCIPAL') ? 'With Principal' : 'In Cabin'),
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: Colors.white),
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
              decoration: const BoxDecoration(color: Color(0xFF00897B)),
              accountName: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              accountEmail: Text('$desig • $dept'),
              currentAccountPicture: const CircleAvatar(
                backgroundColor: Colors.white,
                child: Text('NT', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF00897B))),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.dashboard),
              title: const Text('Faculty Dashboard'),
              onTap: () {
                setState(() => _selectedIndex = 0);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.schedule),
              title: const Text('SRK Teaching Timetable'),
              onTap: () {
                setState(() => _selectedIndex = 1);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.people),
              title: const Text('Student Roster & Scanner'),
              onTap: () {
                setState(() => _selectedIndex = 2);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.mail),
              title: const Text('Principal Requests'),
              onTap: () {
                setState(() => _selectedIndex = 3);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.event_busy),
              title: const Text('Student Leave Approvals'),
              onTap: () {
                setState(() => _selectedIndex = 4);
                Navigator.pop(context);
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
      body: Column(
        children: [
          if (isMobileDataOff)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: Colors.amber.shade100,
              child: Row(
                children: [
                  Icon(Icons.bluetooth_audio, color: Colors.amber.shade900, size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'BLE Mesh Active: Mobile Data is OFF. Class events buffering offline and syncing via student peer gateways.',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.amber.shade900),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.wifi, size: 16),
                    onPressed: () => setState(() => isMobileDataOff = !isMobileDataOff),
                    tooltip: 'Toggle Offline / Online Simulation',
                  ),
                ],
              ),
            ),
          Expanded(child: screens[_selectedIndex > 4 ? 0 : _selectedIndex]),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex > 3 ? 3 : _selectedIndex,
        onDestinationSelected: (i) => setState(() => _selectedIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard), label: 'Dashboard'),
          NavigationDestination(icon: Icon(Icons.schedule), label: 'Schedule'),
          NavigationDestination(icon: Icon(Icons.people), label: 'Roster'),
          NavigationDestination(icon: Icon(Icons.mail), label: 'Principal'),
        ],
      ),
    );
  }

  Widget _buildHomeScreen(String name, String dept, String desig) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Welcome, $name', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          Text('SRK Institute • $desig', style: const TextStyle(color: Colors.grey, fontSize: 13)),
          const SizedBox(height: 16),

          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            color: const Color(0xFF00897B),
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('SESSION 1 (08:40 - 09:40 AM)', style: TextStyle(color: Colors.white70, fontSize: 11, fontWeight: FontWeight.bold)),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(color: Colors.greenAccent.shade700, borderRadius: BorderRadius.circular(8)),
                        child: const Text('LIVE IN CLASS', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 10)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text('DBMS - I (BCA301) • Lecture Hall 3', style: TextStyle(color: Colors.white, fontSize: 19, fontWeight: FontWeight.bold)),
                  const Text('BCA Sem 3 (Div A) • 58 Students Enrolled', style: TextStyle(color: Colors.white70, fontSize: 13)),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildStat('54', 'Present (96% Conf.)', Colors.greenAccent),
                      _buildStat('2', 'Uncertain', Colors.amberAccent),
                      _buildStat('2', 'Pending Scan', Colors.white70),
                    ],
                  ),
                  const Divider(color: Colors.white24, height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      ElevatedButton.icon(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => const RollingQrDisplayScreen(
                                sessionId: 'sess_dbms_301',
                                subject: 'DBMS - I (BCA301)',
                                room: 'Lecture Hall 3',
                              ),
                            ),
                          );
                        },
                        icon: const Icon(Icons.qr_code_2),
                        label: const Text('Show 15s Dynamic QR'),
                        style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: const Color(0xFF00897B)),
                      ),
                      OutlinedButton.icon(
                        onPressed: () {
                          Navigator.push(context, MaterialPageRoute(builder: (_) => const RoomUnlockScannerScreen()));
                        },
                        icon: const Icon(Icons.door_front_door, color: Colors.white, size: 16),
                        label: const Text('Scan LH 3 QR', style: TextStyle(color: Colors.white)),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.push(context, MaterialPageRoute(builder: (_) => const StudentScannerRosterScreen()));
                  },
                  icon: const Icon(Icons.qr_code_scanner, size: 18),
                  label: const Text('Student Roster'),
                  style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 12)),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.push(context, MaterialPageRoute(builder: (_) => const LeaveApprovalsScreen()));
                  },
                  icon: const Icon(Icons.event_busy, size: 18),
                  label: const Text('Leaves (2 Pending)'),
                  style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 12)),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStat(String val, String label, Color col) {
    return Column(
      children: [
        Text(val, style: TextStyle(color: col, fontSize: 18, fontWeight: FontWeight.bold)),
        Text(label, style: const TextStyle(color: Colors.white70, fontSize: 10)),
      ],
    );
  }
}
