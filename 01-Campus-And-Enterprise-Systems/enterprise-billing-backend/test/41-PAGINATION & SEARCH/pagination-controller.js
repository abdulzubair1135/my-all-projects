/**
 * Dedicated Pagination Controller Module using mysql2/promise
 * ES Module Format
 */

import sendPaginated from '../39-API RESPONSE PATTERNS/pagination-response.js';

// Simulated DB Connection Mock / Import real db connection
// import pool from '../config/db.js';

export const getPaginatedStudents = async (req, res, next) => {
  try {
    const page = Math.max(1, parseInt(req.query.page, 10) || 1);
    const limit = Math.max(1, Math.min(100, parseInt(req.query.limit, 10) || 10));
    const offset = (page - 1) * limit;

    /* Real DB Query Example:
    const [[{ total }]] = await pool.query('SELECT COUNT(*) as total FROM students');
    const [rows] = await pool.query(
      'SELECT id, name, email, course FROM students ORDER BY id ASC LIMIT ? OFFSET ?',
      [limit, offset]
    );
    */

    // Simulated dataset for testing/demo
    const totalRecords = 35;
    const mockStudents = Array.from({ length: limit }, (_, i) => ({
      id: offset + i + 1,
      name: `Student ${offset + i + 1}`,
      email: `student${offset + i + 1}@example.com`,
      course: 'BCA'
    })).filter(item => item.id <= totalRecords);

    return sendPaginated(
      res,
      mockStudents,
      page,
      limit,
      totalRecords,
      'Paginated student records retrieved'
    );
  } catch (error) {
    next(error);
  }
};

export default getPaginatedStudents;
