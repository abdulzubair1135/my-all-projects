import * as EmpModel from '../models/employeeModel.js';

export const getEmployees = async (req, res, next) => {
  try {
    const employees = await EmpModel.getAll();
    res.json({ success: true, message: 'Employees retrieved', data: employees });
  } catch (err) { next(err); }
};

export const getEmployee = async (req, res, next) => {
  try {
    const emp = await EmpModel.getById(req.params.id);
    if (!emp) return res.status(404).json({ success: false, message: 'Employee not found' });
    res.json({ success: true, message: 'Employee retrieved', data: emp });
  } catch (err) { next(err); }
};

export const createEmployee = async (req, res, next) => {
  try {
    const id = await EmpModel.create(req.body);
    res.status(201).json({ success: true, message: 'Employee created', data: { id, ...req.body } });
  } catch (err) { next(err); }
};

export const updateEmployee = async (req, res, next) => {
  try {
    const affected = await EmpModel.update(req.params.id, req.body);
    if (!affected) return res.status(404).json({ success: false, message: 'Employee not found' });
    res.json({ success: true, message: 'Employee updated', data: { id: req.params.id, ...req.body } });
  } catch (err) { next(err); }
};

export const deleteEmployee = async (req, res, next) => {
  try {
    const affected = await EmpModel.remove(req.params.id);
    if (!affected) return res.status(404).json({ success: false, message: 'Employee not found' });
    res.json({ success: true, message: 'Employee deleted' });
  } catch (err) { next(err); }
};
