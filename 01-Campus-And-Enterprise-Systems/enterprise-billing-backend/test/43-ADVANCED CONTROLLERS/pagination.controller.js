/**
 * Advanced Dedicated Pagination Controller Module
 * ES Module Format
 */

import { sendPaginated } from '../39-API RESPONSE PATTERNS/pagination-response.js';

/**
 * Handles offset-based pagination controller logic
 */
export const getPaginatedRecords = async (req, res, next) => {
  try {
    const page = Math.max(1, parseInt(req.query.page, 10) || 1);
    const limit = Math.max(1, Math.min(100, parseInt(req.query.limit, 10) || 10));
    const offset = (page - 1) * limit;

    /* Database SQL execution:
    const [[{ total }]] = await pool.query('SELECT COUNT(*) as total FROM students WHERE is_deleted = 0');
    const [rows] = await pool.query(
      'SELECT id, name, email, course FROM students WHERE is_deleted = 0 LIMIT ? OFFSET ?',
      [limit, offset]
    );
    */

    const totalRecords = 50;
    const items = Array.from({ length: limit }, (_, index) => ({
      id: offset + index + 1,
      name: `Student Record ${offset + index + 1}`,
      course: 'BCA'
    })).filter(i => i.id <= totalRecords);

    return sendPaginated(res, items, page, limit, totalRecords, 'Paginated list generated successfully');
  } catch (error) {
    next(error);
  }
};

export default getPaginatedRecords;
