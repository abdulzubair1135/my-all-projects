import 'dart:async';
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class StudentIdQrScreen extends StatefulWidget {
  const StudentIdQrScreen({super.key});

  @override
  State<StudentIdQrScreen> createState() => _StudentIdQrScreenState();
}

class _StudentIdQrScreenState extends State<StudentIdQrScreen> {
  int _secondsRemaining = 300; // 5 min rolling TTL
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _startTimer();
  }

  void _startTimer() {
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) return;
      if (_secondsRemaining > 1) {
        setState(() => _secondsRemaining--);
      } else {
        setState(() => _secondsRemaining = 300);
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final user = StudentApiService().currentUser;
    final name = user?['name'] ?? 'Rahul Shah';
    final enroll = user?['enrollmentNumber'] ?? 'STU2026001';
    final dept = user?['department'] ?? 'Computer Engineering';

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Digital ID QR', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            Card(
              elevation: 6,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    CircleAvatar(
                      radius: 36,
                      backgroundColor: Colors.blue.shade100,
                      child: Text(
                        name.isNotEmpty ? name[0] : 'S',
                        style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFF1565C0)),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(name, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                    Text('$enroll • $dept', style: const TextStyle(color: Colors.grey, fontSize: 13)),
                    const SizedBox(height: 24),

                    // Digital Rolling QR Box
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.grey.shade300, width: 2),
                      ),
                      child: Column(
                        children: [
                          const Icon(Icons.qr_code_2, size: 180, color: Color(0xFF0D47A1)),
                          const SizedBox(height: 12),
                          LinearProgressIndicator(
                            value: _secondsRemaining / 300.0,
                            backgroundColor: Colors.grey.shade200,
                            color: const Color(0xFF1565C0),
                            minHeight: 6,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Rotates in ${_secondsRemaining ~/ 60}:${(_secondsRemaining % 60).toString().padLeft(2, '0')}',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.blueGrey),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Show this QR to your teacher for manual verification during lab sessions or offline attendance checks.',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
