/**
 * User Controller
 * Express Request/Response handle karta hai and Model methods call karta hai.
 */

import { validationResult } from 'express-validator';
import UserModel from '../models/User.js';
import { sendSuccess, sendError } from '../utils/response.js';

// GET /api/users - Read All Users
export const getAllUsers = async (req, res, next) => {
  try {
    const users = await UserModel.findAll();
    return sendSuccess(res, 'Users fetched successfully', users, 200);
  } catch (error) {
    next(error);
  }
};

// GET /api/users/:id - Read Single User
export const getUserById = async (req, res, next) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return sendError(res, 'Validation failed', errors.array(), 400);
    }

    const { id } = req.params;
    const user = await UserModel.findById(id);

    if (!user) {
      return sendError(res, `User with ID ${id} not found`, null, 404);
    }

    return sendSuccess(res, 'User details fetched successfully', user, 200);
  } catch (error) {
    next(error);
  }
};

// POST /api/users - Create New User
export const createUser = async (req, res, next) => {
  try {
    // Validation check
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return sendError(res, 'Validation failed', errors.array(), 400);
    }

    const { name, email, age, city } = req.body;

    // Email duplication check
    const existingUser = await UserModel.findByEmail(email);
    if (existingUser) {
      return sendError(res, 'Email is already registered', null, 400);
    }

    const newUser = await UserModel.create({ name, email, age, city });
    return sendSuccess(res, 'User created successfully', newUser, 201);
  } catch (error) {
    next(error);
  }
};

// PUT /api/users/:id - Update User
export const updateUser = async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return sendError(res, 'Validation failed', errors.array(), 400);
    }

    const { id } = req.params;
    const { name, email, age, city } = req.body;

    // Check user existence
    const user = await UserModel.findById(id);
    if (!user) {
      return sendError(res, `User with ID ${id} not found`, null, 404);
    }

    // Email conflict check
    if (email !== user.email) {
      const emailExists = await UserModel.findByEmail(email);
      if (emailExists) {
        return sendError(res, 'Email address is already in use by another user', null, 400);
      }
    }

    await UserModel.update(id, { name, email, age, city });
    const updatedUser = await UserModel.findById(id);

    return sendSuccess(res, 'User updated successfully', updatedUser, 200);
  } catch (error) {
    next(error);
  }
};

// DELETE /api/users/:id - Delete User
export const deleteUser = async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return sendError(res, 'Validation failed', errors.array(), 400);
    }

    const { id } = req.params;

    const user = await UserModel.findById(id);
    if (!user) {
      return sendError(res, `User with ID ${id} not found`, null, 404);
    }

    await UserModel.delete(id);
    return sendSuccess(res, `User with ID ${id} deleted successfully`, null, 200);
  } catch (error) {
    next(error);
  }
};
