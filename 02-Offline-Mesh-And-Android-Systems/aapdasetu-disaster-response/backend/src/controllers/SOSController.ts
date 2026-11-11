import { Request, Response } from 'express';
import { randomUUID } from 'crypto';
import { SOSEvent } from '../models/SOSEvent.js';
import { SOSRelay } from '../models/SOSRelay.js';
import { SOSAssignment } from '../models/SOSAssignment.js';
import { RescueTeam } from '../models/RescueTeam.js';
import { AuthRequest, logAudit } from '../middleware/auth.js';
import { broadcastEvent } from '../sockets/socket.js';
import { sendEmergencyPushNotification } from '../services/firebaseService.js';

export const createSOS = async (req: AuthRequest, res: Response): Promise<void> => {
  try {
    const {
      eventId,
      originDeviceId,
      type,
      severity,
      description,
      peopleCount,
      injuredCount,
      latitude,
      longitude,
      accuracy,
      addressText,
      source
    } = req.body;

    if (latitude === undefined || longitude === undefined) {
      res.status(400).json({
        success: false,
        error: { code: 'LOCATION_REQUIRED', message: 'Valid GPS latitude and longitude are required.' }
      });
      return;
    }

    const assignedEventId = eventId || randomUUID();
    const assignedDeviceId = originDeviceId || req.deviceId || 'DEVICE_UNKNOWN';

    const existing = await SOSEvent.findOne({ eventId: assignedEventId });
    if (existing) {
      res.json({
        success: true,
        message: 'SOS event already recorded.',
        data: existing,
        serverSynced: true
      });
      return;
    }

    const sos = await SOSEvent.create({
      eventId: assignedEventId,
      userId: req.user?._id,
      userName: req.user?.name || req.body.userName || 'Citizen',
      userPhone: req.user?.phone || req.body.userPhone || '9876543210',
      originDeviceId: assignedDeviceId,
      type: type || 'MEDICAL',
      severity: severity || 'HIGH',
      description: description || '',
      peopleCount: Number(peopleCount) || 1,
      injuredCount: Number(injuredCount) || 0,
      location: {
        type: 'Point',
        coordinates: [Number(longitude), Number(latitude)]
      },
      locationAccuracy: Number(accuracy) || 10,
      addressText: addressText || '',
      status: 'RECEIVED',
      source: source || 'ONLINE',
      hopCount: 0,
      relayPath: []
    });

    broadcastEvent('sos:new', sos);
    broadcastEvent('sos:new', sos, 'gov');
    broadcastEvent('sos:new', sos, 'admin');
    broadcastEvent('sos:new', sos, 'ngo');
    broadcastEvent('sos:new', sos, 'rescue');
    broadcastEvent('sos:alert', sos);
    sendEmergencyPushNotification(
      `🚨 EMERGENCY SOS: ${sos.type} Beacon`,
      `${sos.userName}: ${sos.description || 'Immediate emergency rescue required!'}`,
      { eventId: sos.eventId, type: sos.type, severity: sos.severity }
    ).catch(() => {});
    await logAudit(req, 'CREATE_SOS', 'SOSEvent', sos._id.toString(), { eventId: assignedEventId, source: sos.source });

    res.status(201).json({
      success: true,
      message: 'SOS event successfully created and dispatched.',
      data: sos,
      serverSynced: true
    });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
};

export const getAllSOS = async (req: Request, res: Response): Promise<void> => {
  try {
    const { status, severity, source, limit = 100, page = 1 } = req.query;
    const filter: any = {};

    if (status) filter.status = status;
    if (severity) filter.severity = severity;
    if (source) filter.source = source;

    const skip = (Number(page) - 1) * Number(limit);
    const sosList = await SOSEvent.find(filter)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(Number(limit))
      .populate('assignedTeamId', 'name contactNumber vehicle status');

    const total = await SOSEvent.countDocuments(filter);

    res.json({
      success: true,
      data: sosList,
      pagination: { total, page: Number(page), limit: Number(limit) }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
};

export const getSOSById = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const sos = await SOSEvent.findOne({ $or: [{ _id: id }, { eventId: id }] })
      .populate('assignedTeamId')
      .populate('verifiedBy', 'name phone email role');

    if (!sos) {
      res.status(404).json({ success: false, error: { code: 'NOT_FOUND', message: 'SOS record not found.' } });
      return;
    }

    const relays = await SOSRelay.find({ eventId: sos.eventId }).sort({ receivedAt: 1 });
    const assignments = await SOSAssignment.find({ sosId: sos._id }).sort({ assignedAt: -1 });

    res.json({
      success: true,
      data: { sos, relays, assignments }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
};

export const updateStatus = async (req: AuthRequest, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { status, notes } = req.body;

    const validStatuses = ['CREATED', 'RECEIVED', 'VERIFIED', 'ASSIGNED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED', 'RESOLVED', 'CANCELLED'];
    if (!validStatuses.includes(status)) {
      res.status(400).json({ success: false, error: { code: 'INVALID_STATUS', message: `Invalid status: ${status}` } });
      return;
    }

    const sos = await SOSEvent.findOne({ $or: [{ _id: id }, { eventId: id }] });
    if (!sos) {
      res.status(404).json({ success: false, error: { code: 'NOT_FOUND', message: 'SOS record not found.' } });
      return;
    }

    sos.status = status;
    if (status === 'RESOLVED') {
      sos.resolvedAt = new Date();
      if (sos.assignedTeamId) {
        await RescueTeam.findByIdAndUpdate(sos.assignedTeamId, { status: 'AVAILABLE', currentAssignment: null });
      }
    }
    await sos.save();

    if (notes || status) {
      await SOSAssignment.findOneAndUpdate(
        { sosId: sos._id, status: { $ne: 'RESOLVED' } },
        {
          status,
          ...(status === 'ACCEPTED' ? { acceptedAt: new Date() } : {}),
          ...(status === 'EN_ROUTE' ? { enRouteAt: new Date() } : {}),
          ...(status === 'ARRIVED' ? { arrivedAt: new Date() } : {}),
          ...(status === 'RESOLVED' ? { resolvedAt: new Date() } : {}),
          ...(notes ? { notes } : {})
        }
      );
    }

    broadcastEvent('sos:status_changed', { eventId: sos.eventId, sosId: sos._id, status, resolvedAt: sos.resolvedAt });
    await logAudit(req, 'UPDATE_SOS_STATUS', 'SOSEvent', sos._id.toString(), { status, notes });

    res.json({ success: true, message: `Status updated to ${status}`, data: sos });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
};

export const verifySOS = async (req: AuthRequest, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const sos = await SOSEvent.findOne({ $or: [{ _id: id }, { eventId: id }] });
    if (!sos) {
      res.status(404).json({ success: false, error: { code: 'NOT_FOUND', message: 'SOS record not found.' } });
      return;
    }

    sos.status = 'VERIFIED';
    sos.verifiedBy = req.user?._id;
    await sos.save();

    broadcastEvent('sos:verified', { eventId: sos.eventId, sosId: sos._id, verifiedBy: req.user?.name });
    await logAudit(req, 'VERIFY_SOS', 'SOSEvent', sos._id.toString());

    res.json({ success: true, message: 'SOS successfully verified by authority.', data: sos });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
};

export const assignRescueTeam = async (req: AuthRequest, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { rescueTeamId, notes } = req.body;

    if (!rescueTeamId) {
      res.status(400).json({ success: false, error: { code: 'TEAM_REQUIRED', message: 'rescueTeamId is required.' } });
      return;
    }

    const [sos, team] = await Promise.all([
      SOSEvent.findOne({ $or: [{ _id: id }, { eventId: id }] }),
      RescueTeam.findById(rescueTeamId)
    ]);

    if (!sos) {
      res.status(404).json({ success: false, error: { code: 'NOT_FOUND', message: 'SOS record not found.' } });
      return;
    }

    if (!team) {
      res.status(404).json({ success: false, error: { code: 'TEAM_NOT_FOUND', message: 'Rescue team not found.' } });
      return;
    }

    sos.status = 'ASSIGNED';
    sos.assignedTeamId = team._id as any;
    sos.assignedTeamName = team.name;
    await sos.save();

    team.status = 'ASSIGNED';
    team.currentAssignment = sos._id as any;
    await team.save();

    const assignment = await SOSAssignment.create({
      sosId: sos._id,
      eventId: sos.eventId,
      rescueTeamId: team._id,
      assignedBy: req.user?._id,
      status: 'ASSIGNED',
      notes
    });

    broadcastEvent('sos:assigned', { sos, team, assignment }, 'gov');
    broadcastEvent('sos:assigned', { sos, team, assignment }, 'rescue');
    broadcastEvent('sos:assigned', { sos, team, assignment }, `team:${team._id.toString()}`);

    await logAudit(req, 'ASSIGN_RESCUE', 'SOSEvent', sos._id.toString(), { teamId: team._id, teamName: team.name });

    res.json({
      success: true,
      message: `Assigned team ${team.name} to SOS ${sos.eventId}`,
      data: { sos, assignment }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
};

export const getSOSStats = async (req: Request, res: Response): Promise<void> => {
  try {
    const [totalActive, critical, high, assigned, resolved, offlineBle, allEvents] = await Promise.all([
      SOSEvent.countDocuments({ status: { $nin: ['RESOLVED', 'CANCELLED'] } }),
      SOSEvent.countDocuments({ severity: 'CRITICAL', status: { $nin: ['RESOLVED', 'CANCELLED'] } }),
      SOSEvent.countDocuments({ severity: 'HIGH', status: { $nin: ['RESOLVED', 'CANCELLED'] } }),
      SOSEvent.countDocuments({ status: { $in: ['ASSIGNED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED'] } }),
      SOSEvent.countDocuments({ status: 'RESOLVED' }),
      SOSEvent.countDocuments({ source: { $in: ['OFFLINE_BLE', 'BLE_RELAY'] } }),
      SOSEvent.find({ status: 'RESOLVED', resolvedAt: { $exists: true } }).select('createdAt resolvedAt').limit(50)
    ]);

    let avgResponseTimeMinutes = 0;
    if (allEvents.length > 0) {
      const totalMinutes = allEvents.reduce((acc, curr) => {
        if (curr.resolvedAt && curr.createdAt) {
          return acc + (new Date(curr.resolvedAt).getTime() - new Date(curr.createdAt).getTime()) / (1000 * 60);
        }
        return acc;
      }, 0);
      avgResponseTimeMinutes = Math.round((totalMinutes / allEvents.length) * 10) / 10;
    }

    res.json({
      success: true,
      data: {
        totalActive,
        critical,
        highPriority: high,
        assigned,
        resolved,
        offlineRelayed: offlineBle,
        averageResponseTimeMinutes: avgResponseTimeMinutes
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
};
