// login-security.js
// Secure Express Login Controller with validation & bcrypt password comparison

import bcrypt from 'bcrypt';
import { body, validationResult } from 'express-validator';
import mysql from 'mysql2/promise';
import dotenv from 'dotenv';
dotenv.config();

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'test_db'
});

// Validation rules
export const loginValidationRules = [
  body('email').isEmail().withMessage('Valid email is required'),
  body('password').notEmpty().withMessage('Password is required')
];

// Controller
export const loginUser = async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: "Validation failed",
        error: errors.array()[0].msg
      });
    }

    const { email, password } = req.body;

    // 1. Fetch user by email
    const [users] = await pool.query(
      'SELECT id, name, email, password FROM users WHERE email = ?',
      [email]
    );

    if (users.length === 0) {
      // Security best practice: Generic failure message prevents account enumeration
      return res.status(401).json({
        success: false,
        message: "Invalid email or password",
        error: "INVALID_CREDENTIALS"
      });
    }

    const user = users[0];

    // 2. Compare password with saved hash
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({
        success: false,
        message: "Invalid email or password",
        error: "INVALID_CREDENTIALS"
      });
    }

    // 3. Login Success (Omit password from output response)
    return res.status(200).json({
      success: true,
      message: "Login successful",
      data: {
        id: user.id,
        name: user.name,
        email: user.email
      }
    });

  } catch (error) {
    console.error("Login Error:", error);
    return res.status(500).json({
      success: false,
      message: "Internal server error during login",
      error: error.message
    });
  }
};
