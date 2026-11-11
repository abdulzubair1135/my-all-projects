import 'package:flutter/material.dart';

class AttendanceHistoryScreen extends StatelessWidget {
  const AttendanceHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Attendance & Confidence', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Overall Stats Card
            Card(
              elevation: 4,
              color: const Color(0xFF1565C0),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: const Padding(
                padding: EdgeInsets.all(20.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _StatCol(val: '91.2%', label: 'Overall Attendance'),
                    _StatCol(val: '46 / 50', label: 'Sessions Verified'),
                    _StatCol(val: '96%', label: 'Avg Confidence'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            const Text('SRK BCA SEM 3 SUBJECT-WISE ATTENDANCE', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.blueGrey)),
            const SizedBox(height: 12),

            _buildSubjectProgress('DBMS - I (BCA301) • Prof. Nirali Thakkar (NT)', 0.94, '94%', Colors.green),
            _buildSubjectProgress('Data Structure using C (BCA302) • Prof. Arjunsinh Vaghela (AV)', 0.91, '91%', Colors.teal),
            _buildSubjectProgress('Indian Thinkers (BCA303) • Prof. Rishi Joshi (RJ)', 0.88, '88%', Colors.green),
            _buildSubjectProgress('OOP with Python (BCA304) • Prof. Prakash Lambha (PL)', 0.96, '96%', Colors.green),
            _buildSubjectProgress('CBNT / Cyber Security (BCA305) • Prof. Jinal Sorathiya (JS)', 0.85, '85%', Colors.teal),

            const SizedBox(height: 24),
            const Text('RECENT VERIFIED PRESENCE SCANS', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.blueGrey)),
            const SizedBox(height: 12),

            _buildHistoryItem('DBMS - I (BCA301)', 'Today, 08:40 AM', 'Lecture Hall 3 (LH-3)', 'Present (96% Conf.)', Colors.green),
            _buildHistoryItem('Lab: Data Structure (BCA302L)', 'Yesterday, 09:45 AM', 'DBMS & C Lab', 'Present (95% Conf.)', Colors.green),
            _buildHistoryItem('Indian Thinkers (BCA303)', 'Yesterday, 11:30 AM', 'Lecture Hall 3 (LH-3)', 'Present (92% Conf.)', Colors.green),
            _buildHistoryItem('OOP with Python (BCA304)', '31 Aug, 12:30 PM', 'Lecture Hall 3 (LH-3)', 'Present (97% Conf.)', Colors.green),
          ],
        ),
      ),
    );
  }

  Widget _buildSubjectProgress(String name, double val, String pct, Color col) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(14.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(child: Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13))),
                Text(pct, style: TextStyle(fontWeight: FontWeight.bold, color: col)),
              ],
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(value: val, color: col, backgroundColor: Colors.grey.shade200, minHeight: 6, borderRadius: BorderRadius.circular(4)),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryItem(String title, String time, String room, String status, Color col) {
    return ListTile(
      leading: CircleAvatar(backgroundColor: col.withAlpha(40), child: Icon(Icons.check, color: col, size: 20)),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
      subtitle: Text('$time • $room', style: const TextStyle(fontSize: 12)),
      trailing: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(color: col.withAlpha(30), borderRadius: BorderRadius.circular(8)),
        child: Text(status, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 11)),
      ),
    );
  }
}

class _StatCol extends StatelessWidget {
  final String val;
  final String label;
  const _StatCol({required this.val, required this.label});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(val, style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(color: Colors.white70, fontSize: 11)),
      ],
    );
  }
}
