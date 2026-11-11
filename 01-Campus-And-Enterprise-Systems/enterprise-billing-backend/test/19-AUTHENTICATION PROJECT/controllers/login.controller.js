/**
 * Login & Profile Controllers
 */

import { validationResult } from 'express-validator';
import UserAuthModel from '../models/User.js';
import { comparePassword } from '../helpers/password.helper.js';
import { generateToken } from '../helpers/jwt.helper.js';

// Login User
export const loginController = async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        error: errors.array()
      });
    }

    const { email, password } = req.body;

    // Check user in database
    const user = await UserAuthModel.findByEmail(email);
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password credentials',
        error: 'INVALID_CREDENTIALS'
      });
    }

    // Compare password hash
    const isPasswordValid = await comparePassword(password, user.password);
    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password credentials',
        error: 'INVALID_CREDENTIALS'
      });
    }

    // Generate JWT token
    const tokenPayload = {
      id: user.id,
      email: user.email,
      role: user.role
    };

    const token = generateToken(tokenPayload);

    return res.status(200).json({
      success: true,
      message: 'Login successful',
      data: {
        token,
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          role: user.role
        }
      }
    });
  } catch (error) {
    next(error);
  }
};

// Protected Get Current Profile User Controller
export const getProfileController = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const user = await UserAuthModel.findById(userId);

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User profile not found',
        error: 'NOT_FOUND'
      });
    }

    return res.status(200).json({
      success: true,
      message: 'User profile fetched successfully',
      data: user
    });
  } catch (error) {
    next(error);
  }
};
