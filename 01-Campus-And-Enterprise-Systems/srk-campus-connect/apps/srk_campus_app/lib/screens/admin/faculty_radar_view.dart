import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme.dart';
import '../../services/api_service.dart';
import '../../services/socket_service.dart';
import '../../providers/auth_provider.dart';

class FacultyRadarView extends ConsumerStatefulWidget {
  const FacultyRadarView({super.key});

  @override
  ConsumerState<FacultyRadarView> createState() => _FacultyRadarViewState();
}

class _FacultyRadarViewState extends ConsumerState<FacultyRadarView> {
  bool _isLoading = false;
  List<Map<String, dynamic>> _facultyList = [
    {
      'id': 'fac_1',
      'name': 'Prof. Nirali Thakkar',
      'designation': 'Assistant Professor',
      'dept': 'Computer Applications',
      'status': 'IN_CLASS',
      'location': 'Lecture Hall 03 (LH-3)',
      'subject': 'Web Development using PHP',
      'batch': 'BCA Sem 3',
      'studentCount': 58,
      'responseState': 'NONE',
    },
    {
      'id': 'fac_2',
      'name': 'Prof. Arjunsinh Vaghela',
      'designation': 'Associate Professor',
      'dept': 'Computer Applications',
      'status': 'IN_LAB',
      'location': 'Computer Lab 02',
      'subject': 'Data Structures Lab',
      'batch': 'BCA Sem 3 (Batch B)',
      'studentCount': 30,
      'responseState': 'NONE',
    },
    {
      'id': 'fac_3',
      'name': 'Prof. Kinjal Patel',
      'designation': 'Assistant Professor',
      'dept': 'Management Studies',
      'status': 'IN_CABIN',
      'location': 'Faculty Cabin F-02',
      'subject': 'Free / Office Hours',
      'batch': 'N/A',
      'studentCount': 0,
      'responseState': 'NONE',
    },
    {
      'id': 'fac_4',
      'name': 'Prof. Hardik Joshi',
      'designation': 'Assistant Professor',
      'dept': 'Computer Applications',
      'status': 'IN_CLASS',
      'location': 'Lecture Hall 05 (LH-5)',
      'subject': 'Database Management Systems',
      'batch': 'BCA Sem 5',
      'studentCount': 62,
      'responseState': 'NONE',
    },
  ];

  @override
  void initState() {
    super.initState();
    _fetchRadarData();
    _setupSocketListeners();
  }

  void _setupSocketListeners() {
    SocketService().on('radar.updated', (data) {
      if (mounted) {
        setState(() {
          _fetchRadarData();
        });
      }
    });

    SocketService().on('meeting.updated', (data) {
      if (mounted && data != null) {
        final teacherId = data['teacherId'] ?? data['facultyId'];
        final status = data['status'];
        final autoDetails = data['autoDetails'] ?? {};

        setState(() {
          for (var fac in _facultyList) {
            if (fac['id'] == teacherId || fac['name'].toString().contains('Nirali')) {
              fac['responseState'] = status;
              if (status == 'BUSY') {
                fac['busyReason'] = autoDetails['message'] ?? 'Engaged in scheduled lecture';
                fac['studentCount'] = autoDetails['studentCount'] ?? fac['studentCount'];
              } else if (status == 'ARRIVING') {
                fac['eta'] = '2 mins';
              }
            }
          }
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: status == 'ARRIVING' ? AppTheme.statusGreen : AppTheme.statusAmber,
            content: Text(
              status == 'ARRIVING'
                  ? 'Faculty is on the way to Principal Cabin (ETA 2 mins)'
                  : 'Faculty Auto-Response: Currently busy in ${autoDetails['location'] ?? 'Class'}',
            ),
          ),
        );
      }
    });
  }

  Future<void> _fetchRadarData() async {
    setState(() => _isLoading = true);
    final data = await ApiService().getFacultyRadar();
    if (mounted) {
      setState(() {
        _isLoading = false;
        if (data.isNotEmpty) {
          // Merge real backend data if any
        }
      });
    }
  }

  void _summonTeacher(Map<String, dynamic> faculty) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.notifications_active_rounded, color: AppTheme.statusRed),
            SizedBox(width: 8),
            Text('Urgent Summon', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Summon ${faculty['name']} directly to Principal Cabin?',
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.bgCream,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Current Location: ${faculty['location']}', style: const TextStyle(fontSize: 12)),
                  Text('Active Class: ${faculty['subject']}', style: const TextStyle(fontSize: 12)),
                  Text('Students Present: ${faculty['studentCount']}', style: const TextStyle(fontSize: 12)),
                ],
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Teacher will receive an instant 1-tap zero-typing notification on their phone.',
              style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.statusRed),
            onPressed: () async {
              Navigator.pop(ctx);
              setState(() {
                faculty['responseState'] = 'SUMMON_SENT';
              });
              await ApiService().sendUrgentCabinCall(
                facultyId: faculty['id'],
                location: 'Principal Cabin P-01',
                reason: 'Urgent consultation requested by Principal Dr. Nirdesh Buch',
              );
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    backgroundColor: AppTheme.primaryNavy,
                    content: Text('Urgent summon dispatched to ${faculty['name']} phone.'),
                  ),
                );
              }
            },
            child: const Text('Dispatch Summon'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgCream,
      body: RefreshIndicator(
        onRefresh: _fetchRadarData,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Campus Radar Header Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppTheme.primaryNavy, AppTheme.secondaryNavy],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryNavy.withOpacity(0.2),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.radar_rounded, color: AppTheme.accentGold, size: 24),
                          SizedBox(width: 8),
                          Text(
                            'LIVE FACULTY RADAR',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 1,
                            ),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppTheme.statusGreen.withOpacity(0.25),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: AppTheme.statusGreen.withOpacity(0.5)),
                        ),
                        child: const Row(
                          children: [
                            CircleAvatar(radius: 4, backgroundColor: AppTheme.statusGreen),
                            SizedBox(width: 6),
                            Text('LIVE SYNC', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Real-time tracking across LH 1-10, Labs & Cabins. Instant 1-tap summon with zero-typing status feedback.',
                    style: TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            const Text(
              'FACULTY OCCUPANCY & LOCATIONS',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1, color: AppTheme.textMuted),
            ),
            const SizedBox(height: 10),

            ..._facultyList.map((fac) => _buildFacultyCard(fac)),
          ],
        ),
      ),
    );
  }

  Widget _buildFacultyCard(Map<String, dynamic> faculty) {
    final responseState = faculty['responseState'] ?? 'NONE';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: AppTheme.primaryNavy.withOpacity(0.1),
                  child: Text(
                    faculty['name'].toString().substring(6, 7),
                    style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primaryNavy),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        faculty['name'],
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.textDark),
                      ),
                      Text(
                        '${faculty['designation']} • ${faculty['dept']}',
                        style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                      ),
                    ],
                  ),
                ),
                _buildStatusBadge(faculty['status']),
              ],
            ),
            const Divider(height: 20),

            Row(
              children: [
                const Icon(Icons.room_rounded, size: 16, color: AppTheme.secondaryNavy),
                const SizedBox(width: 6),
                Text(
                  faculty['location'],
                  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Subject: ${faculty['subject']}',
                  style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                ),
                if (faculty['studentCount'] > 0)
                  Text(
                    '${faculty['studentCount']} Students Enrolled',
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.secondaryNavy),
                  ),
              ],
            ),

            if (responseState == 'SUMMON_SENT') ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.amber.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.amber.shade300),
                ),
                child: const Row(
                  children: [
                    SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.amber)),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Summon dispatched. Awaiting faculty 1-tap acknowledgment...',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.brown),
                      ),
                    ),
                  ],
                ),
              ),
            ] else if (responseState == 'BUSY') ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.shade300),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.do_not_disturb_on_rounded, color: AppTheme.statusRed, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('TEACHER AUTO-RESPONSE: BUSY IN CLASS', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: AppTheme.statusRed)),
                          Text(
                            faculty['busyReason'] ?? 'In active lecture at ${faculty['location']} (${faculty['studentCount']} students present).',
                            style: const TextStyle(fontSize: 11, color: Colors.black87),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ] else if (responseState == 'ARRIVING') ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.shade300),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.directions_walk_rounded, color: AppTheme.statusGreen, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('TEACHER STATUS: ON THE WAY / ARRIVING', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: AppTheme.statusGreen)),
                          Text(
                            'Walking to Principal Cabin P-01 • Estimated arrival: ${faculty['eta'] ?? '2 mins'}',
                            style: const TextStyle(fontSize: 11, color: Colors.black87),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryNavy,
                  padding: const EdgeInsets.symmetric(vertical: 10),
                ),
                icon: const Icon(Icons.send_rounded, size: 16),
                label: const Text('Summon to Cabin', style: TextStyle(fontSize: 13)),
                onPressed: () => _summonTeacher(faculty),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    Color bg = Colors.grey.shade200;
    Color fg = Colors.grey.shade800;
    String label = status;

    if (status == 'IN_CLASS') {
      bg = Colors.blue.shade50;
      fg = Colors.blue.shade800;
      label = 'IN LECTURE';
    } else if (status == 'IN_LAB') {
      bg = Colors.purple.shade50;
      fg = Colors.purple.shade800;
      label = 'IN LAB';
    } else if (status == 'IN_CABIN') {
      bg = Colors.green.shade50;
      fg = Colors.green.shade800;
      label = 'IN CABIN';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: fg.withOpacity(0.3)),
      ),
      child: Text(label, style: TextStyle(color: fg, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }
}
