import 'dart:async';
import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../../core/theme.dart';

class AttendanceGeneratorView extends StatefulWidget {
  const AttendanceGeneratorView({super.key});

  @override
  State<AttendanceGeneratorView> createState() => _AttendanceGeneratorViewState();
}

class _AttendanceGeneratorViewState extends State<AttendanceGeneratorView> {
  int _securityOtp = 4821;
  int _secondsRemaining = 15;
  Timer? _timer;
  int _markedCount = 54;
  final int _totalStudents = 60;

  @override
  void initState() {
    super.initState();
    _startOtpTicker();
  }

  void _startOtpTicker() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted) return;
      setState(() {
        if (_secondsRemaining > 1) {
          _secondsRemaining--;
        } else {
          _secondsRemaining = 15;
          _securityOtp = 1000 + (DateTime.now().millisecondsSinceEpoch % 9000);
        }
      });
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final qrData = 'SRK_ATTENDANCE:LH-03:BCA_SEM3:PHP_WEB_DEV:OTP_$_securityOtp';

    return Scaffold(
      backgroundColor: AppTheme.bgCream,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.grey.shade200),
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'DYNAMIC QR ATTENDANCE',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 1,
                              color: AppTheme.primaryNavy,
                            ),
                          ),
                          Text('BCA Sem 3 • Lecture Hall 03', style: TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppTheme.statusGreen.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '$_markedCount / $_totalStudents PRESENT',
                          style: const TextStyle(color: AppTheme.statusGreen, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                  const Divider(height: 24),

                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppTheme.accentGold.withOpacity(0.5), width: 2),
                      boxShadow: [
                        BoxShadow(
                          color: AppTheme.accentGold.withOpacity(0.1),
                          blurRadius: 16,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: QrImageView(
                      data: qrData,
                      version: QrVersions.auto,
                      size: 200.0,
                      eyeStyle: const QrEyeStyle(eyeShape: QrEyeShape.square, color: AppTheme.primaryNavy),
                      dataModuleStyle: const QrDataModuleStyle(dataModuleShape: QrDataModuleShape.square, color: AppTheme.secondaryNavy),
                    ),
                  ),
                  const SizedBox(height: 16),

                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.security_rounded, size: 18, color: AppTheme.statusAmber),
                      const SizedBox(width: 6),
                      Text(
                        'Rolling Dynamic Code: $_securityOtp',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, letterSpacing: 1),
                      ),
                      const SizedBox(width: 8),
                      Text('(${_secondsRemaining}s)', style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Students must scan using the SRK Student Portal to record GPS-verified presence.',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
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
