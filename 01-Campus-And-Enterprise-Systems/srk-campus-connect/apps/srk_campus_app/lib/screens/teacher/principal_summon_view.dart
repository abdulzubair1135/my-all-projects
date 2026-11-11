import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme.dart';
import '../../services/api_service.dart';
import '../../services/socket_service.dart';
import '../../providers/auth_provider.dart';

class PrincipalSummonView extends ConsumerStatefulWidget {
  const PrincipalSummonView({super.key});

  @override
  ConsumerState<PrincipalSummonView> createState() => _PrincipalSummonViewState();
}

class _PrincipalSummonViewState extends ConsumerState<PrincipalSummonView> {
  bool _isResponding = false;
  String _currentResponseStatus = 'PENDING';

  final Map<String, dynamic> _activeLectureContext = {
    'hall': 'Lecture Hall 03 (LH-3)',
    'subject': 'Web Development using PHP',
    'batch': 'BCA Sem 3 (Batch A)',
    'enrolledStudents': 60,
    'presentStudents': 58,
    'startTime': '10:30 AM',
    'endTime': '11:30 AM',
  };

  Map<String, dynamic>? _activeSummon = {
    'id': 'meet_urgent_001',
    'caller': 'Dr. Nirdesh Buch (Principal)',
    'location': 'Principal Cabin P-01',
    'timestamp': 'Just Now',
    'reason': 'Urgent Academic Advisory & Committee Consultation',
    'priority': 'URGENT',
  };

  @override
  void initState() {
    super.initState();
    _listenForSummons();
  }

  void _listenForSummons() {
    SocketService().on('meeting.new', (data) {
      if (mounted && data != null) {
        setState(() {
          _activeSummon = {
            'id': data['id'] ?? data['_id'] ?? 'urgent_${DateTime.now().millisecondsSinceEpoch}',
            'caller': data['callerName'] ?? 'Dr. Nirdesh Buch (Principal)',
            'location': data['location'] ?? 'Principal Cabin P-01',
            'timestamp': 'Just Now',
            'reason': data['reason'] ?? 'Urgent consultation requested by Principal',
            'priority': 'URGENT',
          };
          _currentResponseStatus = 'PENDING';
        });
      }
    });
  }

  Future<void> _respondBusy() async {
    if (_activeSummon == null) return;
    setState(() => _isResponding = true);

    final autoDetails = {
      'status': 'BUSY_IN_CLASS',
      'location': _activeLectureContext['hall'],
      'subject': _activeLectureContext['subject'],
      'batch': _activeLectureContext['batch'],
      'studentCount': _activeLectureContext['presentStudents'],
      'timeWindow': '${_activeLectureContext['startTime']} - ${_activeLectureContext['endTime']}',
      'message': 'Currently conducting ${_activeLectureContext['subject']} in ${_activeLectureContext['hall']} with ${_activeLectureContext['presentStudents']} students present.',
    };

    final res = await ApiService().quickRespondMeeting(
      meetingId: _activeSummon!['id'],
      responseType: 'BUSY',
      autoDetails: autoDetails,
    );

    if (mounted) {
      setState(() {
        _isResponding = false;
        _currentResponseStatus = 'BUSY_SENT';
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AppTheme.primaryNavy,
          content: Text('Class status auto-transmitted to Principal Dr. Nirdesh Buch.'),
        ),
      );
    }
  }

  Future<void> _respondArriving() async {
    if (_activeSummon == null) return;
    setState(() => _isResponding = true);

    final res = await ApiService().quickRespondMeeting(
      meetingId: _activeSummon!['id'],
      responseType: 'ARRIVING',
      transitEtaMinutes: 2,
    );

    if (mounted) {
      setState(() {
        _isResponding = false;
        _currentResponseStatus = 'ARRIVING_SENT';
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AppTheme.statusGreen,
          content: Text('Notified Principal: You are on the way (ETA 2 mins).'),
        ),
      );
    }
  }

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
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppTheme.secondaryNavy.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.class_rounded, color: AppTheme.secondaryNavy, size: 22),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            _activeLectureContext['hall'],
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.textDark),
                          ),
                          const SizedBox(width: 6),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: AppTheme.statusGreen.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: const Text('ACTIVE NOW', style: TextStyle(color: AppTheme.statusGreen, fontSize: 9, fontWeight: FontWeight.bold)),
                          ),
                        ],
                      ),
                      Text(
                        '${_activeLectureContext['subject']} • ${_activeLectureContext['presentStudents']} Students Present',
                        style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          if (_activeSummon != null) ...[
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.statusRed.withOpacity(0.4), width: 1.5),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.statusRed.withOpacity(0.08),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: const BoxDecoration(
                      color: AppTheme.statusRed,
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(14),
                        topRight: Radius.circular(14),
                      ),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.warning_amber_rounded, color: Colors.white, size: 22),
                        SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'URGENT CABIN SUMMON FROM PRINCIPAL',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w900,
                              fontSize: 13,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.account_circle, color: AppTheme.primaryNavy, size: 20),
                            const SizedBox(width: 8),
                            Text(
                              _activeSummon!['caller'],
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.textDark),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            const Icon(Icons.pin_drop_rounded, color: AppTheme.secondaryNavy, size: 16),
                            const SizedBox(width: 8),
                            Text(
                              'Location: ${_activeSummon!['location']}',
                              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.secondaryNavy),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: AppTheme.bgCream,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            'Purpose: "${_activeSummon!['reason']}"',
                            style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic, color: AppTheme.textDark),
                          ),
                        ),
                        const SizedBox(height: 16),

                        const Text(
                          '1-TAP RAPID RESPONSE (NO TYPING REQUIRED):',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.5,
                            color: AppTheme.textMuted,
                          ),
                        ),
                        const SizedBox(height: 12),

                        if (_isResponding)
                          const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator()))
                        else if (_currentResponseStatus == 'BUSY_SENT') ...[
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.red.shade50,
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: Colors.red.shade200),
                            ),
                            child: const Row(
                              children: [
                                Icon(Icons.check_circle_rounded, color: AppTheme.statusRed),
                                SizedBox(width: 10),
                                Expanded(
                                  child: Text(
                                    '"BUSY IN CLASS" details transmitted to Principal.\n(LH-03 • Web Dev • 58 Students)',
                                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.statusRed),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ] else if (_currentResponseStatus == 'ARRIVING_SENT') ...[
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.green.shade50,
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: Colors.green.shade200),
                            ),
                            child: const Row(
                              children: [
                                Icon(Icons.check_circle_rounded, color: AppTheme.statusGreen),
                                SizedBox(width: 10),
                                Expanded(
                                  child: Text(
                                    '"ON THE WAY" notification sent to Principal.\nETA ~2 mins.',
                                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.statusGreen),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ] else ...[
                          Row(
                            children: [
                              Expanded(
                                child: ElevatedButton.icon(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: AppTheme.statusRed,
                                    padding: const EdgeInsets.symmetric(vertical: 14),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                  ),
                                  icon: const Icon(Icons.cancel_rounded, size: 18),
                                  label: const Text(
                                    'BUSY in Class',
                                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                                  ),
                                  onPressed: _respondBusy,
                                ),
                              ),
                              const SizedBox(width: 10),
                              Expanded(
                                child: ElevatedButton.icon(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: AppTheme.statusGreen,
                                    padding: const EdgeInsets.symmetric(vertical: 14),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                  ),
                                  icon: const Icon(Icons.directions_walk_rounded, size: 18),
                                  label: const Text(
                                    'ON THE WAY',
                                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                                  ),
                                  onPressed: _respondArriving,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            '• Tapping "BUSY" automatically sends current hall (LH-3), subject & student count.\n• Tapping "ON THE WAY" informs the Principal of your arrival (ETA 2 mins).',
                            style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
                          ),
                        ],
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
