import 'package:flutter/material.dart';

class LeaveApprovalsScreen extends StatefulWidget {
  const LeaveApprovalsScreen({super.key});

  @override
  State<LeaveApprovalsScreen> createState() => _LeaveApprovalsScreenState();
}

class _LeaveApprovalsScreenState extends State<LeaveApprovalsScreen> {
  final List<Map<String, dynamic>> _leaveRequests = [
    {
      'studentName': 'Rahul Shah',
      'enroll': 'SRK2026BCA001',
      'class': 'BCA Sem 3 (LH-3)',
      'reason': 'Viral Fever & Medical Rest (Doctor Certificate Attached)',
      'dates': '04 Sep - 05 Sep 2026 (2 Days)',
      'currentAttendance': '96%',
      'status': 'PENDING',
    },
    {
      'studentName': 'Priya Sharma',
      'enroll': 'SRK2026BCA002',
      'class': 'BCA Sem 3 (LH-3)',
      'reason': 'State Level Smart India Hackathon at GTU Ahmedabad',
      'dates': '06 Sep - 07 Sep 2026 (2 Days)',
      'currentAttendance': '95%',
      'status': 'PENDING',
    },
    {
      'studentName': 'Aman Khan',
      'enroll': 'SRK2026BCA009',
      'class': 'BCA Sem 3 (LH-3)',
      'reason': 'Family Function / Out of Station',
      'dates': '01 Sep 2026 (1 Day)',
      'currentAttendance': '96%',
      'status': 'APPROVED',
    },
  ];

  void _handleAction(int idx, String action) {
    setState(() {
      _leaveRequests[idx]['status'] = action;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: action == 'APPROVED' ? Colors.teal : Colors.red,
        content: Text('${_leaveRequests[idx]['studentName']}\'s leave marked as $action! Attendance marked as EXCUSED.'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Student Leave Approvals', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF00897B),
        foregroundColor: Colors.white,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: _leaveRequests.length,
        itemBuilder: (ctx, idx) {
          final req = _leaveRequests[idx];
          final isPending = req['status'] == 'PENDING';
          final isApproved = req['status'] == 'APPROVED';

          Color statusCol = isApproved ? Colors.green : (isPending ? Colors.amber.shade800 : Colors.red);

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
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
                            backgroundColor: Colors.teal.shade50,
                            child: Text(req['studentName'][0], style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF00897B))),
                          ),
                          const SizedBox(width: 10),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(req['studentName'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                              Text('${req['enroll']} • ${req['class']}', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                            ],
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(color: statusCol.withAlpha(30), borderRadius: BorderRadius.circular(6)),
                        child: Text(req['status'], style: TextStyle(color: statusCol, fontWeight: FontWeight.bold, fontSize: 11)),
                      ),
                    ],
                  ),
                  const Divider(height: 16),

                  Text('Reason: ${req['reason']}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Duration: ${req['dates']}', style: const TextStyle(fontSize: 11, color: Colors.blueGrey)),
                      Text('Sem Attendance: ${req['currentAttendance']}', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.teal)),
                    ],
                  ),

                  if (isPending) ...[
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        OutlinedButton(
                          onPressed: () => _handleAction(idx, 'REJECTED'),
                          style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                          child: const Text('Reject'),
                        ),
                        const SizedBox(width: 8),
                        ElevatedButton.icon(
                          onPressed: () => _handleAction(idx, 'APPROVED'),
                          icon: const Icon(Icons.check, size: 16),
                          label: const Text('Approve (Excuse Attendance)'),
                          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF00897B), foregroundColor: Colors.white),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
