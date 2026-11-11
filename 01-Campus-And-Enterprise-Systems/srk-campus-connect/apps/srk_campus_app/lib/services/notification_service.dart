import 'dart:async';
import 'package:flutter/material.dart';

class CampusNotificationService {
  static final CampusNotificationService _instance = CampusNotificationService._internal();
  factory CampusNotificationService() => _instance;

  CampusNotificationService._internal();

  final _notificationStreamController = StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get onNotification => _notificationStreamController.stream;

  void triggerUrgentSummon({
    required String callerName,
    required String location,
    required String reason,
    required String meetingId,
  }) {
    _notificationStreamController.add({
      'type': 'URGENT_CABIN_CALL',
      'title': 'URGENT: Principal Cabin Summon',
      'body': '$callerName has summoned you to $location.',
      'caller': callerName,
      'location': location,
      'reason': reason,
      'meetingId': meetingId,
      'timestamp': DateTime.now(),
    });
  }

  void triggerBroadcast({
    required String title,
    required String message,
  }) {
    _notificationStreamController.add({
      'type': 'CAMPUS_BROADCAST',
      'title': title,
      'body': message,
      'timestamp': DateTime.now(),
    });
  }
}
