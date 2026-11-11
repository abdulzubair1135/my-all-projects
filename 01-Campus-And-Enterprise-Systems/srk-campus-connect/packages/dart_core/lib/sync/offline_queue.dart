import 'dart:async';
import '../models/enums.dart';
import '../models/presence_event_model.dart';

class QueueItem {
  final PresenceEventModel event;
  SyncStatus status;
  int retryCount;
  DateTime createdAt;
  DateTime lastAttempt;
  String? errorMessage;

  QueueItem({
    required this.event,
    this.status = SyncStatus.pending,
    this.retryCount = 0,
    DateTime? createdAt,
    DateTime? lastAttempt,
    this.errorMessage,
  })  : createdAt = createdAt ?? DateTime.now(),
        lastAttempt = lastAttempt ?? DateTime.now();

  Map<String, dynamic> toMap() {
    return {
      'eventId': event.eventId,
      'eventJson': event.toJson(),
      'status': status.value,
      'retryCount': retryCount,
      'createdAt': createdAt.toIso8601String(),
      'lastAttempt': lastAttempt.toIso8601String(),
      'errorMessage': errorMessage,
    };
  }
}

abstract class IOfflineQueue {
  Future<void> enqueue(PresenceEventModel event);
  Future<List<QueueItem>> getPendingEvents({int limit = 50});
  Future<void> markSynced(List<String> eventIds);
  Future<void> markFailed(String eventId, String reason);
  Future<int> getPendingCount();
}

class InMemoryOfflineQueue implements IOfflineQueue {
  final List<QueueItem> _items = [];

  @override
  Future<void> enqueue(PresenceEventModel event) async {
    final existingIndex = _items.indexWhere((item) => item.event.eventId == event.eventId);
    if (existingIndex >= 0) return; // Prevent duplicate local queueing
    _items.add(QueueItem(event: event));
  }

  @override
  Future<List<QueueItem>> getPendingEvents({int limit = 50}) async {
    return _items
        .where((item) => item.status == SyncStatus.pending || item.status == SyncStatus.failed)
        .take(limit)
        .toList();
  }

  @override
  Future<void> markSynced(List<String> eventIds) async {
    for (final id in eventIds) {
      final item = _items.firstWhere((i) => i.event.eventId == id, orElse: () => _items.first);
      if (item.event.eventId == id) {
        item.status = SyncStatus.synced;
      }
    }
  }

  @override
  Future<void> markFailed(String eventId, String reason) async {
    final item = _items.firstWhere((i) => i.event.eventId == eventId, orElse: () => _items.first);
    if (item.event.eventId == eventId) {
      item.status = SyncStatus.failed;
      item.retryCount += 1;
      item.errorMessage = reason;
      item.lastAttempt = DateTime.now();
    }
  }

  @override
  Future<int> getPendingCount() async {
    return _items.where((item) => item.status == SyncStatus.pending || item.status == SyncStatus.failed).length;
  }
}
