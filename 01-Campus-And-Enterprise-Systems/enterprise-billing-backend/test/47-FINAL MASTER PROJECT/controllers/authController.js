import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import * as UserModel from '../models/userModel.js';
import { sendSuccess, sendError } from '../utils/response.js';

export const register = async (req, res, next) => {
  try {
    const { name, email, password, role } = req.body;
    const existing = await UserModel.findByEmail(email);
    if (existing) {
      return sendError(res, 'User already exists with this email address.', null, 400);
    }

    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    const userId = await UserModel.createUser(name, email, hashedPassword, role || 'customer');
    const user = await UserModel.findById(userId);

    return sendSuccess(res, 'User account registered successfully', user, 201);
  } catch (error) {
    next(error);
  }
};

export const login = async (req, res, next) => {
  try {
    const { email, password } = req.body;
    const user = await UserModel.findByEmail(email);
    if (!user) {
      return sendError(res, 'Invalid credentials provided.', null, 400);
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return sendError(res, 'Invalid credentials provided.', null, 400);
    }

    const token = jwt.sign(
      { id: user.id, role: user.role },
      process.env.JWT_SECRET || 'super_secret_master_jwt_key_2026',
      { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
    );

    const userData = { id: user.id, name: user.name, email: user.email, role: user.role, avatar: user.avatar };
    return sendSuccess(res, 'Authentication successful', { user: userData, token }, 200);
  } catch (error) {
    next(error);
  }
};

export const getProfile = async (req, res, next) => {
  try {
    const user = await UserModel.findById(req.user.id);
    if (!user) {
      return sendError(res, 'User not found', null, 404);
    }
    return sendSuccess(res, 'Profile data retrieved', user);
  } catch (error) {
    next(error);
  }
};

export const updateAvatar = async (req, res, next) => {
  try {
    if (!req.file) {
      return sendError(res, 'Please upload an image file.', null, 400);
    }
    const avatarUrl = `/uploads/${req.file.filename}`;
    await UserModel.updateAvatar(req.user.id, avatarUrl);
    return sendSuccess(res, 'Profile avatar updated successfully', { avatarUrl });
  } catch (error) {
    next(error);
  }
};
