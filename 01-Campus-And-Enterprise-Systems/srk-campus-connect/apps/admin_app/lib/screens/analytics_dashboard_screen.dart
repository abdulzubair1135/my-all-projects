import 'package:flutter/material.dart';

class AnalyticsDashboardScreen extends StatelessWidget {
  const AnalyticsDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Campus Analytics & Metrics', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF283593),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top Overview Banner
            Card(
              color: const Color(0xFF283593),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: const Padding(
                padding: EdgeInsets.all(20.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _MetricCol(val: '89.4%', label: 'Campus Attendance'),
                    _MetricCol(val: '94.2%', label: 'Avg Presence Conf.'),
                    _MetricCol(val: '21 / 40', label: 'Rooms Active'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            const Text('PRESENCE CONFIDENCE DISTRIBUTION', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 12),
            _buildConfBar('High Confidence (≥85%)', 842, 0.85, Colors.green),
            _buildConfBar('Probable (70% - 84%)', 96, 0.10, Colors.teal),
            _buildConfBar('Uncertain (40% - 69%)', 41, 0.04, Colors.amber.shade800),
            _buildConfBar('Not Detected (0%)', 17, 0.01, Colors.red),

            const SizedBox(height: 24),
            const Text('DEPARTMENT ATTENDANCE LEADERBOARD', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 12),
            _buildDeptCard('Computer Engineering', '93.2% Present', '342 Students', Colors.green),
            _buildDeptCard('Information Technology', '88.5% Present', '280 Students', Colors.teal),
            _buildDeptCard('Mechanical Engineering', '84.0% Present', '220 Students', Colors.amber.shade800),
            _buildDeptCard('Civil Engineering', '81.4% Present', '190 Students', Colors.amber.shade800),
          ],
        ),
      ),
    );
  }

  Widget _buildConfBar(String label, int count, double fraction, Color col) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
              Text('$count Students', style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 13)),
            ],
          ),
          const SizedBox(height: 6),
          LinearProgressIndicator(value: fraction, color: col, backgroundColor: Colors.grey.shade200, minHeight: 8, borderRadius: BorderRadius.circular(4)),
        ],
      ),
    );
  }

  Widget _buildDeptCard(String name, String pct, String count, Color col) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        subtitle: Text(count, style: const TextStyle(fontSize: 12)),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
          decoration: BoxDecoration(color: col.withAlpha(30), borderRadius: BorderRadius.circular(8)),
          child: Text(pct, style: TextStyle(color: col, fontWeight: FontWeight.bold)),
        ),
      ),
    );
  }
}

class _MetricCol extends StatelessWidget {
  final String val;
  final String label;
  const _MetricCol({required this.val, required this.label});

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
