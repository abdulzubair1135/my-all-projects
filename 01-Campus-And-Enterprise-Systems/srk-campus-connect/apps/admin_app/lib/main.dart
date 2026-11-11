import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screens/admin_login_screen.dart';
import 'screens/faculty_radar_screen.dart';
import 'screens/fuzzy_search_screen.dart';
import 'screens/timetable_manager_screen.dart';
import 'screens/analytics_dashboard_screen.dart';
import 'screens/audit_trail_screen.dart';

void main() {
  runApp(const ProviderScope(child: AdminApp()));
}

class AdminApp extends StatefulWidget {
  const AdminApp({super.key});

  @override
  State<AdminApp> createState() => _AdminAppState();
}

class _AdminAppState extends State<AdminApp> {
  bool _isLoggedIn = false;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SRK Principal & Admin Portal',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF283593)),
        useMaterial3: true,
      ),
      home: _isLoggedIn
          ? AdminMainNavigation(onLogout: () => setState(() => _isLoggedIn = false))
          : AdminLoginScreen(onLoginSuccess: () => setState(() => _isLoggedIn = true)),
    );
  }
}

class AdminMainNavigation extends StatefulWidget {
  final VoidCallback onLogout;
  const AdminMainNavigation({super.key, required this.onLogout});

  @override
  State<AdminMainNavigation> createState() => _AdminMainNavigationState();
}

class _AdminMainNavigationState extends State<AdminMainNavigation> {
  int _selectedIndex = 0;

  final List<Map<String, dynamic>> _adminNotifications = [
    {
      'title': '⚠️ BLE Mesh Alert: Prof. Prakash Lambha (PL)',
      'desc': 'Mobile data is OFF. Relaying attendance via student mesh in Python & App Lab.',
      'time': 'Just now',
      'type': 'ALERT',
      'icon': Icons.bluetooth_audio,
      'color': Colors.deepOrange,
    },
    {
      'title': '🟡 Pending Scan: Prof. Jinal Sorathiya (JS)',
      'desc': 'Slot active in Lecture Hall 5 (LH-5). Physical room QR not yet scanned (15 min elapsed).',
      'time': '15 min ago',
      'type': 'COMPLIANCE',
      'icon': Icons.warning_amber,
      'color': Colors.amber.shade900,
    },
    {
      'title': '🟢 Live Class Verified: Dr. Nirdesh Buch (NB)',
      'desc': 'Lecture Hall 6 (LH-6) verified with 98% presence confidence. 52 students present.',
      'time': '08:40 AM',
      'type': 'ROOM',
      'icon': Icons.check_circle,
      'color': Colors.green,
    },
    {
      'title': '🟣 Meeting in Progress: Principal Cabin',
      'desc': 'Prof. Rishi Sonpar (RS - HOD BBA) present with Dr. Nirdesh Buch for NAAC compliance.',
      'time': '08:45 AM',
      'type': 'MEETING',
      'icon': Icons.person_pin,
      'color': Colors.purple,
    },
  ];

  final List<Widget> _screens = const [
    FacultyRadarScreen(),
    FuzzySearchScreen(),
    TimetableManagerScreen(),
    AnalyticsDashboardScreen(),
    AuditTrailScreen(),
  ];

  void _showAdminNotificationCenter() {
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
                      const Icon(Icons.notifications_active, color: Color(0xFF283593)),
                      const SizedBox(width: 8),
                      Text('Principal Live Feed (${_adminNotifications.length})', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                    ],
                  ),
                  IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(ctx)),
                ],
              ),
              const Divider(),
              Expanded(
                child: ListView.builder(
                  controller: scrollController,
                  itemCount: _adminNotifications.length,
                  itemBuilder: (ctx, idx) {
                    final n = _adminNotifications[idx];
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
    return Scaffold(
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            const UserAccountsDrawerHeader(
              decoration: BoxDecoration(color: Color(0xFF283593)),
              accountName: Text('Dr. Nirdesh Buch (NB)', style: TextStyle(fontWeight: FontWeight.bold)),
              accountEmail: Text('Principal & Director • SRK Institute'),
              currentAccountPicture: CircleAvatar(
                backgroundColor: Colors.white,
                child: Text('NB', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF283593))),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.radar),
              title: const Text('SRK Faculty Presence Radar & 2D Map'),
              onTap: () {
                setState(() => _selectedIndex = 0);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.search),
              title: const Text('Campus Global Search'),
              onTap: () {
                setState(() => _selectedIndex = 1);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.edit_calendar),
              title: const Text('SRK Master Timetable Editor'),
              onTap: () {
                setState(() => _selectedIndex = 2);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.insights),
              title: const Text('Campus Analytics & Metrics'),
              onTap: () {
                setState(() => _selectedIndex = 3);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.security),
              title: const Text('Audit Trail'),
              onTap: () {
                setState(() => _selectedIndex = 4);
                Navigator.pop(context);
              },
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.notifications_active),
              title: const Text('Principal Notifications'),
              trailing: Badge(label: Text('${_adminNotifications.length}')),
              onTap: () {
                Navigator.pop(context);
                _showAdminNotificationCenter();
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
      body: _screens[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (i) => setState(() => _selectedIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.radar), label: 'Radar'),
          NavigationDestination(icon: Icon(Icons.search), label: 'Search'),
          NavigationDestination(icon: Icon(Icons.edit_calendar), label: 'Timetable'),
          NavigationDestination(icon: Icon(Icons.insights), label: 'Analytics'),
          NavigationDestination(icon: Icon(Icons.security), label: 'Audit'),
        ],
      ),
    );
  }
}
