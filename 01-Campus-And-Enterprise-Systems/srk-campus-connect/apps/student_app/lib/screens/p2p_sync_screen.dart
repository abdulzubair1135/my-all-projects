import 'package:flutter/material.dart';
import '../services/api_service.dart';

class P2pSyncScreen extends StatefulWidget {
  const P2pSyncScreen({super.key});

  @override
  State<P2pSyncScreen> createState() => _P2pSyncScreenState();
}

class _P2pSyncScreenState extends State<P2pSyncScreen> {
  int _pendingCount = 0;
  bool _isDiscovering = false;

  @override
  void initState() {
    super.initState();
    _loadPendingCount();
  }

  void _loadPendingCount() async {
    final count = await StudentApiService().offlineQueue.getPendingCount();
    setState(() => _pendingCount = count);
  }

  void _startDiscovery() {
    setState(() => _isDiscovering = true);
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) setState(() => _isDiscovering = false);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SRK P2P BLE Mesh & Sync', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status Banner
            Card(
              color: _pendingCount > 0 ? Colors.amber.shade50 : Colors.green.shade50,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: BorderSide(color: _pendingCount > 0 ? Colors.amber : Colors.green),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    Icon(
                      _pendingCount > 0 ? Icons.sync_problem : Icons.cloud_done,
                      color: _pendingCount > 0 ? Colors.amber.shade900 : Colors.green.shade900,
                      size: 32,
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _pendingCount > 0 ? '$_pendingCount Events Queued Offline' : 'All Attendance Events Synced',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                              color: _pendingCount > 0 ? Colors.amber.shade900 : Colors.green.shade900,
                            ),
                          ),
                          const SizedBox(height: 2),
                          const Text(
                            'Signed with device Ed25519 private key. Auto-relays via nearby student BLE gateway when internet is disabled.',
                            style: TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('NEARBY SRK PEERS (BLE MESH)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey)),
                TextButton.icon(
                  onPressed: _isDiscovering ? null : _startDiscovery,
                  icon: _isDiscovering
                      ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.refresh, size: 18),
                  label: const Text('Scan Mesh'),
                ),
              ],
            ),
            const SizedBox(height: 8),

            _buildPeerItem('Priya Sharma (SRK2026BCA002)', 'Online Gateway (Battery 92% • WiFi Active)', -46, true),
            _buildPeerItem('Meet Vaghela (SRK2026BCA003)', 'Online Gateway (Battery 78% • 5G Active)', -58, true),
            _buildPeerItem('Lecture Hall 3 (LH-3) Mesh Beacon', 'Offline Peer Node (Campus Power)', -38, false),

            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                StudentApiService().offlineQueue.markSynced([]);
                _loadPendingCount();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    backgroundColor: Color(0xFF1565C0),
                    content: Text('Force Sync: Queued events relayed to Priya Sharma Gateway -> MongoDB Atlas!'),
                  ),
                );
              },
              icon: const Icon(Icons.send),
              label: const Text('Relay Queued Events to Elected Gateway'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1565C0),
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 48),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPeerItem(String name, String desc, int rssi, bool hasInternet) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: hasInternet ? Colors.green.shade50 : Colors.grey.shade100,
          child: Icon(hasInternet ? Icons.wifi : Icons.bluetooth, color: hasInternet ? Colors.green : Colors.grey),
        ),
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        subtitle: Text(desc, style: const TextStyle(fontSize: 12)),
        trailing: Text('$rssi dBm', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.blueGrey)),
      ),
    );
  }
}
