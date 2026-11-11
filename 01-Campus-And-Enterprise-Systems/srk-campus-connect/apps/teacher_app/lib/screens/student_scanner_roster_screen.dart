import 'package:flutter/material.dart';
import '../services/teacher_api_service.dart';

class StudentScannerRosterScreen extends StatefulWidget {
  const StudentScannerRosterScreen({super.key});

  @override
  State<StudentScannerRosterScreen> createState() => _StudentScannerRosterScreenState();
}

class _StudentScannerRosterScreenState extends State<StudentScannerRosterScreen> {
  String _selectedClass = 'BCA Sem 3 (LH-3)';

  final Map<String, List<Map<String, dynamic>>> _classRosters = {
    'BCA Sem 3 (LH-3)': [
      {'enroll': 'SRK2026BCA001', 'name': 'Rahul Shah', 'status': 'PRESENT', 'conf': 96, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BCA002', 'name': 'Priya Sharma', 'status': 'PRESENT', 'conf': 95, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BCA003', 'name': 'Meet Vaghela', 'status': 'PRESENT', 'conf': 94, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BCA004', 'name': 'Dev Patel', 'status': 'PRESENT', 'conf': 97, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BCA005', 'name': 'Yash Joshi', 'status': 'UNCERTAIN', 'conf': 48, 'source': 'BLE Mesh (Pending Scan)'},
      {'enroll': 'SRK2026BCA006', 'name': 'Anjali Mehta', 'status': 'PRESENT', 'conf': 96, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BCA007', 'name': 'Harsh Trivedi', 'status': 'PRESENT', 'conf': 95, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BCA008', 'name': 'Riya Solanki', 'status': 'NOT_DETECTED', 'conf': 0, 'source': 'Absent'},
      {'enroll': 'SRK2026BCA009', 'name': 'Aman Khan', 'status': 'PRESENT', 'conf': 96, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BCA010', 'name': 'Sneha Dave', 'status': 'PRESENT', 'conf': 93, 'source': 'Dynamic QR Scan'},
    ],
    'BCA Sem 1 (LH-5)': [
      {'enroll': 'SRK2026BCA101', 'name': 'Jay Soni', 'status': 'PRESENT', 'conf': 96, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BCA102', 'name': 'Diya Parekh', 'status': 'PRESENT', 'conf': 94, 'source': 'Dynamic QR Scan'},
    ],
    'BCA Sem 5 (LH-9)': [
      {'enroll': 'SRK2026BCA501', 'name': 'Parth Solanki', 'status': 'PRESENT', 'conf': 97, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BCA502', 'name': 'Riya Rathod', 'status': 'PRESENT', 'conf': 95, 'source': 'Dynamic QR Scan'},
    ],
    'BBA Sem 1 Class I (LH-6)': [
      {'enroll': 'SRK2026BBA101', 'name': 'Rohan Merchant', 'status': 'PRESENT', 'conf': 96, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BBA102', 'name': 'Pooja Zala', 'status': 'PRESENT', 'conf': 95, 'source': 'Dynamic QR Scan'},
    ],
    'BBA Sem 1 Class II (LH-7)': [
      {'enroll': 'SRK2026BBA201', 'name': 'Mihir Bhatt', 'status': 'PRESENT', 'conf': 96, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BBA202', 'name': 'Kruti Dave', 'status': 'PRESENT', 'conf': 94, 'source': 'Dynamic QR Scan'},
    ],
    'BBA Sem 3 (LH-1)': [
      {'enroll': 'SRK2026BBA301', 'name': 'Smit Sonpar', 'status': 'PRESENT', 'conf': 96, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BBA302', 'name': 'Tanvi Shukla', 'status': 'PRESENT', 'conf': 95, 'source': 'Dynamic QR Scan'},
    ],
    'BBA Sem 5 (LH-2)': [
      {'enroll': 'SRK2026BBA501', 'name': 'Karan Mehta', 'status': 'PRESENT', 'conf': 97, 'source': 'Dynamic QR Scan'},
      {'enroll': 'SRK2026BBA502', 'name': 'Jhanvi Thakkar', 'status': 'PRESENT', 'conf': 95, 'source': 'Dynamic QR Scan'},
    ],
  };

  void _scanStudentSim() async {
    final roster = _classRosters[_selectedClass] ?? [];
    if (roster.length > 7) {
      final s = roster[7]; // Riya Solanki
      await TeacherApiService().verifyStudentQr('CAMPUS_STUDENT_ID_V1:${s['enroll']}:verified');
      if (!mounted) return;
      setState(() {
        s['status'] = 'PRESENT';
        s['conf'] = 98;
        s['source'] = 'Teacher Direct ID Scan';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: const Color(0xFF00897B),
          content: Text('Direct Verified: ${s['name']} (${s['enroll']}) -> Present 98% (LH-3)'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final roster = _classRosters[_selectedClass] ?? [];
    final presentCount = roster.where((s) => s['status'] == 'PRESENT').length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('SRK Live Student Attendance', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF00897B),
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Class Dropdown
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: Colors.teal.shade50,
            child: Row(
              children: [
                const Icon(Icons.meeting_room, color: Color(0xFF00897B), size: 20),
                const SizedBox(width: 10),
                const Text('Hall & Class: ', style: TextStyle(fontWeight: FontWeight.bold)),
                Expanded(
                  child: DropdownButton<String>(
                    value: _selectedClass,
                    isExpanded: true,
                    underline: const SizedBox(),
                    items: _classRosters.keys.map((k) => DropdownMenuItem(value: k, child: Text(k, style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF00897B))))).toList(),
                    onChanged: (v) {
                      if (v != null) setState(() => _selectedClass = v);
                    },
                  ),
                ),
              ],
            ),
          ),

          // Action & Stats Bar
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('LIVE ATTENDANCE: $presentCount / ${roster.length}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                    Text('${((presentCount / (roster.isNotEmpty ? roster.length : 1)) * 100).toStringAsFixed(1)}% Real-time Verified', style: const TextStyle(color: Colors.green, fontSize: 12, fontWeight: FontWeight.bold)),
                  ],
                ),
                ElevatedButton.icon(
                  onPressed: _scanStudentSim,
                  icon: const Icon(Icons.qr_code_scanner, size: 16),
                  label: const Text('Scan Student ID'),
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF00897B), foregroundColor: Colors.white),
                ),
              ],
            ),
          ),
          const Divider(height: 1),

          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: roster.length,
              itemBuilder: (ctx, idx) {
                final student = roster[idx];
                final status = student['status'];
                final conf = student['conf'];
                final source = student['source'];

                Color col = Colors.green;
                if (status == 'UNCERTAIN') col = Colors.amber.shade800;
                if (status == 'NOT_DETECTED') col = Colors.red.shade700;

                return Card(
                  elevation: 1,
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: col.withAlpha(40),
                      child: Text(student['name'][0], style: TextStyle(fontWeight: FontWeight.bold, color: col)),
                    ),
                    title: Text(student['name'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                    subtitle: Text('${student['enroll']} • $source ($conf% Conf.)', style: const TextStyle(fontSize: 11)),
                    trailing: PopupMenuButton<String>(
                      initialValue: status,
                      onSelected: (val) {
                        setState(() {
                          student['status'] = val;
                          student['conf'] = val == 'PRESENT' ? 95 : (val == 'LATE' ? 80 : 0);
                          student['source'] = 'Teacher Manual Override';
                        });
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                        decoration: BoxDecoration(color: col.withAlpha(30), borderRadius: BorderRadius.circular(8)),
                        child: Text(status, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 11)),
                      ),
                      itemBuilder: (ctx) => const [
                        PopupMenuItem(value: 'PRESENT', child: Text('🟢 Present')),
                        PopupMenuItem(value: 'LATE', child: Text('🟡 Late')),
                        PopupMenuItem(value: 'NOT_DETECTED', child: Text('🔴 Absent')),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
