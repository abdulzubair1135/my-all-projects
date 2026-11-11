import 'package:flutter/material.dart';
import '../services/teacher_api_service.dart';

class PrincipalRequestsScreen extends StatefulWidget {
  const PrincipalRequestsScreen({super.key});

  @override
  State<PrincipalRequestsScreen> createState() => _PrincipalRequestsScreenState();
}

class _PrincipalRequestsScreenState extends State<PrincipalRequestsScreen> {
  List<dynamic> _requests = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() async {
    final list = await TeacherApiService().getPrincipalRequests();
    if (!mounted) return;
    setState(() {
      _requests = list;
      _isLoading = false;
    });
  }

  void _handleQuickResponse(String id, String responseType) async {
    final autoDetails = {
      'roomName': 'Lecture Hall 3 (LH-3)',
      'subjectName': 'DBMS - I (BCA301)',
      'batchName': 'BCA Sem 3 (Div A)',
      'studentsCount': 54,
    };

    final messenger = ScaffoldMessenger.of(context);
    await TeacherApiService().quickRespondMeeting(
      id: id,
      responseType: responseType,
      autoDetails: responseType == 'BUSY' ? autoDetails : null,
    );

    if (!mounted) return;
    setState(() {
      final req = _requests.firstWhere((r) => r['id'] == id, orElse: () => null);
      if (req != null) {
        req['status'] = responseType == 'BUSY'
            ? 'BUSY_IN_CLASS'
            : (responseType == 'ARRIVING' ? 'ON_THE_WAY' : 'AVAILABLE');
        req['responseNote'] = responseType == 'BUSY'
            ? 'Auto-Dispatched: Taking Lecture in LH-3 (DBMS - I, 54 Students)'
            : (responseType == 'ARRIVING' ? 'Auto-Dispatched: ON THE WAY to Principal Cabin (ETA 2 min)' : 'Available in Cabin');
      }
    });

    String snackMsg = responseType == 'BUSY'
        ? '🔴 Dispatched to Principal: BUSY in LH-3 (DBMS - I with 54 students)'
        : (responseType == 'ARRIVING' ? '🟢 Dispatched to Principal: ON THE WAY (ETA 2 mins)' : '🔵 Dispatched: Available');

    messenger.showSnackBar(
      SnackBar(
        content: Text(snackMsg, style: const TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: responseType == 'BUSY' ? Colors.deepOrange.shade900 : (responseType == 'ARRIVING' ? Colors.green.shade800 : const Color(0xFF00897B)),
        duration: const Duration(seconds: 4),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Principal Cabin Requests', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF00897B),
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _requests.length,
              itemBuilder: (ctx, idx) {
                final req = _requests[idx];
                final status = req['status'] as String? ?? 'PENDING';
                final isPending = status == 'PENDING';
                final isBusy = status == 'BUSY_IN_CLASS';
                final isOnTheWay = status == 'ON_THE_WAY';

                return Card(
                  elevation: isPending ? 5 : 2,
                  margin: const EdgeInsets.only(bottom: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                    side: BorderSide(
                      color: isPending ? Colors.deepOrange.shade400 : Colors.grey.shade200,
                      width: isPending ? 2 : 1,
                    ),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(18.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: isPending ? Colors.red.shade50 : Colors.purple.shade50,
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: isPending ? Colors.red : Colors.purple.shade200),
                              ),
                              child: Row(
                                children: [
                                  Icon(Icons.person_pin, size: 14, color: isPending ? Colors.red : Colors.purple),
                                  const SizedBox(width: 4),
                                  Text(
                                    isPending ? '🚨 URGENT SUMMON' : 'CABIN CALL',
                                    style: TextStyle(
                                      color: isPending ? Colors.red.shade900 : Colors.purple.shade900,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 11,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Text(req['time'] ?? 'Just now', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'From: ${req['sender'] ?? 'Dr. Nirdesh Buch (Principal)'}',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        const SizedBox(height: 6),
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(color: Colors.grey.shade100, borderRadius: BorderRadius.circular(8)),
                          child: Text(
                            req['reason'] ?? 'Immediate meeting in Principal Cabin regarding NAAC Timetable & Attendance Compliance.',
                            style: const TextStyle(fontSize: 13, color: Colors.black87),
                          ),
                        ),
                        const Divider(height: 24),

                        if (isPending) ...[
                          const Text(
                            'ONE-TAP RESPONSE (Zero Typing Required):',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: Colors.grey),
                          ),
                          const SizedBox(height: 10),
                          Row(
                            children: [
                              // BUSY BUTTON (Auto-Gathers Class Details)
                              Expanded(
                                child: ElevatedButton.icon(
                                  onPressed: () => _handleQuickResponse(req['id'], 'BUSY'),
                                  icon: const Icon(Icons.block, size: 16),
                                  label: const Text('🔴 BUSY in Class', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.deepOrange.shade800,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(vertical: 12),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              // ARRIVING BUTTON (On The Way)
                              Expanded(
                                child: ElevatedButton.icon(
                                  onPressed: () => _handleQuickResponse(req['id'], 'ARRIVING'),
                                  icon: const Icon(Icons.directions_walk, size: 16),
                                  label: const Text('🟢 ON THE WAY', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.green.shade800,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(vertical: 12),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ] else ...[
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: isBusy ? Colors.deepOrange.shade50 : (isOnTheWay ? Colors.green.shade50 : Colors.blue.shade50),
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(
                                color: isBusy ? Colors.deepOrange : (isOnTheWay ? Colors.green : Colors.blue),
                              ),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  isBusy ? Icons.block : (isOnTheWay ? Icons.directions_walk : Icons.check_circle),
                                  size: 18,
                                  color: isBusy ? Colors.deepOrange : (isOnTheWay ? Colors.green : Colors.blue),
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    req['responseNote'] ?? 'Dispatched status to Principal Sir',
                                    style: TextStyle(
                                      color: isBusy ? Colors.deepOrange.shade900 : (isOnTheWay ? Colors.green.shade900 : Colors.blue.shade900),
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                              ],
                            ),
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
