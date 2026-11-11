import { Request, Response } from 'express';
import mongoose from 'mongoose';
import { Directive } from '../models/Directive.js';
import { getIO } from '../sockets/socket.js';
import crypto from 'crypto';

const findDirectiveById = async (id: string) => {
  if (mongoose.Types.ObjectId.isValid(id)) {
    return await Directive.findOne({ $or: [{ _id: id }, { directiveId: id }] });
  }
  return await Directive.findOne({ directiveId: id });
};

export const getDirectives = async (req: Request, res: Response): Promise<void> => {
  try {
    const { ngo, status, priority } = req.query;
    const filter: any = {};
    if (ngo) filter.assignedNgoName = new RegExp(String(ngo), 'i');
    if (status) filter.status = status;
    if (priority) filter.priority = priority;

    const directives = await Directive.find(filter).sort({ createdAt: -1 });
    res.json({ success: true, count: directives.length, data: directives });
  } catch (error: any) {
    res.status(500).json({ success: false, error: { message: error.message } });
  }
};

export const createDirective = async (req: Request, res: Response): Promise<void> => {
  try {
    const {
      title,
      category,
      quantity,
      unit,
      targetZone,
      assignedNgoName,
      targetAgency,
      targetShelter,
      location,
      priority,
      instructions,
      description
    } = req.body;

    const finalNgo = assignedNgoName || targetAgency || 'Red Cross Gujarat';
    const finalZone = targetZone || targetShelter || location?.address || 'Paldi Relief Camp';

    if (!title || !category || !quantity) {
      res.status(400).json({ success: false, error: { message: 'Missing required directive fields (title, category, quantity)' } });
      return;
    }

    const directive = await Directive.create({
      directiveId: 'DIR-' + crypto.randomUUID().substring(0, 8).toUpperCase(),
      title,
      category,
      quantity: Number(quantity) || 100,
      unit: unit || 'units',
      targetZone: finalZone,
      assignedNgoName: finalNgo,
      priority: priority || 'HIGH',
      status: 'PENDING',
      instructions: instructions || description || '',
      issuedAt: new Date()
    });

    try {
      const io = getIO();
      io.emit('directive:new', directive);
      io.to('ngo').emit('directive:new', directive);
    } catch (ignored) {}

    res.status(201).json({ success: true, message: 'Government directive issued successfully to NGO.', data: directive });
  } catch (error: any) {
    res.status(500).json({ success: false, error: { message: error.message } });
  }
};

export const updateDirectiveStatus = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { status, fulfilledAt } = req.body;

    const directive = await findDirectiveById(id);
    if (!directive) {
      res.status(404).json({ success: false, error: { message: 'Directive not found' } });
      return;
    }

    directive.status = status;
    if (status === 'FULFILLED') {
      directive.fulfilledAt = fulfilledAt ? new Date(fulfilledAt) : new Date();
    }
    await directive.save();

    try {
      const io = getIO();
      io.emit('directive:update', directive);
    } catch (ignored) {}

    res.json({ success: true, message: 'Directive status updated.', data: directive });
  } catch (error: any) {
    res.status(500).json({ success: false, error: { message: error.message } });
  }
};

export const requestStockShortage = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { missingItems, requestedQuantity, notes } = req.body;

    const directive = await findDirectiveById(id);
    if (!directive) {
      res.status(404).json({ success: false, error: { message: 'Directive not found' } });
      return;
    }

    directive.status = 'CRITICAL_STOCK_SHORTAGE';
    directive.stockShortageDetails = {
      reportedAt: new Date(),
      missingItems: missingItems || directive.category,
      requestedQuantity: Number(requestedQuantity) || directive.quantity,
      notes: notes || ''
    };
    await directive.save();

    try {
      const io = getIO();
      io.emit('directive:stock-requested', {
        directiveId: directive.directiveId,
        ngoName: directive.assignedNgoName,
        shortage: directive.stockShortageDetails,
        directive
      });
      io.to('gov').emit('directive:stock-requested', directive);
    } catch (ignored) {}

    res.json({ 
      success: true, 
      message: 'Stock shortage reported! Requisition alert sent to State Disaster Command.', 
      data: directive 
    });
  } catch (error: any) {
    res.status(500).json({ success: false, error: { message: error.message } });
  }
};

export const replenishStock = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { note } = req.body;

    const directive = await findDirectiveById(id);
    if (!directive) {
      res.status(404).json({ success: false, error: { message: 'Directive not found' } });
      return;
    }

    directive.status = 'IN_TRANSIT';
    directive.govtResponse = {
      replenishedAt: new Date(),
      note: note || 'Government Emergency Supply Depot dispatched replenishment convoys.'
    };
    await directive.save();

    try {
      const io = getIO();
      io.emit('directive:replenished', directive);
    } catch (ignored) {}

    res.json({ 
      success: true, 
      message: 'Government replenishment confirmed. Stock dispatched to NGO relief depot.', 
      data: directive 
    });
  } catch (error: any) {
    res.status(500).json({ success: false, error: { message: error.message } });
  }
};
