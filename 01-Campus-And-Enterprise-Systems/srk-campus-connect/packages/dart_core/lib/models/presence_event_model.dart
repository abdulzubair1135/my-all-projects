import 'enums.dart';

class PresenceEventModel {
  final String eventId;
  final String userId;
  final String deviceId;
  final String sessionId;
  final PresenceSource source;
  final double confidence;
  final int timestamp;
  final String signature;
  final String? gatewayDeviceId;
  final Map<String, dynamic> payload;

  PresenceEventModel({
    required this.eventId,
    required this.userId,
    required this.deviceId,
    required this.sessionId,
    required this.source,
    required this.confidence,
    required this.timestamp,
    required this.signature,
    this.gatewayDeviceId,
    this.payload = const {},
  });

  Map<String, dynamic> toJson() {
    return {
      'eventId': eventId,
      'userId': userId,
      'deviceId': deviceId,
      'sessionId': sessionId,
      'source': source.value,
      'confidence': confidence,
      'timestamp': timestamp,
      'signature': signature,
      if (gatewayDeviceId != null) 'gatewayDeviceId': gatewayDeviceId,
      'payload': payload,
    };
  }

  factory PresenceEventModel.fromJson(Map<String, dynamic> json) {
    return PresenceEventModel(
      eventId: json['eventId'] as String,
      userId: json['userId'] as String,
      deviceId: json['deviceId'] as String,
      sessionId: json['sessionId'] as String,
      source: PresenceSource.fromString(json['source'] as String),
      confidence: (json['confidence'] as num).toDouble(),
      timestamp: json['timestamp'] as int,
      signature: json['signature'] as String,
      gatewayDeviceId: json['gatewayDeviceId'] as String?,
      payload: (json['payload'] as Map<String, dynamic>?) ?? {},
    );
  }
}
