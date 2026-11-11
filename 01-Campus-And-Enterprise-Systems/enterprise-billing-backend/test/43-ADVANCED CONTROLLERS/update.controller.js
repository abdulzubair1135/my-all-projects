/**
 * Advanced Update Controller Module (PUT / PATCH operations)
 * ES Module Format
 */

import { sendSuccess } from '../39-API RESPONSE PATTERNS/success-response.js';
import { sendError } from '../39-API RESPONSE PATTERNS/error-response.js';

/**
 * Updates a resource with validation and pre-existence checks
 */
export const updateStudent = async (req, res, next) => {
  try {
    const studentId = parseInt(req.params.id, 10);
    const { name, email, course, marks } = req.body;

    /* Database Update logic:
    // 1. Verify existence
    const [existing] = await pool.query('SELECT id FROM students WHERE id = ?', [studentId]);
    if (existing.length === 0) {
      return sendError(res, `Student with ID ${studentId} not found`, 404, 'NOT_FOUND');
    }

    // 2. Perform SQL Update query
    await pool.query(
      'UPDATE students SET name = ?, email = ?, course = ?, marks = ? WHERE id = ?',
      [name, email, course, marks, studentId]
    );

    // 3. Return updated object
    const [updatedRows] = await pool.query('SELECT * FROM students WHERE id = ?', [studentId]);
    return sendSuccess(res, updatedRows[0], 'Student profile updated successfully');
    */

    if (studentId === 999) {
      return sendError(res, `Student with ID ${studentId} not found`, 404, 'NOT_FOUND');
    }

    const updatedObject = {
      id: studentId,
      name,
      email,
      course,
      marks,
      updatedAt: new Date().toISOString()
    };

    return sendSuccess(res, updatedObject, 'Student profile updated successfully');
  } catch (error) {
    next(error);
  }
};
