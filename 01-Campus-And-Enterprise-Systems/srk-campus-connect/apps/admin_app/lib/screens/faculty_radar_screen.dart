import 'package:flutter/material.dart';
import '../services/admin_api_service.dart';

class FacultyRadarScreen extends StatefulWidget {
  const FacultyRadarScreen({super.key});

  @override
  State<FacultyRadarScreen> createState() => _FacultyRadarScreenState();
}

class _FacultyRadarScreenState extends State<FacultyRadarScreen> {
  bool _showMapView = false;

  final List<Map<String, dynamic>> _facultyList = [
    {
      'name': 'Prof. Nirali Thakkar (NT)',
      'code': 'NT',
      'dept': 'BCA Department',
      'desig': 'Associate Professor',
      'status': 'IN_CLASS (Teaching - Lecture Hall 3)',
      'statusCode': 'IN_CLASS',
      'expectedRoom': 'Lecture Hall 3 (LH-3)',
      'detectedRoom': 'Lecture Hall 3',
      'confidence': 96,
      'lastVerified': '25s ago (Physical QR Scan Verified)',
      'currentClass': 'DBMS - I (BCA Sem 3)',
    },
    {
      'name': 'Prof. Arjunsinh Vaghela (AV)',
      'code': 'AV',
      'dept': 'BCA Department',
      'desig': 'Professor',
      'status': 'IN_CLASS (Teaching - Lecture Hall 9)',
      'statusCode': 'IN_CLASS',
      'expectedRoom': 'Lecture Hall 9 (LH-9)',
      'detectedRoom': 'Lecture Hall 9',
      'confidence': 95,
      'lastVerified': '45s ago (Physical QR Scan Verified)',
      'currentClass': 'Advanced DBMS (BCA Sem 5)',
    },
    {
      'name': 'Dr. Nirdesh Buch (NB - Principal)',
      'code': 'NB',
      'dept': 'Principal & BBA Department',
      'desig': 'Principal & Director',
      'status': 'IN_CLASS (Teaching - Lecture Hall 6)',
      'statusCode': 'IN_CLASS',
      'expectedRoom': 'Lecture Hall 6 (LH-6)',
      'detectedRoom': 'Lecture Hall 6',
      'confidence': 98,
      'lastVerified': '1 min ago (Physical QR Scan Verified)',
      'currentClass': 'Bhagwad Gita (BBA Sem 1 A)',
    },
    {
      'name': 'Prof. Jinal Sorathiya (JS)',
      'code': 'JS',
      'dept': 'BCA Department',
      'desig': 'Associate Professor',
      'status': 'NOT_IN_CLASS (Pending Room QR Scan)',
      'statusCode': 'NOT_IN_CLASS',
      'expectedRoom': 'Lecture Hall 5 (LH-5)',
      'detectedRoom': 'Pending / Not in Class',
      'confidence': 35,
      'lastVerified': '15 min ago (Slot Active, No Scan)',
      'currentClass': 'Statistics (BCA Sem 1)',
    },
    {
      'name': 'Prof. Rishi Sonpar (RS)',
      'code': 'RS',
      'dept': 'BBA Department',
      'desig': 'Professor & HOD BBA',
      'status': 'WITH_PRINCIPAL (Cabin / Meeting)',
      'statusCode': 'WITH_PRINCIPAL',
      'expectedRoom': 'Lecture Hall 2 (LH-2)',
      'detectedRoom': 'Principal Office',
      'confidence': 98,
      'lastVerified': '1 min ago (Meeting Active)',
      'currentClass': 'Fundamentals of Management',
    },
    {
      'name': 'Prof. Surbhi Ahir (SA - Campus Head)',
      'code': 'SA',
      'dept': 'Campus Head & MBA Department',
      'desig': 'Campus Head',
      'status': 'IN_CABIN (Available / Admin)',
      'statusCode': 'AVAILABLE',
      'expectedRoom': 'Campus Head Office',
      'detectedRoom': 'Campus Head Office',
      'confidence': 98,
      'lastVerified': '30s ago',
      'currentClass': 'Administration & Coordination',
    },
    {
      'name': 'Prof. Prakash Lambha (PL)',
      'code': 'PL',
      'dept': 'BCA Department',
      'desig': 'Professor & HOD BCA',
      'status': 'MOBILE_DATA_OFF (BLE Mesh Active)',
      'statusCode': 'BLE_MESH',
      'expectedRoom': 'Python & App Lab',
      'detectedRoom': 'Python & App Lab',
      'confidence': 85,
      'lastVerified': '2 min ago (Relayed via Student Mesh)',
      'currentClass': 'OOP with Python',
    },
    {
      'name': 'Prof. Stephen Sober (SS)',
      'code': 'SS',
      'dept': 'MBA / BBA Department',
      'desig': 'Associate Professor',
      'status': 'IN_CLASS (Teaching - Lecture Hall 1)',
      'statusCode': 'IN_CLASS',
      'expectedRoom': 'Lecture Hall 1 (LH-1)',
      'detectedRoom': 'Lecture Hall 1',
      'confidence': 94,
      'lastVerified': '30s ago (Physical QR Scan Verified)',
      'currentClass': 'Consumer Behaviour (BBA Sem 3)',
    },
    {
      'name': 'Prof. Abhishek Abhani (AA)',
      'code': 'AA',
      'dept': 'BBA Department',
      'desig': 'Associate Professor',
      'status': 'IN_CLASS (Teaching - Lecture Hall 7)',
      'statusCode': 'IN_CLASS',
      'expectedRoom': 'Lecture Hall 7 (LH-7)',
      'detectedRoom': 'Lecture Hall 7',
      'confidence': 96,
      'lastVerified': '50s ago (Physical QR Scan Verified)',
      'currentClass': 'Business Organization (BBA 1 B)',
    },
    {
      'name': 'Prof. Rishi Joshi (RJ)',
      'code': 'RJ',
      'dept': 'BBA Department',
      'desig': 'Assistant Professor',
      'status': 'IN_CABIN (Available)',
      'statusCode': 'AVAILABLE',
      'expectedRoom': 'Staff Cabin 104',
      'detectedRoom': 'Staff Cabin 104',
      'confidence': 98,
      'lastVerified': '45s ago',
      'currentClass': 'Free / Pre-Class Prep',
    },
    {
      'name': 'Prof. Chandni Thacker (CT)',
      'code': 'CT',
      'dept': 'BBA Department',
      'desig': 'Professor',
      'status': 'IN_CABIN (Available)',
      'statusCode': 'AVAILABLE',
      'expectedRoom': 'Staff Cabin 105',
      'detectedRoom': 'Staff Cabin 105',
      'confidence': 96,
      'lastVerified': '3 min ago',
      'currentClass': 'Available',
    },
    {
      'name': 'Prof. Mayur Meghani (MM)',
      'code': 'MM',
      'dept': 'BBA Department',
      'desig': 'Associate Professor',
      'status': 'IN_CABIN (Available)',
      'statusCode': 'AVAILABLE',
      'expectedRoom': 'Staff Cabin 102',
      'detectedRoom': 'Staff Cabin 102',
      'confidence': 95,
      'lastVerified': '2 min ago',
      'currentClass': 'Available',
    },
    {
      'name': 'Prof. Ankit Gandhi (AG)',
      'code': 'AG',
      'dept': 'MBA Department',
      'desig': 'Assistant Professor',
      'status': 'IN_CABIN (Available)',
      'statusCode': 'AVAILABLE',
      'expectedRoom': 'MBA Faculty Room',
      'detectedRoom': 'MBA Faculty Room',
      'confidence': 94,
      'lastVerified': '1 min ago',
      'currentClass': 'Available',
    },
    {
      'name': 'Prof. Krupa Patel (KP)',
      'code': 'KP',
      'dept': 'MBA Department',
      'desig': 'Professor & HOD MBA',
      'status': 'IN_CABIN (Available)',
      'statusCode': 'AVAILABLE',
      'expectedRoom': 'HOD Office 301',
      'detectedRoom': 'HOD Office 301',
      'confidence': 98,
      'lastVerified': '30s ago',
      'currentClass': 'Available',
    },
    {
      'name': 'Prof. Prayag Joshi (PJ)',
      'code': 'PJ',
      'dept': 'BCA Department',
      'desig': 'Assistant Professor',
      'status': 'IN_CABIN (Available)',
      'statusCode': 'AVAILABLE',
      'expectedRoom': 'BCA Staff Room',
      'detectedRoom': 'BCA Staff Room',
      'confidence': 95,
      'lastVerified': '1 min ago',
      'currentClass': 'Available',
    },
  ];

  String _filter = 'ALL';

  void _showMeetingDialog(Map<String, dynamic> faculty) {
    final reasonController = TextEditingController(text: 'Immediate briefing in Principal Cabin regarding NAAC Timetable & Attendance Compliance');
    String reqType = 'URGENT_CABIN_CALL';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: Row(
            children: [
              const Icon(Icons.person_pin, color: Color(0xFF283593)),
              const SizedBox(width: 8),
              Expanded(child: Text('Summon: ${faculty['name']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Live Location: ${faculty['detectedRoom']} • ${faculty['currentClass']}', style: const TextStyle(fontSize: 12, color: Colors.blueGrey, fontWeight: FontWeight.w600)),
              const SizedBox(height: 14),
              SegmentedButton<String>(
                segments: const [
                  ButtonSegment(value: 'URGENT_CABIN_CALL', label: Text('🚨 Urgent Cabin Call', style: TextStyle(fontSize: 11))),
                  ButtonSegment(value: 'MEETING', label: Text('Request Meeting', style: TextStyle(fontSize: 11))),
                ],
                selected: {reqType},
                onSelectionChanged: (val) => setDialogState(() => reqType = val.first),
              ),
              const SizedBox(height: 14),
              TextField(
                controller: reasonController,
                maxLines: 2,
                decoration: const InputDecoration(
                  labelText: 'Agenda / Purpose for Teacher',
                  border: OutlineInputBorder(),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            ElevatedButton.icon(
              onPressed: () async {
                final messenger = ScaffoldMessenger.of(context);
                final nav = Navigator.of(ctx);
                await AdminApiService().requestMeeting(faculty['name'], reqType, reasonController.text);
                if (!mounted) return;
                setState(() {
                  faculty['summonStatus'] = 'SUMMON_SENT';
                  faculty['summonNote'] = 'Summon Sent • Awaiting 1-Tap Response';
                });
                nav.pop();
                messenger.showSnackBar(
                  SnackBar(
                    backgroundColor: const Color(0xFF283593),
                    content: Text('Dispatched Urgent Summon to ${faculty['name']}. Teacher received instant 1-tap notification.'),
                  ),
                );
              },
              icon: const Icon(Icons.send, size: 16),
              label: const Text('Dispatch to Teacher Phone'),
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF283593), foregroundColor: Colors.white),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _filter == 'ALL'
        ? _facultyList
        : _facultyList.where((f) => f['statusCode'] == _filter).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('SRK Campus Faculty Radar', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF283593),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(_showMapView ? Icons.view_list : Icons.map),
            tooltip: _showMapView ? 'Switch to List View' : 'Switch to 2D Floor Plan Map',
            onPressed: () => setState(() => _showMapView = !_showMapView),
          ),
        ],
      ),
      body: _showMapView
          ? _build2DCampusMap()
          : Column(
              children: [
                // Filter Chips
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  child: Row(
                    children: [
                      _buildFilterChip('ALL', 'All Faculty (15)'),
                      _buildFilterChip('IN_CLASS', '🟢 In Class (5)'),
                      _buildFilterChip('NOT_IN_CLASS', '🟡 Pending Scan (1)'),
                      _buildFilterChip('WITH_PRINCIPAL', '🟣 With Principal (1)'),
                      _buildFilterChip('BLE_MESH', '⚠️ BLE Mesh Only (1)'),
                      _buildFilterChip('AVAILABLE', '🔵 In Cabin (7)'),
                    ],
                  ),
                ),
                const Divider(height: 1),

                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: filtered.length,
                    itemBuilder: (ctx, idx) {
                      final fac = filtered[idx];
                      final code = fac['statusCode'] as String;
                      final conf = fac['confidence'] as int;

                      Color col = Colors.green;
                      IconData icon = Icons.check_circle;
                      if (code == 'NOT_IN_CLASS') {
                        col = Colors.amber.shade800;
                        icon = Icons.warning_amber;
                      } else if (code == 'WITH_PRINCIPAL') {
                        col = Colors.purple;
                        icon = Icons.person_pin;
                      } else if (code == 'BLE_MESH') {
                        col = Colors.deepOrange;
                        icon = Icons.bluetooth_audio;
                      } else if (code == 'AVAILABLE') {
                        col = Colors.teal;
                        icon = Icons.meeting_room;
                      }

                      return Card(
                        elevation: 2,
                        margin: const EdgeInsets.only(bottom: 10),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        child: Padding(
                          padding: const EdgeInsets.all(14.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Row(
                                    children: [
                                      CircleAvatar(
                                        backgroundColor: col.withAlpha(40),
                                        child: Text(fac['code'], style: TextStyle(fontWeight: FontWeight.bold, color: col)),
                                      ),
                                      const SizedBox(width: 12),
                                      Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(fac['name'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                                          Text('${fac['desig']} • ${fac['dept']}', style: TextStyle(color: Colors.grey.shade700, fontSize: 11)),
                                        ],
                                      ),
                                    ],
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                    decoration: BoxDecoration(color: col.withAlpha(30), borderRadius: BorderRadius.circular(8)),
                                    child: Row(
                                      children: [
                                        Icon(icon, size: 12, color: col),
                                        const SizedBox(width: 4),
                                        Text(
                                          code == 'IN_CLASS'
                                              ? 'Teaching'
                                              : (code == 'NOT_IN_CLASS' ? 'Not In Class' : (code == 'WITH_PRINCIPAL' ? 'With Principal' : (code == 'BLE_MESH' ? 'BLE Mesh' : 'In Cabin'))),
                                          style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 11),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                              const Divider(height: 18),

                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Text('TIMETABLE SCHEDULE', style: TextStyle(color: Colors.grey, fontSize: 9, fontWeight: FontWeight.bold)),
                                      Text('${fac['expectedRoom']} • ${fac['currentClass']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                                    ],
                                  ),
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.end,
                                    children: [
                                      const Text('LIVE EVIDENCE & LOCATION', style: TextStyle(color: Colors.grey, fontSize: 9, fontWeight: FontWeight.bold)),
                                      Text('${fac['detectedRoom']} ($conf% Conf.)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: col)),
                                    ],
                                  ),
                                ],
                              ),
                              const SizedBox(height: 10),

                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text('Evidence: ${fac['lastVerified']}', style: const TextStyle(fontSize: 10, color: Colors.blueGrey)),
                                  TextButton.icon(
                                    onPressed: () => _showMeetingDialog(fac),
                                    icon: const Icon(Icons.send, size: 14),
                                    label: const Text('Call / Meet', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                                    style: TextButton.styleFrom(foregroundColor: const Color(0xFF283593)),
                                  ),
                                ],
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

  Widget _build2DCampusMap() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('SRK CAMPUS 2D FLOOR PLAN', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF283593))),
              OutlinedButton.icon(
                onPressed: () => setState(() => _showMapView = false),
                icon: const Icon(Icons.list, size: 16),
                label: const Text('List View'),
              ),
            ],
          ),
          const SizedBox(height: 4),
          const Text('Live physical occupancy of Lecture Halls 1-10, Labs & Executive Offices', style: TextStyle(color: Colors.grey, fontSize: 12)),
          const SizedBox(height: 16),

          // Admin Block
          const Text('ADMINISTRATION BLOCK', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _buildRoomBox('Principal Office', 'Dr. Nirdesh Buch (NB)\nProf. Rishi Sonpar (RS)', '🟣 In Meeting', Colors.purple)),
              const SizedBox(width: 10),
              Expanded(child: _buildRoomBox('Campus Head Office', 'Prof. Surbhi Ahir (SA)', '🔵 Administration', Colors.teal)),
            ],
          ),
          const SizedBox(height: 18),

          // Academic Wing - Lecture Halls 1 to 10
          const Text('ACADEMIC WING — LECTURE HALLS (1 TO 10)', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
          const SizedBox(height: 8),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 10,
            crossAxisSpacing: 10,
            childAspectRatio: 1.5,
            children: [
              _buildRoomBox('LH 1 (BBA Sem 3)', 'Prof. Stephen Sober (SS)', '🟢 In Class (Teaching)', Colors.green),
              _buildRoomBox('LH 2 (BBA Sem 5)', 'Mercantile Law (Scheduled)', '🟣 Teacher with Principal', Colors.purple),
              _buildRoomBox('LH 3 (BCA Sem 3)', 'Prof. Nirali Thakkar (NT)\n54 Students Present', '🟢 In Class (Teaching)', Colors.green),
              _buildRoomBox('LH 4', 'Available / Empty', '⚪ Reserved', Colors.grey),
              _buildRoomBox('LH 5 (BCA Sem 1)', 'Prof. Jinal Sorathiya (JS)', '🟡 Pending Room Scan', Colors.amber.shade800),
              _buildRoomBox('LH 6 (BBA 1 Class I)', 'Dr. Nirdesh Buch (NB)', '🟢 In Class (Teaching)', Colors.green),
              _buildRoomBox('LH 7 (BBA 1 Class II)', 'Prof. Abhishek Abhani (AA)', '🟢 In Class (Teaching)', Colors.green),
              _buildRoomBox('LH 8', 'Available / Empty', '⚪ Reserved', Colors.grey),
              _buildRoomBox('LH 9 (BCA Sem 5)', 'Prof. Arjunsinh Vaghela (AV)', '🟢 In Class (Teaching)', Colors.green),
              _buildRoomBox('LH 10', 'Available / Empty', '⚪ Reserved', Colors.grey),
            ],
          ),
          const SizedBox(height: 18),

          // IT & Practical Labs
          const Text('IT WING — COMPUTER LABS', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _buildRoomBox('Web & Cyber Lab', 'Web Designing Lab', '🟢 Active', Colors.teal)),
              const SizedBox(width: 10),
              Expanded(child: _buildRoomBox('Python & App Lab', 'Prof. Prakash Lambha (PL)', '⚠️ BLE Mesh Active', Colors.deepOrange)),
              const SizedBox(width: 10),
              Expanded(child: _buildRoomBox('DBMS & C Lab', 'Data Structures Lab', '🔵 Ready', Colors.blueGrey)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildRoomBox(String roomName, String occupant, String status, Color col) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: col.withAlpha(20),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: col, width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(roomName, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: col)),
          const SizedBox(height: 2),
          Text(occupant, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: Colors.black87)),
          const SizedBox(height: 4),
          Text(status, style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: col)),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String key, String label) {
    final isSel = _filter == key;
    return Padding(
      padding: const EdgeInsets.only(right: 6.0),
      child: ChoiceChip(
        label: Text(label, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: isSel ? Colors.white : Colors.black87)),
        selected: isSel,
        selectedColor: const Color(0xFF283593),
        onSelected: (sel) {
          if (sel) setState(() => _filter = key);
        },
      ),
    );
  }
}
