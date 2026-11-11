/**
 * Franchise Controller
 */

import Franchise from '../03-Models/Franchise.js';

export const getFranchises = async (req, res, next) => {
  try {
    const franchises = await Franchise.findAll();
    return res.status(200).json({
      success: true,
      message: 'Franchises fetched successfully',
      data: franchises
    });
  } catch (error) {
    next(error);
  }
};

export const getFranchiseById = async (req, res, next) => {
  try {
    const { id } = req.params;
    const franchise = await Franchise.findById(id);

    if (!franchise) {
      return res.status(404).json({ success: false, message: 'Franchise not found', error: 'NOT_FOUND' });
    }

    return res.status(200).json({
      success: true,
      message: 'Franchise details fetched successfully',
      data: franchise
    });
  } catch (error) {
    next(error);
  }
};

export const createFranchise = async (req, res, next) => {
  try {
    const { name, code, location, contact_number } = req.body;

    const existingCode = await Franchise.findByCode(code);
    if (existingCode) {
      return res.status(400).json({ success: false, message: 'Franchise code already exists', error: 'CODE_EXISTS' });
    }

    const newFranchise = await Franchise.create({ name, code, location, contact_number });
    return res.status(201).json({
      success: true,
      message: 'Franchise created successfully',
      data: newFranchise
    });
  } catch (error) {
    next(error);
  }
};
