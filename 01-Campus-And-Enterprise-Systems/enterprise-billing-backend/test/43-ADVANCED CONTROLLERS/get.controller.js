/**
 * Advanced Get Controller Module (GET All & GET Single operations)
 * ES Module Format
 */

import { sendSuccess } from '../39-API RESPONSE PATTERNS/success-response.js';
import { sendError } from '../39-API RESPONSE PATTERNS/error-response.js';

/**
 * Retrieves all resources from the database
 */
export const getAllStudents = async (req, res, next) => {
  try {
    /* SQL execution:
    const [rows] = await pool.query('SELECT id, name, email, course, marks FROM students');
    */

    const mockStudents = [
      { id: 1, name: 'Rahul Sharma', email: 'rahul@example.com', course: 'BCA', marks: 88 },
      { id: 2, name: 'Priya Verma', email: 'priya@example.com', course: 'BCA', marks: 92 }
    ];

    return sendSuccess(res, mockStudents, 'All student records retrieved');
  } catch (error) {
    next(error);
  }
};

/**
 * Retrieves a single resource by unique primary key ID
 */
export const getStudentById = async (req, res, next) => {
  try {
    const studentId = parseInt(req.params.id, 10);

    /* SQL execution:
    const [rows] = await pool.query('SELECT id, name, email, course, marks FROM students WHERE id = ?', [studentId]);
    if (rows.length === 0) {
      return sendError(res, `Student with ID ${studentId} not found`, 404, 'NOT_FOUND');
    }
    return sendSuccess(res, rows[0], 'Student record retrieved');
    */

    if (studentId === 999) {
      return sendError(res, `Student with ID ${studentId} not found`, 404, 'NOT_FOUND');
    }

    const mockStudent = {
      id: studentId,
      name: 'Rahul Sharma',
      email: 'rahul@example.com',
      course: 'BCA',
      marks: 88
    };

    return sendSuccess(res, mockStudent, 'Student record retrieved');
  } catch (error) {
    next(error);
  }
};
