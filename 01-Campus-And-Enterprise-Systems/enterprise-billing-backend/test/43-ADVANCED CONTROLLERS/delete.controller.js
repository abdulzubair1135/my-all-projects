/**
 * Advanced Delete Controller Module (Hard & Soft Delete operations)
 * ES Module Format
 */

import { sendSuccess } from '../39-API RESPONSE PATTERNS/success-response.js';
import { sendError } from '../39-API RESPONSE PATTERNS/error-response.js';

/**
 * Hard Delete Controller (Permanently deletes row from database)
 */
export const hardDeleteStudent = async (req, res, next) => {
  try {
    const studentId = parseInt(req.params.id, 10);

    /* Database SQL Hard Delete:
    const [result] = await pool.query('DELETE FROM students WHERE id = ?', [studentId]);
    if (result.affectedRows === 0) {
      return sendError(res, `Student with ID ${studentId} not found`, 404, 'NOT_FOUND');
    }
    */

    if (studentId === 999) {
      return sendError(res, `Student with ID ${studentId} not found`, 404, 'NOT_FOUND');
    }

    return sendSuccess(res, { deletedId: studentId }, `Student with ID ${studentId} permanently deleted`);
  } catch (error) {
    next(error);
  }
};

/**
 * Soft Delete Controller (Marks status = 'deleted' or is_deleted = 1)
 */
export const softDeleteStudent = async (req, res, next) => {
  try {
    const studentId = parseInt(req.params.id, 10);

    /* Database SQL Soft Delete:
    const [result] = await pool.query(
      'UPDATE students SET is_deleted = 1, deleted_at = NOW() WHERE id = ?',
      [studentId]
    );
    if (result.affectedRows === 0) {
      return sendError(res, `Student with ID ${studentId} not found`, 404, 'NOT_FOUND');
    }
    */

    return sendSuccess(res, { id: studentId, is_deleted: true }, 'Student record deactivated successfully');
  } catch (error) {
    next(error);
  }
};
