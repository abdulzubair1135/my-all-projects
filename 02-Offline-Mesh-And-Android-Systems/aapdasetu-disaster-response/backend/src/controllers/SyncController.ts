import { Request, Response } from 'express';
import { SOSEvent } from '../models/SOSEvent.js';
import { SOSRelay } from '../models/SOSRelay.js';
import { EmergencyMessage } from '../models/EmergencyMessage.js';
import { broadcastEvent } from '../sockets/socket.js';

export const syncBatch = async (req: Request, res: Response): Promise<void> => {
  try {
    const { sosEvents = [], messages = [], deviceId } = req.body;
    const acks: Array<{ eventId: string; status: string; syncedAt: Date }> = [];

    // 1. Process offline stored SOS events
    for (const item of sosEvents) {
      if (!item.eventId) continue;

      let existing = await SOSEvent.findOne({ eventId: item.eventId });
      if (!existing) {
        existing = await SOSEvent.create({
          eventId: item.eventId,
          originDeviceId: item.originDeviceId || deviceId || 'OFFLINE_NODE',
          type: item.type || 'MEDICAL',
          severity: item.severity || 'HIGH',
          description: item.description || '',
          peopleCount: Number(item.peopleCount) || 1,
          injuredCount: Number(item.injuredCount) || 0,
          location: {
            type: 'Point',
            coordinates: [Number(item.longitude || 0), Number(item.latitude || 0)]
          },
          locationAccuracy: Number(item.accuracy) || 10,
          addressText: item.addressText || '',
          status: 'RECEIVED',
          source: 'OFFLINE_BLE',
          hopCount: Number(item.hopCount) || 0,
          relayPath: item.relayPath || [],
          createdAt: item.createdAt ? new Date(item.createdAt) : new Date()
        });

        broadcastEvent('sos:new', existing, 'gov');
        broadcastEvent('sos:new', existing, 'rescue');
      }

      acks.push({
        eventId: item.eventId,
        status: 'SYNCED',
        syncedAt: new Date()
      });
    }

    // 2. Process emergency chat messages
    for (const msg of messages) {
      if (!msg.messageId) continue;
      const existingMsg = await EmergencyMessage.findOne({ messageId: msg.messageId });
      if (!existingMsg) {
        await EmergencyMessage.create({
          messageId: msg.messageId,
          senderDeviceId: msg.senderDeviceId || deviceId || 'UNKNOWN',
          receiverDeviceId: msg.receiverDeviceId || 'ALL',
          type: msg.type || 'CHAT',
          content: msg.content || '',
          location: {
            type: 'Point',
            coordinates: [Number(msg.longitude || 0), Number(msg.latitude || 0)]
          },
          timestamp: Number(msg.timestamp) || Date.now(),
          ttl: Number(msg.ttl) || 5,
          hopCount: Number(msg.hopCount) || 0,
          source: 'OFFLINE_BLE',
          status: 'SYNCED',
          syncedAt: new Date()
        });
      }
    }

    res.json({
      success: true,
      message: `Batch synchronized successfully. Processed ${sosEvents.length} SOS and ${messages.length} messages.`,
      acks,
      serverSynced: true
    });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
};

export const relayUpload = async (req: Request, res: Response): Promise<void> => {
  try {
    const {
      eventId,
      originDeviceId,
      relayDeviceId,
      fromDeviceId,
      hopCount = 1,
      type,
      severity,
      description,
      peopleCount,
      injuredCount,
      latitude,
      longitude,
      accuracy,
      relayPath = []
    } = req.body;

    if (!eventId || latitude === undefined || longitude === undefined) {
      res.status(400).json({
        success: false,
        error: { code: 'INVALID_PACKET', message: 'eventId, latitude, and longitude are required for SOS relay.' }
      });
      return;
    }

    await SOSRelay.create({
      eventId,
      originDeviceId: originDeviceId || 'UNKNOWN',
      relayDeviceId: relayDeviceId || 'GATEWAY_NODE',
      fromDeviceId: fromDeviceId || 'UNKNOWN',
      hopCount: Number(hopCount),
      receivedAt: new Date(),
      networkAvailable: true,
      uploadedToServer: true
    });

    let sos = await SOSEvent.findOne({ eventId });
    if (!sos) {
      sos = await SOSEvent.create({
        eventId,
        originDeviceId: originDeviceId || 'ORIGIN_NODE',
        type: type || 'MEDICAL',
        severity: severity || 'CRITICAL',
        description: description || '',
        peopleCount: Number(peopleCount) || 1,
        injuredCount: Number(injuredCount) || 0,
        location: {
          type: 'Point',
          coordinates: [Number(longitude), Number(latitude)]
        },
        locationAccuracy: Number(accuracy) || 15,
        status: 'RECEIVED',
        source: 'BLE_RELAY',
        hopCount: Number(hopCount),
        relayPath: [...relayPath, relayDeviceId || 'GATEWAY']
      });

      broadcastEvent('sos:new', sos, 'gov');
      broadcastEvent('sos:new', sos, 'rescue');
    } else {
      if (!sos.relayPath.includes(relayDeviceId)) {
        sos.relayPath.push(relayDeviceId);
        await sos.save();
      }
    }

    res.json({
      success: true,
      message: 'SOS Relay successfully recorded by gateway server.',
      eventId,
      source: 'BLE_RELAY',
      hopCount,
      serverSynced: true
    });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
};
