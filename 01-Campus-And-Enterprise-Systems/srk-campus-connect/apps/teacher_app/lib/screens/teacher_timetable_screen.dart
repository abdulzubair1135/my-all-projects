import 'package:flutter/material.dart';
import '../services/teacher_api_service.dart';
import 'room_unlock_scanner_screen.dart';

class TeacherTimetableScreen extends StatelessWidget {
  const TeacherTimetableScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final schedule = TeacherApiService().getTeachingSchedule('Monday');

    return Scaffold(
      appBar: AppBar(
        title: const Text('SRK Teaching Timetable', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF00897B),
        foregroundColor: Colors.white,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: schedule.length,
        itemBuilder: (ctx, idx) {
          final slot = schedule[idx];
          final isActive = slot['active'] as bool;
          return Card(
            elevation: isActive ? 4 : 1,
            margin: const EdgeInsets.only(bottom: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
              side: BorderSide(color: isActive ? const Color(0xFF00897B) : Colors.grey.shade200, width: isActive ? 2 : 1),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(slot['session'] as String, style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF00897B), fontSize: 12)),
                      if (isActive)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(color: Colors.green.shade50, borderRadius: BorderRadius.circular(6)),
                          child: const Text('CURRENT LIVE SLOT', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 10)),
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(slot['sub'] as String, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
                  Text('${slot['class']} • ${slot['room']}', style: TextStyle(color: Colors.grey.shade700, fontSize: 13)),
                  const SizedBox(height: 12),

                  if (isActive)
                    ElevatedButton.icon(
                      onPressed: () {
                        Navigator.push(context, MaterialPageRoute(builder: (_) => const RoomUnlockScannerScreen()));
                      },
                      icon: const Icon(Icons.qr_code_scanner, size: 16),
                      label: const Text('Scan Room 201 QR & Start Teaching'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF00897B),
                        foregroundColor: Colors.white,
                        minimumSize: const Size(double.infinity, 44),
                      ),
                    ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
