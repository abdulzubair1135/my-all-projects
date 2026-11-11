import 'package:flutter/material.dart';
import '../services/admin_api_service.dart';

class AuditTrailScreen extends StatefulWidget {
  const AuditTrailScreen({super.key});

  @override
  State<AuditTrailScreen> createState() => _AuditTrailScreenState();
}

class _AuditTrailScreenState extends State<AuditTrailScreen> {
  List<dynamic> _logs = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() async {
    final list = await AdminApiService().getAuditLogs();
    setState(() {
      _logs = list;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('System Audit Trail', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF283593),
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: _logs.length,
              itemBuilder: (ctx, idx) {
                final log = _logs[idx];
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    leading: const CircleAvatar(
                      backgroundColor: Color(0xFFE8EAF6),
                      child: Icon(Icons.security, color: Color(0xFF283593), size: 20),
                    ),
                    title: Text(log['action'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                    subtitle: Text('Actor: ${log['actor']} • Resource: ${log['resource']}', style: const TextStyle(fontSize: 12)),
                    trailing: Text(log['time'], style: const TextStyle(color: Colors.grey, fontSize: 11)),
                  ),
                );
              },
            ),
    );
  }
}
