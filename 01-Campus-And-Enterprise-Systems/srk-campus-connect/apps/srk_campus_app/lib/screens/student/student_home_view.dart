import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme.dart';
import '../../services/api_service.dart';
import '../../providers/auth_provider.dart';

class StudentHomeView extends ConsumerStatefulWidget {
  const StudentHomeView({super.key});

  @override
  ConsumerState<StudentHomeView> createState() => _StudentHomeViewState();
}

class _StudentHomeViewState extends ConsumerState<StudentHomeView> {
  final List<Map<String, dynamic>> _todayClasses = [
    {
      'subject': 'Web Development using PHP',
      'code': 'BCA-301',
      'faculty': 'Prof. Nirali Thakkar',
      'time': '10:30 AM - 11:30 AM',
      'room': 'Lecture Hall 03 (LH-3)',
      'isLive': true,
      'attendanceStatus': 'MARKED_PRESENT',
    },
    {
      'subject': 'Data Structures using C++',
      'code': 'BCA-302',
      'faculty': 'Prof. Arjunsinh Vaghela',
      'time': '11:45 AM - 12:45 PM',
      'room': 'Computer Lab 02',
      'isLive': false,
      'attendanceStatus': 'UPCOMING',
    },
    {
      'subject': 'Database Management Systems',
      'code': 'BCA-303',
      'faculty': 'Prof. Hardik Joshi',
      'time': '01:30 PM - 02:30 PM',
      'room': 'Lecture Hall 05 (LH-5)',
      'isLive': false,
      'attendanceStatus': 'UPCOMING',
    },
  ];

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authProvider).user;

    return Scaffold(
      backgroundColor: AppTheme.bgCream,
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          user?.name ?? 'Rahul Shah',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          '${user?.rollNo ?? '24BCA001'} • ${user?.department ?? 'BCA Sem 3'}',
                          style: const TextStyle(color: Colors.white70, fontSize: 12),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppTheme.accentGold.withOpacity(0.25),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AppTheme.accentGold.withOpacity(0.5)),
                      ),
                      child: const Text(
                        '91.4% ATTENDANCE',
                        style: TextStyle(color: AppTheme.accentGold, fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.blue.shade200),
            ),
            child: const Row(
              children: [
                Icon(Icons.bluetooth_audio_rounded, color: AppTheme.secondaryNavy, size: 20),
                SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'BLE Mesh Offline Sync: Active',
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.secondaryNavy),
                      ),
                      Text(
                        'Campus notices and classroom updates sync automatically even without internet.',
                        style: TextStyle(fontSize: 11, color: Colors.black87),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          const Text(
            "TODAY'S LECTURES & LABS",
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 10),

          ..._todayClasses.map((item) => _buildClassCard(item)),
        ],
      ),
    );
  }

  Widget _buildClassCard(Map<String, dynamic> item) {
    final bool isLive = item['isLive'] == true;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: isLive ? AppTheme.accentGold : Colors.grey.shade200,
          width: isLive ? 1.5 : 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: isLive ? AppTheme.statusGreen.withOpacity(0.15) : Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    isLive ? 'IN SESSION' : item['time'],
                    style: TextStyle(
                      color: isLive ? AppTheme.statusGreen : Colors.grey.shade800,
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
                Text(
                  item['code'],
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12, color: AppTheme.textMuted),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              item['subject'],
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.textDark),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(Icons.person_pin_circle_outlined, size: 16, color: AppTheme.secondaryNavy),
                const SizedBox(width: 4),
                Text(item['faculty'], style: const TextStyle(fontSize: 12, color: AppTheme.textDark)),
              ],
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(Icons.meeting_room_outlined, size: 16, color: AppTheme.secondaryNavy),
                const SizedBox(width: 4),
                Text(item['room'], style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.secondaryNavy)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
