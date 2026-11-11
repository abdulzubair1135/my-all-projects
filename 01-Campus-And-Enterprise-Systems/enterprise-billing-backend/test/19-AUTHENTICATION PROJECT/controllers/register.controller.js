/**
 * Register Controller
 */

import { validationResult } from 'express-validator';
import UserAuthModel from '../models/User.js';
import { hashPassword } from '../helpers/password.helper.js';

export const registerController = async (req, res, next) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        error: errors.array()
      });
    }

    const { name, email, password, role } = req.body;

    // Check if user already exists
    const existingUser = await UserAuthModel.findByEmail(email);
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'User email is already registered',
        error: 'EMAIL_EXISTS'
      });
    }

    // Hash plain password
    const hashedPassword = await hashPassword(password);

    // Save to Database
    const newUser = await UserAuthModel.create({
      name,
      email,
      password: hashedPassword,
      role: role || 'user'
    });

    return res.status(201).json({
      success: true,
      message: 'User registered successfully',
      data: newUser
    });
  } catch (error) {
    next(error);
  }
};
