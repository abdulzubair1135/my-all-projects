import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/theme.dart';
import '../core/constants.dart';
import '../providers/auth_provider.dart';
import '../widgets/institutional_logo.dart';
import 'admin/faculty_radar_view.dart';
import 'teacher/principal_summon_view.dart';
import 'teacher/attendance_generator_view.dart';
import 'student/student_home_view.dart';
import 'student/qr_scanner_view.dart';
import 'student/faculty_locator_view.dart';
import 'chat/campus_chat_screen.dart';
import 'settings/app_settings_sheet.dart';
import 'control_panel_screen.dart';

class MainShellScreen extends ConsumerStatefulWidget {
  const MainShellScreen({super.key});

  @override
  ConsumerState<MainShellScreen> createState() => _MainShellScreenState();
}

class _MainShellScreenState extends ConsumerState<MainShellScreen> {
  int _currentIndex = 0;

  void _showRoleSwitcherDialog() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Switch Active Institutional Profile',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppTheme.primaryNavy),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const Divider(),
              _buildRoleSwitchTile(ctx, 'principal', 'Principal (Dr. Nirdesh Buch)', Icons.admin_panel_settings_rounded, AppTheme.primaryNavy),
              _buildRoleSwitchTile(ctx, 'campus_head', 'Campus Head (Prof. Surbhi Ahir)', Icons.account_balance_rounded, AppTheme.secondaryNavy),
              _buildRoleSwitchTile(ctx, 'teacher_nirali', 'Teacher (Prof. Nirali Thakkar)', Icons.person_pin_circle_rounded, AppTheme.accentGold),
              _buildRoleSwitchTile(ctx, 'student_rahul', 'Student (Rahul Shah - BCA 3)', Icons.school_rounded, AppTheme.statusGreen),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRoleSwitchTile(BuildContext ctx, String key, String title, IconData icon, Color color) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: color.withOpacity(0.12),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
      trailing: const Icon(Icons.chevron_right, size: 18),
      onTap: () {
        Navigator.pop(ctx);
        setState(() => _currentIndex = 0);
        ref.read(authProvider.notifier).quickLogin(key);
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final user = authState.user;

    List<Widget> screens = [];
    List<BottomNavigationBarItem> navItems = [];

    if (user?.isPrincipal == true) {
      screens = [
        const FacultyRadarView(),
        const FacultyLocatorView(),
        const CampusChatScreen(),
      ];
      navItems = const [
        BottomNavigationBarItem(
          icon: Icon(Icons.radar_rounded),
          label: 'Radar',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.apartment_rounded),
          label: 'Cabins',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.chat_bubble_outline_rounded),
          activeIcon: Icon(Icons.chat_bubble_rounded),
          label: 'Messages',
        ),
      ];
    } else if (user?.isTeacher == true) {
      screens = [
        const PrincipalSummonView(),
        const AttendanceGeneratorView(),
        const CampusChatScreen(),
      ];
      navItems = const [
        BottomNavigationBarItem(
          icon: Icon(Icons.notifications_none_rounded),
          activeIcon: Icon(Icons.notifications_active_rounded),
          label: 'Summons',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.qr_code_2_rounded),
          label: 'Attendance',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.chat_bubble_outline_rounded),
          activeIcon: Icon(Icons.chat_bubble_rounded),
          label: 'Messages',
        ),
      ];
    } else {
      screens = [
        const StudentHomeView(),
        const QrScannerView(),
        const CampusChatScreen(),
        const FacultyLocatorView(),
      ];
      navItems = const [
        BottomNavigationBarItem(
          icon: Icon(Icons.class_outlined),
          activeIcon: Icon(Icons.class_rounded),
          label: 'Classes',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.qr_code_scanner_rounded),
          label: 'Attendance',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.chat_bubble_outline_rounded),
          activeIcon: Icon(Icons.chat_bubble_rounded),
          label: 'Messages',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.people_outline_rounded),
          activeIcon: Icon(Icons.people_alt_rounded),
          label: 'Faculty',
        ),
      ];
    }

    if (_currentIndex >= screens.length) {
      _currentIndex = 0;
    }

    String roleBadge = 'STUDENT';
    if (user?.role == 'PRINCIPAL') {
      roleBadge = 'PRINCIPAL';
    } else if (user?.role == 'CAMPUS_HEAD') {
      roleBadge = 'CAMPUS HEAD';
    } else if (user?.role == 'FACULTY') {
      roleBadge = 'FACULTY';
    }

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 0,
        title: Row(
          children: [
            const SizedBox(width: 12),
            const InstitutionalLogo(size: 32, animate: true),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    user?.name ?? 'SRK Campus',
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, letterSpacing: 0.3),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Container(
                    margin: const EdgeInsets.only(top: 2),
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: AppTheme.accentGold.withOpacity(0.5), width: 0.8),
                    ),
                    child: Text(
                      roleBadge,
                      style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w700, letterSpacing: 0.8, color: AppTheme.accentGold),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Share App',
            icon: const Icon(Icons.share_outlined, color: Colors.white, size: 20),
            onPressed: () => AppSettingsSheet.show(context),
          ),
          IconButton(
            tooltip: 'Control Panel',
            icon: const Icon(Icons.tune_rounded, color: Colors.white, size: 20),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const ControlPanelScreen()),
            ),
          ),
          IconButton(
            tooltip: 'Switch Profile',
            icon: const Icon(Icons.swap_horiz_rounded, color: Colors.white70, size: 20),
            onPressed: _showRoleSwitcherDialog,
          ),
          IconButton(
            tooltip: 'Logout',
            icon: const Icon(Icons.logout_rounded, color: Colors.white70, size: 19),
            onPressed: () => ref.read(authProvider.notifier).logout(),
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.06),
              blurRadius: 10,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) => setState(() => _currentIndex = index),
          selectedItemColor: AppTheme.primaryNavy,
          unselectedItemColor: Colors.grey.shade500,
          selectedLabelStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 11),
          unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w500, fontSize: 11),
          type: BottomNavigationBarType.fixed,
          backgroundColor: Colors.white,
          elevation: 8,
          items: navItems,
        ),
      ),
    );
  }
}
