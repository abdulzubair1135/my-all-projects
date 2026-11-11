import * as InvModel from '../models/inventoryModel.js';

export const getItems = async (req, res, next) => {
  try {
    const items = await InvModel.getAll();
    res.json({ success: true, message: 'Inventory items retrieved', data: items });
  } catch (err) { next(err); }
};

export const getItem = async (req, res, next) => {
  try {
    const item = await InvModel.getById(req.params.id);
    if (!item) return res.status(404).json({ success: false, message: 'Item not found' });
    res.json({ success: true, message: 'Item retrieved', data: item });
  } catch (err) { next(err); }
};

export const createItem = async (req, res, next) => {
  try {
    const id = await InvModel.create(req.body);
    res.status(201).json({ success: true, message: 'Item created', data: { id, ...req.body } });
  } catch (err) { next(err); }
};

export const updateItem = async (req, res, next) => {
  try {
    const affected = await InvModel.update(req.params.id, req.body);
    if (!affected) return res.status(404).json({ success: false, message: 'Item not found' });
    res.json({ success: true, message: 'Item updated', data: { id: req.params.id, ...req.body } });
  } catch (err) { next(err); }
};

export const deleteItem = async (req, res, next) => {
  try {
    const affected = await InvModel.remove(req.params.id);
    if (!affected) return res.status(404).json({ success: false, message: 'Item not found' });
    res.json({ success: true, message: 'Item deleted' });
  } catch (err) { next(err); }
};
