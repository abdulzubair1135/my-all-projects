import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../core/theme.dart';
import '../../core/constants.dart';
import '../../providers/auth_provider.dart';
import '../../services/socket_service.dart';

class CampusChatMessage {
  final String id;
  final String fromUid;
  final String fromName;
  final String toUid;
  final String toName;
  final String message;
  final DateTime timestamp;
  final bool isMe;

  CampusChatMessage({
    required this.id,
    required this.fromUid,
    required this.fromName,
    required this.toUid,
    required this.toName,
    required this.message,
    required this.timestamp,
    required this.isMe,
  });
}

class CampusChatScreen extends ConsumerStatefulWidget {
  const CampusChatScreen({super.key});

  @override
  ConsumerState<CampusChatScreen> createState() => _CampusChatScreenState();
}

class _CampusChatScreenState extends ConsumerState<CampusChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  Map<String, String>? _selectedRecipient;
  String _activeFilter = 'ALL';
  String _searchQuery = '';

  final List<CampusChatMessage> _messages = [
    CampusChatMessage(
      id: 'm1',
      fromUid: 'SRK-ADM-001',
      fromName: 'Dr. Nirdesh Buch (Principal)',
      toUid: 'ALL',
      toName: 'All Campus Members',
      message: 'Welcome to SRK Institute live coordination channel.',
      timestamp: DateTime.now().subtract(const Duration(minutes: 45)),
      isMe: false,
    ),
    CampusChatMessage(
      id: 'm2',
      fromUid: 'SRK-FAC-101',
      fromName: 'Prof. Nirali Thakkar',
      toUid: 'ALL',
      toName: 'All Campus Members',
      message: 'CS-301 Lecture notes uploaded to portal.',
      timestamp: DateTime.now().subtract(const Duration(minutes: 20)),
      isMe: false,
    ),
  ];

  final List<String> _quickPhrases = [
    'Please report to Principal Cabin P-01',
    'Class is postponed by 10 minutes',
    'Please share today\'s lecture notes',
    'Arrived on campus',
    'Currently in lecture / laboratory',
    'Acknowledged. On my way.',
    'Available for consultation / discussion',
  ];

  @override
  void initState() {
    super.initState();
    _setupSocketListener();
  }

  void _setupSocketListener() {
    SocketService().on('campus_direct_message', (data) {
      if (!mounted || data == null) return;

      final currentUser = ref.read(authProvider).user;
      final fromUid = data['fromUid'] ?? 'SRK-FAC';
      final isMe = currentUser != null && (currentUser.uid == fromUid || currentUser.email == fromUid);

      if (!isMe) {
        setState(() {
          _messages.add(
            CampusChatMessage(
              id: data['id'] ?? 'msg_${DateTime.now().millisecondsSinceEpoch}',
              fromUid: fromUid,
              fromName: data['fromName'] ?? 'Faculty / Student',
              toUid: data['toUid'] ?? 'ALL',
              toName: data['toName'] ?? 'Campus',
              message: data['message'] ?? '',
              timestamp: DateTime.now(),
              isMe: false,
            ),
          );
        });
        _scrollToBottom();
      }
    });
  }

  void _sendMessage([String? customText]) {
    final text = (customText ?? _messageController.text).trim();
    if (text.isEmpty) return;

    final currentUser = ref.read(authProvider).user;
    final fromUid = currentUser?.uid ?? 'SRK-USR-01';
    final fromName = currentUser?.name ?? 'Campus Member';

    final targetUid = _selectedRecipient?['uid'] ?? 'ALL';
    final targetName = _selectedRecipient?['name'] ?? 'Campus Broadcast Channel';

    final newMsg = CampusChatMessage(
      id: 'msg_${DateTime.now().millisecondsSinceEpoch}',
      fromUid: fromUid,
      fromName: fromName,
      toUid: targetUid,
      toName: targetName,
      message: text,
      timestamp: DateTime.now(),
      isMe: true,
    );

    setState(() {
      _messages.add(newMsg);
      _messageController.clear();
    });

    // Broadcast over Socket.IO
    SocketService().emit('campus_direct_message', {
      'id': newMsg.id,
      'fromUid': fromUid,
      'fromName': fromName,
      'toUid': targetUid,
      'toName': targetName,
      'message': text,
      'timestamp': DateTime.now().toIso8601String(),
    });

    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent + 80,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _openRecipientSelector() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModalState) {
          final filtered = AppConstants.seedCampusUids.where((u) {
            final matchCategory = _activeFilter == 'ALL' ||
                (_activeFilter == 'ADMIN' && (u['role'] == 'ADMIN' || u['role'] == 'PRINCIPAL')) ||
                (_activeFilter == 'FACULTY' && u['role'] == 'FACULTY') ||
                (_activeFilter == 'STUDENT' && u['role'] == 'STUDENT');

            final matchSearch = _searchQuery.isEmpty ||
                u['name']!.toLowerCase().contains(_searchQuery.toLowerCase()) ||
                u['uid']!.toLowerCase().contains(_searchQuery.toLowerCase());

            return matchCategory && matchSearch;
          }).toList();

          return Container(
            height: MediaQuery.of(context).size.height * 0.75,
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
            ),
            child: Column(
              children: [
                Container(
                  margin: const EdgeInsets.only(top: 12),
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Select Recipient / Campus UID',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.primaryNavy),
                          ),
                          Text(
                            'Choose recipient for 1-to-1 secure direct messaging',
                            style: TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                        ],
                      ),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () => Navigator.pop(ctx),
                      ),
                    ],
                  ),
                ),
                // Search bar
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: 'Search by name or UID (e.g. SRK-FAC-101)...',
                      prefixIcon: const Icon(Icons.search, size: 20),
                      filled: true,
                      fillColor: Colors.grey.shade100,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                    ),
                    onChanged: (val) {
                      setModalState(() => _searchQuery = val);
                    },
                  ),
                ),
                // Filter Tabs
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 10, 20, 6),
                  child: Row(
                    children: [
                      _buildModalFilterChip('ALL', 'All', setModalState),
                      const SizedBox(width: 8),
                      _buildModalFilterChip('ADMIN', 'Admin (5)', setModalState),
                      const SizedBox(width: 8),
                      _buildModalFilterChip('FACULTY', 'Faculty (15)', setModalState),
                      const SizedBox(width: 8),
                      _buildModalFilterChip('STUDENT', 'Students (10)', setModalState),
                    ],
                  ),
                ),
                const Divider(),
                // All Broadcast Option
                ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: AppTheme.primaryNavy,
                    child: Icon(Icons.campaign_rounded, color: Colors.white, size: 20),
                  ),
                  title: const Text('Campus Broadcast Channel', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                  subtitle: const Text('Broadcasts message to all campus members', style: TextStyle(fontSize: 11)),
                  onTap: () {
                    setState(() => _selectedRecipient = null);
                    Navigator.pop(ctx);
                  },
                ),
                const Divider(height: 1),
                Expanded(
                  child: ListView.separated(
                    itemCount: filtered.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (ctx, i) {
                      final item = filtered[i];
                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor: item['role'] == 'FACULTY'
                              ? AppTheme.accentGold.withOpacity(0.2)
                              : (item['role'] == 'STUDENT' ? AppTheme.statusGreen.withOpacity(0.2) : Colors.purple.shade100),
                          child: Text(
                            item['name']!.substring(0, 1),
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: item['role'] == 'FACULTY' ? Colors.amber.shade900 : AppTheme.primaryNavy,
                            ),
                          ),
                        ),
                        title: Text(item['name']!, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                        subtitle: Text('${item['uid']} • ${item['title'] ?? item['role']}', style: const TextStyle(fontSize: 11)),
                        trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: Colors.grey),
                        onTap: () {
                          setState(() => _selectedRecipient = item);
                          Navigator.pop(ctx);
                        },
                      );
                    },
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildModalFilterChip(String key, String label, void Function(void Function()) setModalState) {
    final isSelected = _activeFilter == key;
    return GestureDetector(
      onTap: () {
        setModalState(() => _activeFilter = key);
        setState(() => _activeFilter = key);
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: isSelected ? AppTheme.primaryNavy : Colors.grey.shade200,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.bold,
            color: isSelected ? Colors.white : Colors.grey.shade700,
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final currentUser = ref.watch(authProvider).user;

    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(
        title: GestureDetector(
          onTap: _openRecipientSelector,
          child: Row(
            children: [
              CircleAvatar(
                radius: 16,
                backgroundColor: AppTheme.accentGold.withOpacity(0.3),
                child: Icon(
                  _selectedRecipient == null ? Icons.campaign_rounded : Icons.person_rounded,
                  size: 18,
                  color: Colors.white,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _selectedRecipient?['name'] ?? 'Campus Broadcast Channel',
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                      overflow: TextOverflow.ellipsis,
                    ),
                    Text(
                      _selectedRecipient == null
                          ? 'Tap to select specific Teacher / Student'
                          : 'UID: ${_selectedRecipient!['uid']}',
                      style: const TextStyle(fontSize: 10, color: AppTheme.accentGoldLight),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.arrow_drop_down, color: Colors.white),
            ],
          ),
        ),
      ),
      body: Column(
        children: [
          // Quick Action Phrases Bar
          Container(
            height: 42,
            margin: const EdgeInsets.symmetric(vertical: 6),
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: _quickPhrases.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (ctx, i) {
                final phrase = _quickPhrases[i];
                return ActionChip(
                  label: Text(phrase, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                  backgroundColor: Colors.white,
                  side: BorderSide(color: Colors.grey.shade300),
                  onPressed: () => _sendMessage(phrase),
                );
              },
            ),
          ),

          // Message Bubbles List
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
              itemCount: _messages.length,
              itemBuilder: (ctx, i) {
                final msg = _messages[i];
                return _buildMessageBubble(msg);
              },
            ),
          ),

          // Bottom Message Input
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: SafeArea(
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.contacts_rounded, color: AppTheme.primaryNavy),
                    tooltip: 'Select Recipient',
                    onPressed: _openRecipientSelector,
                  ),
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      textCapitalization: TextCapitalization.sentences,
                      decoration: InputDecoration(
                        hintText: _selectedRecipient == null
                            ? 'Message to all campus members...'
                            : 'Message ${_selectedRecipient!['name']}...',
                        hintStyle: TextStyle(fontSize: 13, color: Colors.grey.shade500),
                        filled: true,
                        fillColor: Colors.grey.shade100,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                      ),
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  CircleAvatar(
                    backgroundColor: AppTheme.primaryNavy,
                    child: IconButton(
                      icon: const Icon(Icons.send_rounded, color: AppTheme.accentGold, size: 18),
                      onPressed: () => _sendMessage(),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(CampusChatMessage msg) {
    final timeStr = DateFormat('hh:mm a').format(msg.timestamp);

    return Align(
      alignment: msg.isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.78),
        decoration: BoxDecoration(
          color: msg.isMe ? AppTheme.primaryNavy : Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(msg.isMe ? 16 : 2),
            bottomRight: Radius.circular(msg.isMe ? 2 : 16),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (!msg.isMe)
              Padding(
                padding: const EdgeInsets.only(bottom: 2),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      msg.fromName,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: AppTheme.secondaryNavy),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '(${msg.fromUid})',
                      style: TextStyle(fontSize: 9, color: Colors.grey.shade600),
                    ),
                  ],
                ),
              ),
            Text(
              msg.message,
              style: TextStyle(
                fontSize: 13,
                color: msg.isMe ? Colors.white : Colors.black87,
              ),
            ),
            const SizedBox(height: 3),
            Align(
              alignment: Alignment.bottomRight,
              child: Text(
                timeStr,
                style: TextStyle(
                  fontSize: 9,
                  color: msg.isMe ? Colors.white70 : Colors.grey.shade500,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
