import 'dart:async';
import 'package:flutter/material.dart';
import '../services/teacher_api_service.dart';

class RollingQrDisplayScreen extends StatefulWidget {
  final String sessionId;
  final String subject;
  final String room;

  const RollingQrDisplayScreen({
    super.key,
    required this.sessionId,
    required this.subject,
    required this.room,
  });

  @override
  State<RollingQrDisplayScreen> createState() => _RollingQrDisplayScreenState();
}

class _RollingQrDisplayScreenState extends State<RollingQrDisplayScreen> {
  int _secondsRemaining = 15;
  int _verifiedStudentsCount = 44;
  Timer? _timer;
  String _qrPayload = '';

  @override
  void initState() {
    super.initState();
    _refreshQr();
    _startTimer();
  }

  void _startTimer() {
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) return;
      if (_secondsRemaining > 1) {
        setState(() => _secondsRemaining--);
      } else {
        _refreshQr();
      }
    });
  }

  void _refreshQr() async {
    final data = await TeacherApiService().getDynamicQr(widget.sessionId);
    setState(() {
      _qrPayload = data['qrCode'] ?? '';
      _secondsRemaining = data['expiresInSeconds'] ?? 15;
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dynamic Class QR', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF00897B),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            // Class Info Banner
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(widget.subject, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                        Text('Room ${widget.room} • Active Session', style: const TextStyle(color: Colors.grey, fontSize: 13)),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(color: Colors.green.shade50, borderRadius: BorderRadius.circular(10)),
                      child: Text(
                        '$_verifiedStudentsCount Present',
                        style: TextStyle(color: Colors.green.shade900, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // DYNAMIC ROLLING QR DISPLAY CARD
            Card(
              elevation: 8,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    const Icon(Icons.qr_code_scanner, size: 220, color: Color(0xFF004D40)),
                    const SizedBox(height: 16),
                    LinearProgressIndicator(
                      value: _secondsRemaining / 15.0,
                      backgroundColor: Colors.grey.shade200,
                      color: _secondsRemaining > 4 ? const Color(0xFF00897B) : Colors.red,
                      minHeight: 8,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.timer, size: 18, color: _secondsRemaining > 4 ? const Color(0xFF00897B) : Colors.red),
                        const SizedBox(width: 6),
                        Text(
                          'Rotating in $_secondsRemaining seconds (HMAC Token)',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                            color: _secondsRemaining > 4 ? const Color(0xFF00897B) : Colors.red,
                          ),
                        ),
                      ],
                    ),
                    if (_qrPayload.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Text(
                        'Token: ${_qrPayload.length > 24 ? '${_qrPayload.substring(0, 24)}...' : _qrPayload}',
                        style: const TextStyle(fontSize: 10, color: Colors.grey, fontFamily: 'monospace'),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            const Text(
              'Dynamic QR updates every 15s to prevent screenshot sharing or proxy attendance. Display this to your students.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
            const SizedBox(height: 24),

            ElevatedButton.icon(
              onPressed: () {
                setState(() => _verifiedStudentsCount += 1);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Simulated Student Verified (+1)')),
                );
              },
              icon: const Icon(Icons.person_add),
              label: const Text('Simulate Incoming Student Scan'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF00897B),
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 48),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
