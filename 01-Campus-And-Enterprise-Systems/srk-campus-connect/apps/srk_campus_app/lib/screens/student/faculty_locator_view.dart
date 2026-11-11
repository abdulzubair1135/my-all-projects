import 'package:flutter/material.dart';
import '../../core/theme.dart';

class FacultyLocatorView extends StatelessWidget {
  const FacultyLocatorView({super.key});

  final List<Map<String, dynamic>> _professors = const [
    {
      'name': 'Dr. Nirdesh Buch',
      'role': 'Campus Principal',
      'dept': 'Institutional Administration',
      'cabin': 'Principal Cabin P-01 (Ground Floor)',
      'status': 'AVAILABLE_IN_CABIN',
    },
    {
      'name': 'Prof. Surbhi Ahir',
      'role': 'Campus Head',
      'dept': 'Academic Affairs',
      'cabin': 'Cabin A-01 (First Floor)',
      'status': 'AVAILABLE_IN_CABIN',
    },
    {
      'name': 'Prof. Nirali Thakkar',
      'role': 'Assistant Professor',
      'dept': 'Computer Applications (BCA)',
      'cabin': 'Faculty Cabin F-04 (Second Floor)',
      'status': 'IN_LECTURE_HALL_3',
    },
    {
      'name': 'Prof. Arjunsinh Vaghela',
      'role': 'Associate Professor',
      'dept': 'Computer Applications (BCA)',
      'cabin': 'Faculty Cabin F-08 (Second Floor)',
      'status': 'IN_COMPUTER_LAB_2',
    },
    {
      'name': 'Prof. Kinjal Patel',
      'role': 'Assistant Professor',
      'dept': 'Management Studies (BBA)',
      'cabin': 'Faculty Cabin F-02 (Second Floor)',
      'status': 'AVAILABLE_IN_CABIN',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgCream,
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey.shade200),
            ),
            child: const Row(
              children: [
                Icon(Icons.search_rounded, color: AppTheme.primaryNavy),
                SizedBox(width: 8),
                Text('Search 15 SRK Professors & Cabin locations', style: TextStyle(fontSize: 12, color: AppTheme.textMuted)),
              ],
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'PROFESSOR CABINS & CURRENT STATUS',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 10),
          ..._professors.map((p) => _buildProfessorCard(p)),
        ],
      ),
    );
  }

  Widget _buildProfessorCard(Map<String, dynamic> prof) {
    final bool isAvailable = prof['status'] == 'AVAILABLE_IN_CABIN';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CircleAvatar(
              backgroundColor: AppTheme.primaryNavy.withOpacity(0.1),
              child: const Icon(Icons.person, color: AppTheme.primaryNavy),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        prof['name'],
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.textDark),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: isAvailable ? AppTheme.statusGreen.withOpacity(0.15) : Colors.amber.shade50,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          isAvailable ? 'IN CABIN' : 'IN LECTURE',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: isAvailable ? AppTheme.statusGreen : Colors.amber.shade900,
                          ),
                        ),
                      ),
                    ],
                  ),
                  Text(
                    '${prof['role']} • ${prof['dept']}',
                    style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      const Icon(Icons.location_on_outlined, size: 14, color: AppTheme.secondaryNavy),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          prof['cabin'],
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.secondaryNavy),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
