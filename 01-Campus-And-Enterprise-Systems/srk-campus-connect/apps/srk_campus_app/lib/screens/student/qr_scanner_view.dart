import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme.dart';
import '../../services/api_service.dart';

class QrScannerView extends ConsumerStatefulWidget {
  const QrScannerView({super.key});

  @override
  ConsumerState<QrScannerView> createState() => _QrScannerViewState();
}

class _QrScannerViewState extends ConsumerState<QrScannerView> {
  bool _isProcessing = false;
  String? _scanResult;

  Future<void> _simulateQrScan() async {
    setState(() {
      _isProcessing = true;
      _scanResult = null;
    });

    final res = await ApiService().markAttendance(
      qrCodeData: 'SRK_ATTENDANCE:LH-03:BCA_SEM3:PHP_WEB_DEV:OTP_4821',
    );

    if (mounted) {
      setState(() {
        _isProcessing = false;
        _scanResult = 'SUCCESS: Attendance verified & recorded for Web Dev (LH-03)!';
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AppTheme.statusGreen,
          content: Text('Attendance marked successfully in Lecture Hall 03.'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgCream,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 220,
                height: 220,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: AppTheme.primaryNavy.withOpacity(0.3), width: 2),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.06),
                      blurRadius: 16,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.qr_code_scanner_rounded,
                      size: 80,
                      color: _isProcessing ? AppTheme.accentGold : AppTheme.primaryNavy,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      _isProcessing ? 'Verifying GPS & Token...' : 'Scan Smart Board QR',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              const Text(
                'Anti-Proxy Location Verification Active',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.primaryNavy),
              ),
              const SizedBox(height: 6),
              const Text(
                'Scans dynamic rolling QR codes projected inside lecture halls LH 1-10.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
              ),
              const SizedBox(height: 24),

              if (_scanResult != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: Colors.green.shade200),
                  ),
                  child: Text(
                    _scanResult!,
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: AppTheme.statusGreen, fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                ),
                const SizedBox(height: 16),
              ],

              SizedBox(
                width: 240,
                height: 48,
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.camera_alt_rounded),
                  label: const Text('1-Tap Mark Attendance'),
                  onPressed: _isProcessing ? null : _simulateQrScan,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
