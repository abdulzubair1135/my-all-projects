/**
 * Advanced Create Controller Module (POST operations)
 * ES Module Format with mysql2/promise & express-validator integration
 */

import { sendCreated } from '../39-API RESPONSE PATTERNS/create-response.js';
import { sendError } from '../39-API RESPONSE PATTERNS/error-response.js';

// Import real database connection:
// import pool from '../config/db.js';

/**
 * Creates a new resource (e.g. Student) with Duplicate Checks & 201 Response
 */
export const createStudent = async (req, res, next) => {
  try {
    const { name, email, course, marks } = req.body;

    /* Database logic pattern:
    // 1. Check duplicate record
    const [existing] = await pool.query('SELECT id FROM students WHERE email = ?', [email]);
    if (existing.length > 0) {
      return sendError(res, 'Student with this email address already exists', 409, 'DUPLICATE_EMAIL');
    }

    // 2. Perform parameterized SQL INSERT
    const [result] = await pool.query(
      'INSERT INTO students (name, email, course, marks) VALUES (?, ?, ?, ?)',
      [name, email, course, marks]
    );

    const createdRecord = {
      id: result.insertId,
      name,
      email,
      course,
      marks
    };
    */

    // Demo created object representation
    const createdRecord = {
      id: Math.floor(Math.random() * 1000) + 1,
      name,
      email,
      course: course || 'BCA',
      marks: marks || 80,
      createdAt: new Date().toISOString()
    };

    return sendCreated(res, createdRecord, 'Student created successfully');
  } catch (error) {
    next(error);
  }
};

export default createStudent;
