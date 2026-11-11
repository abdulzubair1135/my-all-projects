import 'dart:async';
import '../models/presence_event_model.dart';

enum GatewayStatus {
  online('ONLINE'),
  offline('OFFLINE'),
  relaying('RELAYING');

  final String value;
  const GatewayStatus(this.value);
}

class PeerDevice {
  final String deviceId;
  final String deviceName;
  final bool hasInternet;
  final int batteryLevel; // 0 - 100
  final int signalStrengthRssi; // dBm
  final DateTime lastSeen;

  PeerDevice({
    required this.deviceId,
    required this.deviceName,
    required this.hasInternet,
    required this.batteryLevel,
    required this.signalStrengthRssi,
    DateTime? lastSeen,
  }) : lastSeen = lastSeen ?? DateTime.now();

  /// Gateway suitability score based on Internet availability, battery level and signal strength
  double get gatewayScore {
    if (!hasInternet) return 0.0;
    // Score based on battery (50%) + signal strength (50%)
    final batteryScore = batteryLevel / 100.0;
    final normalizedRssi = ((signalStrengthRssi + 100).clamp(0, 100)) / 100.0;
    return (batteryScore * 0.5) + (normalizedRssi * 0.5);
  }
}

abstract class IP2PTransport {
  Future<void> startAdvertising({required String deviceId, required bool hasInternet});
  Future<void> stopAdvertising();
  Future<void> startDiscovery();
  Future<void> stopDiscovery();

  Stream<List<PeerDevice>> get discoveredPeersStream;

  /// Elect the best available gateway among discovered peers
  PeerDevice? electGateway(List<PeerDevice> peers) {
    final eligibleGateways = peers.where((p) => p.hasInternet).toList();
    if (eligibleGateways.isEmpty) return null;

    eligibleGateways.sort((a, b) => b.gatewayScore.compareTo(a.gatewayScore));
    return eligibleGateways.first;
  }

  /// Forward a batch of encrypted/signed presence events to elected gateway peer
  Future<bool> forwardEventsToPeer({
    required PeerDevice targetPeer,
    required List<PresenceEventModel> events,
  });

  /// Receive forwarded events from nearby peers when acting as Gateway
  Stream<List<PresenceEventModel>> get incomingEventsStream;
}
