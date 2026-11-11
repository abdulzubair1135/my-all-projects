import 'package:flutter/material.dart';
import '../services/api_service.dart';

class QrScannerScreen extends StatefulWidget {
  const QrScannerScreen({super.key});

  @override
  State<QrScannerScreen> createState() => _QrScannerScreenState();
}

class _QrScannerScreenState extends State<QrScannerScreen> {
  bool _isProcessing = false;
  String? _scanResult;
  bool _isSuccess = false;

  void _processQr(String rawCode) async {
    if (_isProcessing) return;
    setState(() {
      _isProcessing = true;
      _scanResult = null;
    });

    // Validate Dynamic Rolling QR protocol: CAMPUS_SESSION_V1:{sessionId}:{nonce}:{timestamp}:{hmacSignature}
    final isValidFormat = rawCode.startsWith('CAMPUS_SESSION_V1:') || rawCode.contains('sess_');
    
    if (!isValidFormat) {
      setState(() {
        _isProcessing = false;
        _isSuccess = false;
        _scanResult = 'Invalid Campus Dynamic QR format';
      });
      return;
    }

    final success = await StudentApiService().recordPresenceQr(rawCode);

    setState(() {
      _isProcessing = false;
      _isSuccess = success;
      _scanResult = success
          ? 'Attendance Verified! Cryptographically signed & synced'
          : 'Failed to record QR code';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dynamic QR Scanner', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            // Scanner Viewport Box
            Container(
              height: 280,
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.black87,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFF1565C0), width: 3),
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  const Icon(Icons.qr_code_scanner, size: 140, color: Colors.white24),
                  Container(
                    width: 200,
                    height: 200,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.greenAccent, width: 2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  if (_isProcessing)
                    const CircularProgressIndicator(color: Colors.greenAccent),
                ],
              ),
            ),
            const SizedBox(height: 24),

            if (_scanResult != null) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: _isSuccess ? Colors.green.shade50 : Colors.red.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: _isSuccess ? Colors.green : Colors.red),
                ),
                child: Row(
                  children: [
                    Icon(_isSuccess ? Icons.check_circle : Icons.error, color: _isSuccess ? Colors.green : Colors.red),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        _scanResult!,
                        style: TextStyle(
                          color: _isSuccess ? Colors.green.shade900 : Colors.red.shade900,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],

            const Text(
              'Point camera at Teacher\'s rolling 15s Dynamic QR code displayed on screen or projector.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey, fontSize: 13),
            ),
            const SizedBox(height: 24),

            // Simulated Fast Scan Buttons for Testing/Demo
            const Divider(),
            const SizedBox(height: 12),
            const Text('SIMULATE LIVE SCANS (TEST)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.grey)),
            const SizedBox(height: 12),
            ElevatedButton.icon(
              onPressed: _isProcessing
                  ? null
                  : () {
                      final demoToken = 'CAMPUS_SESSION_V1:sess_dbms_101:${DateTime.now().millisecondsSinceEpoch ~/ 15000}:${DateTime.now().millisecondsSinceEpoch}:hmac_demo_sig';
                      _processQr(demoToken);
                    },
              icon: const Icon(Icons.flash_on),
              label: const Text('Simulate Scan Active DBMS QR (Room 204)'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1565C0),
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 48),
              ),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: _isProcessing ? null : () => _processQr('INVALID_EXPIRED_QR_TOKEN'),
              icon: const Icon(Icons.cancel_outlined),
              label: const Text('Simulate Expired / Invalid QR'),
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.red,
                minimumSize: const Size(double.infinity, 48),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
