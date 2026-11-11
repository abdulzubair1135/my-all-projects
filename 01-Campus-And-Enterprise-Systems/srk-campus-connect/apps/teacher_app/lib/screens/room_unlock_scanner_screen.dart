import 'package:flutter/material.dart';
import '../services/teacher_api_service.dart';
import 'rolling_qr_display_screen.dart';

class RoomUnlockScannerScreen extends StatefulWidget {
  const RoomUnlockScannerScreen({super.key});

  @override
  State<RoomUnlockScannerScreen> createState() => _RoomUnlockScannerScreenState();
}

class _RoomUnlockScannerScreenState extends State<RoomUnlockScannerScreen> {
  bool _isVerifying = false;

  void _verifyAndStart(String roomQr) async {
    setState(() => _isVerifying = true);
    await TeacherApiService().unlockRoomAndStartClass(roomQr);
    setState(() => _isVerifying = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Room 204 Verified! Class Session Activated')),
      );
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => const RollingQrDisplayScreen(
            sessionId: 'sess_dbms_101',
            subject: 'DBMS (CS401)',
            room: '204',
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Unlock Classroom', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF00897B),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            Container(
              height: 260,
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.black87,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFF00897B), width: 3),
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  const Icon(Icons.meeting_room, size: 120, color: Colors.white24),
                  Container(
                    width: 180,
                    height: 180,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.tealAccent, width: 2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  if (_isVerifying) const CircularProgressIndicator(color: Colors.tealAccent),
                ],
              ),
            ),
            const SizedBox(height: 24),

            const Text(
              'Scan the permanent physical QR sticker mounted at Classroom Door / Podium to verify your physical presence and start class.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey, fontSize: 13),
            ),
            const SizedBox(height: 24),

            ElevatedButton.icon(
              onPressed: _isVerifying
                  ? null
                  : () => _verifyAndStart('CAMPUS_ROOM_V1:204:room_204_dbms_sig'),
              icon: const Icon(Icons.flash_on),
              label: const Text('Simulate Scan: Room 204 QR Sticker'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF00897B),
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 50),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
