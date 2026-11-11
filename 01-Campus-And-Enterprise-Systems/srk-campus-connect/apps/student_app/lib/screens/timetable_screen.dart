import 'package:flutter/material.dart';
import '../services/api_service.dart';

class StudentTimetableScreen extends StatefulWidget {
  const StudentTimetableScreen({super.key});

  @override
  State<StudentTimetableScreen> createState() => _StudentTimetableScreenState();
}

class _StudentTimetableScreenState extends State<StudentTimetableScreen> {
  String _selectedProgram = 'BCA Sem 3 (LH-3)';
  String _selectedDay = 'Monday';

  final List<String> _programs = [
    'BCA Sem 3 (LH-3)',
    'BCA Sem 1 (LH-5)',
    'BCA Sem 5 (LH-9)',
    'BBA Sem 1 Class I (LH-6)',
    'BBA Sem 1 Class II (LH-7)',
    'BBA Sem 3 (LH-1)',
    'BBA Sem 5 (LH-2)',
  ];

  @override
  Widget build(BuildContext context) {
    final scheduleMap = StudentApiService().getSRKTimetable(_selectedProgram, _selectedDay);
    final schedule = scheduleMap[_selectedDay] ?? scheduleMap['Monday'] ?? [];

    return Scaffold(
      appBar: AppBar(
        title: const Text('SRK Master Timetable', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Program Selector with Lecture Halls
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: Colors.blue.shade50,
            child: Row(
              children: [
                const Icon(Icons.meeting_room, color: Color(0xFF1565C0), size: 20),
                const SizedBox(width: 10),
                const Text('Hall & Class: ', style: TextStyle(fontWeight: FontWeight.bold)),
                Expanded(
                  child: DropdownButton<String>(
                    value: _selectedProgram,
                    isExpanded: true,
                    underline: const SizedBox(),
                    items: _programs.map((p) => DropdownMenuItem(value: p, child: Text(p, style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF1565C0))))).toList(),
                    onChanged: (v) {
                      if (v != null) setState(() => _selectedProgram = v);
                    },
                  ),
                ),
              ],
            ),
          ),

          // Day Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Row(
              children: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map((day) {
                final isSelected = _selectedDay == day;
                return Padding(
                  padding: const EdgeInsets.only(right: 8.0),
                  child: ChoiceChip(
                    label: Text(day),
                    selected: isSelected,
                    selectedColor: const Color(0xFF1565C0),
                    labelStyle: TextStyle(color: isSelected ? Colors.white : Colors.black87, fontWeight: FontWeight.bold),
                    onSelected: (selected) {
                      if (selected) setState(() => _selectedDay = day);
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          const Divider(height: 1),

          // Schedule List
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: schedule.length,
              itemBuilder: (ctx, index) {
                final item = schedule[index];
                final isCurrent = index == 0 && _selectedDay == 'Monday';
                final isFree = item['subject'] == 'FREE';

                return Card(
                  elevation: isCurrent ? 3 : 1,
                  margin: const EdgeInsets.only(bottom: 12),
                  color: isFree ? Colors.grey.shade50 : Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                    side: BorderSide(
                      color: isCurrent ? const Color(0xFF1565C0) : Colors.grey.shade200,
                      width: isCurrent ? 2 : 1,
                    ),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      children: [
                        Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: isCurrent ? Colors.blue.shade50 : (isFree ? Colors.grey.shade200 : Colors.indigo.shade50),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Icon(
                            isFree ? Icons.coffee : Icons.menu_book,
                            color: isCurrent ? const Color(0xFF1565C0) : Colors.indigo,
                          ),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(item['session'] ?? '', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF1565C0))),
                              const SizedBox(height: 2),
                              Text(item['subject'] ?? '', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: isFree ? Colors.grey : Colors.black87)),
                              if (!isFree) ...[
                                const SizedBox(height: 3),
                                Text('${item['faculty']} • ${item['room']}', style: TextStyle(color: Colors.grey.shade700, fontSize: 13, fontWeight: FontWeight.w600)),
                              ],
                            ],
                          ),
                        ),
                        if (isCurrent)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(color: Colors.green.shade50, borderRadius: BorderRadius.circular(8)),
                            child: Text('LIVE', style: TextStyle(color: Colors.green.shade900, fontWeight: FontWeight.bold, fontSize: 10)),
                          ),
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
