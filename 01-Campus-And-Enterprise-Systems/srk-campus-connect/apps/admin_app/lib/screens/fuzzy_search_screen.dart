import 'package:flutter/material.dart';
import '../services/admin_api_service.dart';

class FuzzySearchScreen extends StatefulWidget {
  const FuzzySearchScreen({super.key});

  @override
  State<FuzzySearchScreen> createState() => _FuzzySearchScreenState();
}

class _FuzzySearchScreenState extends State<FuzzySearchScreen> {
  final _searchController = TextEditingController();
  List<dynamic> _results = [];
  bool _isSearching = false;

  @override
  void initState() {
    super.initState();
    _performSearch('');
  }

  void _performSearch(String q) async {
    setState(() => _isSearching = true);
    final data = await AdminApiService().searchCampus(q);
    setState(() {
      _results = data;
      _isSearching = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Campus Global Search', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF283593),
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              onChanged: _performSearch,
              decoration: InputDecoration(
                hintText: 'Search Faculty, Students, Classrooms, Subjects...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _performSearch('');
                        },
                      )
                    : null,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
          const Divider(height: 1),

          Expanded(
            child: _isSearching
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: _results.length,
                    itemBuilder: (ctx, idx) {
                      final item = _results[idx];
                      final type = item['type'] as String;

                      IconData icon = Icons.person;
                      Color col = Colors.blue;
                      if (type == 'ROOM') {
                        icon = Icons.meeting_room;
                        col = Colors.amber.shade900;
                      } else if (type == 'STUDENT') {
                        icon = Icons.school;
                        col = Colors.green;
                      }

                      return Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: col.withAlpha(30),
                            child: Icon(icon, color: col),
                          ),
                          title: Text(item['title'], style: const TextStyle(fontWeight: FontWeight.bold)),
                          subtitle: Text(item['subtitle'], style: const TextStyle(fontSize: 12)),
                          trailing: const Icon(Icons.chevron_right, size: 20),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
