import 'package:flutter/material.dart';

class TimetableManagerScreen extends StatefulWidget {
  const TimetableManagerScreen({super.key});

  @override
  State<TimetableManagerScreen> createState() => _TimetableManagerScreenState();
}

class _TimetableManagerScreenState extends State<TimetableManagerScreen> {
  String _selectedClass = 'BCA Sem 3 (LH-3)';
  String _selectedDay = 'Monday';

  final List<String> _classList = [
    'BBA Sem 3 (LH-1)',
    'BBA Sem 5 (LH-2)',
    'BCA Sem 3 (LH-3)',
    'Lecture Hall 4 (Reserved/Null)',
    'BCA Sem 1 (LH-5)',
    'BBA Sem 1 Class I (LH-6)',
    'BBA Sem 1 Class II (LH-7)',
    'Lecture Hall 8 (Reserved/Null)',
    'BCA Sem 5 (LH-9)',
    'Lecture Hall 10 (Reserved/Null)',
  ];

  final Map<String, List<Map<String, dynamic>>> _masterTimetable = {
    'BCA Sem 3 (LH-3)': [
      {'session': 'Session 1 (08:40 - 09:40 AM)', 'sub': 'DBMS - I', 'code': 'BCA301', 'faculty': 'Prof. Nirali Thakkar (NT)', 'room': 'Lecture Hall 3'},
      {'session': 'Session 2 (09:45 - 10:40 AM)', 'sub': 'Lab: Data Structure using C', 'code': 'BCA302L', 'faculty': 'Prof. Arjunsinh Vaghela (AV)', 'room': 'DBMS & C Lab'},
      {'session': 'Recess (10:40 - 11:25 AM)', 'sub': 'RECESS - All Classes', 'code': 'BREAK', 'faculty': '-', 'room': 'Campus Cafe'},
      {'session': 'Session 3 (11:30 - 12:25 PM)', 'sub': 'Indian Thinkers', 'code': 'BCA303', 'faculty': 'Prof. Rishi Joshi (RJ)', 'room': 'Lecture Hall 3'},
      {'session': 'Session 4 (12:30 - 01:25 PM)', 'sub': 'Understanding OOP with Python', 'code': 'BCA304', 'faculty': 'Prof. Prakash Lambha (PL)', 'room': 'Lecture Hall 3'},
    ],
    'BBA Sem 3 (LH-1)': [
      {'session': 'Session 1 (08:40 - 09:40 AM)', 'sub': 'Consumer Behaviour', 'code': 'BBA301', 'faculty': 'Prof. Stephen Sober (SS)', 'room': 'Lecture Hall 1'},
      {'session': 'Session 2 (09:45 - 10:40 AM)', 'sub': 'Humanities', 'code': 'BBA302', 'faculty': 'Prof. Abhishek Abhani (AA)', 'room': 'Lecture Hall 1'},
      {'session': 'Recess (10:40 - 11:25 AM)', 'sub': 'RECESS - All Classes', 'code': 'BREAK', 'faculty': '-', 'room': 'Campus Cafe'},
      {'session': 'Session 3 (11:30 - 12:25 PM)', 'sub': 'HRM-1', 'code': 'BBA303', 'faculty': 'Prof. Rishi Sonpar (RS)', 'room': 'Lecture Hall 1'},
      {'session': 'Session 4 (12:30 - 01:25 PM)', 'sub': 'Practical English - III', 'code': 'BBA304', 'faculty': 'Prof. Rishi Joshi (RJ)', 'room': 'Lecture Hall 1'},
    ],
    'BBA Sem 5 (LH-2)': [
      {'session': 'Session 1 (08:40 - 09:40 AM)', 'sub': 'Mercantile Law', 'code': 'BBA501', 'faculty': 'Prof. Rishi Sonpar (RS)', 'room': 'Lecture Hall 2'},
      {'session': 'Session 2 (09:45 - 10:40 AM)', 'sub': 'Direct Tax', 'code': 'BBA502', 'faculty': 'Prof. Chandni Thacker (CT)', 'room': 'Lecture Hall 2'},
      {'session': 'Recess (10:40 - 11:25 AM)', 'sub': 'RECESS - All Classes', 'code': 'BREAK', 'faculty': '-', 'room': 'Campus Cafe'},
      {'session': 'Session 3 (11:30 - 12:25 PM)', 'sub': 'Business Environment - 2', 'code': 'BBA503', 'faculty': 'Dr. Nirdesh Buch (NB - Principal)', 'room': 'Lecture Hall 2'},
      {'session': 'Session 4 (12:30 - 01:25 PM)', 'sub': 'CM & OD', 'code': 'BBA504', 'faculty': 'Prof. Stephen Sober (SS)', 'room': 'Lecture Hall 2'},
    ],
    'BCA Sem 1 (LH-5)': [
      {'session': 'Session 1 (08:40 - 09:40 AM)', 'sub': 'Statistics', 'code': 'BCA101', 'faculty': 'Prof. Jinal Sorathiya (JS)', 'room': 'Lecture Hall 5'},
      {'session': 'Session 2 (09:45 - 10:40 AM)', 'sub': 'Web Designing using HTML/CSS/JS', 'code': 'BCA102', 'faculty': 'Prof. Nirali Thakkar (NT)', 'room': 'Lecture Hall 5'},
      {'session': 'Recess (10:40 - 11:25 AM)', 'sub': 'RECESS - All Classes', 'code': 'BREAK', 'faculty': '-', 'room': 'Campus Cafe'},
      {'session': 'Session 3 (11:30 - 12:25 PM)', 'sub': 'Digital Electronics', 'code': 'BCA103', 'faculty': 'Prof. Prakash Lambha (PL)', 'room': 'Lecture Hall 5'},
      {'session': 'Session 4 (12:30 - 01:25 PM)', 'sub': 'Bhagavad Gita & Life Management', 'code': 'BCA104', 'faculty': 'Dr. Nirdesh Buch (NB - Principal)', 'room': 'Lecture Hall 5'},
    ],
    'BBA Sem 1 Class I (LH-6)': [
      {'session': 'Session 1 (08:40 - 09:40 AM)', 'sub': 'Introduction to Bhagwad Gita', 'code': 'BBA101', 'faculty': 'Dr. Nirdesh Buch (NB - Principal)', 'room': 'Lecture Hall 6'},
      {'session': 'Session 2 (09:45 - 10:40 AM)', 'sub': 'Fundamentals of Management', 'code': 'BBA102', 'faculty': 'Prof. Rishi Sonpar (RS)', 'room': 'Lecture Hall 6'},
      {'session': 'Recess (10:40 - 11:25 AM)', 'sub': 'RECESS - All Classes', 'code': 'BREAK', 'faculty': '-', 'room': 'Campus Cafe'},
      {'session': 'Session 3 (11:30 - 12:25 PM)', 'sub': 'E-Commerce & Digital Solutions', 'code': 'BBA103', 'faculty': 'Prof. Mayur Meghani (MM)', 'room': 'Lecture Hall 6'},
      {'session': 'Session 4 (12:30 - 01:25 PM)', 'sub': 'Economics-1', 'code': 'BBA104', 'faculty': 'Prof. Chandni Thacker (CT)', 'room': 'Lecture Hall 6'},
    ],
    'BBA Sem 1 Class II (LH-7)': [
      {'session': 'Session 1 (08:40 - 09:40 AM)', 'sub': 'Business Organization & Structure', 'code': 'BBA105', 'faculty': 'Prof. Abhishek Abhani (AA)', 'room': 'Lecture Hall 7'},
      {'session': 'Session 2 (09:45 - 10:40 AM)', 'sub': 'E-Commerce & Digital Solutions', 'code': 'BBA103', 'faculty': 'Prof. Mayur Meghani (MM)', 'room': 'Lecture Hall 7'},
      {'session': 'Recess (10:40 - 11:25 AM)', 'sub': 'RECESS - All Classes', 'code': 'BREAK', 'faculty': '-', 'room': 'Campus Cafe'},
      {'session': 'Session 3 (11:30 - 12:25 PM)', 'sub': 'Business Statistics/Ecology', 'code': 'BBA106', 'faculty': 'Prof. Jinal Sorathiya (JS)', 'room': 'Lecture Hall 7'},
      {'session': 'Session 4 (12:30 - 01:25 PM)', 'sub': 'Fundamentals of Management', 'code': 'BBA102', 'faculty': 'Prof. Rishi Sonpar (RS)', 'room': 'Lecture Hall 7'},
    ],
    'BCA Sem 5 (LH-9)': [
      {'session': 'Session 1 (08:40 - 09:40 AM)', 'sub': 'Advanced DBMS', 'code': 'BCA501', 'faculty': 'Prof. Arjunsinh Vaghela (AV)', 'room': 'Lecture Hall 9'},
      {'session': 'Session 2 (09:45 - 10:40 AM)', 'sub': 'Operational Research', 'code': 'BCA502', 'faculty': 'Prof. Jinal Sorathiya (JS)', 'room': 'Lecture Hall 9'},
      {'session': 'Recess (10:40 - 11:25 AM)', 'sub': 'RECESS - All Classes', 'code': 'BREAK', 'faculty': '-', 'room': 'Campus Cafe'},
      {'session': 'Session 3 (11:30 - 12:25 PM)', 'sub': 'Software Engineering', 'code': 'BCA503', 'faculty': 'Prof. Nirali Thakkar (NT)', 'room': 'Lecture Hall 9'},
      {'session': 'Session 4 (12:30 - 01:25 PM)', 'sub': 'Understanding Operating Systems', 'code': 'BCA504', 'faculty': 'Prof. Arjunsinh Vaghela (AV)', 'room': 'Lecture Hall 9'},
    ],
  };

  void _showConflictSimulation() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.warning, color: Colors.amber),
            SizedBox(width: 8),
            Text('SRK 3-Tier Conflict Check'),
          ],
        ),
        content: const Text(
          'Attempting to schedule new slot in Lecture Hall 3 at 08:40 AM...\n\n'
          '❌ 3-Tier Conflict Blocked:\n'
          '• Tier 1 (Room Collision): Lecture Hall 3 already occupied by DBMS - I (BCA Sem 3)\n'
          '• Tier 2 (Faculty Collision): Prof. Nirali Thakkar (NT) scheduled in LH-3\n'
          '• Tier 3 (Batch Collision): BCA Sem 3 active in LH-3\n\n'
          'The master scheduler prevented double-booking and preserved Lecture Hall integrity.',
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx),
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF283593), foregroundColor: Colors.white),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showSubstituteDialog(Map<String, dynamic> slot) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.swap_horiz, color: Color(0xFF283593)),
            const SizedBox(width: 8),
            Expanded(child: Text('Auto-Substitute: ${slot['sub']}', style: const TextStyle(fontSize: 16))),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Current Faculty: ${slot['faculty']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
            Text('Time: ${slot['session']}', style: const TextStyle(fontSize: 12, color: Colors.grey)),
            const SizedBox(height: 14),
            const Text('AVAILABLE FACULTY IN SAME DEPARTMENT (FREE SLOT):', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.blueGrey)),
            const SizedBox(height: 8),
            _buildSubstituteOption(ctx, slot, 'Prof. Prayag Joshi (PJ)', 'Free during this session • Ready to cover'),
            _buildSubstituteOption(ctx, slot, 'Prof. Arjunsinh Vaghela (AV)', 'Free during this session • Subject Specialist'),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
        ],
      ),
    );
  }

  Widget _buildSubstituteOption(BuildContext ctx, Map<String, dynamic> slot, String subFac, String desc) {
    return Card(
      margin: const EdgeInsets.only(bottom: 6),
      child: ListTile(
        leading: const CircleAvatar(backgroundColor: Color(0xFFE8EAF6), child: Icon(Icons.person, color: Color(0xFF283593))),
        title: Text(subFac, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
        subtitle: Text(desc, style: const TextStyle(fontSize: 11)),
        trailing: ElevatedButton(
          onPressed: () {
            setState(() => slot['faculty'] = '$subFac (Substitute Assigned)');
            Navigator.pop(ctx);
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(backgroundColor: const Color(0xFF283593), content: Text('Assigned $subFac as substitute for ${slot['sub']}!')),
            );
          },
          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF283593), foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6)),
          child: const Text('Assign', style: TextStyle(fontSize: 11)),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final slots = _masterTimetable[_selectedClass] ?? _masterTimetable['BCA Sem 3 (LH-3)'] ?? [];

    return Scaffold(
      appBar: AppBar(
        title: const Text('SRK Master Timetable & Conflict Engine', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF283593),
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Class Dropdown
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: Colors.indigo.shade50,
            child: Row(
              children: [
                const Icon(Icons.meeting_room, color: Color(0xFF283593), size: 20),
                const SizedBox(width: 10),
                const Text('Hall & Class: ', style: TextStyle(fontWeight: FontWeight.bold)),
                Expanded(
                  child: DropdownButton<String>(
                    value: _selectedClass,
                    isExpanded: true,
                    underline: const SizedBox(),
                    items: _classList.map((c) => DropdownMenuItem(value: c, child: Text(c, style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF283593))))).toList(),
                    onChanged: (v) {
                      if (v != null) setState(() => _selectedClass = v);
                    },
                  ),
                ),
              ],
            ),
          ),

          // Day Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map((day) {
                final isSel = _selectedDay == day;
                return Padding(
                  padding: const EdgeInsets.only(right: 6.0),
                  child: ChoiceChip(
                    label: Text(day, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: isSel ? Colors.white : Colors.black87)),
                    selected: isSel,
                    selectedColor: const Color(0xFF283593),
                    onSelected: (sel) {
                      if (sel) setState(() => _selectedDay = day);
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          const Divider(height: 1),

          Expanded(
            child: slots.isEmpty
                ? const Center(child: Text('Lecture Hall is Available / Reserved (Null)', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)))
                : ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: slots.length,
                    itemBuilder: (ctx, idx) {
                      final slot = slots[idx];
                      final isRecess = slot['code'] == 'BREAK';

                      return Card(
                        margin: const EdgeInsets.only(bottom: 10),
                        color: isRecess ? Colors.amber.shade50 : Colors.white,
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: isRecess ? Colors.amber.shade100 : const Color(0xFFE8EAF6),
                            child: Icon(isRecess ? Icons.coffee : Icons.schedule, color: isRecess ? Colors.amber.shade900 : const Color(0xFF283593)),
                          ),
                          title: Text(slot['sub'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                          subtitle: Text('${slot['session']}\n${slot['faculty']} • ${slot['room']}', style: const TextStyle(fontSize: 12)),
                          isThreeLine: true,
                          trailing: !isRecess
                              ? Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    IconButton(
                                      icon: const Icon(Icons.swap_horiz, color: Color(0xFF283593)),
                                      onPressed: () => _showSubstituteDialog(slot),
                                      tooltip: 'Find Substitute Faculty',
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.edit_calendar, color: Color(0xFF283593)),
                                      onPressed: _showConflictSimulation,
                                      tooltip: 'Reschedule Slot (Check Conflicts)',
                                    ),
                                  ],
                                )
                              : null,
                        ),
                      );
                    },
                  ),
          ),

          Padding(
            padding: const EdgeInsets.all(12.0),
            child: ElevatedButton.icon(
              onPressed: _showConflictSimulation,
              icon: const Icon(Icons.add_task),
              label: const Text('Simulate New Slot (Test 3-Tier Conflict Detector)'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF283593),
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 46),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
